# Generated by Django 2.2.10 on 2020-06-24 11:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0018_require_user_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='core_member',
        ),
    ]
