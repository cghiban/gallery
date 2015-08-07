from django.core.files import File

from django.core.urlresolvers import reverse

from apps.photos.models import Person, Location, Thumbnail, Photo, Album
from apps.photos.tests import SuperuserTest, MediaMixin


class PhotoTest(MediaMixin, SuperuserTest):
    def create_data(self):
        imgfile = File(open('apps/photos/fixtures/milkyway.jpg', 'rb'))
        self.person = Person.objects.create(name='person1')
        self.location = Location.objects.create(name='location1')
        self.album = self.location.album_set.create(name='album1')
        self.photo = self.album.photo_set.create(name='photo1', file=imgfile)
        self.photo.people.add(self.person)
        self.thumbnail = Thumbnail.objects.create(photo=self.photo, size='200x200-fit')


class PhotoDetailView(PhotoTest):
    def get_photo_detail(self, kwargs):
        response = self.client.get(reverse('photo', kwargs=kwargs))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('photo' in response.context)
        self.assertTrue('paginator' in response.context)
        return response

    def test_detail_pagination(self):
        """
        Test that the photo detail view works properly with pagination.
        """
        self.create_data()
        imgfile = File(open('apps/photos/fixtures/milkyway.jpg', 'rb'))
        self.album.photo_set.create(name='photo2', file=imgfile)
        self.album.photo_set.create(name='photo3', file=imgfile)
        kwargs = {'pk': 2}
        response = self.get_photo_detail(kwargs)
        self.assertEqual(response.context['paginator']['has_next'], True)
        self.assertEqual(response.context['paginator']['has_previous'], True)
        self.assertIsNotNone(response.context['paginator']['previous_url'])
        self.assertIsNotNone(response.context['paginator']['next_url'])

    def test_detail_query(self):
        """
        Test that the photo detail view works properly from search.
        """
        self.create_data()
        kwargs = {'pk': 1, 'query': 'q=photo'}
        response = self.get_photo_detail(kwargs)
        self.assertIsNotNone(response.context['query'])

    def test_detail_person(self):
        """
        Test that the photo detail view works properly from person page.
        """
        self.create_data()
        kwargs = {'pk': 1, 'person_pk': 1}
        response = self.get_photo_detail(kwargs)
        self.assertIsNotNone(response.context['person'])

    def test_detail_location(self):
        """
        Test that the photo detail view works properly from location/album.
        """
        self.create_data()
        kwargs = {'pk': 1, 'location_pk': 1, 'album_pk': 1}
        response = self.get_photo_detail(kwargs)
        self.assertIsNotNone(response.context['location'])


class PhotoRotateView(PhotoTest):
    def test_rotate(self):
        """
        Test that the photo rotate view works properly.
        """
        self.create_data()
        self.json_post_value(
            reverse('photo_rotate', kwargs=dict(pk=1)), 'url', {'submit': 1})


class PhotoRenameView(PhotoTest):
    def test_rename(self):
        """
        Test that the photo rename view works properly.
        """
        self.create_data()
        self.assertEqual(Photo.objects.get(pk=1).name, 'photo1')
        # invalid photo, redisplay
        data = {'name': 'dd' * 500}  # name is too long
        self.json_post_value(
            reverse('photo_rename', kwargs=dict(pk=1)), 'html', data)
        # valid photo, redirect
        data = {'name': 'new-name'}
        self.json_post_value(
            reverse('photo_rename', kwargs=dict(pk=1)), 'url', data)
        self.assertEqual(Photo.objects.get(pk=1).name, 'new-name')


class PhotoMoveView(PhotoTest):
    def test_move(self):
        """
        Test that the photo move works properly.
        """
        self.create_data()
        Album.objects.create(name='album2')
        self.assertEqual(Photo.objects.get(pk=1).album.name, 'album1')
        data = {'album': 2}
        self.json_get_value(reverse('photo_move', kwargs=dict(pk=1)), 'html')
        self.json_post_value(reverse('photo_move', kwargs=dict(pk=1)), 'url', data)
        self.assertEqual(Photo.objects.get(pk=1).album.name, 'album2')


class PhotoTagView(PhotoTest):
    def test_move(self):
        """
        Test that the photo move works properly.
        """
        self.create_data()
        Person.objects.create(name='person2')
        self.assertEqual(Photo.objects.get(pk=1).people.count(), 1)
        data = {'people': [1, 2]}
        self.json_get_value(reverse('photo_tag', kwargs=dict(pk=1)), 'html')
        self.json_post_value(reverse('photo_tag', kwargs=dict(pk=1)), 'url', data)
        self.assertEqual(Photo.objects.get(pk=1).people.count(), 2)


class PhotoDeleteView(PhotoTest):
    def test_delete(self):
        self.create_data()
        self.assertEqual(Photo.objects.count(), 1)
        self.json_get_value(reverse('photo_delete', kwargs=dict(pk=1)), 'html')
        data = {'submit': True}
        self.json_post_value(reverse('photo_delete', kwargs=dict(pk=1)), 'url', data)
        self.assertEqual(Photo.objects.count(), 0)
