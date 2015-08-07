import mimetypes

from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, View

from apps.photos.forms import PhotoMoveForm, PhotoNameForm, PhotoTagForm
from apps.photos.models import Person, Photo, Location
from apps.photos.utils import rotate_image
from apps.photos.views import get_search_queryset
from utils.views import AjaxDeleteView, AjaxUpdateView, AjaxFormMixin


class Detail(DetailView):
    model = Photo
    template_name = 'photos/photo_detail.html'
    person = None
    location = None
    query = None

    def paginate(self, queryset, obj):
        """
        Figure out where this photo is located in the queryset (sorted by id). Queryset can be variable
        based on how the user accessed the photo. Return a simple paginator dictionary.
        """
        values_list = list(queryset.order_by('name').values_list('id', flat=True))
        index = values_list.index(obj.id)

        def build_url(pk):
            newkwargs = self.kwargs.copy()
            newkwargs['pk'] = pk
            return reverse('photo', kwargs=newkwargs)

        next_url, prev_url = None, None
        if len(values_list) > 1:
            if obj.id != values_list[0]:
                prev_url = build_url(values_list[index - 1])
            if obj.id != values_list[-1]:
                next_url = build_url(values_list[index + 1])

        self.paginator = {
            'has_next': (next_url is not None),
            'next_url': next_url,
            'has_previous': (prev_url is not None),
            'previous_url': prev_url,
            'index': (index + 1),
            'count': len(values_list)
        }
        return obj

    def get_object(self, queryset=None):
        """
        Get the photo object, set the proper "back" link, and create the paginator object.
        """
        obj = get_object_or_404(Photo, pk=self.kwargs[self.pk_url_kwarg])

        if 'query' in self.kwargs:
            self.query = self.kwargs['query']
            self.back_link = reverse('results', kwargs={'query': self.kwargs['query']}), _('Results')
            self.paginate(get_search_queryset(self.kwargs['query']), obj)
            return obj

        if 'person_pk' in self.kwargs:
            self.person = get_object_or_404(Person, pk=self.kwargs['person_pk'])
            self.back_link = reverse('person', kwargs={'pk': self.person.pk}), self.person.name
            self.paginate(self.person.photo_set, obj)
            return obj

        if 'location_pk' in self.kwargs:
            self.location = get_object_or_404(Location, pk=self.kwargs.get('location_pk'))
            album = get_object_or_404(self.location.album_set, pk=self.kwargs.get('location_pk'))
            self.back_link = reverse('album', kwargs={'pk': album.pk, 'location_pk': self.location.pk}), album.name
            self.paginate(album.photo_set, obj)
            return obj

        self.back_link = reverse('album', kwargs={'pk': obj.album.pk}), obj.album.name
        self.paginate(obj.album.photo_set, obj)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.query
        context['person'] = self.person
        context['location'] = self.location
        context['back_link'] = self.back_link
        context['paginator'] = self.paginator
        return context


class Move(AjaxUpdateView):
    template_name = 'photos/ajax_form.html'
    form_class = PhotoMoveForm
    model = Photo

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Move Photo')
        context['form_submit'] = _('Save')
        return context


class Rename(AjaxUpdateView):
    template_name = 'photos/ajax_form.html'
    form_class = PhotoNameForm
    model = Photo

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Rename Photo')
        context['form_submit'] = _('Save')
        return context


class Tag(AjaxUpdateView):
    template_name = 'photos/ajax_form.html'
    form_class = PhotoTagForm
    model = Photo

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Tag Photo')
        context['form_submit'] = _('Save')
        return context


class Rotate(AjaxFormMixin, View):
    def post(self, request, *args, **kwargs):
        photo = get_object_or_404(Photo, pk=kwargs['pk'])
        rotate_image(photo.file)
        for thumb in photo.thumbnail_set.all():
            rotate_image(thumb.file)
        return self.json(url=photo.get_absolute_url())


class Delete(AjaxDeleteView):
    template_name = 'photos/ajax_form.html'
    model = Photo

    def get_success_url(self):
        return self.object.album.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Delete Photo')
        context['form_submit'] = _('Delete')
        context['form_messages'] = (
            _('Are you sure you want to delete this photo?'),
        )
        return context


class Download(DetailView):
    model = Photo

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        file_data = self.object.file.file.read()
        mimetype = mimetypes.guess_type(self.object.file.name, strict=False)[0]
        response = HttpResponse(file_data, content_type=mimetype)
        response['Content-Disposition'] = 'attachment; filename={}'.format(self.object.file.name.split('/')[-1])
        return response


detail = login_required(Detail.as_view())
move = permission_required('photos.edit_photo')(Move.as_view())
rename = permission_required('photos.edit_photo')(Rename.as_view())
tag = permission_required('photos.edit_photo')(Tag.as_view())
rotate = permission_required('photos.edit_photo')(Rotate.as_view())
delete = permission_required('photos.delete_album')(Delete.as_view())
download = login_required(Download.as_view())
