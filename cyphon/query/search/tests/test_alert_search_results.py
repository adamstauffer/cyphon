# -*- coding: utf-8 -*-
# Copyright 2017 Dunbar Security Solutions, Inc.
#
# This file is part of Cyphon Engine.
#
# Cyphon Engine is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Cyphon Engine is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Cyphon Engine. If not, see <http://www.gnu.org/licenses/>.
"""
Tests for the AlertSearchResults class.
"""

# third party
from django.test import TestCase
from django.test import RequestFactory
from django.contrib.auth import get_user_model

# local
from query.search.alert_search_results import AlertSearchResults
from query.search.search_query import SearchQuery
from tests.fixture_manager import get_fixtures


class AlertSearchResultsTestCase(TestCase):
    """

    """
    fixtures = get_fixtures(['alerts', 'comments', 'users'])
    user_model = get_user_model()

    def _get_request(self):
        return self.request_factory.get('')

    @staticmethod
    def _get_search_results(query, page=1, page_size=10):
        return AlertSearchResults(query, page, page_size)

    def setUp(self):
        self.request_factory = RequestFactory()
        self.user = self.user_model.objects.get(pk=1)

    def test_no_results(self):
        """
        Tests that no results are returned for an instance with no keywords.
        """
        alert_results = self._get_search_results(
            SearchQuery('ip_address=2', self.user),
        )

        self.assertEqual(alert_results.count, 0)
        self.assertEqual(len(alert_results.results), 0)

    def test_notes_search(self):
        """
        Tests that the the class searches through alert notes.
        """
        search_query = SearchQuery('"Some example notes"', self.user)
        alert_results = self._get_search_results(search_query)

        self.assertEqual(alert_results.count, 2)
        self.assertEqual(len(alert_results.results), 2)
        self.assertEqual(alert_results.results[0].pk, 3)

    def test_data_search(self):
        """
        Tests that the class searches through alert data.
        """
        search_query = SearchQuery('"user@example.com"', self.user)
        alert_results = self._get_search_results(search_query)

        self.assertEqual(alert_results.count, 1)
        self.assertEqual(alert_results.results[0].pk, 2)

    def test_title_search(self):
        """
        Tests that the class searches through alert titles.
        """
        search_query = SearchQuery('"Acme Supply co"', self.user)
        alert_results = self._get_search_results(search_query)

        self.assertEqual(alert_results.count, 3)

        alert_ids = [alert.pk for alert in alert_results.results]

        self.assertEqual(alert_ids, [4, 3, 1])

    def test_comment_search(self):
        """
        Tests that the class searches through alert comments.
        """
        search_query = SearchQuery(
            '"This alert isn\'t this important"', self.user)
        alert_results = self._get_search_results(search_query)

        self.assertEqual(alert_results.count, 1)
        self.assertEqual(alert_results.results[0].pk, 2)

    def test_as_dict(self):
        """
        Tests that the correct dictionary shape is returned from as_dict().
        """
        search_query = SearchQuery('example', self.user)
        alert_results = self._get_search_results(search_query)
        alert_results_as_dict = alert_results.as_dict(self._get_request())

        self.assertEqual(alert_results_as_dict['count'], 3)
        self.assertIsNone(alert_results_as_dict['next'])
        self.assertIsNone(alert_results_as_dict['previous'])
        self.assertEqual(len(alert_results_as_dict['results']), 3)

    def test_restricted_user(self):
        """
        Tests that alerts specific to a certain user are limited.
        """
        restricted_user = self.user_model.objects.get(pk=3)
        search_query = SearchQuery('"Pied Piper"', restricted_user)
        alert_results = self._get_search_results(search_query)

        self.assertEqual(alert_results.count, 0)

    def test_next_page(self):
        """
        Tests that a 'next' url is created if there is more than one page
        of results.
        """
        search_query = SearchQuery('example', self.user)
        alert_results = self._get_search_results(search_query, page_size=1)
        alert_results_as_dict = alert_results.as_dict(self._get_request())

        self.assertEqual(alert_results_as_dict['count'], 3)
        self.assertEqual(
            alert_results_as_dict['next'],
            'http://testserver/api/v1/search/alerts/?page=2',
        )
        self.assertIsNone(alert_results_as_dict['previous'])
        self.assertEqual(len(alert_results_as_dict['results']), 1)

    def test_previous_page(self):
        """
        Tests that the 'previous' url is created if there is a previous
        page of results.
        """
        search_query = SearchQuery('example', self.user)
        alert_results = self._get_search_results(
            search_query, page=3, page_size=1,
        )
        alert_results_as_dict = alert_results.as_dict(self._get_request())

        self.assertEqual(alert_results_as_dict['count'], 3)
        self.assertEqual(
            alert_results_as_dict['previous'],
            'http://testserver/api/v1/search/alerts/?page=2',
        )
        self.assertIsNone(alert_results_as_dict['next'])
        self.assertEqual(len(alert_results_as_dict['results']), 1)

    def test_filtered_alert_searching(self):
        """
        Tests that only distilleries specified are searched.
        """

        passing_search = SearchQuery('"This is some text"', self.user)
        alert_results = self._get_search_results(passing_search)

        self.assertEqual(len(alert_results.results), 1)

        failing_search = SearchQuery(
            '@source=test_index.test_logs "This is some text"', self.user)
        alert_results = self._get_search_results(failing_search)

        self.assertEqual(len(alert_results.results), 0)

        passing_search = SearchQuery(
            '@source=test_index.test_logs "Acme Supply Co"', self.user)
        alert_results = self._get_search_results(passing_search)

        self.assertEqual(len(alert_results.results), 1)
