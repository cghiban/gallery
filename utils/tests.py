from collections import namedtuple
import json
from urllib.parse import urlparse

from django.core.exceptions import PermissionDenied
from django.http import Http404, QueryDict
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
            # ( params, page, prev_params, next_params, results )

            # page 1 (default)
            ( '', 1, None, 'p=2', ['Test1', 'Test2', 'Test3']),
            # page 1 is default for non-numeric
            ( 'p=invalid', 1, None, 'p=2', ['Test1', 'Test2', 'Test3']),
            # page 2 has next and previous
            ( 'p=2', 2, 'p=1', 'p=3', ['Test4', 'Test5', 'Test6']),
            # page 3 does not have next
            ( 'p=3', 3, 'p=2', None, ['Test7', 'Test8', 'Test9']),
            # additional query params
            ( 'a=1&b=2&p=2', 2, 'a=1&b=2&p=1', 'a=1&b=2&p=3', ['Test4', 'Test5', 'Test6']),
        )

    def test_paginate(self):
        """
        Test that our custom paginate() method works properly.
        """
        factory = RequestFactory()
        articles = self.get_article_set()
        url = '/dummy/page'

        for test in self.get_scenarios():
            params, page, prev_params, next_params, results = test
            request = factory.get(url + '?' + QueryDict(params).urlencode())
            paginator, queryset = paginate(request, articles, 3)
            self.assertEqual(paginator.this_page.number, page)
            self.assertEqual(queryset, results)
            if next_params:
                next_dict = QueryDict(next_params)
                pag_dict = QueryDict(urlparse(paginator.next_url).query)
                self.assertEqual(next_dict, pag_dict)
            if prev_params:
                prev_dict = QueryDict(prev_params)
                pag_dict = QueryDict(urlparse(paginator.previous_url).query)
                self.assertEqual(prev_dict, pag_dict)

        # there is no page 4 so it throws an error
        request = factory.get('/dummy?p=4')
        with self.assertRaises(Http404):
            paginate(request, articles, 3)

        # allow empty works
        request = factory.get('/dummy')
        paginator, queryset = paginate(request, [], 3, allow_empty=True)
        self.assertEqual(queryset, [])

        # don't allow empty
        request = factory.get('/dummy')
        with self.assertRaises(Http404):
            paginate(request, [], 3, allow_empty=False)