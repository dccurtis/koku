#
# Copyright 2019 Red Hat, Inc.
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
"""Sources HTTP Client."""
import requests
from requests.exceptions import RequestException
from sources.config import Config


class SourcesHTTPClientError(Exception):
    """SourcesHTTPClient Error."""

    pass


class SourcesHTTPClient:
    """Sources HTTP client for Sources API service."""

    def __init__(self, auth_header, source_id=None):
        """Initialize the client."""
        self._source_id = source_id
        self._sources_host = Config.SOURCES_API_URL
        self._base_url = '{}{}'.format(self._sources_host, Config.SOURCES_API_PREFIX)
        self._internal_url = '{}{}'.format(self._sources_host, Config.SOURCES_INTERNAL_API_PREFIX)

        header = {'x-rh-identity': auth_header}
        self._identity_header = header

    def get_source_details(self):
        """Get details on source_id."""
        url = '{}/{}/{}'.format(self._base_url, 'sources', str(self._source_id))
        r = requests.get(url, headers=self._identity_header)
        if r.status_code != 200:
            raise SourcesHTTPClientError('Status Code: ', r.status_code)
        response = r.json()
        return response

    def get_endpoint_id(self):
        """Get Sources Endpoint ID from Source ID."""
        endpoint_url = '{}/endpoints?filter[source_id]={}'.format(
            self._base_url, self._source_id)
        r = requests.get(endpoint_url, headers=self._identity_header)

        if r.status_code != 200:
            raise SourcesHTTPClientError('Status Code: ', r.status_code)
        endpoint_response = r.json()

        if not endpoint_response.get('data'):
            raise SourcesHTTPClientError(f'No authentication details for Source: {self._source_id}')
        endpoint_id = endpoint_response.get('data')[0].get('id')

        return endpoint_id

    def get_cost_management_application_type_id(self):
        """Get the cost management application type id."""
        application_type_url = '{}/application_types?filter[name]=/insights/platform/cost-management'.format(
            self._base_url)
        try:
            r = requests.get(application_type_url, headers=self._identity_header)
        except RequestException as conn_error:
            raise SourcesHTTPClientError('Unable to get cost management application ID Type. Reason: ', str(conn_error))

        if r.status_code != 200:
            raise SourcesHTTPClientError(f'Status Code: {r.status_code}. Response: {r.text}')

        endpoint_response = r.json()
        application_type_id = endpoint_response.get('data')[0].get('id')
        return int(application_type_id)

    def get_source_type_name(self, type_id):
        """Get the source name for a give type id."""
        application_type_url = '{}/source_types?filter[id]={}'.format(
            self._base_url, type_id)
        try:
            r = requests.get(application_type_url, headers=self._identity_header)
        except RequestException as conn_error:
            raise SourcesHTTPClientError('Unable to get source name. Reason: ', str(conn_error))

        if r.status_code != 200:
            raise SourcesHTTPClientError(f'Status Code: {r.status_code}. Response: {r.text}')

        endpoint_response = r.json()
        source_name = endpoint_response.get('data')[0].get('name')
        return source_name

    def get_aws_role_arn(self):
        """Get the roleARN from Sources Authentication service."""
        endpoint_url = '{}/endpoints?filter[source_id]={}'.format(self._base_url, str(self._source_id))
        r = requests.get(endpoint_url, headers=self._identity_header)
        endpoint_response = r.json()
        resource_id = endpoint_response.get('data')[0].get('id')

        authentications_url = \
            '{}/authentications?filter[resource_type]=Endpoint&[authtype]=arn&[resource_id]={}'.format(self._base_url,
                                                                                                       str(resource_id))
        r = requests.get(authentications_url, headers=self._identity_header)
        authentications_response = r.json()
        if not authentications_response.get('data'):
            raise SourcesHTTPClientError(f'No authentication details for Source: {self._source_id}')
        authentications_id = authentications_response.get('data')[0].get('id')

        authentications_internal_url = '{}/authentications/{}?expose_encrypted_attribute[]=password'.format(
            self._internal_url, str(authentications_id))
        r = requests.get(authentications_internal_url, headers=self._identity_header)
        authentications_internal_response = r.json()
        password = authentications_internal_response.get('password')

        return password

    def get_azure_credentials(self):
        """Get the Azure Credentials from Sources Authentication service."""
        endpoint_url = '{}/endpoints?filter[source_id]={}'.format(self._base_url, str(self._source_id))
        r = requests.get(endpoint_url, headers=self._identity_header)
        endpoint_response = r.json()
        resource_id = endpoint_response.get('data')[0].get('id')

        authentications_url = \
            (f'{self._base_url}/authentications?filter[resource_type]=Endpoint&'
             f'[authtype]=tenant_id_client_id_client_secret&[resource_id]={str(resource_id)}')
        r = requests.get(authentications_url, headers=self._identity_header)
        authentications_response = r.json()
        if not authentications_response.get('data'):
            raise SourcesHTTPClientError(f'No authentication details for Source: {self._source_id}')
        data_dict = authentications_response.get('data')[0]
        authentications_id = data_dict.get('id')

        authentications_internal_url = '{}/authentications/{}?expose_encrypted_attribute[]=password'.format(
            self._internal_url, str(authentications_id))
        r = requests.get(authentications_internal_url, headers=self._identity_header)
        authentications_internal_response = r.json()
        password = authentications_internal_response.get('password')

        azure_credentials = {'client_id': data_dict.get('username'),
                             'client_secret': password,
                             'tenant_id': data_dict.get('extra').get('azure').get('tenant_id')}
        return azure_credentials

    def set_source_status(self, error_msg):
        """Set the source status with error message."""
        application_query_url = '{}/applications?filter[source_id]={}'.format(self._base_url, str(self._source_id))
        application_query_response = requests.get(application_query_url, headers=self._identity_header)
        application_id = application_query_response.json().get('data')[0].get('id')

        application_url = '{}/applications/{}'.format(self._base_url, str(application_id))
        if error_msg:
            status = "unavailable"
        else:
            status = "available"
            error_msg = ""
        json_data = {"availability_status": status, "availability_status_error": str(error_msg)}
        application_response = requests.patch(application_url, json=json_data, headers=self._identity_header)
        if application_response.status_code != 204:
            raise SourcesHTTPClientError(f'Unable to set status for Source: {self._source_id}')
