from django.core.files import File
from django.db.models.fields.files import ImageFieldFile
from django.test import TestCase

from apps.photos.models import Person, Location, Thumbnail, Photo
from apps.photos.tests import MediaMixin


class ModelTest(MediaMixin, TestCase):
    def setUp(self):
        imgfile = File(open('apps/photos/fixtures/milkyway.jpg', 'rb'))
        self.person = Person.objects.create(name='person1')
        self.location = Location.objects.create(name='location1')
        self.album = self.location.album_set.create(name='album1')
        self.photo = self.album.photo_set.create(name='photo1', file=imgfile)
        self.photo.people.add(self.person)
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
