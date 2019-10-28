# Generated by Django 2.2.4 on 2019-10-22 16:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0031_auto_20191022_1615'),
    ]

    operations = [
        migrations.AddField(
            model_name='providerstatus',
            name='provider',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.Provider'),
        ),
        migrations.RunSQL(
            """
                UPDATE api_providerstatus AS ps
                    SET provider_id = provider_uuid
            """
        ),
    ]
