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
Test version middleware and helper functions.
"""

# standard library
try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch

# third party
from django.test import TestCase
from django.test.client import RequestFactory

# local
from cyphon.version import VersionMiddleware


class VersionMiddlewareTest(TestCase):
    """
    Tests the VersionMiddleware class.
    """

    def setUp(self):
        self.version_number = '1.3.0-97-gbd968c1'
        self.get_response = MagicMock(return_value={})
        self.factory = RequestFactory()

    def create_middleware(self):
        """
        Creates a VersionMiddleware instance.
        """
        return VersionMiddleware(self.get_response)

    def check_get_response_is_called(self, request):
        """

        """
        self.get_response.assert_called_once_with(request)

    @staticmethod
    def check_output_is_called(check_output):
        """

        """
        check_output.assert_called_once_with(
            ['git', 'describe', '--tags', '--abbrev=0'])

    @patch('cyphon.version.check_output', return_value=b'1.2.0')
    def test_correct_version_added(self, check_output):
        """
        Tests that the correct version number is returned when a call to
        """
        middleware = self.create_middleware()
        self.check_output_is_called(check_output)

        request = self.factory.get('/login/')
        response = middleware(request)

        self.check_get_response_is_called(request)
        self.assertEqual(response[VersionMiddleware.VERSION_HEADER], '1.2.0')

    @patch('cyphon.version.check_output', return_value=b'incorrect')
    def test_incorrect_git_response(self, check_output):
        """
        Tests that the version number is blank if git returns a tag that
        doesn't contain the version number.
        """

        middleware = self.create_middleware()
        self.check_output_is_called(check_output)

        request = self.factory.get('/login/')
        response = middleware(request)

        self.check_get_response_is_called(request)
        self.assertEqual(response[VersionMiddleware.VERSION_HEADER], '')

    @patch('cyphon.version.check_output', return_value=b'1.2.0')
    def test_mock_view(self, check_output):
        """
        Tests that the version header is added to any requests.
        """
        response = self.client.get('/login/')
        self.check_output_is_called(check_output)
        self.assertEqual(response[VersionMiddleware.VERSION_HEADER], '1.2.0')

        response = self.client.get('/api/v1/')
        self.assertEqual(response[VersionMiddleware.VERSION_HEADER], '1.2.0')
