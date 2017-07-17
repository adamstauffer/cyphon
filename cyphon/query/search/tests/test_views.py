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
Tests for the search endpoint.
"""

# third party
from django.test import TestCase

# local
from tests.api_tests import CyphonAPITestCase


class SearchViewTestCase(CyphonAPITestCase):
    model_url = 'search/'

    def test_valid_query(self):
        response = self.get_api_response('?query=valid')
        self.assertEqual(response.status_code, 200)


