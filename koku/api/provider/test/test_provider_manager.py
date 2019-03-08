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
"""Test the Provider views."""
import json
import logging
from datetime import datetime
from unittest.mock import patch
from dateutil import relativedelta
from dateutil import parser
from tenant_schemas.utils import tenant_context

from api.iam.models import Customer
from api.iam.serializers import UserSerializer
from api.iam.test.iam_test_case import IamTestCase
from api.provider.models import Provider, ProviderAuthentication, ProviderBillingSource
from api.provider.provider_manager import ProviderManager, ProviderManagerError
from api.report.test.ocp.helpers import OCPReportDataGenerator
from rates.models import Rate


class MockResponse:
    """A mock response that can convert response text to json."""

    def __init__(self, status_code, response_text):
        """Initialize the response."""
        self.status_code = status_code
        self.response_text = response_text

    def json(self):
        """Return JSON of response."""
        return json.loads(self.response_text)


class ProviderManagerTest(IamTestCase):
    """Tests for Provider Manager."""

    def setUp(self):
        """Set up the provider manager tests."""
        super().setUp()
        self.customer = Customer.objects.get(
            account_id=self.customer_data['account_id']
        )
        serializer = UserSerializer(data=self.user_data, context=self.request_context)
        if serializer.is_valid(raise_exception=True):
            self.user = serializer.save()

    def test_get_name(self):
        """Can the provider name be returned."""
        # Create Provider
        provider_name = 'sample_provider'
        provider = Provider.objects.create(name=provider_name,
                                           created_by=self.user,
                                           customer=self.customer)

        # Get Provider UUID
        provider_uuid = provider.uuid

        # Get Provider Manager
        manager = ProviderManager(provider_uuid)
        self.assertEqual(manager.get_name(), provider_name)

    def test_get_providers_queryset_for_customer(self):
        """Verify all providers returned by a customer."""
        # Verify no providers are returned
        self.assertFalse(ProviderManager.get_providers_queryset_for_customer(self.customer).exists())

        # Create Providers
        provider_1 = Provider.objects.create(name='provider1',
                                             created_by=self.user,
                                             customer=self.customer)
        provider_2 = Provider.objects.create(name='provider2',
                                             created_by=self.user,
                                             customer=self.customer)

        providers = ProviderManager.get_providers_queryset_for_customer(self.customer)
        # Verify providers are returned
        provider_1_found = False
        provider_2_found = False

        for provider in providers:
            if provider.uuid == provider_1.uuid:
                provider_1_found = True
            elif provider.uuid == provider_2.uuid:
                provider_2_found = True

        self.assertTrue(provider_1_found)
        self.assertTrue(provider_2_found)
        self.assertEqual((len(providers)), 2)

    def test_is_removable_by_user(self):
        """Can current user remove provider."""
        # Create Provider
        provider = Provider.objects.create(name='providername',
                                           created_by=self.user,
                                           customer=self.customer)
        provider_uuid = provider.uuid
        user_data = self._create_user_data()
        request_context = self._create_request_context(self._create_customer_data(),
                                                       user_data)
        new_user = None
        serializer = UserSerializer(data=user_data, context=request_context)
        if serializer.is_valid(raise_exception=True):
            new_user = serializer.save()

        manager = ProviderManager(provider_uuid)
        self.assertTrue(manager.is_removable_by_user(self.user))
        self.assertFalse(manager.is_removable_by_user(new_user))

    def test_provider_manager_error(self):
        """Raise ProviderManagerError."""
        with self.assertRaises(ProviderManagerError):
            ProviderManager(uuid='4216c8c7-8809-4381-9a24-bd965140efe2')

        with self.assertRaises(ProviderManagerError):
            ProviderManager(uuid='abc')

    @patch('api.provider.provider_manager.ProviderManager._delete_report_data')
    def test_remove_aws(self, mock_delete_report):
        """Remove aws provider."""
        # Create Provider
        provider_authentication = ProviderAuthentication.objects.create(provider_resource_name='arn:aws:iam::2:role/mg')
        provider_billing = ProviderBillingSource.objects.create(bucket='my_s3_bucket')
        provider = Provider.objects.create(name='awsprovidername',
                                           created_by=self.user,
                                           customer=self.customer,
                                           authentication=provider_authentication,
                                           billing_source=provider_billing)
        provider_uuid = provider.uuid

        new_user_dict = self._create_user_data()
        request_context = self._create_request_context(self.customer_data,
                                                       new_user_dict, False)
        user_serializer = UserSerializer(data=new_user_dict, context=request_context)
        other_user = None
        if user_serializer.is_valid(raise_exception=True):
            other_user = user_serializer.save()

        with tenant_context(self.tenant):
            manager = ProviderManager(provider_uuid)
            manager.remove(other_user)
        provider_query = Provider.objects.all().filter(uuid=provider_uuid)
        auth_count = ProviderAuthentication.objects.count()
        billing_count = ProviderBillingSource.objects.count()
        self.assertFalse(provider_query)
        self.assertEqual(auth_count, 0)
        self.assertEqual(billing_count, 0)

    @patch('api.provider.provider_manager.ProviderManager._delete_report_data')
    def test_remove_aws_auth_billing_remain(self, mock_delete_report):
        """Remove aws provider."""
        # Create Provider
        provider_authentication = ProviderAuthentication.objects.create(provider_resource_name='arn:aws:iam::2:role/mg')
        provider_authentication2 = ProviderAuthentication.objects.create(
            provider_resource_name='arn:aws:iam::3:role/mg'
        )
        provider_billing = ProviderBillingSource.objects.create(bucket='my_s3_bucket')
        provider = Provider.objects.create(name='awsprovidername',
                                           created_by=self.user,
                                           customer=self.customer,
                                           authentication=provider_authentication,
                                           billing_source=provider_billing)
        provider2 = Provider.objects.create(name='awsprovidername2',
                                            created_by=self.user,
                                            customer=self.customer,
                                            authentication=provider_authentication2,
                                            billing_source=provider_billing)
        provider_uuid = provider2.uuid

        self.assertNotEqual(provider.uuid, provider2.uuid)
        new_user_dict = self._create_user_data()
        request_context = self._create_request_context(self.customer_data,
                                                       new_user_dict, False)
        user_serializer = UserSerializer(data=new_user_dict, context=request_context)
        other_user = None
        if user_serializer.is_valid(raise_exception=True):
            other_user = user_serializer.save()

        with tenant_context(self.tenant):
            manager = ProviderManager(provider_uuid)
            manager.remove(other_user)
        auth_count = ProviderAuthentication.objects.count()
        billing_count = ProviderBillingSource.objects.count()
        provider_query = Provider.objects.all().filter(uuid=provider_uuid)

        self.assertFalse(provider_query)
        self.assertEqual(auth_count, 1)
        self.assertEqual(billing_count, 1)

    @patch('api.provider.provider_manager.ProviderManager._delete_report_data')
    def test_remove_ocp(self, mock_delete_report):
        """Remove ocp provider."""
        # Create Provider
        provider_authentication = ProviderAuthentication.objects.create(provider_resource_name='cluster_id_1001')
        provider = Provider.objects.create(name='ocpprovidername',
                                           created_by=self.user,
                                           customer=self.customer,
                                           authentication=provider_authentication,)
        provider_uuid = provider.uuid

        new_user_dict = self._create_user_data()
        request_context = self._create_request_context(self.customer_data,
                                                       new_user_dict, False)
        user_serializer = UserSerializer(data=new_user_dict, context=request_context)
        other_user = None
        if user_serializer.is_valid(raise_exception=True):
            other_user = user_serializer.save()

        with tenant_context(self.tenant):
            rate = {'provider_uuid': provider.uuid,
                    'metric': Rate.METRIC_CPU_CORE_USAGE_HOUR,
                    'rates': {'tiered_rate': [{
                        'unit': 'USD',
                        'value': 1.0,
                        'usage_start': None,
                        'usage_end': None
                    }]}
                    }

            Rate.objects.create(**rate)
            manager = ProviderManager(provider_uuid)
            manager.remove(other_user)
            rates_query = Rate.objects.all().filter(provider_uuid=provider_uuid)
            self.assertFalse(rates_query)
        provider_query = Provider.objects.all().filter(uuid=provider_uuid)
        self.assertFalse(provider_query)

    @patch('api.provider.provider_manager.requests.delete')
    def test_delete_report_data(self, mock_delete):
        """Test that the masu API call returns a response."""
        logging.disable(logging.NOTSET)

        response = MockResponse(200, '{"Response": "OK"}')
        mock_delete.return_value = response
        expected_message = f'INFO:api.provider.provider_manager:Response: {response.json()}'

        provider_authentication = ProviderAuthentication.objects.create(
            provider_resource_name='arn:aws:iam::2:role/mg'
        )
        provider_billing = ProviderBillingSource.objects.create(
            bucket='my_s3_bucket'
        )
        provider = Provider.objects.create(name='awsprovidername',
                                           created_by=self.user,
                                           customer=self.customer,
                                           authentication=provider_authentication,
                                           billing_source=provider_billing)
        provider_uuid = provider.uuid
        manager = ProviderManager(provider_uuid)

        with self.assertLogs('api.provider.provider_manager', level='INFO') as logger:
            manager._delete_report_data()
            self.assertIn(expected_message, logger.output)

    def test_provider_statistics(self):
        """Test that the provider statistics method returns report stats."""
        # Create Provider
        provider_authentication = ProviderAuthentication.objects.create(provider_resource_name='cluster_id_1001')
        provider = Provider.objects.create(name='ocpprovidername',
                                           type='OCP',
                                           created_by=self.user,
                                           customer=self.customer,
                                           authentication=provider_authentication,)

        data_generator = OCPReportDataGenerator(self.tenant)
        data_generator.add_data_to_tenant(provider.id)

        provider_uuid = provider.uuid
        manager = ProviderManager(provider_uuid)

        stats = manager.provider_statistics(self.tenant)

        self.assertIn(str(data_generator.dh.this_month_start.date()), stats.keys())
        self.assertIn(str(data_generator.dh.last_month_start.date()), stats.keys())

        for key, value in stats.items():
            key_date_obj = parser.parse(key)
            value_data = value.pop()

            self.assertIsNotNone(value_data.get('assembly_id'))
            self.assertIsNotNone(value_data.get('files_processed'))
            self.assertEqual(value_data.get('billing_period_start'), key_date_obj.date())
            self.assertGreater(parser.parse(value_data.get('last_process_start_date')), key_date_obj)
            self.assertGreater(parser.parse(value_data.get('last_process_complete_date')), key_date_obj)
            self.assertGreater(parser.parse(value_data.get('summary_data_creation_datetime')), key_date_obj)
            self.assertGreater(parser.parse(value_data.get('summary_data_updated_datetime')), key_date_obj)

    def test_provider_statistics_no_report_data(self):
        """Test that the provider statistics method returns no report stats with no report data."""
        # Create Provider
        provider_authentication = ProviderAuthentication.objects.create(provider_resource_name='cluster_id_1001')
        provider = Provider.objects.create(name='ocpprovidername',
                                           type='OCP',
                                           created_by=self.user,
                                           customer=self.customer,
                                           authentication=provider_authentication,)

        data_generator = OCPReportDataGenerator(self.tenant)
        data_generator.remove_data_from_reporting_common()
        data_generator.remove_data_from_tenant()

        provider_uuid = provider.uuid
        manager = ProviderManager(provider_uuid)

        stats = manager.provider_statistics(self.tenant)
        self.assertEqual(stats, {})

    def test_provider_statistics_negative_case(self):
        """Test that the provider statistics method returns None for tenant misalignment."""
        # Create Provider
        provider_authentication = ProviderAuthentication.objects.create(provider_resource_name='cluster_id_1001')
        provider = Provider.objects.create(name='ocpprovidername',
                                           type='AWS',
                                           created_by=self.user,
                                           customer=self.customer,
                                           authentication=provider_authentication,)

        data_generator = OCPReportDataGenerator(self.tenant)
        data_generator.add_data_to_tenant(provider.id)

        provider_uuid = provider.uuid
        manager = ProviderManager(provider_uuid)

        stats = manager.provider_statistics(self.tenant)

        self.assertIn(str(data_generator.dh.this_month_start.date()), stats.keys())
        self.assertIn(str(data_generator.dh.last_month_start.date()), stats.keys())

        for key, value in stats.items():
            key_date_obj = parser.parse(key)
            value_data = value.pop()

            self.assertIsNotNone(value_data.get('assembly_id'))
            self.assertIsNotNone(value_data.get('files_processed'))
            self.assertEqual(value_data.get('billing_period_start'), key_date_obj.date())
            self.assertGreater(parser.parse(value_data.get('last_process_start_date')), key_date_obj)
            self.assertGreater(parser.parse(value_data.get('last_process_complete_date')), key_date_obj)
            self.assertIsNone(value_data.get('summary_data_creation_datetime'))
            self.assertIsNone(value_data.get('summary_data_updated_datetime'))

    def test_provider_is_processing_in_progress(self):
        """Test is_processing_in_progress."""
        # Create Provider
        provider_authentication = ProviderAuthentication.objects.create(provider_resource_name='cluster_id_1001')
        provider = Provider.objects.create(name='ocpprovidername',
                                           type='OCP',
                                           created_by=self.user,
                                           customer=self.customer,
                                           authentication=provider_authentication,)

        data_generator = OCPReportDataGenerator(self.tenant)
        data_generator.add_data_to_tenant(provider.id)

        provider_uuid = provider.uuid
        manager = ProviderManager(provider_uuid)

        stats = manager.provider_statistics(self.tenant)

        self.assertIn(str(data_generator.dh.this_month_start.date()), stats.keys())
        self.assertIn(str(data_generator.dh.last_month_start.date()), stats.keys())

        for key, value in stats.items():
            key_date_obj = parser.parse(key)
            value_data = value.pop()

            self.assertIsNotNone(value_data.get('assembly_id'))
            self.assertIsNotNone(value_data.get('files_processed'))
            self.assertEqual(value_data.get('billing_period_start'), key_date_obj.date())
            self.assertGreater(parser.parse(value_data.get('last_process_start_date')), key_date_obj)
            self.assertGreater(parser.parse(value_data.get('last_process_complete_date')), key_date_obj)
            self.assertGreater(parser.parse(value_data.get('summary_data_creation_datetime')), key_date_obj)
            self.assertGreater(parser.parse(value_data.get('summary_data_updated_datetime')), key_date_obj)

        self.assertFalse(manager.is_processing_in_progress(self.tenant))


    def test_provider_is_processing_in_progress_missing_file(self):
        """Test is_processing_in_progress when 1/2 files are processed."""
        # Create Provider
        current_month = datetime.today().date().replace(day=1)
        stats_response = {}
        stats_response[str(current_month)] = [{'assembly_id': '1f54e1ec-1dc3-4626-ba96-e5a812279a08',
                                               'billing_period_start': current_month,
                                               'files_processed': '1/2',
                                               'last_process_start_date': '2019-03-03 00:00:00',
                                               'last_process_complete_date': '2019-03-04 00:00:00',
                                               'summary_data_creation_datetime': '2019-03-07 22:11:19',
                                               'summary_data_updated_datetime': '2019-03-07 22:11:19'}]

        provider_authentication = ProviderAuthentication.objects.create(provider_resource_name='cluster_id_1001')
        provider = Provider.objects.create(name='ocpprovidername',
                                           type='OCP',
                                           created_by=self.user,
                                           customer=self.customer,
                                           authentication=provider_authentication,)

        provider_uuid = provider.uuid
        manager = ProviderManager(provider_uuid)

        with patch.object(ProviderManager, 'provider_statistics', return_value=stats_response):
            self.assertTrue(manager.is_processing_in_progress(self.tenant))

    def test_provider_is_processing_in_progress_missing_line_processing(self):
        """Test is_processing_in_progress when line processing not complete."""
        # Create Provider
        current_month = datetime.today().date().replace(day=1)
        stats_response = {}
        stats_response[str(current_month)] = [{'assembly_id': '1f54e1ec-1dc3-4626-ba96-e5a812279a08',
                                               'billing_period_start': current_month,
                                               'files_processed': '1/1',
                                               'last_process_start_date': '2019-03-03 00:00:00',
                                               'last_process_complete_date': None,
                                               'summary_data_creation_datetime': '2019-03-07 22:11:19',
                                               'summary_data_updated_datetime': '2019-03-07 22:11:19'}]

        provider_authentication = ProviderAuthentication.objects.create(provider_resource_name='cluster_id_1001')
        provider = Provider.objects.create(name='ocpprovidername',
                                           type='OCP',
                                           created_by=self.user,
                                           customer=self.customer,
                                           authentication=provider_authentication,)

        provider_uuid = provider.uuid
        manager = ProviderManager(provider_uuid)

        with patch.object(ProviderManager, 'provider_statistics', return_value=stats_response):
            self.assertTrue(manager.is_processing_in_progress(self.tenant))

    def test_provider_is_processing_in_progress_missing_summary_processing(self):
        """Test is_processing_in_progress when line processing not complete."""
        # Create Provider
        current_month = datetime.today().date().replace(day=1)
        stats_response = {}
        stats_response[str(current_month)] = [{'assembly_id': '1f54e1ec-1dc3-4626-ba96-e5a812279a08',
                                               'billing_period_start': current_month,
                                               'files_processed': '1/1',
                                               'last_process_start_date': '2019-03-03 00:00:00',
                                               'last_process_complete_date': '2019-03-04 00:00:00',
                                               'summary_data_creation_datetime': '2019-03-07 22:11:19',
                                               'summary_data_updated_datetime': None}]

        provider_authentication = ProviderAuthentication.objects.create(provider_resource_name='cluster_id_1001')
        provider = Provider.objects.create(name='ocpprovidername',
                                           type='OCP',
                                           created_by=self.user,
                                           customer=self.customer,
                                           authentication=provider_authentication,)

        provider_uuid = provider.uuid
        manager = ProviderManager(provider_uuid)

        with patch.object(ProviderManager, 'provider_statistics', return_value=stats_response):
            self.assertTrue(manager.is_processing_in_progress(self.tenant))
