# Generated by Django 2.2.10 on 2020-02-21 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0008_order_answer_by_question'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='age_group',
            field=models.CharField(blank=True, choices=[('<=25', '25 or under'), ('26-30', '26-30'), ('31-35', '31-35'), ('36-40', '36-40'), ('41-45', '41-45'), ('46-50', '46-50'), ('51-55', '51-55'), ('56-60', '56-60'), ('>=61', '61 or older'), ('N', 'Prefer not to say')], max_length=5),
        ),
        migrations.AddField(
            model_name='person',
            name='gender',
            field=models.CharField(blank=True, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other'), ('N', 'Prefer not to say')], max_length=1),
        ),
    ]
