import json

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.test import TestCase, RequestFactory

from utils.uploads import split_extension, file_allowed, get_unique_upload_path
from utils.views import json_render, json_redirect


class FakeModel:
    class Meta:
        app_label = 'testing'
        model_name = 'fake_model'

    def __init__(self):
        self._meta = FakeModel.Meta()


class Uploads(TestCase):
    def test_split_extension(self):
        """
        Test that split_extension method works properly.
        """
        scenarios = {
            'awesome_filename.jpg': ['awesome_filename', 'jpg'],
            'path/awesome_filename.GIF': ['path/awesome_filename', 'gif'],
            'path/path/awesome_filename': ['path/path/awesome_filename', ''],
        }
        for input, output in scenarios.items():
            name, ext = split_extension(input)
            self.assertEqual(name, output[0])
            self.assertEqual(ext, output[1])

    def test_file_allowed(self):
        """
        Test that file_allowed method works properly on all ALLOWED_EXTENSIONS
        and does not allow other file types.
        """
        scenarios = {
            'path/awesome_filename.exe': False,
            'path/awesome_filename.dll': False,
            'path/awesome_filename.sh': False,
            'path/awesome_filename': False,
        }
        for ext in settings.ALLOWED_EXTENSIONS:
            scenarios['path/awesome_filename.{}'.format(ext)] = True
        for input, output in scenarios.items():
            result = file_allowed(input)
            self.assertEqual(result, output)

    def test_get_unique_upload_path(self):
        """
        Test that get_unique_upload_path works properly.
        """
        instance = FakeModel()
        filename = get_unique_upload_path(instance, 'image.jpg')
        self.assertEqual(len(filename), 55)
        self.assertEqual(filename[:19], 'testing/fake_model/')
        self.assertEqual(filename[-4:], '.jpg')


class Views(TestCase):
    def test_json_render(self):
        """
        Test that the json_render view works properly.
        """
        self.factory = RequestFactory()
        # raises an error if not an ajax request
        request = self.factory.get('/dummy')
        with self.assertRaises(PermissionDenied):
            response = json_render(request, 'base.html', {})
        # works fine if it is an ajax request
        request = self.factory.get(
            '/dummy', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response = json_render(request, 'base.html', {})
        result = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('html' in result)

    def test_json_redirect(self):
        """
        Test that the json_redirect view works properly.
        """
        self.factory = RequestFactory()
        # raises an error if not an ajax request
        request = self.factory.get('/dummy')
        with self.assertRaises(PermissionDenied):
            response = json_redirect(request, '/dummy2')
        # works fine if it is an ajax request
        request = self.factory.get(
            '/dummy', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response = json_redirect(request, '/dummy2')
        result = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('url' in result)
