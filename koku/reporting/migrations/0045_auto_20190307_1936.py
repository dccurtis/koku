# Generated by Django 2.1.7 on 2019-03-07 19:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0044_costssummary'),
    ]

    operations = [
        migrations.RunSQL(
            """
            DROP VIEW IF EXISTS reporting_costs_summary;

            CREATE OR REPLACE VIEW reporting_costs_summary AS (
                SELECT usageli.usage_start,
                    usageli.usage_end,
                    usageli.cluster_id,
                    usageli.namespace,
                    usageli.pod,
                    usageli.pod_charge_cpu_core_hours,
                    usageli.pod_charge_memory_gigabyte_hours,
                    storageli.persistentvolumeclaim_charge_gb_month
                FROM reporting_ocpusagelineitem_daily_summary as usageli
                LEFT JOIN reporting_ocpstoragelineitem_daily_summary as storageli
                    ON usageli.usage_start = storageli.usage_start
                        AND usageli.usage_end = storageli.usage_end
                        AND usageli.cluster_id = storageli.cluster_id
                        AND usageli.namespace = storageli.namespace
                        AND usageli.pod = storageli.pod
                WHERE usageli.usage_start = storageli.usage_start
                        AND usageli.usage_end = storageli.usage_end
                        AND usageli.cluster_id = storageli.cluster_id
                        AND usageli.namespace = storageli.namespace
                        AND usageli.pod = storageli.pod
            )
            ;
            """
        )
    ]
