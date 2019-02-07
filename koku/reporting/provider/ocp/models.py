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

"""Models for OCP cost entry tables."""

from django.contrib.postgres.fields import ArrayField, JSONField
from django.contrib.postgres.indexes import GinIndex
from django.db import models


class OCPUsageReportPeriod(models.Model):
    """The report period information for a Operator Metering report.

    The reporting period (1 month) will cover many reports.

    """

    class Meta:
        """Meta for OCPUsageReportPeriod."""

        unique_together = ('cluster_id', 'report_period_start')

    cluster_id = models.CharField(max_length=50, null=False)
    report_period_start = models.DateTimeField(null=False)
    report_period_end = models.DateTimeField(null=False)

    summary_data_creation_datetime = models.DateTimeField(null=True)
    summary_data_updated_datetime = models.DateTimeField(null=True)
    # provider_id is intentionally not a foreign key
    # to prevent masu complication
    provider_id = models.IntegerField(null=True)


class OCPUsageReport(models.Model):
    """An entry for a single report from Operator Metering.

    A cost entry covers a specific time interval (e.g. 1 hour).

    """

    class Meta:
        """Meta for OCPUsageReport."""

        unique_together = ('report_period', 'interval_start')

        indexes = [
            models.Index(
                fields=['interval_start'],
                name='ocp_interval_start_idx',
            ),
        ]

    interval_start = models.DateTimeField(null=False)
    interval_end = models.DateTimeField(null=False)

    report_period = models.ForeignKey('OCPUsageReportPeriod',
                                      on_delete=models.PROTECT)


class OCPUsageLineItem(models.Model):
    """Raw report data for OpenShift pods."""

    class Meta:
        """Meta for OCPUsageLineItem."""

        unique_together = ('report', 'namespace', 'pod', 'node')

    id = models.BigAutoField(primary_key=True)

    report_period = models.ForeignKey('OCPUsageReportPeriod',
                                      on_delete=models.PROTECT)

    report = models.ForeignKey('OCPUsageReport',
                               on_delete=models.PROTECT)

    # Kubernetes objects by convention have a max name length of 253 chars
    namespace = models.CharField(max_length=253, null=False)

    pod = models.CharField(max_length=253, null=False)

    node = models.CharField(max_length=253, null=False)

    # Another node identifier used to tie the node to an EC2 instance
    resource_id = models.CharField(max_length=253, null=True)

    pod_usage_cpu_core_seconds = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    pod_request_cpu_core_seconds = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    pod_limit_cpu_core_seconds = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    pod_usage_memory_byte_seconds = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    pod_request_memory_byte_seconds = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    pod_limit_memory_byte_seconds = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    node_capacity_cpu_cores = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    node_capacity_cpu_core_seconds = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    node_capacity_memory_bytes = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    node_capacity_memory_byte_seconds = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    pod_labels = JSONField(null=True)


class OCPUsageLineItemDaily(models.Model):
    """A daily aggregation of line items.

    This table is aggregated by OCP resource.

    """

    class Meta:
        """Meta for OCPUsageLineItemDaily."""

        db_table = 'reporting_ocpusagelineitem_daily'

        indexes = [
            models.Index(
                fields=['usage_start'],
                name='ocp_usage_idx',
            ),
            models.Index(
                fields=['namespace'],
                name='namespace_idx',
            ),
            models.Index(
                fields=['pod'],
                name='pod_idx',
            ),
            models.Index(
                fields=['node'],
                name='node_idx',
            ),
        ]

    id = models.BigAutoField(primary_key=True)

    cluster_id = models.CharField(max_length=50, null=True)

    cluster_alias = models.CharField(max_length=256, null=True)

    # Kubernetes objects by convention have a max name length of 253 chars
    namespace = models.CharField(max_length=253, null=False)

    pod = models.CharField(max_length=253, null=False)

    node = models.CharField(max_length=253, null=False)

    # Another node identifier used to tie the node to an EC2 instance
    resource_id = models.CharField(max_length=253, null=True)

    usage_start = models.DateTimeField(null=False)
    usage_end = models.DateTimeField(null=False)

    pod_usage_cpu_core_seconds = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    pod_request_cpu_core_seconds = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    pod_limit_cpu_core_seconds = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    pod_usage_memory_byte_seconds = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    pod_request_memory_byte_seconds = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    pod_limit_memory_byte_seconds = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    node_capacity_cpu_cores = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    node_capacity_cpu_core_seconds = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    node_capacity_memory_bytes = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    node_capacity_memory_byte_seconds = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    cluster_capacity_cpu_core_seconds = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    cluster_capacity_memory_byte_seconds = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    total_seconds = models.IntegerField()

    pod_labels = JSONField(null=True)


class OCPUsageLineItemDailySummary(models.Model):
    """A daily aggregation of line items.

    This table is aggregated by OCP resource.

    """

    class Meta:
        """Meta for OCPUsageLineItemDailySummary."""

        db_table = 'reporting_ocpusagelineitem_daily_summary'

        indexes = [
            models.Index(
                fields=['usage_start'],
                name='summary_ocp_usage_idx',
            ),
            models.Index(
                fields=['namespace'],
                name='summary_namespace_idx',
            ),
            models.Index(
                fields=['pod'],
                name='summary_pod_idx',
            ),
            models.Index(
                fields=['node'],
                name='summary_node_idx',
            ),
            GinIndex(
                fields=['pod_labels'],
                name='pod_labels_idx',
            ),
        ]

    id = models.BigAutoField(primary_key=True)

    cluster_id = models.CharField(max_length=50, null=True)

    cluster_alias = models.CharField(max_length=256, null=True)

    # Kubernetes objects by convention have a max name length of 253 chars
    namespace = models.CharField(max_length=253, null=False)

    pod = models.CharField(max_length=253, null=False)

    node = models.CharField(max_length=253, null=False)

    # Another node identifier used to tie the node to an EC2 instance
    resource_id = models.CharField(max_length=253, null=True)

    usage_start = models.DateTimeField(null=False)
    usage_end = models.DateTimeField(null=False)

    pod_labels = JSONField(null=True)

    pod_usage_cpu_core_hours = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    pod_request_cpu_core_hours = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    pod_limit_cpu_core_hours = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    pod_charge_cpu_core_hours = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    pod_usage_memory_gigabyte_hours = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    pod_request_memory_gigabyte_hours = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    pod_charge_memory_gigabyte_hours = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    pod_limit_memory_gigabyte_hours = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    node_capacity_cpu_cores = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    node_capacity_cpu_core_hours = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    node_capacity_memory_gigabytes = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    node_capacity_memory_gigabyte_hours = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    cluster_capacity_cpu_core_hours = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    cluster_capacity_memory_gigabyte_hours = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )


class OCPUsageLineItemAggregates(models.Model):
    """Total aggregates for OCP usage.

    This table is aggregated by namespace, pod, and node.
    The contents of this table should be considered ephemeral.
    It will be regularly deleted from and repopulated.

    """

    class Meta:
        """Meta for OCPUsageLineItemDailySummary."""

        db_table = 'reporting_ocpusagelineitem_aggregates'

    time_scope_value = models.IntegerField()

    cluster_id = models.CharField(max_length=50, null=True)

    # Kubernetes objects by convention have a max name length of 253 chars
    namespace = models.CharField(max_length=253, null=False)

    pod = models.CharField(max_length=253, null=False)

    node = models.CharField(max_length=253, null=False)

    # Another node identifier used to tie the node to an EC2 instance
    resource_id = models.CharField(max_length=253, null=True)

    pod_usage_cpu_core_hours = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    pod_request_cpu_core_hours = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    pod_limit_cpu_core_hours = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    pod_usage_memory_gigabytes = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    pod_request_memory_gigabytes = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    pod_limit_memory_gigabytes = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    node_capacity_cpu_cores = models.DecimalField(
        max_digits=20,
        decimal_places=6,
        null=True
    )

    node_capacity_cpu_core_hours = models.DecimalField(
        max_digits=20,
        decimal_places=6,
        null=True
    )

    node_capacity_memory_bytes = models.DecimalField(
        max_digits=20,
        decimal_places=6,
        null=True
    )

    node_capacity_memory_byte_hours = models.DecimalField(
        max_digits=20,
        decimal_places=6,
        null=True
    )


class OCPUsagePodLabelSummary(models.Model):
    """A collection of all current existing tag key and values."""

    class Meta:
        """Meta for OCPUsageTagSummary."""

        db_table = 'reporting_ocpusagepodlabel_summary'

    key = models.CharField(primary_key=True, max_length=253)
    values = ArrayField(models.CharField(max_length=253))


class OCPAWSCostLineItemDaily(models.Model):
    """A daily view of OCP and AWS daily entries that share a resource_id."""

    class Meta:
        """Meta for OCPAWSCostLineItemDaily."""

        db_table = 'reporting_ocpawscostlineitem_daily'
        managed = False

    # OCP Fields
    cluster_id = models.CharField(max_length=50, null=True)

    cluster_alias = models.CharField(max_length=256, null=True)

    # Kubernetes objects by convention have a max name length of 253 chars
    namespace = models.CharField(max_length=253, null=False)

    pod = models.CharField(max_length=253, null=False)

    node = models.CharField(max_length=253, null=False)

    # Another node identifier used to tie the node to an EC2 instance
    resource_id = models.CharField(max_length=253, null=True)

    usage_start = models.DateTimeField(null=False)

    usage_end = models.DateTimeField(null=False)

    pod_usage_cpu_core_seconds = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    pod_request_cpu_core_seconds = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    pod_limit_cpu_core_seconds = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    pod_usage_memory_byte_seconds = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    pod_request_memory_byte_seconds = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    pod_limit_memory_byte_seconds = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    node_capacity_cpu_cores = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    node_capacity_cpu_core_seconds = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    node_capacity_memory_bytes = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    node_capacity_memory_byte_seconds = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    cluster_capacity_cpu_core_seconds = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    cluster_capacity_memory_byte_seconds = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    total_seconds = models.IntegerField()

    pod_labels = JSONField(null=True)

    # AWS Fields
    cost_entry_product = models.ForeignKey('AWSCostEntryProduct',
                                           on_delete=models.DO_NOTHING, null=True)

    cost_entry_pricing = models.ForeignKey('AWSCostEntryPricing',
                                           on_delete=models.DO_NOTHING, null=True)

    cost_entry_reservation = models.ForeignKey('AWSCostEntryReservation',
                                               on_delete=models.DO_NOTHING,
                                               null=True)

    line_item_type = models.CharField(max_length=50, null=False)

    usage_account_id = models.CharField(max_length=50, null=False)

    product_code = models.CharField(max_length=50, null=False)

    usage_type = models.CharField(max_length=50, null=True)

    operation = models.CharField(max_length=50, null=True)

    availability_zone = models.CharField(max_length=50, null=True)

    usage_amount = models.FloatField(null=True)

    normalization_factor = models.FloatField(null=True)

    normalized_usage_amount = models.FloatField(null=True)

    currency_code = models.CharField(max_length=10)

    unblended_rate = models.DecimalField(max_digits=17, decimal_places=9,
                                         null=True)

    unblended_cost = models.DecimalField(max_digits=17, decimal_places=9,
                                         null=True)

    blended_rate = models.DecimalField(max_digits=17, decimal_places=9,
                                       null=True)

    blended_cost = models.DecimalField(max_digits=17, decimal_places=9,
                                       null=True)

    public_on_demand_cost = models.DecimalField(max_digits=17, decimal_places=9,
                                                null=True)

    public_on_demand_rate = models.DecimalField(max_digits=17, decimal_places=9,
                                                null=True)

    tax_type = models.TextField(null=True)

    tags = JSONField(null=True)


class OCPAWSCostLineItemDailySummary(models.Model):
    """A summarized view of OCP on AWS cost."""

    class Meta:
        """Meta for OCPAWSCostLineItemDailySummary."""

        db_table = 'reporting_ocpawscostlineitem_daily_summary'

        indexes = [
            models.Index(
                fields=['usage_start'],
                name='cost_summary_ocp_usage_idx',
            ),
            models.Index(
                fields=['namespace'],
                name='cost_summary_namespace_idx',
            ),
            models.Index(
                fields=['node'],
                name='cost_summary_node_idx',
            ),
            GinIndex(
                fields=['pod_labels'],
                name='cost_pod_labels_idx',
            ),
        ]

    # OCP Fields
    cluster_id = models.CharField(max_length=50, null=True)

    cluster_alias = models.CharField(max_length=256, null=True)

    # Kubernetes objects by convention have a max name length of 253 chars
    namespace = models.CharField(max_length=253, null=False)

    pod = models.CharField(max_length=253, null=False)

    node = models.CharField(max_length=253, null=False)

    # Another node identifier used to tie the node to an EC2 instance
    resource_id = models.CharField(max_length=253, null=True)

    usage_start = models.DateTimeField(null=False)

    usage_end = models.DateTimeField(null=False)

    pod_labels = JSONField(null=True)

    # AWS Fields
    product_code = models.CharField(max_length=50, null=False)

    product_family = models.CharField(max_length=150, null=True)

    usage_account_id = models.CharField(max_length=50, null=False)

    account_alias = models.ForeignKey('AWSAccountAlias',
                                      on_delete=models.PROTECT,
                                      null=True)

    availability_zone = models.CharField(max_length=50, null=True)

    region = models.CharField(max_length=50, null=True)

    unit = models.CharField(max_length=63, null=True)

    tags = JSONField(null=True)

    # Cost breakdown can be done by cluster, node, project, and pod.
    # Cluster and node cost can be determined by summing the AWS unblended_cost
    # with a GROUP BY cluster/node.
    # Project cost is a summation of pod_cost with a GROUP BY project
    # The cost of un-utilized resources = sum(unblended_cost) - sum(pod_cost)
    unblended_cost = models.DecimalField(max_digits=17, decimal_places=9,
                                         null=True)

    pod_cost = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

class OCPStorageLineItem(models.Model):
    """Raw report storage data for OpenShift pods."""

    class Meta:
        """Meta for OCPStorageLineItem."""

        unique_together = ('report', 'namespace', 'persistentvolumeclaim',)

    id = models.BigAutoField(primary_key=True)

    report_period = models.ForeignKey('OCPUsageReportPeriod',
                                      on_delete=models.PROTECT)

    report = models.ForeignKey('OCPUsageReport',
                               on_delete=models.PROTECT)

    # Kubernetes objects by convention have a max name length of 253 chars
    namespace = models.CharField(max_length=253, null=False)

    pod = models.CharField(max_length=253, null=True)

    persistentvolumeclaim = models.CharField(max_length=253)

    persistentvolume = models.CharField(max_length=253, null=True)

    storageclass = models.CharField(max_length=50, null=True)

    persistentvolumeclaim_capacity_bytes = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    persistentvolumeclaim_capacity_byte_seconds = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    volume_request_storage_byte_seconds = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    persistentvolumeclaim_usage_byte_seconds = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    persistentvolume_labels = JSONField(null=True)
    persistentvolumeclaim_labels = JSONField(null=True)

class OCPUStorageLineItemDaily(models.Model):
    """A daily aggregation of storage line items.

    This table is aggregated by OCP resource.

    """

    class Meta:
        """Meta for OCPUStorageLineItemDaily."""

        db_table = 'reporting_ocpstoragelineitem_daily'

    id = models.BigAutoField(primary_key=True)

    cluster_id = models.CharField(max_length=50, null=True)

    cluster_alias = models.CharField(max_length=256, null=True)

    # Kubernetes objects by convention have a max name length of 253 chars
    namespace = models.CharField(max_length=253, null=False)

    pod = models.CharField(max_length=253, null=True)

    usage_start = models.DateTimeField(null=False)
    usage_end = models.DateTimeField(null=False)

    persistentvolumeclaim_capacity_bytes = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    persistentvolumeclaim_capacity_byte_seconds = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    volume_request_storage_byte_seconds = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    persistentvolumeclaim_usage_byte_seconds = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    total_seconds = models.IntegerField()

    persistentvolume_labels = JSONField(null=True)
    persistentvolumeclaim_labels = JSONField(null=True)

class OCPStorageLineItemDailySummary(models.Model):
    """A daily aggregation of storage line items.

    This table is aggregated by OCP resource.

    """

    class Meta:
        """Meta for OCPStorageLineItemDailySummary."""

        db_table = 'reporting_ocpstoragelineitem_daily_summary'

    id = models.BigAutoField(primary_key=True)

    cluster_id = models.CharField(max_length=50, null=True)

    cluster_alias = models.CharField(max_length=256, null=True)

    # Kubernetes objects by convention have a max name length of 253 chars
    namespace = models.CharField(max_length=253, null=False)

    pod = models.CharField(max_length=253, null=False)

    usage_start = models.DateTimeField(null=False)
    usage_end = models.DateTimeField(null=False)

    persistentvolume_labels = JSONField(null=True)
    persistentvolumeclaim_labels = JSONField(null=True)

    persistentvolumeclaim_capacity_gigabyte = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    persistentvolumeclaim_capacity_gigabyte_hours = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    volume_request_storage_gigabyte_hours = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )

    persistentvolumeclaim_usage_gigabyte_hours = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True
    )
