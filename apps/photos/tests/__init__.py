import json
import shutil
import tempfile

from django.contrib.auth.models import User
from django.test import TestCase, Client, override_settings, SimpleTestCase

MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class MediaMixin(SimpleTestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT)


class SuperuserTest(TestCase):
    def ajax_post(self, url, form_data):
        response = self.client.post(
            url, form_data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        return json.loads(response.content.decode("utf-8"))

    def ajax_get(self, url):
        response = self.client.get(
            url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        return json.loads(response.content.decode("utf-8"))

    def json_get_value(self, url, value):
        result = self.ajax_get(url)
        self.assertTrue(value in result)

    def json_post_value(self, url, value, data):
        result = self.ajax_post(url, data)
        self.assertTrue(value in result)

    def setUp(self):
        # create a superuser so that we can test create/update
        self.user = User.objects.create_superuser(
            'tim', 'tim@example.com', 'secret')
        self.client = Client()
        self.client.login(username='tim', password='secret')
