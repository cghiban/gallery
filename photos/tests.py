import json

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from .models import Location, Person, Album


class SuperuserTest(TestCase):
    def ajax_post(self, url, form_data):
        response = self.client.post(
            url, form_data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        return json.loads(response.content.decode("utf-8"))

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
        result = self.ajax_post(reverse('location_create'), data)
        self.assertTrue('html' in result)
        # valid location, redirect (via ajax)
        data = {'name': 'location1'}
        result = self.ajax_post(reverse('location_create'), data)
        self.assertTrue('url' in result)

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
        result = self.ajax_post(
            reverse('location_rename', kwargs=dict(pk=1)), data)
        self.assertTrue('html' in result)
        # valid location, redirect (via ajax)
        data = {'name': 'location2'}
        result = self.ajax_post(
            reverse('location_rename', kwargs=dict(pk=1)), data)
        self.assertTrue('url' in result)
        self.assertEqual(Location.objects.get(pk=1).name, 'location2')

    def test_delete(self):
        Location.objects.create(name='location1')
        self.assertEqual(Location.objects.count(), 1)
        data = {'submit': True}
        result = self.ajax_post(
            reverse('location_delete', kwargs=dict(pk=1)), data)
        self.assertTrue('url' in result)
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
        result = self.ajax_post(reverse('person_create'), data)
        self.assertTrue('html' in result)
        # valid person, redirect (via ajax)
        data = {'name': 'person1'}
        result = self.ajax_post(reverse('person_create'), data)
        self.assertTrue('url' in result)

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
        result = self.ajax_post(
            reverse('person_rename', kwargs=dict(pk=1)), data)
        self.assertTrue('html' in result)
        # valid person, redirect (via ajax)
        data = {'name': 'person2'}
        result = self.ajax_post(
            reverse('person_rename', kwargs=dict(pk=1)), data)
        self.assertTrue('url' in result)
        self.assertEqual(Person.objects.get(pk=1).name, 'person2')

    def test_delete(self):
        Person.objects.create(name='person1')
        self.assertEqual(Person.objects.count(), 1)
        data = {'submit': True}
        result = self.ajax_post(
            reverse('person_delete', kwargs=dict(pk=1)), data)
        self.assertTrue('url' in result)
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
        result = self.ajax_post(reverse('album_create'), data)
        self.assertTrue('html' in result)
        # valid album, redirect (via ajax)
        data = {'name': 'album1'}
        result = self.ajax_post(reverse('album_create'), data)
        self.assertTrue('url' in result)

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
        result = self.ajax_post(
            reverse('album_edit', kwargs=dict(pk=1)), data)
        self.assertTrue('html' in result)
        # valid album, redirect (via ajax)
        data = {'name': 'album2'}
        result = self.ajax_post(
            reverse('album_edit', kwargs=dict(pk=1)), data)
        self.assertTrue('url' in result)
        self.assertEqual(Album.objects.get(pk=1).name, 'album2')

    def test_delete(self):
        Album.objects.create(name='album1')
        self.assertEqual(Album.objects.count(), 1)
        data = {'submit': True}
        result = self.ajax_post(
            reverse('album_delete', kwargs=dict(pk=1)), data)
        self.assertTrue('url' in result)
        self.assertEqual(Album.objects.count(), 0)
