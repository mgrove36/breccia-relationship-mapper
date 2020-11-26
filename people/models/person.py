import logging
import typing

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from django_countries.fields import CountryField
from django_settings_export import settings_export
from post_office import mail

from backports.db.models.enums import TextChoices

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

__all__ = [
    'User',
    'Organisation',
    'Theme',
    'PersonQuestion',
    'PersonQuestionChoice',
    'Person',
    'PersonAnswerSet',
]


class User(AbstractUser):
    """
    Custom user model in case we need to make changes later.
    """
    email = models.EmailField(_('email address'), blank=False, null=False)

    def has_person(self) -> bool:
        """
        Does this user have a linked :class:`Person` record?
        """
        return hasattr(self, 'person')

    def send_welcome_email(self) -> None:
        """Send a welcome email to a new user."""
        # Get exported data from settings.py first
        context = settings_export(None)
        context.update({
            'user': self,
        })

        logger.info('Sending welcome mail to user \'%s\'', self.username)

        try:
            mail.send(
                [self.email],
                sender=settings.DEFAULT_FROM_EMAIL,
                template=settings.TEMPLATE_WELCOME_EMAIL_NAME,
                context=context,
                priority='now'  # Send immediately - don't add to queue
            )

        except ValidationError:
            logger.error(
                'Sending welcome mail failed, invalid email for user \'%s\'',
                self.username)


class Organisation(models.Model):
    """
    Organisation to which a :class:`Person` belongs.
    """
    name = models.CharField(max_length=255, blank=False, null=False)

    def __str__(self) -> str:
        return self.name


class Theme(models.Model):
    """
    Project theme within which a :class:`Person` works.
    """
    name = models.CharField(max_length=255, blank=False, null=False)

    def __str__(self) -> str:
        return self.name


class PersonQuestion(models.Model):
    """Question which may be asked about a person."""
    class Meta:
        ordering = [
            'order',
            'text',
        ]

    #: Version number of this question - to allow modification without invalidating existing data
    version = models.PositiveSmallIntegerField(default=1,
                                               blank=False, null=False)

    #: Text of question
    text = models.CharField(max_length=255,
                            blank=False, null=False)

    #: Position of this question in the list
    order = models.SmallIntegerField(default=0,
                                     blank=False, null=False)

    @property
    def choices(self) -> typing.List[typing.List[str]]:
        """
        Convert the :class:`PersonQuestionChoice`s for this question into Django choices.
        """
        return [
            [choice.pk, str(choice)] for choice in self.answers.all()
        ]

    @property
    def slug(self) -> str:
        return slugify(self.text)

    def __str__(self) -> str:
        return self.text


class PersonQuestionChoice(models.Model):
    """
    Allowed answer to a :class:`PersonQuestion`.
    """
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['question', 'text'],
                                    name='unique_question_answer')
        ]
        ordering = [
            'question__order',
            'order',
            'text',
        ]

    #: Question to which this answer belongs
    question = models.ForeignKey(PersonQuestion, related_name='answers',
                                 on_delete=models.CASCADE,
                                 blank=False, null=False)

    #: Text of answer
    text = models.CharField(max_length=255,
                            blank=False, null=False)

    #: Position of this answer in the list
    order = models.SmallIntegerField(default=0,
                                     blank=False, null=False)

    @property
    def slug(self) -> str:
        return slugify(self.text)

    def __str__(self) -> str:
        return self.text


class Person(models.Model):
    """
    A person may be a member of the BRECcIA core team or an external stakeholder.
    """
    class Meta:
        verbose_name_plural = 'people'

    #: User account belonging to this person
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                related_name='person',
                                on_delete=models.CASCADE,
                                blank=True,
                                null=True)

    #: Name of the person
    name = models.CharField(max_length=255, blank=False, null=False)

    #: People with whom this person has relationship - via intermediate :class:`Relationship` model
    relationship_targets = models.ManyToManyField(
        'self',
        related_name='relationship_sources',
        through='Relationship',
        through_fields=('source', 'target'),
        symmetrical=False)

    ###############################################################
    # Data collected for analysis of community makeup and structure

    class GenderChoices(TextChoices):
        MALE = 'M', _('Male')
        FEMALE = 'F', _('Female')
        OTHER = 'O', _('Other')
        PREFER_NOT_TO_SAY = 'N', _('Prefer not to say')

    gender = models.CharField(max_length=1,
                              choices=GenderChoices.choices,
                              blank=True,
                              null=False)

    class AgeGroupChoices(TextChoices):
        LTE_25 = '<=25', _('25 or under')
        BETWEEN_26_30 = '26-30', _('26-30')
        BETWEEN_31_35 = '31-35', _('31-35')
        BETWEEN_36_40 = '36-40', _('36-40')
        BETWEEN_41_45 = '41-45', _('41-45')
        BETWEEN_46_50 = '46-50', _('46-50')
        BETWEEN_51_55 = '51-55', _('51-55')
        BETWEEN_56_60 = '56-60', _('56-60')
        GTE_61 = '>=61', _('61 or older')
        PREFER_NOT_TO_SAY = 'N', _('Prefer not to say')

    age_group = models.CharField(max_length=5,
                                 choices=AgeGroupChoices.choices,
                                 blank=True,
                                 null=False)

    nationality = CountryField(blank=True, null=True)

    country_of_residence = CountryField(blank=True, null=True)

    #: Organisation this person is employed by or affiliated with
    organisation = models.ForeignKey(Organisation,
                                     on_delete=models.PROTECT,
                                     related_name='members',
                                     blank=True,
                                     null=True)

    #: When did this person start at their current organisation?
    organisation_started_date = models.DateField(
        'Date started at this organisation', blank=False, null=True)

    #: Job title this person holds within their organisation
    job_title = models.CharField(max_length=255, blank=True, null=False)

    #: Discipline(s) within which this person works
    disciplines = models.CharField(max_length=255, blank=True, null=True)

    #: Project themes within this person works
    themes = models.ManyToManyField(Theme, related_name='people', blank=True)

    @property
    def relationships(self):
        return self.relationships_as_source.all().union(
            self.relationships_as_target.all())

    @property
    def current_answers(self) -> 'PersonAnswerSet':
        return self.answer_sets.last()

    def get_absolute_url(self):
        return reverse('people:person.detail', kwargs={'pk': self.pk})

    def __str__(self) -> str:
        return self.name


class PersonAnswerSet(models.Model):
    """
    The answers to the person questions at a particular point in time.
    """

    class Meta:
        ordering = [
            'timestamp',
        ]

    #: Person to which this answer set belongs
    person = models.ForeignKey(Person,
                               on_delete=models.CASCADE,
                               related_name='answer_sets',
                               blank=False, null=False)

    #: Answers to :class:`PersonQuestion`s
    question_answers = models.ManyToManyField(PersonQuestionChoice)

    #: When were these answers collected?
    timestamp = models.DateTimeField(auto_now_add=True,
                                     editable=False)

    replaced_timestamp = models.DateTimeField(blank=True, null=True,
                                              editable=False)

    def get_absolute_url(self):
        return self.person.get_absolute_url()
