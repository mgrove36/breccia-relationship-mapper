# Generated by Django 2.2.10 on 2021-03-19 11:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0049_relationship_latest_by_timestamp'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='organisationrelationship',
            options={},
        ),
        migrations.RemoveField(
            model_name='organisationrelationship',
            name='created',
        ),
        migrations.RemoveField(
            model_name='organisationrelationship',
            name='expired',
        ),
        migrations.AlterModelOptions(
            name='relationship',
            options={},
        ),
        migrations.RemoveField(
            model_name='relationship',
            name='created',
        ),
        migrations.RemoveField(
            model_name='relationship',
            name='expired',
        ),
    ]
