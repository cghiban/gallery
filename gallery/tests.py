from django.core.handlers.wsgi import WSGIHandler
from django.test import TestCase

from gallery.wsgi import application


class TestGallery(TestCase):
    def test_wsgi(self):
        """
        Test that WSGI application works.
        """
        self.assertTrue(isinstance(application, WSGIHandler))