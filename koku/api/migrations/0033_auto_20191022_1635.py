# Generated by Django 2.2.4 on 2019-10-22 16:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0032_auto_20191022_1620'),
    ]

    operations = [
        migrations.AlterField(
            model_name='providerstatus',
            name='provider',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Provider'),
        ),
        migrations.RemoveField(
            model_name='providerstatus',
            name='provider_uuid',
        ),
    ]
