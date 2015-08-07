from io import StringIO
import os

from django.core.files import File
from django.core.management import call_command
from django.test import TestCase

from apps.photos.models import Album, Photo
from apps.photos.tests import MEDIA_ROOT, MediaMixin


class TestCleanupPhotosCommand(MediaMixin, TestCase):
    def setUp(self):
        """
        Create some photos and thumbnails for our tests.
        """
        self.album = Album.objects.create(name='album1')
        for x in range(1, 5):
            p = self.album.photo_set.create(name='photo%s' % x)
            p.file = File(open('apps/photos/fixtures/milkyway.jpg', 'rb'))
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
