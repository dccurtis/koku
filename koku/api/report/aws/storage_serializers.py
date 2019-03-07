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
"""Report Serializers."""
from rest_framework import serializers

from api.report.aws.serializers import (FilterSerializer,
                                        GroupBySerializer,
                                        OrderBySerializer,
                                        QueryParamSerializer,
                                        validate_field)
from api.report.serializers import StringOrListField


class AWSStorageGroupBySerializer(GroupBySerializer):
    """Serializer for handling query parameter group_by."""
    SERVICE_CHOICES = (
        ('S3', 'S3'),
        ('Glacier', 'Glacier'),
        ('RDS', 'RDS'),
        ('*', '*')
    )

    services = serializers.ChoiceField(choices=SERVICE_CHOICES,
                                       required=False)
    def __init__(self, *args, **kwargs):
        """Initialize the GroupBySerializer."""
        super().__init__(*args, **kwargs)

class AWSStorageOrderBySerializer(OrderBySerializer):
    """Serializer for handling query parameter order_by."""
    SERVICE_CHOICES = (
        ('S3', 'S3'),
        ('Glacier', 'Glacier'),
        ('RDS', 'RDS')
    )

    services = serializers.ChoiceField(choices=SERVICE_CHOICES,
                                       required=False)


class AWSStorageFilterSerializer(FilterSerializer):
    """Serializer for handling query parameter filter."""
    SERVICE_CHOICES = (
        ('S3', 'S3'),
        ('Glacier', 'Glacier'),
        ('RDS', 'RDS'),
        ('*', '*')
    )
    service = serializers.ChoiceField(choices=SERVICE_CHOICES,
                                        required=False)
    def __init__(self, *args, **kwargs):
        """Initialize the FilterSerializer."""
        super().__init__(*args, **kwargs)

class AWSStorageQueryParamSerializer(QueryParamSerializer):
    """Serializer for handling query parameters."""

    group_by = AWSStorageGroupBySerializer(required=False)
    order_by = AWSStorageOrderBySerializer(required=False)
    filter = AWSStorageFilterSerializer(required=False)

    def __init__(self, *args, **kwargs):
        """Initialize the AWS query param serializer."""
        super().__init__(*args, **kwargs)

        tag_fields = {
            'filter': AWSStorageFilterSerializer(required=False, tag_keys=self.tag_keys),
            'group_by': AWSStorageGroupBySerializer(required=False, tag_keys=self.tag_keys)
        }

        self.fields.update(tag_fields)

    def validate_group_by(self, value):
        """Validate incoming group_by data.

        Args:
            data    (Dict): data to be validated
        Returns:
            (Dict): Validated data
        Raises:
            (ValidationError): if group_by field inputs are invalid
        """
        validate_field(self, 'group_by', AWSStorageGroupBySerializer, value,
                       tag_keys=self.tag_keys)
        return value

    def validate_order_by(self, value):
        """Validate incoming order_by data.

        Args:
            data    (Dict): data to be validated
        Returns:
            (Dict): Validated data
        Raises:
            (ValidationError): if order_by field inputs are invalid
        """
        validate_field(self, 'order_by', AWSStorageOrderBySerializer, value)
        return value

    def validate_filter(self, value):
        """Validate incoming filter data.

        Args:
            data    (Dict): data to be validated
        Returns:
            (Dict): Validated data
        Raises:
            (ValidationError): if filter field inputs are invalid
        """
        # import pdb; pdb.set_trace()
        validate_field(self, 'filter', AWSStorageFilterSerializer, value,
                       tag_keys=self.tag_keys)
        value.update(service=[value.get('service')])
        return value
