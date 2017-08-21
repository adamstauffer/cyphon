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
Tests views for Distilleries.
"""

# third party
from rest_framework import status

# local
from tests.api_tests import CyphonAPITestCase
from tests.fixture_manager import get_fixtures


class TagAPITests(CyphonAPITestCase):
    """
    Tests REST API endpoints for Distilleries.
    """
    fixtures = get_fixtures(['tags'])

    model_url = 'tags/'
    obj_url = '1/'

    def test_get_tag(self):
        """
        Tests the GET /api/v1/tags/1 REST API endpoint.
        """
        response = self.get_api_response(self.obj_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_tags(self):
        """
        Tests the GET /api/v1/tag/ REST API endpoint.
        """
        response = self.get_api_response()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
