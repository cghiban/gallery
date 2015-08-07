from django.utils.translation import ugettext as _
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from apps.photos.forms import LocationNameForm
from apps.photos.models import Location
from apps.stream.utils import send_action
from utils.views import AjaxCreateView, AjaxUpdateView, AjaxDeleteView


class List(ListView):
    model = Location
    paginate_by = settings.PHOTOS_PER_PAGE
    template_name = 'photos/location_list.html'


class Detail(ListView):
    paginate_by = settings.PHOTOS_PER_PAGE
    actions_template_name = 'photos/_location_actions.html'
    template_name = 'photos/album_list.html'

    def get_location(self):
        return get_object_or_404(Location, pk=self.kwargs['pk'])

    def get_queryset(self):
        self.location = self.get_location()
        return self.location.album_set.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_link'] = reverse('locations'), _('Locations')
        context['page_title'] = self.location.name
        context['location'] = self.location
        return context


class Create(AjaxCreateView):
    template_name = 'photos/ajax_form.html'
    form_class = LocationNameForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Create Location')
        context['form_submit'] = _('Save')
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        send_action(self.request.user, 'created the location', target=self.object)
        return response


class Rename(AjaxUpdateView):
    template_name = 'photos/ajax_form.html'
    form_class = LocationNameForm
    model = Location

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Rename Location')
        context['form_submit'] = _('Save')
        return context


class Delete(AjaxDeleteView):
    template_name = 'photos/ajax_form.html'
    model = Location
    success_url = reverse_lazy('locations')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Delete Location')
        context['form_submit'] = _('Delete')
        context['form_messages'] = (
            _('Are you sure you want to delete this location?'),
            _('This will also remove this location from any albums.')
        )
        return context


list = login_required(List.as_view())
detail = login_required(Detail.as_view())
create = permission_required('photos.add_location')(Create.as_view())
rename = permission_required('photos.edit_location')(Rename.as_view())
delete = permission_required('photos.delete_location')(Delete.as_view())
