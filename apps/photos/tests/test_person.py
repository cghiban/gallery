from django.core.urlresolvers import reverse

from apps.photos.models import Person
from apps.photos.tests import SuperuserTest


class PersonListView(SuperuserTest):
    def test_list(self):
        """
        Test that the person list view works properly.
        """
        response = self.client.get(reverse('people'))
        self.assertTrue('person_list' in response.context)
        self.assertTrue('paginator' in response.context)


class PersonCreateView(SuperuserTest):
    def test_create(self):
        """
        Test that person creation works properly.
        """
        # invalid person, display form again
        data = {'name': ''}
        self.json_post_value(reverse('person_create'), 'html', data)
        # valid person, redirect (via ajax)
        data = {'name': 'person1'}
        self.json_post_value(reverse('person_create'), 'url', data)


class PersonDetailView(SuperuserTest):
    def test_detail(self):
        """
        Test that the person detail view works properly.
        """
        Person.objects.create(name='person1')
        response = self.client.get(reverse('person', kwargs=dict(pk=1)))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('person' in response.context)
        self.assertTrue('paginator' in response.context)
        self.assertTrue('photo_list' in response.context)


class PersonRenameView(SuperuserTest):
    def test_rename(self):
        """
        Test that the person rename view works properly.
        """
        Person.objects.create(name='person1')
        self.assertEqual(Person.objects.get(pk=1).name, 'person1')
        # invalid person, display form again
        data = {'name': ''}
        self.json_post_value(
            reverse('person_rename', kwargs=dict(pk=1)), 'html', data)
        # valid person, redirect (via ajax)
        data = {'name': 'person2'}
        self.json_post_value(
            reverse('person_rename', kwargs=dict(pk=1)), 'url', data)
        self.assertEqual(Person.objects.get(pk=1).name, 'person2')


class PersonDeleteView(SuperuserTest):
    def test_delete(self):
        Person.objects.create(name='person1')
        self.assertEqual(Person.objects.count(), 1)
        data = {'submit': True}
        self.json_post_value(
            reverse('person_delete', kwargs=dict(pk=1)), 'url', data)
        self.assertEqual(Person.objects.count(), 0)
