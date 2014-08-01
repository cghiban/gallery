from collections import namedtuple
import json

from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.test import TestCase, RequestFactory

from utils.paginate import paginate

from utils.views import json_render, json_redirect


class Views(TestCase):
    def test_json_render(self):
        """
        Test that the json_render view works properly.
        """
        self.factory = RequestFactory()
        # raises an error if not an ajax request
        request = self.factory.get('/dummy')
        with self.assertRaises(PermissionDenied):
            response = json_render(request, 'base.html', {})
        # works fine if it is an ajax request
        request = self.factory.get(
            '/dummy', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response = json_render(request, 'base.html', {})
        result = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('html' in result)

    def test_json_redirect(self):
        """
        Test that the json_redirect view works properly.
        """
        self.factory = RequestFactory()
        # raises an error if not an ajax request
        request = self.factory.get('/dummy')
        with self.assertRaises(PermissionDenied):
            response = json_redirect(request, '/dummy2')
        # works fine if it is an ajax request
        request = self.factory.get(
            '/dummy', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response = json_redirect(request, '/dummy2')
        result = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('url' in result)


class Paginate(TestCase):
    def get_article_set(self):
        """
        Return a list of article instances.
        """
        # Our paginator does not care if the instance is a model or not, so
        # create a dummy class here to use instead of an actual model.
        Article = namedtuple("Article", field_names=('title'))

        output = []
        for x in range(1, 10):
            output += Article(title='Test%s' % x)
        return output

    def get_scenarios(self):
        return (
            # page 1 is default
            ('/dummy', 1, '/dummy?p=2', None, ['Test1', 'Test2', 'Test3']),
            # page 2 has next and previous
            ('/dummy?p=2', 2, '/dummy?p=3', '/dummy?p=1',
             ['Test4', 'Test5', 'Test6']),
            # page 3 does not have next
            ('/dummy?p=3', 3, None, '/dummy?p=2', ['Test7', 'Test8', 'Test9']),
            # invalid number defaults to page 1
            ('/dummy?p=str', 1, '/dummy?p=2', None,
             ['Test1', 'Test2', 'Test3']),
            # additional query params
            ('/dummy?id=1&p=2&pk=5', 2, '/dummy?p=3&id=1&pk=5',
             '/dummy?p=1&id=1&pk=5', ['Test4', 'Test5', 'Test6']),
        )

    def test_paginator(self):
        """
        Test that our custom paginate() method works properly.
        """
        factory = RequestFactory()
        articles = self.get_article_set()

        for test_row in self.get_scenarios():
            url, page, next_url, prev_url, results = test_row
            request = factory.get(url)
            paginator, queryset = paginate(request, articles, 3)
            self.assertEqual(paginator.this_page.number, page)
            self.assertEqual(paginator.next_url, next_url)
            self.assertEqual(paginator.previous_url, prev_url)
            self.assertEqual(queryset, results)

        # there is no page 4 so it throws an error
        request = factory.get('/dummy?p=4')
        with self.assertRaises(Http404):
            paginate(request, articles, 3)
