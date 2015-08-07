from django.conf import settings
from django.contrib.auth.decorators import permission_required, login_required
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import QueryDict
from django.views.generic import FormView, ListView
from django.utils.translation import ugettext as _

from apps.photos.forms import UploadForm, SearchForm
from apps.photos.models import Photo
from apps.stream.utils import send_action


def get_search_queryset(query):
    """
    Build and return a Photo queryset based on the parameters passed in, which will be a querystring
    containing the user's search terms.
    """
    data = QueryDict(query)
    queryset = Photo.objects.all()

    q = data.get('q')
    a = data.getlist('a')
    p = data.getlist('p')
    l = data.getlist('l')

    if q:
        queryset = queryset.filter(Q(name__icontains=q) | Q(album__name__icontains=q))
    if a:
        queryset = queryset.filter(album__in=a)
    if p:
        queryset = queryset.filter(people__in=p)
    if l:
        queryset = queryset.filter(album__location__in=l)

    return queryset


class Upload(FormView):
    template_name = 'photos/upload.html'
    form_class = UploadForm

    def form_valid(self, form):
        album = form.save()
        self.success_url = album.get_absolute_url()
        action = 'added {} photos to the album'.format(form.photo_count)
        send_action(self.request.user, action, target=album)
        return super().form_valid(form)


class Search(FormView):
    template_name = 'photos/search.html'
    form_class = SearchForm

    def form_valid(self, form):
        datacopy = form.data.copy()
        if 'csrfmiddlewaretoken' in datacopy:
            del datacopy['csrfmiddlewaretoken']
        self.success_url = reverse('results', kwargs={'query': datacopy.urlencode()})
        return super().form_valid(form)


class Results(ListView):
    paginate_by = settings.PHOTOS_PER_PAGE
    template_name = 'photos/photo_list.html'

    def get_queryset(self):
        return get_search_queryset(self.kwargs['query'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        back_link = reverse('search'), _('Search')

        context['query'] = self.kwargs['query']
        context['back_link'] = back_link
        context['page_title'] = _('Results')
        return context


upload = permission_required('photos.add_photo')(Upload.as_view())
search = login_required(Search.as_view())
results = login_required(Results.as_view())
