# Generated by Django 2.2.10 on 2020-02-24 08:16

from django.db import migrations
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0009_add_first_person_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='country_of_residence',
            field=django_countries.fields.CountryField(blank=True, max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='person',
            name='nationality',
            field=django_countries.fields.CountryField(blank=True, max_length=2, null=True),
        ),
    ]
