# Generated by Django 4.1.6 on 2023-03-02 11:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('nmscdcl_services', '0006_alter_datastore_connection_params'),
    ]

    operations = [
        migrations.CreateModel(
            name='Style',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('title', models.CharField(blank=True, max_length=120, null=True)),
                ('is_default', models.BooleanField(default=False)),
                ('sld', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='LayerStyle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('layer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='styleLayer', to='nmscdcl_services.layer')),
                ('style', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignStyle', to='nmscdcl_styling.style')),
            ],
        ),
    ]