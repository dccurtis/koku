# Generated by Django 2.2.9 on 2020-01-21 17:46
import json
import pkgutil

import django.contrib.postgres.fields.jsonb
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    replaces = [
        ("reporting_common", "0001_initial_squashed_0007_auto_20190208_0316"),
        ("reporting_common", "0008_auto_20190412_1330"),
        ("reporting_common", "0009_costusagereportstatus_history"),
        ("reporting_common", "0010_remove_costusagereportstatus_history"),
        ("reporting_common", "0011_auto_20190723_1655"),
        ("reporting_common", "0012_auto_20190812_1805"),
        ("reporting_common", "0013_auto_20190823_1442"),
        ("reporting_common", "0014_auto_20190820_1513"),
        ("reporting_common", "0015_auto_20190827_1536"),
        ("reporting_common", "0016_auto_20190829_2053"),
        ("reporting_common", "0017_auto_20190923_1410"),
        ("reporting_common", "0018_auto_20190923_1838"),
        ("reporting_common", "0019_auto_20191022_1602"),
    ]

    dependencies = [("api", "0001_initial_squashed_0008_auto_20190305_2015")]

    operations = [
        migrations.CreateModel(
            name="CostUsageReportManifest",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("assembly_id", models.TextField()),
                ("manifest_creation_datetime", models.DateTimeField(default=django.utils.timezone.now, null=True)),
                ("manifest_updated_datetime", models.DateTimeField(default=django.utils.timezone.now, null=True)),
                ("billing_period_start_datetime", models.DateTimeField()),
                ("num_processed_files", models.IntegerField(default=0)),
                ("num_total_files", models.IntegerField()),
                ("provider", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="api.Provider")),
                ("task", models.UUIDField(null=True)),
                ("manifest_completed_datetime", models.DateTimeField(null=True)),
            ],
            options={"unique_together": {("provider", "assembly_id")}},
        ),
        migrations.CreateModel(
            name="CostUsageReportStatus",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("report_name", models.CharField(max_length=128)),
                ("last_completed_datetime", models.DateTimeField(null=True)),
                ("last_started_datetime", models.DateTimeField(null=True)),
                ("etag", models.CharField(max_length=64, null=True)),
                (
                    "manifest",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="reporting_common.CostUsageReportManifest",
                    ),
                ),
            ],
            options={"unique_together": {("manifest", "report_name")}},
        ),
        migrations.CreateModel(
            name="RegionMapping",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("region", models.CharField(max_length=32, unique=True)),
                ("region_name", models.CharField(max_length=64, unique=True)),
            ],
            options={"db_table": "region_mapping"},
        ),
        migrations.CreateModel(
            name="ReportColumnMap",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "provider_type",
                    models.CharField(
                        choices=[
                            ("AWS", "AWS"),
                            ("OCP", "OCP"),
                            ("Azure", "Azure"),
                            ("GCP", "GCP"),
                            ("AWS-local", "AWS-local"),
                            ("Azure-local", "Azure-local"),
                            ("GCP-local", "GCP-local"),
                        ],
                        default="AWS",
                        max_length=50,
                    ),
                ),
                ("provider_column_name", models.CharField(max_length=128)),
                ("database_table", models.CharField(max_length=50)),
                ("database_column", models.CharField(max_length=128)),
                ("report_type", models.CharField(max_length=50, null=True)),
            ],
            options={"unique_together": {("report_type", "provider_column_name")}},
        ),
        # This index was missing and I cannot find where it is being created. So I have copied the DDL from the DB created in master.
        migrations.RunSQL(
            sql="""
            CREATE INDEX if not exists reporting_common_reportc_provider_column_name_e01eaba3_like
                ON public.reporting_common_reportcolumnmap USING btree (provider_column_name varchar_pattern_ops);
            """
        ),
        migrations.CreateModel(
            name="SIUnitScale",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("prefix", models.CharField(max_length=12, unique=True)),
                ("prefix_symbol", models.CharField(max_length=1)),
                ("multiplying_factor", models.DecimalField(decimal_places=24, max_digits=49)),
            ],
            options={"db_table": "si_unit_scale"},
        ),
    ]
