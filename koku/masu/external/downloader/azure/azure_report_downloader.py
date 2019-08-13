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
"""Azure Report Downloader."""

# pylint: disable=fixme
# disabled until we get travis to not fail on warnings, or the fixme is
# resolved.

import datetime
import json
import logging
import os
import shutil
import struct

import boto3
from botocore.exceptions import ClientError

from masu.config import Config
from masu.exceptions import MasuProviderError
from masu.external import UNCOMPRESSED
from masu.external.downloader.downloader_interface import DownloaderInterface
from masu.external.downloader.report_downloader_base import ReportDownloaderBase
from masu.util.azure import common as utils
from masu.external.downloader.azure.azure_service import AzureService
from masu.util.common import extract_uuids_from_string

DATA_DIR = Config.TMP_DIR
LOG = logging.getLogger(__name__)


class AzureReportDownloaderError(Exception):
    """AWS Report Downloader error."""


class AzureReportDownloaderNoFileError(Exception):
    """AWS Report Downloader error for missing file."""


class AzureReportDownloader(ReportDownloaderBase, DownloaderInterface):
    """
    Azure Cost and Usage Report Downloader.

    """

    empty_manifest = {'reportKeys': []}

    def __init__(self, customer_name, auth_credential, bucket, report_name=None, **kwargs):
        """
        Constructor.

        Args:
            customer_name    (String) Name of the customer
            auth_credential  (String) Authentication credential for S3 bucket (RoleARN)
            report_name      (String) Name of the Cost Usage Report to download (optional)
            bucket           (String) Name of the S3 bucket containing the CUR

        """
        super().__init__(**kwargs)
        self._provider_id = kwargs.get('provider_id')

        self.resource_group_name = auth_credential.get('resource_group_name') #'RG1'
        self.storage_account_name = auth_credential.get('storage_account_name') #'mysa1'
        self.container_name = bucket #'output'
        self.export_name = report_name #'cost/costreport'
        #blob = AzureService().get_latest_cost_export(
        #    self.resource_group_name, self.storage_account_name, self.container_name, self.export_name)
        #print(f'{blob.name} = {blob.properties.etag} - {blob.properties.last_modified}')

    def _get_report_path(self, date_time):
        """
        Return path of report files.

        Args:
            date_time (DateTime): The starting datetime object

        Returns:
            (String): "/prefix/report_name/YYYYMMDD-YYYYMMDD",
                    example: "/my-prefix/my-report/19701101-19701201"

        """
        report_date_range = utils.month_date_range(date_time)
        return '{}/{}'.format(self.export_name,
                              report_date_range)

    def _get_manifest(self, date_time):
        """
        Download and return the CUR manifest for the given date.

        Args:
            date_time (DateTime): The starting datetime object

        Returns:
            (Dict): A dict-like object serialized from JSON data.

        """
        billing_period_range = self._get_report_path(date_time)
        blob = AzureService().get_cost_export_for_date(billing_period_range,
                                                       self.resource_group_name,
                                                       self.storage_account_name,
                                                       self.container_name,
                                                       self.export_name)
        report_name = blob.name
        manifest = {}
        manifest['uuid'] = ''
        manifest['assemblyId'] = extract_uuids_from_string(report_name).pop()
        billing_period = {'start': (billing_period_range.split('/')[-1]).split('-')[0],
                          'end': (billing_period_range.split('/')[-1]).split('-')[1]}
        manifest['billingPeriod'] = billing_period
        manifest['reportKeys'] = [report_name]
        
        return manifest

    def get_report_context_for_date(self, date_time):
        """
        Get the report context for a provided date.

        Args:
            date_time (DateTime): The starting datetime object

        Returns:
            ({}) Dictionary containing the following keys:
                manifest_id - (String): Manifest ID for ReportManifestDBAccessor
                assembly_id - (String): UUID identifying report file
                compression - (String): Report compression format
                files       - ([]): List of report files.

        """
        should_download = True
        manifest_dict = {}
        report_dict = {}
        manifest = self._get_manifest(date_time)
        import pdb; pdb.set_trace()
        manifest_id = None
        if manifest != {}:
            manifest_dict = self._prepare_db_manifest_record(manifest)
            should_download = self.check_if_manifest_should_be_downloaded(
                manifest_dict.get('assembly_id')
            )

        if not should_download:
            manifest_id = self._get_existing_manifest_db_id(manifest_dict.get('assembly_id'))
            stmt = ('This manifest has already been downloaded and processed:\n'
                    ' customer: {},\n'
                    ' provider_id: {},\n'
                    ' manifest_id: {}')
            stmt = stmt.format(self.customer_name,
                               self._provider_id,
                               manifest_id)
            LOG.info(stmt)
            return report_dict

        if manifest_dict:
            manifest_id = self._process_manifest_db_record(
                manifest_dict.get('assembly_id'),
                manifest_dict.get('billing_start'),
                manifest_dict.get('num_of_files')
            )

            report_dict['manifest_id'] = manifest_id
            report_dict['assembly_id'] = manifest.get('assemblyId')
            report_dict['compression'] = self.report.get('Compression')
            report_dict['files'] = manifest.get('reportKeys')
        return report_dict


    @property
    def manifest_date_format(self):
        """Set the Azure manifest date format."""
        return '%Y%m%d'

    def _prepare_db_manifest_record(self, manifest):
        """Prepare to insert or update the manifest DB record."""
        assembly_id = manifest.get('assemblyId')
        billing_str = manifest.get('billingPeriod', {}).get('start')
        billing_start = datetime.datetime.strptime(
            billing_str,
            self.manifest_date_format
        )
        num_of_files = len(manifest.get('reportKeys', []))
        return {
            'assembly_id': assembly_id,
            'billing_start': billing_start,
            'num_of_files': num_of_files
        }

    def get_local_file_for_report(self, report):
        pass

    def download_file(self, key, stored_etag=None):
        pass
    