# Generated by Django 4.1.6 on 2023-02-14 05:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nmscdcl_services', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='shp',
            name='connection_params',
            field=models.JSONField(default={}),
        ),
    ]
