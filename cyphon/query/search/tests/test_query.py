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
Tests for the SearchQuery class.
"""

# third party
from django.test import TestCase

# local
from query.search.query import SearchQuery
from query.search.parameter import SearchParameter
from query.search.parameter_type import SearchParameterType
from query.search.parameter_value import KeywordValue
from tests.fixture_manager import get_fixtures


class SearchQueryTestCase(TestCase):
    """
    Tests the SearchQuery class.
    """

    fixtures = get_fixtures(['distilleries'])
    keyword_query = 'keyword "Another Keyword"'

    @staticmethod
    def _create_keyword_search_query():
        return SearchQuery(SearchQueryTestCase.keyword_query)

    def test_parameters_created(self):
        """
        Tests that the correct number of parameters were created.
        """
        search_query = SearchQueryTestCase._create_keyword_search_query()
        self.assertEqual(len(search_query.parameters), 2)

    def test_parameters_class(self):
        """
        Tests that the parameters property is a list of SearchQueryParameters.
        """
        search_query = SearchQueryTestCase._create_keyword_search_query()

        for parameter in search_query.parameters:
            self.assertIsInstance(parameter, SearchParameter)

    def test_keywords_created(self):
        """
        Tests that the parameters created are KEYWORD types.
        """
        search_query = SearchQueryTestCase._create_keyword_search_query()

        for parameter in search_query.parameters:
            self.assertEqual(parameter.type, SearchParameterType.KEYWORD)

    def test_keywords_valid(self):
        """
        Tests that the keyword parameters are valid.
        """
        search_query = SearchQueryTestCase._create_keyword_search_query()

        self.assertTrue(search_query.is_valid())

        for parameter in search_query.parameters:
            self.assertTrue(parameter.is_valid())

    def test_keyword_value_class(self):
        """
        Tests that the value property on each paramter is a
        SearchQueryParameterKeywordValue class.
        """
        search_query = SearchQueryTestCase._create_keyword_search_query()

        for parameter in search_query.parameters:
            self.assertIsInstance(
                parameter.value,
                KeywordValue
            )

    def test_keyword_empty(self):
        """
        Tests that an EMPTY_VALUE error is thrown on an incorrect keyword.
        """
        incorrect_keyword = '""'
        search_query = SearchQuery(incorrect_keyword)

        self.assertEqual(len(search_query.parameters), 1)
        self.assertFalse(search_query.parameters[0].is_valid())
        self.assertEqual(len(search_query.parameters[0].errors), 1)
        self.assertEqual(
            search_query.parameters[0].errors[0],
            KeywordValue.EMPTY_VALUE
        )
        self.assertFalse(search_query.is_valid())
        self.assertTrue(bool(search_query._errors))
        self.assertDictEqual(
            search_query._errors,
            {'parameters': [{
                'parameter': '""',
                'type': 'keyword',
                'index': 0,
                'errors': ['Keyword value is empty.']
            }]}
        )
