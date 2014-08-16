from io import StringIO
import json
import os
import shutil
import tempfile

from django.db.models.fields.files import ImageFieldFile
from django.test import TestCase, Client, override_settings
from django.core.urlresolvers import reverse
from django.core.files import File
from django.contrib.auth.models import User
from django.core.management import call_command

from .models import Location, Person, Album, Photo, Thumbnail

from photos.utils import friendly_filename


MEDIA_ROOT = tempfile.mkdtemp()


class SuperuserTest(TestCase):
    def ajax_post(self, url, form_data):
        response = self.client.post(
            url, form_data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        return json.loads(response.content.decode("utf-8"))

    def value_in_result(self, url, value, data):
        result = self.ajax_post(url, data)
        self.assertTrue(value in result)

    def setUp(self):
        # create a superuser so that we can test create/update
        self.user = User.objects.create_superuser(
            'tim', 'tim@example.com', 'secret')
        self.client = Client()
        self.client.login(username='tim', password='secret')


class LocationViews(SuperuserTest):
    def test_list(self):
        """
        Test that the location list view works properly.
        """
        response = self.client.get(reverse('locations'))
        self.assertTrue('location_list' in response.context)
        self.assertTrue('paginator' in response.context)

    def test_create(self):
        """
        Test that location creation works properly.
        """
        # invalid location, display form again
        data = {'name': ''}
        self.value_in_result(reverse('location_create'), 'html', data)
        # valid location, redirect (via ajax)
        data = {'name': 'location1'}
        self.value_in_result(reverse('location_create'), 'url', data)

    def test_detail(self):
        """
        Test that the location detail view works properly.
        """
        Location.objects.create(name='location1')
        response = self.client.get(reverse('location', kwargs=dict(pk=1)))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('location' in response.context)
        self.assertTrue('paginator' in response.context)
        self.assertTrue('back_link' in response.context)
        self.assertTrue('album_list' in response.context)

    def test_rename(self):
        """
        Test that the location rename view works properly.
        """
        Location.objects.create(name='location1')
        self.assertEqual(Location.objects.get(pk=1).name, 'location1')
        # invalid location, display form again
        data = {'name': ''}
        self.value_in_result(
            reverse('location_rename', kwargs=dict(pk=1)), 'html', data)
        # valid location, redirect (via ajax)
        data = {'name': 'location2'}
        self.value_in_result(
            reverse('location_rename', kwargs=dict(pk=1)), 'url', data)
        self.assertEqual(Location.objects.get(pk=1).name, 'location2')

    def test_delete(self):
        Location.objects.create(name='location1')
        self.assertEqual(Location.objects.count(), 1)
        data = {'submit': True}
        self.value_in_result(
            reverse('location_delete', kwargs=dict(pk=1)), 'url', data)
        self.assertEqual(Location.objects.count(), 0)


class PersonViews(SuperuserTest):
    def test_list(self):
        """
        Test that the person list view works properly.
        """
        response = self.client.get(reverse('people'))
        self.assertTrue('person_list' in response.context)
        self.assertTrue('paginator' in response.context)

    def test_create(self):
        """
        Test that person creation works properly.
        """
        # invalid person, display form again
        data = {'name': ''}
        self.value_in_result(reverse('person_create'), 'html', data)
        # valid person, redirect (via ajax)
        data = {'name': 'person1'}
        self.value_in_result(reverse('person_create'), 'url', data)

    def test_detail(self):
        """
        Test that the person detail view works properly.
        """
        Person.objects.create(name='person1')
        response = self.client.get(reverse('person', kwargs=dict(pk=1)))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('person' in response.context)
        self.assertTrue('paginator' in response.context)
        self.assertTrue('back_link' in response.context)
        self.assertTrue('photo_list' in response.context)

    def test_rename(self):
        """
        Test that the person rename view works properly.
        """
        Person.objects.create(name='person1')
        self.assertEqual(Person.objects.get(pk=1).name, 'person1')
        # invalid person, display form again
        data = {'name': ''}
        self.value_in_result(
            reverse('person_rename', kwargs=dict(pk=1)), 'html', data)
        # valid person, redirect (via ajax)
        data = {'name': 'person2'}
        self.value_in_result(
            reverse('person_rename', kwargs=dict(pk=1)), 'url', data)
        self.assertEqual(Person.objects.get(pk=1).name, 'person2')

    def test_delete(self):
        Person.objects.create(name='person1')
        self.assertEqual(Person.objects.count(), 1)
        data = {'submit': True}
        self.value_in_result(
            reverse('person_delete', kwargs=dict(pk=1)), 'url', data)
        self.assertEqual(Person.objects.count(), 0)


class AlbumViews(SuperuserTest):
    def test_list(self):
        """
        Test that the album list view works properly.
        """
        response = self.client.get(reverse('albums'))
        self.assertTrue('album_list' in response.context)
        self.assertTrue('paginator' in response.context)

    def test_create(self):
        """
        Test that album creation works properly.
        """
        # invalid album, display form again
        data = {'name': ''}
        self.value_in_result(reverse('album_create'), 'html', data)
        # valid album, redirect (via ajax)
        data = {'name': 'album1'}
        self.value_in_result(reverse('album_create'), 'url', data)

    def test_detail(self):
        """
        Test that the album detail view works properly.
        """
        Album.objects.create(name='album1')
        response = self.client.get(reverse('album', kwargs=dict(pk=1)))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('album' in response.context)
        self.assertTrue('paginator' in response.context)
        self.assertTrue('back_link' in response.context)
        self.assertTrue('photo_list' in response.context)

    def test_edit(self):
        """
        Test that the album edit view works properly.
        """
        Album.objects.create(name='album1')
        self.assertEqual(Album.objects.get(pk=1).name, 'album1')
        # invalid album, display form again
        data = {'name': ''}
        self.value_in_result(
            reverse('album_edit', kwargs=dict(pk=1)), 'html', data)
        # valid album, redirect (via ajax)
        data = {'name': 'album2'}
        self.value_in_result(
            reverse('album_edit', kwargs=dict(pk=1)), 'url', data)
        self.assertEqual(Album.objects.get(pk=1).name, 'album2')

    def test_delete(self):
        Album.objects.create(name='album1')
        self.assertEqual(Album.objects.count(), 1)
        data = {'submit': True}
        self.value_in_result(
            reverse('album_delete', kwargs=dict(pk=1)), 'url', data)
        self.assertEqual(Album.objects.count(), 0)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ModelTest(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT)

    def setUp(self):
        self.person = Person.objects.create(name='person1')
        self.location = Location.objects.create(name='location1')
        self.album = self.location.album_set.create(name='album1')
        self.photo = self.album.photo_set.create(name='photo1')
        self.photo.people.add(self.person)
        self.photo.file = File(open('photos/fixtures/milkyway.jpg', 'rb'))
        self.photo.save()
        self.thumbnail = Thumbnail.objects.create(
            photo=self.photo, size='200x200-fit')

    def test_str(self):
        """
        Test the various outputs for __str__.
        """
        self.assertEqual(str(self.location), self.location.name)
        self.assertEqual(str(self.album), self.album.name)
        self.assertEqual(str(self.photo), self.photo.name)
        self.assertEqual(str(self.person), self.person.name)
        self.assertEqual(str(self.thumbnail), 'photo1 (200x200-fit)')

    def test_cover_photo(self):
        """
        Test that cover photo is an instance of Photo.
        """
        self.assertTrue(isinstance(self.location.cover_photo, Photo))
        self.assertTrue(isinstance(self.album.cover_photo, Photo))
        self.assertTrue(isinstance(self.person.cover_photo, Photo))

    def test_photo_thumbnail(self):
        """
        Test that a thumbnail can be created for a photo.
        """
        thumbnail = self.photo.thumbnail('800x600-fit')
        self.assertTrue(isinstance(thumbnail, ImageFieldFile))
        self.assertTrue(isinstance(self.photo.file_medium, ImageFieldFile))
        self.assertTrue(isinstance(self.photo.file_thumb, ImageFieldFile))
        # and also test the sizes of the thumbnail
        self.assertEqual(self.photo.file_medium.height, 630)
        self.assertEqual(self.photo.file_medium.width, 1024)
        self.assertEqual(self.photo.file_thumb.height, 200)
        self.assertEqual(self.photo.file_thumb.width, 200)

    def test_album_date_display(self):
        """
        Test the date display for an album.
        """
        self.album.month = 12
        self.album.year = 2013
        self.assertEqual(self.album.get_date_display(), 'December 2013')
        self.album.month = 12
        self.album.year = None
        self.assertEqual(self.album.get_date_display(), 'December')
        self.album.month = None
        self.album.year = 2013
        self.assertEqual(self.album.get_date_display(), '2013')


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
            result = friendly_filename(input)
            self.assertEqual(result, output)
        self.assertEqual('A' * 200, friendly_filename('A' * 201))


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestCleanupPhotosCommand(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT)

    def setUp(self):
        """
        Create some photos and thumbnails for our tests.
        """
        self.album = Album.objects.create(name='album1')
        for x in range(1, 5):
            p = self.album.photo_set.create(name='photo%s' % x)
            p.file = File(open('photos/fixtures/milkyway.jpg', 'rb'))
            p.save()
            p.thumbnail('200x200-fit')
        for x in range(1, 4):
            p = Photo.objects.get(pk=x)
            p.delete()

    def test_command(self):
        """
        Test that the management command works properly.
        """
        photo_dir = os.path.join(MEDIA_ROOT, 'photos', 'photo')
        thumb_dir = os.path.join(MEDIA_ROOT, 'photos', 'thumbnail')
        # When the test starts there should be 4 files in each directory
        self.assertEqual(len(os.listdir(photo_dir)), 4)
        self.assertEqual(len(os.listdir(thumb_dir)), 4)
        # Then we call the command to clean up
        call_command('cleanup_photos', stdout=StringIO(), verbosity=2)
        # And it should delete all but one of the files
        self.assertEqual(len(os.listdir(photo_dir)), 1)
        self.assertEqual(len(os.listdir(thumb_dir)), 1)
