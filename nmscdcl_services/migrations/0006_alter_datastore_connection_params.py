# Generated by Django 4.1.6 on 2023-02-22 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nmscdcl_services', '0005_datastore_layergroup_workspace_layer_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datastore',
            name='connection_params',
            field=models.JSONField(),
        ),
    ]
