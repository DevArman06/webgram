# Generated by Django 4.1.6 on 2023-02-21 07:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nmscdcl_services', '0003_alter_shp_connection_params'),
    ]

    operations = [
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('title', models.CharField(blank=True, max_length=100, null=True)),
                ('description', models.CharField(blank=True, max_length=500, null=True)),
                ('type', models.CharField(choices=[('geoserver', 'geoserver'), ('mapserver', 'mapserver')], default='geoserver', max_length=50)),
                ('frontend_url', models.CharField(max_length=500)),
                ('user', models.CharField(max_length=25)),
                ('password', models.CharField(max_length=100)),
                ('default', models.BooleanField(default=False)),
                ('is_delete', models.BooleanField(default=False)),
                ('timestamp', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AlterField(
            model_name='shp',
            name='connection_params',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
