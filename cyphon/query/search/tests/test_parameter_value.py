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
Tests for the SearchQueryParameterValue classes.
"""

# third party
from django.test import TestCase

# local
from query.search.parameter import SearchParameter
from query.search.parameter_type import SearchParameterType
from query.search.parameter_value import (
    SearchParameterValue,
    KeywordValue,
    FieldValue
)
from tests.fixture_manager import get_fixtures


class SearchQueryParameterValueTestCase(TestCase):
    """
    Tests for the SearchQueryParameterValue base class.
    """

    def setUp(self):
        self.parameter_value = SearchParameterValue()

    def test_errors(self):
        """
        Ensures that there is an errors property on the instance.
        """
        self.assertListEqual(self.parameter_value.errors, [])

    def test_is_valid(self):
        """
        Tests that the is_valid returns true if there are no errors.
        """
        self.assertTrue(self.parameter_value.is_valid())

    def test_is_invalid(self):
        self.parameter_value._add_error('blah')
        self.assertListEqual(self.parameter_value.errors, ['blah'])
        self.assertFalse(self.parameter_value.is_valid())


class SearchQueryParameterKeywordValueTestCase(TestCase):
    """
    Tests the SearchQueryParameterKeywordValue class
    """

    def test_quotes_stripped(self):
        """
        Ensures that passed in parameters are stripped of double quotations.
        """
        parameter_value = KeywordValue('""')
        self.assertEqual(parameter_value.keyword, '')
        parameter_value = KeywordValue('"testing phrase"')
        self.assertEqual(parameter_value.keyword, 'testing phrase')
        parameter_value = KeywordValue('another')
        self.assertEqual(parameter_value.keyword, 'another')

    def test_empty_value_error(self):
        """
        Tests that an EMPTY_VALUE error is thrown whenever
        Returns
        -------

        """
        parameter_value = KeywordValue('""')
        self.assertFalse(parameter_value.is_valid())
        self.assertListEqual(
            parameter_value.errors,
            [KeywordValue.EMPTY_VALUE],
        )
