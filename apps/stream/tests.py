from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from apps.stream.models import Action


class StreamViews(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='jacob', email='jacob@example.com', password='secret')

    def test_views_unathenticated(self):
        """
        Test to make sure an unauthenticated user can not get to secure views.
        """
        client = Client()
        response = client.get(reverse('home'))
        self.assertRedirects(
            response,
            '%s?next=%s' % (reverse('accounts:login'), reverse('home')))

    def test_views_authenticated(self):
        """
        Test to make sure an authenticated user can get to secure views.
        """
        client = Client()
        client.login(username='jacob', password='secret')
        response = client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('action_list' in response.context)


class StreamModel(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='jacob', email='jacob@example.com', password='secret')

    def test_str(self):
        """
        Test the various outputs for Action.__str__.
        """
        action = Action(user=self.user, verb='tested')
        self.assertEqual(str(action), 'jacob tested')
        action = Action(user=self.user, verb='tested', action_object=self.user)
        self.assertEqual(str(action), 'jacob tested jacob')
        action = Action(user=self.user, verb='tested', target=self.user)
        self.assertEqual(str(action), 'jacob tested jacob')
        action = Action(user=self.user, verb='tested', join='on', action_object=self.user, target=self.user)
        self.assertEqual(str(action), 'jacob tested jacob on jacob')
