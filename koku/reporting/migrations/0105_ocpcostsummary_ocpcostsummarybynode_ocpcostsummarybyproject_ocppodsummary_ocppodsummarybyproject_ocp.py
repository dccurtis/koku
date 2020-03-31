# Generated by Django 2.2.11 on 2020-03-30 20:22
import django.contrib.postgres.fields.jsonb
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        (
            "reporting",
            "0104_ocpallcomputesummary_ocpallcostsummary_ocpallcostsummarybyaccount_ocpallcostsummarybyregion_ocpallco",
        )
    ]

    operations = [
        migrations.CreateModel(
            name="OCPCostSummary",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("cluster_id", models.TextField()),
                ("cluster_alias", models.TextField(null=True)),
                ("usage_start", models.DateField()),
                ("usage_end", models.DateField()),
                ("infrastructure_raw_cost", models.DecimalField(decimal_places=15, max_digits=33, null=True)),
                ("infrastructure_usage_cost", django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ("infrastructure_markup_cost", models.DecimalField(decimal_places=15, max_digits=33, null=True)),
                ("infrastructure_monthly_cost", models.DecimalField(decimal_places=15, max_digits=33, null=True)),
                ("supplementary_usage_cost", django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ("supplementary_monthly_cost", models.DecimalField(decimal_places=15, max_digits=33, null=True)),
            ],
            options={"db_table": "reporting_ocp_cost_summary", "managed": False},
        ),
        migrations.CreateModel(
            name="OCPCostSummaryByNode",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("cluster_id", models.TextField()),
                ("cluster_alias", models.TextField(null=True)),
                ("node", models.CharField(max_length=253)),
                ("usage_start", models.DateField()),
                ("usage_end", models.DateField()),
                ("infrastructure_raw_cost", models.DecimalField(decimal_places=15, max_digits=33, null=True)),
                ("infrastructure_usage_cost", django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ("infrastructure_markup_cost", models.DecimalField(decimal_places=15, max_digits=33, null=True)),
                ("infrastructure_monthly_cost", models.DecimalField(decimal_places=15, max_digits=33, null=True)),
                ("supplementary_usage_cost", django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ("supplementary_monthly_cost", models.DecimalField(decimal_places=15, max_digits=33, null=True)),
            ],
            options={"db_table": "reporting_ocp_cost_summary_by_node", "managed": False},
        ),
        migrations.CreateModel(
            name="OCPCostSummaryByProject",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("cluster_id", models.TextField()),
                ("cluster_alias", models.TextField(null=True)),
                ("namespace", models.CharField(max_length=253)),
                ("usage_start", models.DateField()),
                ("usage_end", models.DateField()),
                ("infrastructure_project_raw_cost", models.DecimalField(decimal_places=15, max_digits=33, null=True)),
                ("infrastructure_usage_cost", django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                (
                    "infrastructure_project_markup_cost",
                    models.DecimalField(decimal_places=15, max_digits=33, null=True),
                ),
                ("infrastructure_monthly_cost", models.DecimalField(decimal_places=15, max_digits=33, null=True)),
                ("supplementary_usage_cost", django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ("supplementary_monthly_cost", models.DecimalField(decimal_places=15, max_digits=33, null=True)),
            ],
            options={"db_table": "reporting_ocp_cost_summary_by_project", "managed": False},
        ),
        migrations.CreateModel(
            name="OCPPodSummary",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("cluster_id", models.TextField()),
                ("cluster_alias", models.TextField(null=True)),
                (
                    "resource_ids",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=256), null=True, size=None
                    ),
                ),
                ("resource_count", models.IntegerField(null=True)),
                ("data_source", models.CharField(max_length=64, null=True)),
                ("usage_start", models.DateField()),
                ("usage_end", models.DateField()),
                ("infrastructure_raw_cost", models.DecimalField(decimal_places=15, max_digits=33, null=True)),
                ("infrastructure_usage_cost", django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ("infrastructure_markup_cost", models.DecimalField(decimal_places=15, max_digits=33, null=True)),
                ("supplementary_usage_cost", django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ("pod_usage_cpu_core_hours", models.DecimalField(decimal_places=9, max_digits=27, null=True)),
                ("pod_request_cpu_core_hours", models.DecimalField(decimal_places=9, max_digits=27, null=True)),
                ("pod_limit_cpu_core_hours", models.DecimalField(decimal_places=9, max_digits=27, null=True)),
                ("pod_usage_memory_gigabyte_hours", models.DecimalField(decimal_places=9, max_digits=27, null=True)),
                ("pod_request_memory_gigabyte_hours", models.DecimalField(decimal_places=9, max_digits=27, null=True)),
                ("pod_limit_memory_gigabyte_hours", models.DecimalField(decimal_places=9, max_digits=27, null=True)),
                ("cluster_capacity_cpu_core_hours", models.DecimalField(decimal_places=9, max_digits=27, null=True)),
                ("total_capacity_cpu_core_hours", models.DecimalField(decimal_places=9, max_digits=27, null=True)),
                (
                    "total_capacity_memory_gigabyte_hours",
                    models.DecimalField(decimal_places=9, max_digits=27, null=True),
                ),
                (
                    "cluster_capacity_memory_gigabyte_hours",
                    models.DecimalField(decimal_places=9, max_digits=27, null=True),
                ),
            ],
            options={"db_table": "reporting_ocp_pod_summary", "managed": False},
        ),
        migrations.CreateModel(
            name="OCPPodSummaryByProject",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("cluster_id", models.TextField()),
                ("cluster_alias", models.TextField(null=True)),
                ("namespace", models.CharField(max_length=253, null=True)),
                (
                    "resource_ids",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=256), null=True, size=None
                    ),
                ),
                ("resource_count", models.IntegerField(null=True)),
                ("data_source", models.CharField(max_length=64, null=True)),
                ("usage_start", models.DateField()),
                ("usage_end", models.DateField()),
                ("supplementary_usage_cost", django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ("infrastructure_raw_cost", models.DecimalField(decimal_places=15, max_digits=33, null=True)),
                ("infrastructure_usage_cost", django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ("infrastructure_markup_cost", models.DecimalField(decimal_places=15, max_digits=33, null=True)),
                ("pod_usage_cpu_core_hours", models.DecimalField(decimal_places=9, max_digits=27, null=True)),
                ("pod_request_cpu_core_hours", models.DecimalField(decimal_places=9, max_digits=27, null=True)),
                ("pod_limit_cpu_core_hours", models.DecimalField(decimal_places=9, max_digits=27, null=True)),
                ("pod_usage_memory_gigabyte_hours", models.DecimalField(decimal_places=9, max_digits=27, null=True)),
                ("pod_request_memory_gigabyte_hours", models.DecimalField(decimal_places=9, max_digits=27, null=True)),
                ("pod_limit_memory_gigabyte_hours", models.DecimalField(decimal_places=9, max_digits=27, null=True)),
                ("cluster_capacity_cpu_core_hours", models.DecimalField(decimal_places=9, max_digits=27, null=True)),
                ("total_capacity_cpu_core_hours", models.DecimalField(decimal_places=9, max_digits=27, null=True)),
                (
                    "total_capacity_memory_gigabyte_hours",
                    models.DecimalField(decimal_places=9, max_digits=27, null=True),
                ),
                (
                    "cluster_capacity_memory_gigabyte_hours",
                    models.DecimalField(decimal_places=9, max_digits=27, null=True),
                ),
            ],
            options={"db_table": "reporting_ocp_pod_summary_by_project", "managed": False},
        ),
        migrations.CreateModel(
            name="OCPVolumeSummary",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("cluster_id", models.TextField()),
                ("cluster_alias", models.TextField(null=True)),
                (
                    "resource_ids",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=256), null=True, size=None
                    ),
                ),
                ("resource_count", models.IntegerField(null=True)),
                ("data_source", models.CharField(max_length=64, null=True)),
                ("usage_start", models.DateField()),
                ("usage_end", models.DateField()),
                ("supplementary_usage_cost", django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ("infrastructure_raw_cost", models.DecimalField(decimal_places=15, max_digits=33, null=True)),
                ("infrastructure_usage_cost", django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ("infrastructure_markup_cost", models.DecimalField(decimal_places=15, max_digits=33, null=True)),
                (
                    "persistentvolumeclaim_usage_gigabyte_months",
                    models.DecimalField(decimal_places=9, max_digits=27, null=True),
                ),
                (
                    "volume_request_storage_gigabyte_months",
                    models.DecimalField(decimal_places=9, max_digits=27, null=True),
                ),
                (
                    "persistentvolumeclaim_capacity_gigabyte_months",
                    models.DecimalField(decimal_places=9, max_digits=27, null=True),
                ),
            ],
            options={"db_table": "reporting_ocp_volume_summary", "managed": False},
        ),
        migrations.CreateModel(
            name="OCPVolumeSummaryByProject",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("cluster_id", models.TextField()),
                ("cluster_alias", models.TextField(null=True)),
                ("namespace", models.CharField(max_length=253, null=True)),
                (
                    "resource_ids",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=256), null=True, size=None
                    ),
                ),
                ("resource_count", models.IntegerField(null=True)),
                ("data_source", models.CharField(max_length=64, null=True)),
                ("usage_start", models.DateField()),
                ("usage_end", models.DateField()),
                ("supplementary_usage_cost", django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ("infrastructure_raw_cost", models.DecimalField(decimal_places=15, max_digits=33, null=True)),
                ("infrastructure_usage_cost", django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ("infrastructure_markup_cost", models.DecimalField(decimal_places=15, max_digits=33, null=True)),
                (
                    "persistentvolumeclaim_usage_gigabyte_months",
                    models.DecimalField(decimal_places=9, max_digits=27, null=True),
                ),
                (
                    "volume_request_storage_gigabyte_months",
                    models.DecimalField(decimal_places=9, max_digits=27, null=True),
                ),
                (
                    "persistentvolumeclaim_capacity_gigabyte_months",
                    models.DecimalField(decimal_places=9, max_digits=27, null=True),
                ),
            ],
            options={"db_table": "reporting_ocp_volume_summary_by_project", "managed": False},
        ),
        migrations.RunSQL(
            sql="""
            CREATE MATERIALIZED VIEW reporting_ocp_pod_summary AS(
                SELECT row_number() OVER(ORDER BY usage_start, cluster_id, cluster_alias) as id,
                    usage_start as usage_start,
                    usage_start as usage_end,
                    cluster_id,
                    cluster_alias,
                    max(data_source) as data_source,
                    array_agg(DISTINCT resource_id) as resource_ids,
                    count(DISTINCT resource_id) as resource_count,
                    json_build_object('cpu', sum((supplementary_usage_cost->>'cpu')::decimal),
                                    'memory', sum((supplementary_usage_cost->>'memory')::decimal),
                                    'storage', sum((supplementary_usage_cost->>'storage')::decimal)) as supplementary_usage_cost,
                    json_build_object('cpu', sum((infrastructure_usage_cost->>'cpu')::decimal),
                                    'memory', sum((infrastructure_usage_cost->>'memory')::decimal),
                                    'storage', sum((infrastructure_usage_cost->>'storage')::decimal)) as infrastructure_usage_cost,
                    sum(infrastructure_raw_cost) as infrastructure_raw_cost,
                    sum(infrastructure_markup_cost) as infrastructure_markup_cost,
                    sum(pod_usage_cpu_core_hours) as pod_usage_cpu_core_hours,
                    sum(pod_request_cpu_core_hours) as pod_request_cpu_core_hours,
                    sum(pod_limit_cpu_core_hours) as pod_limit_cpu_core_hours,
                    max(cluster_capacity_cpu_core_hours) as cluster_capacity_cpu_core_hours,
                    max(total_capacity_cpu_core_hours) as total_capacity_cpu_core_hours,
                    sum(pod_usage_memory_gigabyte_hours) as pod_usage_memory_gigabyte_hours,
                    sum(pod_request_memory_gigabyte_hours) as pod_request_memory_gigabyte_hours,
                    sum(pod_limit_memory_gigabyte_hours) as pod_limit_memory_gigabyte_hours,
                    max(total_capacity_memory_gigabyte_hours) as total_capacity_memory_gigabyte_hours,
                    max(cluster_capacity_memory_gigabyte_hours) as cluster_capacity_memory_gigabyte_hours

                FROM reporting_ocpusagelineitem_daily_summary
                -- Get data for this month or last month
                WHERE usage_start >= DATE_TRUNC('month', NOW() - '1 month'::interval)::date AND data_source = 'Pod'
                GROUP BY usage_start, cluster_id, cluster_alias
            )
            ;

            CREATE UNIQUE INDEX ocp_pod_summary
            ON reporting_ocp_pod_summary (usage_start, cluster_id, cluster_alias)
            ;

            CREATE MATERIALIZED VIEW reporting_ocp_pod_summary_by_project AS(
                SELECT row_number() OVER(ORDER BY usage_start, cluster_id, cluster_alias, namespace) as id,
                    usage_start as usage_start,
                    usage_start as usage_end,
                    cluster_id,
                    cluster_alias,
                    namespace,
                    max(data_source) as data_source,
                    array_agg(DISTINCT resource_id) as resource_ids,
                    count(DISTINCT resource_id) as resource_count,
                    json_build_object('cpu', sum((supplementary_usage_cost->>'cpu')::decimal),
                                    'memory', sum((supplementary_usage_cost->>'memory')::decimal),
                                    'storage', sum((supplementary_usage_cost->>'storage')::decimal)) as supplementary_usage_cost,
                    json_build_object('cpu', sum((infrastructure_usage_cost->>'cpu')::decimal),
                                    'memory', sum((infrastructure_usage_cost->>'memory')::decimal),
                                    'storage', sum((infrastructure_usage_cost->>'storage')::decimal)) as infrastructure_usage_cost,
                    sum(infrastructure_raw_cost) as infrastructure_raw_cost,
                    sum(infrastructure_markup_cost) as infrastructure_markup_cost,
                    sum(pod_usage_cpu_core_hours) as pod_usage_cpu_core_hours,
                    sum(pod_request_cpu_core_hours) as pod_request_cpu_core_hours,
                    sum(pod_limit_cpu_core_hours) as pod_limit_cpu_core_hours,
                    max(cluster_capacity_cpu_core_hours) as cluster_capacity_cpu_core_hours,
                    max(total_capacity_cpu_core_hours) as total_capacity_cpu_core_hours,
                    sum(pod_usage_memory_gigabyte_hours) as pod_usage_memory_gigabyte_hours,
                    sum(pod_request_memory_gigabyte_hours) as pod_request_memory_gigabyte_hours,
                    sum(pod_limit_memory_gigabyte_hours) as pod_limit_memory_gigabyte_hours,
                    max(total_capacity_memory_gigabyte_hours) as total_capacity_memory_gigabyte_hours,
                    max(cluster_capacity_memory_gigabyte_hours) as cluster_capacity_memory_gigabyte_hours

                FROM reporting_ocpusagelineitem_daily_summary
                -- Get data for this month or last month
                WHERE usage_start >= DATE_TRUNC('month', NOW() - '1 month'::interval)::date AND data_source = 'Pod'
                GROUP BY usage_start, cluster_id, cluster_alias, namespace
            )
            ;

            CREATE UNIQUE INDEX ocp_pod_summary_by_project
            ON reporting_ocp_pod_summary_by_project (usage_start, cluster_id, cluster_alias, namespace)
            ;

            CREATE MATERIALIZED VIEW reporting_ocp_volume_summary AS(
                SELECT row_number() OVER(ORDER BY usage_start, cluster_id, cluster_alias) as id,
                    usage_start as usage_start,
                    usage_start as usage_end,
                    cluster_id,
                    cluster_alias,
                    max(data_source) as data_source,
                    array_agg(DISTINCT resource_id) as resource_ids,
                    count(DISTINCT resource_id) as resource_count,
                    json_build_object('cpu', sum((supplementary_usage_cost->>'cpu')::decimal),
                                    'memory', sum((supplementary_usage_cost->>'memory')::decimal),
                                    'storage', sum((supplementary_usage_cost->>'storage')::decimal)) as supplementary_usage_cost,
                    json_build_object('cpu', sum((infrastructure_usage_cost->>'cpu')::decimal),
                                    'memory', sum((infrastructure_usage_cost->>'memory')::decimal),
                                    'storage', sum((infrastructure_usage_cost->>'storage')::decimal)) as infrastructure_usage_cost,
                    sum(infrastructure_raw_cost) as infrastructure_raw_cost,
                    sum(infrastructure_markup_cost) as infrastructure_markup_cost,
                    sum(persistentvolumeclaim_usage_gigabyte_months) as persistentvolumeclaim_usage_gigabyte_months,
                    sum(volume_request_storage_gigabyte_months) as volume_request_storage_gigabyte_months,
                    sum(persistentvolumeclaim_capacity_gigabyte_months) as persistentvolumeclaim_capacity_gigabyte_months
                FROM reporting_ocpusagelineitem_daily_summary
                -- Get data for this month or last month
                WHERE usage_start >= DATE_TRUNC('month', NOW() - '1 month'::interval)::date AND data_source = 'Storage'
                GROUP BY usage_start, cluster_id, cluster_alias
            )
            ;

            CREATE UNIQUE INDEX ocp_volume_summary
            ON reporting_ocp_volume_summary (usage_start, cluster_id, cluster_alias)
            ;

            CREATE MATERIALIZED VIEW reporting_ocp_volume_summary_by_project AS(
                SELECT row_number() OVER(ORDER BY usage_start, cluster_id, cluster_alias, namespace) as id,
                    usage_start as usage_start,
                    usage_start as usage_end,
                    cluster_id,
                    cluster_alias,
                    namespace,
                    max(data_source) as data_source,
                    array_agg(DISTINCT resource_id) as resource_ids,
                    count(DISTINCT resource_id) as resource_count,
                    json_build_object('cpu', sum((supplementary_usage_cost->>'cpu')::decimal),
                                    'memory', sum((supplementary_usage_cost->>'memory')::decimal),
                                    'storage', sum((supplementary_usage_cost->>'storage')::decimal)) as supplementary_usage_cost,
                    json_build_object('cpu', sum((infrastructure_usage_cost->>'cpu')::decimal),
                                    'memory', sum((infrastructure_usage_cost->>'memory')::decimal),
                                    'storage', sum((infrastructure_usage_cost->>'storage')::decimal)) as infrastructure_usage_cost,
                    sum(infrastructure_raw_cost) as infrastructure_raw_cost,
                    sum(infrastructure_markup_cost) as infrastructure_markup_cost,
                    sum(persistentvolumeclaim_usage_gigabyte_months) as persistentvolumeclaim_usage_gigabyte_months,
                    sum(volume_request_storage_gigabyte_months) as volume_request_storage_gigabyte_months,
                    sum(persistentvolumeclaim_capacity_gigabyte_months) as persistentvolumeclaim_capacity_gigabyte_months
                FROM reporting_ocpusagelineitem_daily_summary
                -- Get data for this month or last month
                WHERE usage_start >= DATE_TRUNC('month', NOW() - '1 month'::interval)::date AND data_source = 'Storage'
                GROUP BY usage_start, cluster_id, cluster_alias, namespace
            )
            ;

            CREATE UNIQUE INDEX ocp_volume_summary_by_project
            ON reporting_ocp_volume_summary_by_project (usage_start, cluster_id, cluster_alias, namespace)
            ;

            CREATE MATERIALIZED VIEW reporting_ocp_cost_summary AS(
                SELECT row_number() OVER(ORDER BY usage_start, cluster_id, cluster_alias) as id,
                    usage_start as usage_start,
                    usage_start as usage_end,
                    cluster_id,
                    cluster_alias,
                    json_build_object('cpu', sum((supplementary_usage_cost->>'cpu')::decimal),
                                    'memory', sum((supplementary_usage_cost->>'memory')::decimal),
                                    'storage', sum((supplementary_usage_cost->>'storage')::decimal)) as supplementary_usage_cost,
                    json_build_object('cpu', sum((infrastructure_usage_cost->>'cpu')::decimal),
                                    'memory', sum((infrastructure_usage_cost->>'memory')::decimal),
                                    'storage', sum((infrastructure_usage_cost->>'storage')::decimal)) as infrastructure_usage_cost,
                    sum(infrastructure_raw_cost) as infrastructure_raw_cost,
                    sum(infrastructure_markup_cost) as infrastructure_markup_cost,
                    sum(supplementary_monthly_cost) as supplementary_monthly_cost,
                    sum(infrastructure_monthly_cost) as infrastructure_monthly_cost
                FROM reporting_ocpusagelineitem_daily_summary
                -- Get data for this month or last month
                WHERE usage_start >= DATE_TRUNC('month', NOW() - '1 month'::interval)::date
                GROUP BY usage_start, cluster_id, cluster_alias
            )
            ;

            CREATE UNIQUE INDEX ocp_cost_summary
            ON reporting_ocp_cost_summary (usage_start, cluster_id, cluster_alias)
            ;

            CREATE MATERIALIZED VIEW reporting_ocp_cost_summary_by_project AS(
                SELECT row_number() OVER(ORDER BY usage_start, cluster_id, cluster_alias, namespace) as id,
                    usage_start as usage_start,
                    usage_start as usage_end,
                    cluster_id,
                    cluster_alias,
                    namespace,
                    json_build_object('cpu', sum((supplementary_usage_cost->>'cpu')::decimal),
                                    'memory', sum((supplementary_usage_cost->>'memory')::decimal),
                                    'storage', sum((supplementary_usage_cost->>'storage')::decimal)) as supplementary_usage_cost,
                    json_build_object('cpu', sum((infrastructure_usage_cost->>'cpu')::decimal),
                                    'memory', sum((infrastructure_usage_cost->>'memory')::decimal),
                                    'storage', sum((infrastructure_usage_cost->>'storage')::decimal)) as infrastructure_usage_cost,
                    sum(infrastructure_project_raw_cost) as infrastructure_project_raw_cost,
                    sum(infrastructure_project_markup_cost) as infrastructure_project_markup_cost,
                    sum(supplementary_monthly_cost) as supplementary_monthly_cost,
                    sum(infrastructure_monthly_cost) as infrastructure_monthly_cost
                FROM reporting_ocpusagelineitem_daily_summary
                -- Get data for this month or last month
                WHERE usage_start >= DATE_TRUNC('month', NOW() - '1 month'::interval)::date
                GROUP BY usage_start, cluster_id, cluster_alias, namespace
            )
            ;

            CREATE UNIQUE INDEX ocp_cost_summary_by_project
            ON reporting_ocp_cost_summary_by_project (usage_start, cluster_id, cluster_alias, namespace)
            ;

            CREATE MATERIALIZED VIEW reporting_ocp_cost_summary_by_node AS(
                SELECT row_number() OVER(ORDER BY usage_start, cluster_id, cluster_alias, node) as id,
                    usage_start as usage_start,
                    usage_start as usage_end,
                    cluster_id,
                    cluster_alias,
                    node,
                    json_build_object('cpu', sum((supplementary_usage_cost->>'cpu')::decimal),
                                    'memory', sum((supplementary_usage_cost->>'memory')::decimal),
                                    'storage', sum((supplementary_usage_cost->>'storage')::decimal)) as supplementary_usage_cost,
                    json_build_object('cpu', sum((infrastructure_usage_cost->>'cpu')::decimal),
                                    'memory', sum((infrastructure_usage_cost->>'memory')::decimal),
                                    'storage', sum((infrastructure_usage_cost->>'storage')::decimal)) as infrastructure_usage_cost,
                    sum(infrastructure_raw_cost) as infrastructure_raw_cost,
                    sum(infrastructure_markup_cost) as infrastructure_markup_cost,
                    sum(supplementary_monthly_cost) as supplementary_monthly_cost,
                    sum(infrastructure_monthly_cost) as infrastructure_monthly_cost,
                    sum(infrastructure_project_markup_cost) as infrastructure_project_markup_cost,
                    sum(infrastructure_project_raw_cost) as infrastructure_project_raw_cost
                FROM reporting_ocpusagelineitem_daily_summary
                -- Get data for this month or last month
                WHERE usage_start >= DATE_TRUNC('month', NOW() - '1 month'::interval)::date
                GROUP BY usage_start, cluster_id, cluster_alias, node
            )
            ;

            CREATE UNIQUE INDEX ocp_cost_summary_by_node
            ON reporting_ocp_cost_summary_by_node (usage_start, cluster_id, cluster_alias, node)
            ;

            """
        ),
    ]
