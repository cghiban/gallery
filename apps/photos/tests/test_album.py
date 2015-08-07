from django.core.urlresolvers import reverse

from apps.photos.models import Album, Location
from apps.photos.tests import SuperuserTest


class AlbumListView(SuperuserTest):
    def test_list(self):
        """
        Test that the album list view works properly.
        """
        response = self.client.get(reverse('albums'))
        self.assertTrue('album_list' in response.context)
        self.assertTrue('paginator' in response.context)


class AlbumCreateView(SuperuserTest):
    def test_create(self):
        """
        Test that album creation works properly.
        """
        # invalid album, display form again
        data = {'name': ''}
        self.json_post_value(reverse('album_create'), 'html', data)
        # valid album, redirect (via ajax)
        data = {'name': 'album1'}
        self.json_post_value(reverse('album_create'), 'url', data)


class AlbumDetailView(SuperuserTest):
    def test_detail(self):
        """
        Test that the album detail view works properly.
        """
        Album.objects.create(name='album1')
        response = self.client.get(reverse('album', kwargs=dict(pk=1)))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('album' in response.context)
        self.assertTrue('paginator' in response.context)
        self.assertTrue('photo_list' in response.context)

    def test_detail_location(self):
        """
        Test that the album detail view works properly from location.
        """
        loc = Location.objects.create(name='location1')
        loc.album_set.create(name='album1')
        kwargs = {'pk': 1, 'location_pk': 1}
        response = self.client.get(reverse('album', kwargs=kwargs))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('album' in response.context)
        self.assertTrue('paginator' in response.context)
        self.assertTrue('photo_list' in response.context)


class AlbumEditView(SuperuserTest):
    def test_edit(self):
        """
        Test that the album edit view works properly.
        """
        Album.objects.create(name='album1')
        self.assertEqual(Album.objects.get(pk=1).name, 'album1')
        # invalid album, display form again
        data = {'name': ''}
        self.json_post_value(
            reverse('album_edit', kwargs=dict(pk=1)), 'html', data)
        # valid album, redirect (via ajax)
        data = {'name': 'album2'}
        self.json_post_value(
            reverse('album_edit', kwargs=dict(pk=1)), 'url', data)
        self.assertEqual(Album.objects.get(pk=1).name, 'album2')


class AlbumDeleteView(SuperuserTest):
    def test_delete(self):
        Album.objects.create(name='album1')
        self.assertEqual(Album.objects.count(), 1)
        self.json_get_value(
            reverse('album_delete', kwargs=dict(pk=1)), 'html')
        data = {'submit': True}
        self.json_post_value(
            reverse('album_delete', kwargs=dict(pk=1)), 'url', data)
        self.assertEqual(Album.objects.count(), 0)
