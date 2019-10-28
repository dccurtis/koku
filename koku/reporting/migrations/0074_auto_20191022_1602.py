# Generated by Django 2.2.4 on 2019-10-22 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0073_auto_20191017_1629'),
    ]

    operations = [
        migrations.AddField(
            model_name='awscostentrybill',
            name='provider_uuid',
            field=models.UUIDField(null=True),
        ),
        migrations.AddField(
            model_name='azurecostentrybill',
            name='provider_uuid',
            field=models.UUIDField(null=True),
        ),
        migrations.AddField(
            model_name='ocpusagereportperiod',
            name='provider_uuid',
            field=models.UUIDField(null=True),
        ),
        migrations.RunSQL(
            """
                UPDATE reporting_awscostentrybill AS b
                    SET provider_uuid = p.uuid
                FROM public.api_provider AS p
                WHERE p.id = b.provider_id
            """
        ),
        migrations.RunSQL(
            """
                UPDATE reporting_azurecostentrybill AS b
                    SET provider_uuid = p.uuid
                FROM public.api_provider AS p
                WHERE p.id = b.provider_id
            """
        ),
        migrations.RunSQL(
            """
                UPDATE reporting_ocpusagereportperiod AS b
                    SET provider_uuid = p.uuid
                FROM public.api_provider AS p
                WHERE p.id = b.provider_id
            """
        ),
    ]
