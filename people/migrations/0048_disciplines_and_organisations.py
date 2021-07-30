# Generated by Django 2.2.10 on 2021-03-16 08:14

from django.core.exceptions import ObjectDoesNotExist
from django.db import migrations, models


def forward_disciplines(apps, schema_editor):
    PersonQuestion = apps.get_model('people', 'PersonQuestion')

    try:
        question = PersonQuestion.objects.filter(
            text='Disciplinary background').latest('version')

        PersonAnswerSet = apps.get_model('people', 'PersonAnswerSet')
        for answerset in PersonAnswerSet.objects.all():
            answerset.disciplinary_background = ', '.join(
                answerset.question_answers.filter(question=question).values_list(
                    'text', flat=True))
            answerset.save()

        question.delete()

    except ObjectDoesNotExist:
        pass


def forward_organisations(apps, schema_editor):
    PersonQuestion = apps.get_model('people', 'PersonQuestion')

    try:
        question = PersonQuestion.objects.filter(
            text='Please list the main organisations external to BRECcIA work that you have been working with since 1st January 2019 that are involved in food/water security in African dryland regions'
        ).latest('version')

        PersonAnswerSet = apps.get_model('people', 'PersonAnswerSet')
        for answerset in PersonAnswerSet.objects.all():
            answerset.external_organisations = ', '.join(
                answerset.question_answers.filter(question=question).values_list(
                    'text', flat=True))
            answerset.save()

        question.delete()

    except ObjectDoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0047_remove_personanswerset_external_organisations'),
    ]

    operations = [
        migrations.AddField(
            model_name='personanswerset',
            name='disciplinary_background',
            field=models.CharField(blank=True, help_text='Research discipline(s) you feel most affiliated with', max_length=255),
        ),
        migrations.RunPython(forward_disciplines),
        migrations.AddField(
            model_name='personanswerset',
            name='external_organisations',
            field=models.CharField(blank=True, max_length=1023),
        ),
        migrations.RunPython(forward_organisations),
    ]
