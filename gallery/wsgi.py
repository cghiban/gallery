import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gallery.settings.local')

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
