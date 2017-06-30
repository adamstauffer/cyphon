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

# standard library
from unittest.mock import patch

# third party
from django.test import TestCase

# local
from distilleries.models import Distillery
from engines.queries import EngineQuery
from cyphon.fieldsets import QueryFieldset
from query.search.search_query import SearchQuery, UnknownParameter
from query.search.field_search_parameter import FieldSearchParameter
from query.search.distillery_filter_parameter import DistilleryFilterParameter
from query.search.keyword_search_parameter import KeywordSearchParameter
from tests.fixture_manager import get_fixtures

MOCK_RESULTS_LIST = [{'id': 1, 'content': 'content'}]

MOCK_RESULTS = {
    'count': 1,
    'results': MOCK_RESULTS_LIST,
}

MOCK_FIND = patch(
    'distilleries.models.Distillery.find',
    return_value=MOCK_RESULTS,
)


class SearchQueryTestCase(TestCase):
    """
    Tests the SearchQuery class.
    """

    fixtures = get_fixtures(['distilleries'])

    def test_empty_search_query_error(self):
        """
        Tests that an empty error is thrown if the query is empty.
        """
        query = SearchQuery('')

        self.assertFalse(query.is_valid())
        self.assertEqual(len(query.errors), 1)
        self.assertEqual(query.errors[0], SearchQuery.EMPTY_SEARCH_QUERY)

    def test_parsing_error(self):
        """
        Tests that a parsing error is thrown if the query cannot be parsed.
        """
        query = SearchQuery(' ')

        self.assertFalse(query.is_valid())
        self.assertEqual(len(query.errors), 1)
        self.assertEqual(query.errors[0], SearchQuery.PARSING_ERROR.format(' '))

    def test_unknown_parameters(self):
        """
        Tests that unknown parameter types are correctly identified.
        """
        unknown_parameter_string_1 = 'fjlk#!!.!@#$'
        unknown_parameter_string_2 = 'fieoh$%@.!@98'
        unknown_parameter_1 = UnknownParameter(0, unknown_parameter_string_1)
        unknown_parameter_2 = UnknownParameter(1, unknown_parameter_string_2)
        query = SearchQuery(
            '{} {}'.format(
                unknown_parameter_string_1,
                unknown_parameter_string_2,
            )
        )

        self.assertFalse(query.is_valid())
        self.assertEqual(len(query.unknown), 2)
        self.assertEqual(len(query.parameter_errors), 2)
        self.assertEqual(
            query.parameter_errors[0],
            unknown_parameter_1.get_parameter_info(),
        )
        self.assertEqual(
            query.parameter_errors[1],
            unknown_parameter_2.get_parameter_info(),
        )

    def test_parameter_index(self):
        """
        Tests that the parameter index is correct for each search
        parameter.
        """
        query = SearchQuery('ip_address=34.25.12.32 "search phrase"')

        self.assertTrue(query.is_valid())
        self.assertEqual(len(query.keywords), 1)
        self.assertEqual(query.keywords[0].index, 1)
        self.assertEqual(len(query.fields), 1)
        self.assertEqual(query.fields[0].index, 0)

    def test_distillery_parameter(self):
        """
        Tests that a distillery filter string is correctly identified.
        """
        query = SearchQuery('@source=*.test_logs')

        self.assertTrue(query.is_valid())
        self.assertEqual(len(query.distilleries), 1)

    def test_parameter_errors(self):
        """
        Tests that the parameter errors are passed onto the search
        query object.
        """
        field_parameter_string = 'field_name=blah'
        field_parameter = FieldSearchParameter(0, field_parameter_string)
        query = SearchQuery(field_parameter_string)

        self.assertFalse(query.is_valid())
        self.assertEqual(len(query.parameter_errors), 1)
        self.assertEqual(
            query.parameter_errors[0],
            field_parameter.get_parameter_info(),
        )

    def test_multiple_distillery_filters_error(self):
        """
        Tests that the query invalidates when multiple distillery filters are
        used.
        """
        query = SearchQuery('@source=*.test_logs @source=*.test_logs')

        self.assertFalse(query.is_valid())
        self.assertEqual(len(query.errors), 1)
        self.assertEqual(
            query.errors[0],
            SearchQuery.MULTPIPLE_DISTILLERY_FILTERS,
        )

    def test_get_error_dict(self):
        """
        Tests that the query outputs the correct error dictionary
        format.
        """
        field_parameter_string = 'field_name=blah'
        distillery_parameter_string = '@source=*.test_meh'
        field_parameter = FieldSearchParameter(2, field_parameter_string)
        distillery_parameter = DistilleryFilterParameter(
            1,
            distillery_parameter_string,
        )

        query = SearchQuery(
            '@source=*.test_logs {} {}'.format(
                distillery_parameter_string,
                field_parameter_string,
            )
        )

        self.assertEqual(query.get_error_dict(), {
            'query': [SearchQuery.MULTPIPLE_DISTILLERY_FILTERS],
            'parameters': [
                distillery_parameter.get_parameter_info(),
                field_parameter.get_parameter_info(),
            ]
        })

    def test_get_field_results(self):
        """
        Tests that field queries are turned into the correct
        QueryFieldsets.
        """
        query = SearchQuery('ip_address=34.23.12.32 subject=blah')
        matching_distilleries = Distillery.objects.filter(
            container__bottle__name__in=['test_doc', 'mail']
        )
        ip_address_field = FieldSearchParameter(0, 'ip_address=34.23.12.32')
        subject_field = FieldSearchParameter(1, 'subject=blah')
        expected_results = [
            {
                'count': 1,
                'distillery': distillery.pk,
                'results': MOCK_RESULTS_LIST,
            }
            for distillery
            in matching_distilleries
        ]

        self.assertTrue(query.is_valid())
        self.assertEqual(len(query.fields), 2)

        with MOCK_FIND as mock_find:
            results = query.get_results()
            self.assertEqual(
                mock_find.call_count,
                matching_distilleries.count(),
            )
            self.assertEqual(len(results), matching_distilleries.count())
            self.assertListEqual(results, expected_results)
            self.assertEqual(len(mock_find.call_args_list), 2)

            ip_address_query = mock_find.call_args_list[0][0][0]

            self.assertEqual(len(ip_address_query.subqueries), 1)
            self.assertEqual(
                vars(ip_address_query.subqueries[0]),
                vars(ip_address_field.create_fieldset())
            )
            self.assertEqual(ip_address_query.joiner, 'OR')

            subject_query = mock_find.call_args_list[1][0][0]

            self.assertEqual(len(subject_query.subqueries), 1)
            self.assertEqual(
                vars(subject_query.subqueries[0]),
                vars(subject_field.create_fieldset())
            )
            self.assertEqual(subject_query.joiner, 'OR')

    def test_get_keyword_results(self):
        """
        Tests that keyword searchs are properly transformed into the
        correct QueryFieldsets
        """
        query = SearchQuery('keyword "search phrase"')
        distilleries = [distillery for distillery in Distillery.objects.all()]

        self.assertTrue(query.is_valid())
        self.assertEqual(len(query.keywords), 2)

        with MOCK_FIND as mock_find:
            results = query.get_results()

            self.assertEqual(mock_find.call_count, len(distilleries))
            self.assertEqual(len(results), len(distilleries))

            for index, call_args in enumerate(mock_find.call_args_list):
                text_fields = distilleries[index].get_text_fields()
                expected_fieldsets = [
                    QueryFieldset(
                        field.field_name,
                        field.field_type,
                        'regex',
                        'keyword|search phrase',
                    )
                    for field
                    in text_fields
                ]
                engine_query = call_args[0][0]

                self.assertEqual(len(engine_query.subqueries), len(text_fields))

                for s_index, subquery in enumerate(engine_query.subqueries):
                    self.assertEqual(
                        vars(expected_fieldsets[s_index]),
                        vars(subquery)
                    )

    def test_distillery_filter(self):
        """
        Tests that it filters the search by distillery and that all
        keyword/field searches are present.
        """
        query = SearchQuery('@source=test_index.test_docs hello ip_address=56')
        distillery = Distillery.objects.get(
            collection__warehouse__name='test_index',
            collection__name='test_docs',
        )
        text_fields = distillery.get_text_fields()
        expected_fieldset_count = len(text_fields) + 1

        with MOCK_FIND as mock_find:
            results = query.get_results()

            self.assertEqual(len(results), 1)
            self.assertEqual(mock_find.call_count, 1)

            subqueries = mock_find.call_args[0][0].subqueries

            self.assertEqual(len(subqueries), expected_fieldset_count)

            self.assertEqual(
                vars(subqueries[0]),
                vars(FieldSearchParameter(0, 'ip_address=56').create_fieldset()),
            )

            expected_text_fieldsets = [
                QueryFieldset(
                    field.field_name,
                    field.field_type,
                    'regex',
                    'hello',
                )
                for field
                in text_fields
            ]
            text_subqueries = subqueries[1:]

            for index, subquery in enumerate(text_subqueries):
                self.assertEqual(
                    vars(expected_text_fieldsets[index]),
                    vars(subquery),
                )
