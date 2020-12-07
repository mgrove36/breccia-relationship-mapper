# Generated by Django 2.2.10 on 2020-11-25 15:50

from django.core.exceptions import ObjectDoesNotExist
from django.db import migrations
from django.utils import timezone

from .utils.question_sets import port_question


def migrate_forward(apps, schema_editor):
    Person = apps.get_model('people', 'Person')
    Role = apps.get_model('people', 'Role')

    role_question = port_question(apps, 'Role',
                                  Role.objects.values_list('name', flat=True))

    for person in Person.objects.all():
        try:
            prev_set = person.answer_sets.latest('timestamp')

        except ObjectDoesNotExist:
            prev_set = None

        try:

            answer_set = person.answer_sets.create()
            answer_set.question_answers.add(
                role_question.answers.get(text=person.role.name))

            prev_set.replaced_timestamp = timezone.datetime.now()

        except AttributeError:
            pass


def migrate_backward(apps, schema_editor):
    Person = apps.get_model('people', 'Person')
    Role = apps.get_model('people', 'Role')

    for person in Person.objects.all():
        try:
            current_answers = person.answer_sets.latest('timestamp')
            role_answer = current_answers.question_answers.get(
                question__text='Role')
            person.role, _ = Role.objects.get_or_create(name=role_answer.text)
            person.save()

        except ObjectDoesNotExist:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0022_refactor_person_questions'),
    ]

    operations = [
        migrations.RunPython(migrate_forward, migrate_backward),
        migrations.RemoveField(
            model_name='person',
            name='role',
        ),
        migrations.DeleteModel('Role'),
    ]
