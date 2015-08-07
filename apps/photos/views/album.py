from tempfile import NamedTemporaryFile
from zipfile import ZipFile
from os import path

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.views.generic import ListView, DetailView

from apps.photos.forms import AlbumForm, AlbumMergeForm
from apps.photos.models import Album, Location
from utils.views import AjaxCreateView, AjaxUpdateView, AjaxDeleteView


class List(ListView):
    model = Album
    paginate_by = settings.PHOTOS_PER_PAGE
    template_name = 'photos/album_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Albums')
        return context


class Detail(ListView):
    paginate_by = settings.PHOTOS_PER_PAGE
    actions_template_name = 'photos/_album_actions.html'
    template_name = 'photos/photo_list.html'

    def get_album(self):
        return get_object_or_404(Album, pk=self.kwargs['pk'])

    def get_queryset(self):
        self.album = self.get_album()
        return self.album.photo_set.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        back_link = reverse('albums'), _('Albums')
        location = None
        if 'location_pk' in self.kwargs:
            location = get_object_or_404(Location, pk=self.kwargs.get('location_pk'))
            back_link = reverse('location', kwargs={'pk': location.pk}), location.name

        context['location'] = location
        context['back_link'] = back_link
        context['page_title'] = self.album.name
        context['album'] = self.album
        return context


class Create(AjaxCreateView):
    template_name = 'photos/ajax_form.html'
    form_class = AlbumForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Create Album')
        context['form_submit'] = _('Save')
        return context


class Edit(AjaxUpdateView):
    template_name = 'photos/ajax_form.html'
    form_class = AlbumForm
    model = Album

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Edit Album')
        context['form_submit'] = _('Save')
        return context


class Merge(AjaxUpdateView):
    template_name = 'photos/ajax_form.html'
    form_class = AlbumMergeForm
    model = Album

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Merge Album')
        context['form_submit'] = _('Merge')
        return context


class Delete(AjaxDeleteView):
    template_name = 'photos/ajax_form.html'
    model = Album
    success_url = reverse_lazy('albums')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Delete Album')
        context['form_submit'] = _('Delete')
        context['form_messages'] = (
            _('Are you sure you want to delete this album?'),
            _('This will also delete all the photos in the album.')
        )
        return context


class Download(DetailView):
    model = Album

    def get_zip_file(self):
        zip_file = NamedTemporaryFile()
        with ZipFile(zip_file, 'w') as handle:
            for photo in self.object.photo_set.all():
                full_path = path.join(settings.MEDIA_ROOT, photo.file.name)
                handle.write(full_path, photo.file.name.split('/')[-1])
        zip_file.seek(0)
        return zip_file

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        response = HttpResponse(self.get_zip_file().read(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename={}.zip'.format(self.object.name)
        return response


list = login_required(List.as_view())
detail = login_required(Detail.as_view())
create = permission_required('photos.add_album')(Create.as_view())
edit = permission_required('photos.edit_album')(Edit.as_view())
merge = permission_required('photos.edit_album')(Merge.as_view())
delete = permission_required('photos.delete_album')(Delete.as_view())
download = login_required(Download.as_view())
