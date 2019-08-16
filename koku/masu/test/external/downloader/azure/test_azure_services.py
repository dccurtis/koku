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

"""Test the AzureService object."""
from unittest.mock import patch
from datetime import datetime
from dateutil.relativedelta import relativedelta
from faker import Faker

from masu.external.downloader.azure.azure_service import AzureService, AzureCostReportNotFound

from masu.test import MasuTestCase

FAKE = Faker()


class MockAzureClientFactory:
    def __init__(self, subscription_id, container_name, current_date_time):
        self._subscription_id = subscription_id
        self._container_name = container_name
        self._current_date_time = current_date_time

    def describe_cost_management_exports(self):
        return [{"name": self.export_name, "container": self.container, "directory": self.directory}]

    def cloud_storage_account(self, resource_group_name, storage_account_name):
        class MockBlobProperties:
            def __init__(self, last_modified_date):
                self.last_modified = last_modified_date

        class MockBlob:
            def __init__(self, container_name, last_modified):
                self.name = '{}_{}_day_{}'.format(container_name, 'blob', last_modified.day)
                self.properties = MockBlobProperties(last_modified)

        class MockBlobService:
            def __init__(self, context_container_name, current_day_time):
                self._container_name = context_container_name
                self._current_day_time = current_day_time

            def list_blobs(self, container_name):
                today = self._current_day_time
                yesterday = today - relativedelta(days=1)
                if container_name == self._container_name:
                    blob_list = [MockBlob(self._container_name, today),
                                 MockBlob(self._container_name, yesterday)]
                    return blob_list
                else:
                    return []

        class MockStorageAccount:
            def __init__(self, context_container_name, current_date_time):
                self._container_name = context_container_name
                self._current_date_time = current_date_time

            def create_block_blob_service(self):
                return MockBlobService(self._container_name, self._current_date_time)
        return MockStorageAccount(self._container_name, self._current_date_time)

    @property
    def credentials(self):
        """Service Principal Credentials property."""
        creds = "secretcreds"
        return creds

    @property
    def subscription_id(self):
        """Subscription ID property."""
        return self._subscription_id

    @property
    def cost_management_client(self):
        """Get cost management client with subscription and credentials."""
        class Mock
        class MockExports:
            def list(self, scope):
                return []

        class MockCostManagementClient:
            exports = MockExports()
        return MockCostManagementClient()

class AzureServiceTest(MasuTestCase):
    """Test Cases for the AzureService object."""

    @patch('masu.external.downloader.azure.azure_service.AzureClientFactory')
    def setUp(self, mock_factory):
        """Set up each test."""

        super().setUp()
        self.subscription_id = FAKE.uuid4()
        self.tenant_id = FAKE.uuid4()
        self.client_id = FAKE.uuid4()
        self.client_secret = FAKE.word()
        self.resource_group_name = FAKE.word()
        self.storage_account_name = FAKE.word()

        self.container_name = FAKE.word()
        self.current_date_time = datetime.today()
        mock_factory.return_value = MockAzureClientFactory(self.subscription_id,
                                                           self.container_name,
                                                           self.current_date_time)

        self.client = AzureService(
            subscription_id=self.subscription_id,
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            client_secret=self.client_secret,
            resource_group_name=self.resource_group_name,
            storage_account_name=self.storage_account_name)

    def test_initializer(self):
        """Test the AzureService initializer."""
        self.assertIsNotNone(self.client._factory)
        self.assertIsNotNone(self.client._cloud_storage_account)

    def test_get_cost_export_for_key(self):
        """Test that a cost export is retrieved by a key."""
        today = self.current_date_time
        yesterday = today - relativedelta(days=1)
        test_matrix = [{'key': '{}_{}_day_{}'.format(self.container_name, 'blob', today.day),
                        'expected_date': today.date()},
                       {'key': '{}_{}_day_{}'.format(self.container_name, 'blob', yesterday.day),
                        'expected_date': yesterday.date()}]

        for test in test_matrix:
            key = test.get('key')
            expected_modified_date = test.get('expected_date')
            cost_export = self.client.get_cost_export_for_key(key, self.container_name)
            self.assertIsNotNone(cost_export)
            self.assertEquals(cost_export.name, key)
            self.assertEquals(cost_export.properties.last_modified.date(), expected_modified_date)

    def test_get_cost_export_for_missing_key(self):
        """Test that a cost export is not retrieved by an incorrect key."""
        key = '{}_{}_wrong'.format(self.container_name, 'blob')
        with self.assertRaises(AzureCostReportNotFound):
            self.client.get_cost_export_for_key(key, self.container_name)

    def test_get_latest_cost_export_for_path(self):
        """Test that the latest cost export is returned for a given path."""
        report_path = '{}_{}'.format(self.container_name, 'blob')
        cost_export = self.client.get_latest_cost_export_for_path(report_path, self.container_name)
        self.assertEquals(cost_export.properties.last_modified.date(), self.current_date_time.date())

    def test_get_latest_cost_export_for_path_missing(self):
        """Test that the no cost export is returned for a missing path."""
        report_path = FAKE.word()
        with self.assertRaises(AzureCostReportNotFound):
            self.client.get_latest_cost_export_for_path(report_path, self.container_name)

    def test_describe_cost_management_exports(self):
        """Test that cost management exports are returned for the account."""
        import pdb; pdb.set_trace()
        exports = self.client.describe_cost_management_exports()
