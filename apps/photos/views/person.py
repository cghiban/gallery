from django.contrib.auth.decorators import login_required, permission_required

from django.utils.translation import ugettext as _
from django.conf import settings
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from apps.photos.forms import PersonNameForm
from apps.photos.models import Person
from apps.stream.utils import send_action
from utils.views import AjaxDeleteView, AjaxCreateView, AjaxUpdateView


class List(ListView):
    model = Person
    paginate_by = settings.PHOTOS_PER_PAGE
    template_name = 'photos/person_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('People')
        return context


class Detail(ListView):
    paginate_by = settings.PHOTOS_PER_PAGE
    actions_template_name = 'photos/_person_actions.html'
    template_name = 'photos/photo_list.html'

    def get_person(self):
        return get_object_or_404(Person, pk=self.kwargs['pk'])

    def get_queryset(self):
        self.person = self.get_person()
        return self.person.photo_set.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_link'] = reverse('people'), _('People')
        context['page_title'] = self.person.name
        context['person'] = self.person
        return context


class Create(AjaxCreateView):
    template_name = 'photos/ajax_form.html'
    form_class = PersonNameForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Create Person')
        context['form_submit'] = _('Save')
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        send_action(self.request.user, 'created the person', target=self.object)
        return response


class Rename(AjaxUpdateView):
    template_name = 'photos/ajax_form.html'
    form_class = PersonNameForm
    model = Person

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Edit Person')
        context['form_submit'] = _('Save')
        return context


class Delete(AjaxDeleteView):
    template_name = 'photos/ajax_form.html'
    model = Person
    success_url = reverse_lazy('people')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Delete Person')
        context['form_submit'] = _('Delete')
        context['form_messages'] = (
            _('Are you sure you want to delete this person?'),
            _('This will also remove tags from any photos.')
        )
        return context


list = login_required(List.as_view())
detail = login_required(Detail.as_view())
create = permission_required('photos.add_person')(Create.as_view())
rename = permission_required('photos.edit_person')(Rename.as_view())
delete = permission_required('photos.delete_person')(Delete.as_view())
