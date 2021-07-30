# Generated by Django 2.2.10 on 2021-02-23 13:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0034_remove_personanswerset_disciplines'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrganisationQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.PositiveSmallIntegerField(default=1)),
                ('text', models.CharField(max_length=255)),
                ('is_multiple_choice', models.BooleanField(default=False)),
                ('allow_free_text', models.BooleanField(default=False)),
                ('order', models.SmallIntegerField(default=0)),
                ('answer_is_public', models.BooleanField(default=True, help_text='Should answers to this question be displayed on profiles?')),
            ],
            options={
                'ordering': ['order', 'text'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrganisationQuestionChoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=255)),
                ('order', models.SmallIntegerField(default=0)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='people.OrganisationQuestion')),
            ],
            options={
                'ordering': ['question__order', 'order', 'text'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrganisationAnswerSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('replaced_timestamp', models.DateTimeField(blank=True, editable=False, null=True)),
                ('organisation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answer_sets', to='people.Organisation')),
                ('question_answers', models.ManyToManyField(to='people.OrganisationQuestionChoice')),
            ],
            options={
                'ordering': ['timestamp'],
                'abstract': False,
            },
        ),
        migrations.AddConstraint(
            model_name='organisationquestionchoice',
            constraint=models.UniqueConstraint(fields=('question', 'text'), name='unique_question_answer'),
        ),
    ]
