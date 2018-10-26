#
# Copyright 2018 Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
"""Query Handling for Reports."""
import datetime
import logging
from collections import OrderedDict
from decimal import Decimal, DivisionByZero, InvalidOperation
from itertools import groupby

from dateutil import relativedelta
from django.db.models import Value
from django.db.models.functions import (Concat,
                                        TruncDay,
                                        TruncMonth)

from api.report.query_filter import QueryFilter, QueryFilterCollection
from api.utils import DateHelper
from reporting.models import (AWSCostEntryLineItem,
                              AWSCostEntryLineItemAggregates,
                              AWSCostEntryLineItemDailySummary,
                              OCPUsageLineItem,
                              OCPUsageLineItemDailySummary,
                              OCPUsageLineItemAggregates)

LOG = logging.getLogger(__name__)
WILDCARD = '*'
OPERATION_SUM = 'sum'
OPERATION_NONE = 'none'


class ProviderMap(object):
    """Data structure mapping between API params and DB Model names.

    The idea here is that reports ought to be operating on largely similar
    data - counts, costs, etc. The only variable is determining which
    DB tables and fields are supplying the requested data.

    ProviderMap supplies ReportQueryHandler with the appropriate model
    references.
    """

    # main mapping data structure
    # this data should be considered static and read-only.
    mapping = [{
        'provider': 'AWS',
        'operation': {
            OPERATION_SUM: {
                'alias': 'account_alias__account_alias',
                'annotations': {'account': 'usage_account_id',
                                'service': 'product_code',
                                'avail_zone': 'availability_zone'},
                'end_date': 'usage_end',
                'filters': {
                    'account': {'field': 'account_alias__account_alias',
                                'operation': 'icontains'},
                    'service': {'field': 'product_code',
                                'operation': 'icontains'},
                    'avail_zone': {'field': 'availability_zone',
                                   'operation': 'icontains'},
                    'region': {'field': 'availability_zone',
                               'operation': 'icontains'}
                },
                'report_type': {
                    'costs': {
                        'aggregate_key': 'unblended_cost',
                        'count': None,
                        'filter': {},
                        'units_key': 'currency_code',
                    },
                    'instance_type': {
                        'aggregate_key': 'usage_amount',
                        'count': 'resource_count',
                        'filter': {
                            'field': 'instance_type',
                            'operation': 'isnull',
                            'parameter': False
                        },
                        'units_key': 'unit',
                    },
                    'storage': {
                        'aggregate_key': 'usage_amount',
                        'count': None,
                        'filter': {
                            'field': 'product_family',
                            'operation': 'contains',
                            'parameter': 'Storage'
                        },
                        'units_key': 'unit',
                    }
                },
                'start_date': 'usage_start',
                'tables': {'previous_query': AWSCostEntryLineItemDailySummary,
                           'query': AWSCostEntryLineItemDailySummary,
                           'total': AWSCostEntryLineItemAggregates},
            },
            OPERATION_NONE: {
                'alias': 'account_alias__account_alias',
                'annotations': {'account': 'usage_account_id',
                                'service': 'product_code',
                                'avail_zone': 'availability_zone',
                                'region': 'cost_entry_product__region'},
                'end_date': 'usage_end',
                'filters': {
                    'account': {'field': 'account_alias__account_alias',
                                'operation': 'icontains'},
                    'service': {'field': 'product_code',
                                'operation': 'icontains'},
                    'avail_zone': {'field': 'availability_zone',
                                   'operation': 'icontains'},
                    'region': {'field': 'availability_zone',
                               'operation': 'icontains',
                               'table': 'cost_entry_product'}
                },
                'report_type': {
                    'costs': {
                        'aggregate_key': 'unblended_cost',
                        'count': None,
                        'filter': {},
                        'units_key': 'currency_code',
                    },
                    'instance_type': {
                        'aggregate_key': 'usage_amount',
                        'count': 'resource_id',
                        'filter': {
                            'field': 'instance_type',
                            'table': 'cost_entry_product',
                            'operation': 'isnull',
                            'parameter': False
                        },
                        'units_key': 'cost_entry_pricing__unit',
                    },
                    'storage': {
                        'aggregate_key': 'usage_amount',
                        'count': None,
                        'filter': {
                            'field': 'product_family',
                            'table': 'cost_entry_product',
                            'operation': 'contains',
                            'parameter': 'Storage'
                        },
                        'units_key': 'cost_entry_pricing__unit',
                    },
                },
                'start_date': 'usage_start',
                'tables': {'query': AWSCostEntryLineItem,
                           'previous_query': AWSCostEntryLineItem,
                           'total': AWSCostEntryLineItemAggregates},
            }
        },
    },
    {
        'provider': 'OCP',
        'operation': {
            OPERATION_SUM: {
                'annotations': {'cluster': 'cluster_id',
                                'project': 'namespace',
                                'cpu_usage': 'pod_usage_cpu_core_hours',
                                'cpu_request': 'pod_request_cpu_core_hours',
                                'cpu_limit': 'pod_limit_cpu_cores'},
                'end_date': 'usage_end',
                'filters': {
                    'project': {'field': 'namespace',
                                'operation': 'icontains'},
                    'cluster': {'field': 'cluster_id',
                                'operation': 'icontains'},
                    'pod': {'field': 'pod',
                                   'operation': 'icontains'},
                },
                'report_type': {
                    'cpu': {
                        'aggregate_key': 'pod_usage_cpu_core_hours',
                        'cpu_usage': 'pod_usage_cpu_core_hours',
                        'cpu_request': 'pod_request_cpu_core_hours',
                        'cpu_limit': 'pod_limit_cpu_cores',
                        'count': None,
                        'filter': {},
                    },
                    'mem': {
                        'aggregate_key': 'pod_usage_cpu_core_hours',
                        'mem_usage': 'pod_usage_memory_gigabytes',
                        'mem_request' : 'pod_request_memory_gigabytes',
                        'count': None,
                        'filter': {},
                    }
                },
                'start_date': 'usage_start',
                'tables': {'previous_query': OCPUsageLineItemDailySummary,
                           'query': OCPUsageLineItemDailySummary,
                           'total': OCPUsageLineItemAggregates},
            },
        },
    }]

    @staticmethod
    def provider_data(provider):
        """Return provider portion of map structure."""
        for item in ProviderMap.mapping:
            if provider in item.get('provider'):
                return item

    @staticmethod
    def operation_data(operation, provider):
        """Return operation portion of map structure."""
        prov = ProviderMap.provider_data(provider)
        return prov.get('operation').get(operation)

    @staticmethod
    def report_type_data(report_type, operation, provider):
        """Return report_type portion of map structure."""
        op_data = ProviderMap.operation_data(operation, provider)
        return op_data.get('report_type').get(report_type)

    def __init__(self, provider, operation, report_type):
        """Constructor."""
        self._provider = provider
        self._operation = operation
        self._report_type = report_type

        self._map = ProviderMap.mapping
        self._provider_map = ProviderMap.provider_data(provider)
        self._operation_map = ProviderMap.operation_data(operation, provider)
        self._report_type_map = ProviderMap.report_type_data(report_type, operation, provider)

    @property
    def count(self):
        """Return the count property."""
        return self._report_type_map.get('count')

    @property
    def units_key(self):
        """Return the units_key property."""
        return self._report_type_map.get('units_key')


class TruncDayString(TruncDay):
    """Class to handle string formated day truncation."""

    def convert_value(self, value, expression, connection):
        """Convert value to a string after super."""
        value = super().convert_value(value, expression, connection)
        return value.strftime('%Y-%m-%d')


class TruncMonthString(TruncMonth):
    """Class to handle string formated day truncation."""

    def convert_value(self, value, expression, connection):
        """Convert value to a string after super."""
        value = super().convert_value(value, expression, connection)
        return value.strftime('%Y-%m')


class ReportQueryHandler(object):
    """Handles report queries and responses."""

    def __init__(self, query_parameters, url_data,
                 tenant, default_ordering, group_by_options, **kwargs):
        """Establish report query handler.

        Args:
            query_parameters    (Dict): parameters for query
            url_data        (String): URL string to provide order information
            tenant    (String): the tenant to use to access CUR data
            kwargs    (Dict): A dictionary for internal query alteration based on path
        """
        LOG.debug(f'Query Params: {query_parameters}')

        self.default_ordering = default_ordering
        self.group_by_options = group_by_options
        self._accept_type = None
        self._annotations = None
        self._group_by = None
        self.end_datetime = None
        self.resolution = None
        self.start_datetime = None
        self.time_interval = []
        self.time_scope_units = None
        self.time_scope_value = None

        self.query_parameters = query_parameters
        self.tenant = tenant
        self.url_data = url_data

        self.operation = self.query_parameters.get('operation', OPERATION_SUM)

        self._delta = self.query_parameters.get('delta')
        self._limit = self.get_query_param_data('filter', 'limit')
        self._get_timeframe()
        self.query_delta = {'value': None, 'percent': None}

        if kwargs:
            elements = ['accept_type', 'annotations', 'delta',
                        'group_by', 'report_type']
            for key, value in kwargs.items():
                if key in elements:
                    setattr(self, f'_{key}', value)

        assert getattr(self, '_report_type'), \
            'kwargs["report_type"] is missing!'
        self._mapper = ProviderMap(provider=kwargs.get('provider'),
                                   operation=self.operation,
                                   report_type=self._report_type)
        self.query_filter = self._get_filter()

    @property
    def is_sum(self):
        """Determine the type of API call this is.

        is_sum == True -> API Summary data
        is_sum == False -> Full data download

        """
        return self.operation == OPERATION_SUM

    @staticmethod
    def has_wildcard(in_list):
        """Check if list has wildcard.

        Args:
            in_list (List[String]): List of strings to check for wildcard
        Return:
            (Boolean): if wildcard is present in list
        """
        if not in_list:
            return False
        return any(WILDCARD == item for item in in_list)

    def check_query_params(self, key, in_key):
        """Test if query parameters has a given key and key within it.

        Args:
        key     (String): key to check in query parameters
        in_key  (String): key to check if key is found in query parameters

        Returns:
            (Boolean): True if they keys given appear in given query parameters.

        """
        return (self.query_parameters and key in self.query_parameters and  # noqa: W504
                in_key in self.query_parameters.get(key))

    def get_query_param_data(self, dictkey, key, default=None):
        """Extract the value from a query parameter dictionary or return None.

        Args:
            dictkey (String): the key to access a query parameter dictionary
            key     (String): the key to obtain from the dictionar data
        Returns:
            (Object): The value found with the given key or the default value
        """
        value = default
        if self.check_query_params(dictkey, key):
            value = self.query_parameters.get(dictkey).get(key)
        return value

    @property
    def order_field(self):
        """Order-by field name.

        The default is 'total'
        """
        order_by = self.query_parameters.get('order_by', self.default_ordering)
        return list(order_by.keys()).pop()

    @property
    def order_direction(self):
        """Order-by orientation value.

        Returns:
            (str) 'asc' or 'desc'; default is 'desc'

        """
        order_by = self.query_parameters.get('order_by', self.default_ordering)
        return list(order_by.values()).pop()

    @property
    def order(self):
        """Extract order_by parameter and apply ordering to the appropriate field.

        Returns:
            (String): Ordering value. Default is '-total'

        Example:
            `order_by[total]=asc` returns `total`
            `order_by[total]=desc` returns `-total`

        """
        order_map = {'asc': '', 'desc': '-'}
        return f'{order_map[self.order_direction]}{self.order_field}'

    def get_resolution(self):
        """Extract resolution or provide default.

        Returns:
            (String): The value of how data will be sliced.

        """
        if self.resolution:
            return self.resolution

        self.resolution = self.get_query_param_data('filter', 'resolution')
        time_scope_value = self.get_time_scope_value()
        if not self.resolution:
            self.resolution = 'daily'
            if int(time_scope_value) in [-1, -2]:
                self.resolution = 'monthly'

        if self.resolution == 'monthly':
            self.date_to_string = lambda dt: dt.strftime('%Y-%m')
            self.string_to_date = lambda dt: datetime.datetime.strptime(dt, '%Y-%m').date()
            self.date_trunc = TruncMonthString
            self.gen_time_interval = DateHelper().list_months
        else:
            self.date_to_string = lambda dt: dt.strftime('%Y-%m-%d')
            self.string_to_date = lambda dt: datetime.datetime.strptime(dt, '%Y-%m-%d').date()
            self.date_trunc = TruncDayString
            self.gen_time_interval = DateHelper().list_days

        return self.resolution

    def get_time_scope_units(self):
        """Extract time scope units or provide default.

        Returns:
            (String): The value of how data will be sliced.

        """
        if self.time_scope_units:
            return self.time_scope_units

        time_scope_units = self.get_query_param_data('filter', 'time_scope_units')
        time_scope_value = self.get_query_param_data('filter', 'time_scope_value')
        if not time_scope_units:
            time_scope_units = 'day'
            if time_scope_value and int(time_scope_value) in [-1, -2]:
                time_scope_units = 'month'

        self.time_scope_units = time_scope_units
        return self.time_scope_units

    def get_time_scope_value(self):
        """Extract time scope value or provide default.

        Returns:
            (Integer): time relative value providing query scope

        """
        if self.time_scope_value:
            return self.time_scope_value

        time_scope_units = self.get_query_param_data('filter', 'time_scope_units')
        time_scope_value = self.get_query_param_data('filter', 'time_scope_value')

        if not time_scope_value:
            time_scope_value = -10
            if time_scope_units == 'month':
                time_scope_value = -1

        self.time_scope_value = int(time_scope_value)
        return self.time_scope_value

    def _create_time_interval(self):
        """Create list of date times in interval.

        Returns:
            (List[DateTime]): List of all interval slices by resolution

        """
        self.time_interval = sorted(self.gen_time_interval(
            self.start_datetime,
            self.end_datetime))
        return self.time_interval

    def _get_timeframe(self):
        """Obtain timeframe start and end dates.

        Returns:
            (DateTime): start datetime for query filter
            (DateTime): end datetime for query filter

        """
        self.get_resolution()
        time_scope_value = self.get_time_scope_value()
        time_scope_units = self.get_time_scope_units()
        start = None
        end = None
        dh = DateHelper()
        if time_scope_units == 'month':
            if time_scope_value == -1:
                # get current month
                start = dh.this_month_start
                end = dh.this_month_end
            else:
                # get previous month
                start = dh.last_month_start
                end = dh.last_month_end
        else:
            if time_scope_value == -10:
                # get last 10 days
                start = dh.n_days_ago(dh.this_hour, 10)
                end = dh.this_hour
            else:
                # get last 30 days
                start = dh.n_days_ago(dh.this_hour, 30)
                end = dh.this_hour

        self.start_datetime = start
        self.end_datetime = end
        self._create_time_interval()
        return (self.start_datetime, self.end_datetime, self.time_interval)

    def _get_search_filter(self, filters):
        """Populate the query filter collection for search filters.

        Args:
            filters (QueryFilterCollection): collection of query filters
        Returns:
            (QueryFilterCollection): populated collection of query filters
        """
        # define filter parameters using API query params.
        fields = self._mapper._operation_map.get('filters')
        for q_param, filt in fields.items():
            group_by = self.get_query_param_data('group_by', q_param, list())
            filter_ = self.get_query_param_data('filter', q_param, list())
            list_ = list(set(group_by + filter_))    # uniquify the list
            if list_ and not ReportQueryHandler.has_wildcard(list_):
                for item in list_:
                    q_filter = QueryFilter(parameter=item, **filt)
                    filters.add(q_filter)

        composed_filters = filters.compose()
        LOG.debug(f'_get_search_filter: {composed_filters}')
        return composed_filters

    def _get_filter(self, delta=False):
        """Create dictionary for filter parameters.

        Args:
            delta (Boolean): Construct timeframe for delta
        Returns:
            (Dict): query filter dictionary

        """
        filters = QueryFilterCollection()

        # set up filters for instance-type and storage queries.
        filters.add(**self._mapper._report_type_map.get('filter'))

        if delta:
            if self.time_scope_value in [-1, -2]:
                date_delta = relativedelta.relativedelta(months=1)
            elif self.time_scope_value == -30:
                date_delta = datetime.timedelta(days=30)
            else:
                date_delta = datetime.timedelta(days=10)
            start = self.start_datetime - date_delta
            end = self.end_datetime - date_delta
        else:
            start = self.start_datetime
            end = self.end_datetime

        start_filter = QueryFilter(field='usage_start', operation='gte',
                                   parameter=start)
        end_filter = QueryFilter(field='usage_end', operation='lte',
                                 parameter=end)
        filters.add(query_filter=start_filter)
        filters.add(query_filter=end_filter)

        # define filter parameters using API query params.
        composed_filters = self._get_search_filter(filters)

        LOG.debug(f'_get_filter: {composed_filters}')
        return composed_filters

    def _get_group_by(self):
        """Create list for group_by parameters."""
        group_by = []
        for item in self.group_by_options:
            group_data = self.get_query_param_data('group_by', item)
            if group_data:
                group_pos = self.url_data.index(item)
                group_by.append((item, group_pos))

        group_by = sorted(group_by, key=lambda g_item: g_item[1])
        group_by = [item[0] for item in group_by]
        if self._group_by:
            group_by += self._group_by
        return group_by

    def _get_annotations(self, fields=None):
        """Create dictionary for query annotations.

        Args:
            fields (dict): Fields to create annotations for

        Returns:
            (Dict): query annotations dictionary

        """
        annotations = {
            'date': self.date_trunc('usage_start'),
            'units': Concat(self._mapper.units_key, Value(''))
        }
        if self._annotations and not self.is_sum:
            annotations.update(self._annotations)

        # { query_param: database_field_name }
        if not fields:
            fields = self._mapper._operation_map.get('annotations')

        for q_param, db_field in fields.items():
            annotations[q_param] = Concat(db_field, Value(''))

        return annotations

    @staticmethod
    def _group_data_by_list(group_by_list, group_index, data):
        """Group data by list.

        Args:
            group_by_list (List): list of strings to group data by
            data    (List): list of query results
        Returns:
            (Dict): dictionary of grouped query results or the original data
        """
        group_by_list_len = len(group_by_list)
        if group_index >= group_by_list_len:
            return data

        out_data = OrderedDict()
        curr_group = group_by_list[group_index]

        for key, group in groupby(data, lambda by: by.get(curr_group)):
            grouped = list(group)
            grouped = ReportQueryHandler._group_data_by_list(group_by_list,
                                                             (group_index + 1),
                                                             grouped)
            datapoint = out_data.get(key)
            if datapoint and isinstance(datapoint, dict):
                out_data[key].update(grouped)
            elif datapoint and isinstance(datapoint, list):
                out_data[key] = grouped + datapoint
            else:
                out_data[key] = grouped
        return out_data

    def _apply_group_by(self, query_data):
        """Group data by date for given time interval then group by list.

        Args:
            query_data  (List(Dict)): Queried data
        Returns:
            (Dict): Dictionary of grouped dictionaries

        """
        bucket_by_date = OrderedDict()
        for item in self.time_interval:
            date_string = self.date_to_string(item)
            bucket_by_date[date_string] = []

        for result in query_data:
            date_string = result.get('date')
            date_bucket = bucket_by_date.get(date_string)
            if date_bucket is not None:
                date_bucket.append(result)

        for date, data_list in bucket_by_date.items():
            data = data_list
            if self._limit:
                data = self._ranked_list(data_list)
            group_by = self._get_group_by()
            grouped = ReportQueryHandler._group_data_by_list(group_by, 0,
                                                             data)
            bucket_by_date[date] = grouped
        return bucket_by_date

    def _transform_data(self, groups, group_index, data):
        """Transform dictionary data points to lists."""
        groups_len = len(groups)
        if not groups or group_index >= groups_len:
            return data

        out_data = []
        label = 'values'
        group_type = groups[group_index]
        next_group_index = (group_index + 1)

        if next_group_index < groups_len:
            label = groups[next_group_index] + 's'

        for group, group_value in data.items():
            cur = {group_type: group,
                   label: self._transform_data(groups, next_group_index,
                                               group_value)}
            out_data.append(cur)

        return out_data

    def _percent_delta(self, a, b):
        """Calculate a percent delta.

        Args:
            a (int or float or Decimal) the current value
            b (int or float or Decimal) the previous value

        Returns:
            (Decimal) (a - b) / b * 100

            Returns Decimal(0) if b is zero.

        """
        try:
            return Decimal((a - b) / b * 100)
        except (DivisionByZero, ZeroDivisionError, InvalidOperation):
            return Decimal(0)
