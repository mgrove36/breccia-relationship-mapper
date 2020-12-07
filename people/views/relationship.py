"""
Views for displaying or manipulating instances of :class:`Relationship`.
"""

from django.db import IntegrityError
from django.forms import ValidationError
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, DetailView, FormView

from people import forms, models, permissions


class RelationshipDetailView(permissions.UserIsLinkedPersonMixin, DetailView):
    """
    View displaying details of a :class:`Relationship`.
    """
    model = models.Relationship
    template_name = 'people/relationship/detail.html'
    related_person_field = 'source'


class RelationshipCreateView(permissions.UserIsLinkedPersonMixin, FormView):
    """
    View for creating a :class:`Relationship`.

    Displays / processes a form containing the :class:`RelationshipQuestion`s.
    """
    model = models.Relationship
    template_name = 'people/relationship/create.html'
    form_class = forms.RelationshipForm

    def get_person(self) -> models.Person:
        return models.Person.objects.get(pk=self.kwargs.get('person_pk'))

    def get_test_person(self) -> models.Person:
        return self.get_person()

    def form_valid(self, form):
        try:
            self.object = models.Relationship.objects.create(
                source=self.get_person(), target=form.cleaned_data['target'])

        except IntegrityError:
            form.add_error(
                None,
                ValidationError('This relationship already exists',
                                code='already-exists'))
            return self.form_invalid(form)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['person'] = self.get_person()

        return context

    def get_success_url(self):
        return reverse('people:relationship.update',
                       kwargs={'relationship_pk': self.object.pk})


class RelationshipUpdateView(permissions.UserIsLinkedPersonMixin, CreateView):
    """
    View for updating the details of a relationship.

    Creates a new :class:`RelationshipAnswerSet` for the :class:`Relationship`.
    Displays / processes a form containing the :class:`RelationshipQuestion`s.
    """
    model = models.RelationshipAnswerSet
    template_name = 'people/relationship/update.html'
    form_class = forms.RelationshipAnswerSetForm

    def get_test_person(self) -> models.Person:
        """
        Get the person instance which should be used for access control checks.
        """
        relationship = models.Relationship.objects.get(
            pk=self.kwargs.get('relationship_pk'))

        return relationship.source

    def get(self, request, *args, **kwargs):
        self.relationship = models.Relationship.objects.get(
            pk=self.kwargs.get('relationship_pk'))
        self.person = self.relationship.source

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.relationship = models.Relationship.objects.get(
            pk=self.kwargs.get('relationship_pk'))
        self.person = self.relationship.source

        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['person'] = self.person
        context['relationship'] = self.relationship

        return context

    def get_initial(self):
        initial = super().get_initial()

        initial['relationship'] = self.relationship

        return initial

    def form_valid(self, form):
        """
        Mark any previous answer sets as replaced.
        """
        response = super().form_valid(form)
        now_date = timezone.now().date()

        # Shouldn't be more than one after initial updates after migration
        for answer_set in self.relationship.answer_sets.exclude(
                pk=self.object.pk):
            answer_set.replaced_timestamp = now_date
            answer_set.save()

        return response
