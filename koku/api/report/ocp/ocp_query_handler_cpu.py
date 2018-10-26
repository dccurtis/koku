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
"""OCP Query Handling for Reports."""
from django.db.models import (F,
                              Max,
                              Q,
                              Sum,
                              Window)
from django.db.models.functions import DenseRank
from tenant_schemas.utils import tenant_context

from api.report.ocp.ocp_query_handler import OCPReportQueryHandler
from api.report.query_filter import QueryFilterCollection

class OCPReportQueryHandlerCPU(OCPReportQueryHandler):
    """Handles report queries and responses for AWS."""
    default_ordering = {'pod_usage_cpu_core_hours': 'desc'}

    def __init__(self, query_parameters, url_data,
                 tenant, **kwargs):
        """Establish AWS report query handler.

        Args:
            query_parameters    (Dict): parameters for query
            url_data        (String): URL string to provide order information
            tenant    (String): the tenant to use to access CUR data
            kwargs    (Dict): A dictionary for internal query alteration based on path
        """
        super().__init__(query_parameters, url_data,
                         tenant, self.default_ordering, **kwargs)

    def _build_query(self, query_data, query_group_by):
        cpu_usage = self._mapper._report_type_map.get('cpu_usage')
        cpu_request = self._mapper._report_type_map.get('cpu_request')
        cpu_limit = self._mapper._report_type_map.get('cpu_limit')
        query_data = query_data.values(*query_group_by)\
            .annotate(cpu_usage_core_hours=Sum(cpu_usage))\
            .annotate(cpu_requests_core_hours=Sum(cpu_request))\
            .annotate(cpu_limit=Sum(cpu_limit))
        return query_data

    def execute_sum_query(self):
        """Execute query and return provided data when self.is_sum == True.

        Returns:
            (Dict): Dictionary response of query params, data, and total

        """

        query_sum = {'value': 0}
        data = []

        q_table = self._mapper._operation_map.get('tables').get('query')
        with tenant_context(self.tenant):
            query = q_table.objects.filter(self.query_filter)
            query_annotations = self._get_annotations()
            query_data = query.annotate(**query_annotations)
            group_by_value = self._get_group_by()
            query_group_by = ['date'] + group_by_value

            query_order_by = ('-date', )
            # if self.order_field != 'delta':
                # query_order_by += (self.order,)
            query_data = self._build_query(query_data, query_group_by)
            if self._mapper.count:
                # This is a sum because the summary table already
                # has already performed counts
                query_data = query_data.annotate(count=Sum(self._mapper.count))

            if self._limit and group_by_value:
                rank_order = getattr(F(group_by_value.pop()), self.order_direction)()
                dense_rank_by_total = Window(
                    expression=DenseRank(),
                    partition_by=F('date'),
                    order_by=rank_order
                )
                query_data = query_data.annotate(rank=dense_rank_by_total)
                query_order_by = query_order_by + ('rank',)

            if self.order_field != 'delta':
                query_data = query_data.order_by(*query_order_by)

            if query.exists():
                query_sum = self.calculate_total()

            if self._delta:
                query_data = self.add_deltas(query_data, query_sum)

            is_csv_output = self._accept_type and 'text/csv' in self._accept_type

            if is_csv_output:
                if self._limit:
                    data = self._ranked_list(list(query_data))
                else:
                    data = list(query_data)
            else:
                data = self._apply_group_by(list(query_data))
                data = self._transform_data(query_group_by, 0, data)
        self.query_sum = query_sum
        self.query_data = data
        return self._format_query_response()

    def calculate_total(self):
        """Calculate aggregated totals for the query.

        Args:
            units_value (str): The unit of the reported total

        Returns:
            (dict) The aggregated totals for the query

        """
        filt_collection = QueryFilterCollection()
        total_filter = self._get_search_filter(filt_collection)

        time_scope_value = self.get_query_param_data('filter',
                                                     'time_scope_value',
                                                     -10)
        time_and_report_filter = Q(time_scope_value=time_scope_value)

        if total_filter is None:
            total_filter = time_and_report_filter
        else:
            total_filter = total_filter & time_and_report_filter

        q_table = self._mapper._operation_map.get('tables').get('total')
        total_query = q_table.objects.filter(total_filter)

        total_dict = {}
        cpu_usage_key = self._mapper._report_type_map.get('cpu_usage')
        cpu_request_key = self._mapper._report_type_map.get('cpu_request')
        cpu_usage_sum = total_query.aggregate(cpu_usage=Sum(cpu_usage_key))
        cpu_request_sum = total_query.aggregate(cpu_request=Sum(cpu_request_key))
        total_dict['cpu_usage_core_hours'] = cpu_usage_sum.get('cpu_usage')
        total_dict['cpu_requests_core_hours'] = cpu_request_sum.get('cpu_request')
        
        return total_dict
