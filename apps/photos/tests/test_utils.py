from django.test import TestCase

from apps.photos.utils import friendly_name


class UtilsTest(TestCase):
    def test_friendly_filename(self):
        """
        Test that friendly_filename method works properly.
        """
        scenarios = {
            'path/awesome_filename.jpg': 'awesome filename',
            'path/awesome_[]#_filename.jpg': 'awesome filename',
            'path/family photo # 1  .jpg': 'family photo 1',
        }
        for input, output in scenarios.items():
            result = friendly_name(input)
            self.assertEqual(result, output)
        self.assertEqual('A' * 200, friendly_name('A' * 201))
