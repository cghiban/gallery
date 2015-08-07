from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings

from apps.stream.views import action_list

urlpatterns = [
    url(r'^$', action_list, name='home'),
    url(r'^auth/', include('apps.accounts.urls', 'accounts')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('apps.photos.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
