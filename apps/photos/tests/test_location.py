from django.core.urlresolvers import reverse

from apps.photos.models import Location
from apps.photos.tests import SuperuserTest


class LocationListView(SuperuserTest):
    def test_list(self):
        """
        Test that the location list view works properly.
        """
        response = self.client.get(reverse('locations'))
        self.assertTrue('location_list' in response.context)
        self.assertTrue('paginator' in response.context)


class LocationCreateView(SuperuserTest):
    def test_create(self):
        """
        Test that location creation works properly.
        """
        # invalid location, display form again
        data = {'name': ''}
        self.json_post_value(reverse('location_create'), 'html', data)
        # valid location, redirect (via ajax)
        data = {'name': 'location1'}
        self.json_post_value(reverse('location_create'), 'url', data)


class LocationDetailView(SuperuserTest):
    def test_detail(self):
        """
        Test that the location detail view works properly.
        """
        Location.objects.create(name='location1')
        response = self.client.get(reverse('location', kwargs=dict(pk=1)))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('location' in response.context)
        self.assertTrue('paginator' in response.context)
        self.assertTrue('album_list' in response.context)


class LocationRenameView(SuperuserTest):
    def test_rename(self):
        """
        Test that the location rename view works properly.
        """
        Location.objects.create(name='location1')
        self.assertEqual(Location.objects.get(pk=1).name, 'location1')
        # invalid location, display form again
        data = {'name': ''}
        self.json_post_value(
            reverse('location_rename', kwargs=dict(pk=1)), 'html', data)
        # valid location, redirect (via ajax)
        data = {'name': 'location2'}
        self.json_post_value(
            reverse('location_rename', kwargs=dict(pk=1)), 'url', data)
        self.assertEqual(Location.objects.get(pk=1).name, 'location2')


class LocationDeleteView(SuperuserTest):
    def test_delete(self):
        Location.objects.create(name='location1')
        self.json_get_value(
            reverse('location_delete', kwargs=dict(pk=1)), 'html')
        self.assertEqual(Location.objects.count(), 1)
        data = {'submit': True}
        self.json_post_value(
            reverse('location_delete', kwargs=dict(pk=1)), 'url', data)
        self.assertEqual(Location.objects.count(), 0)
