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
Tests the Pipe class and the related RateLimit and SpecSheet classes.
"""

# standard library
from unittest.mock import Mock, patch

# local
from responder.actions.models import Action
from tests.api_tests import CyphonAPITestCase
from tests.fixture_manager import get_fixtures


class ActionsViewTestCase(CyphonAPITestCase):
    """
    Base class for testing the Action views.
    """

    fixtures = get_fixtures(['actions', 'alerts'])

    model_url = 'actions/'

    obj_url = '1/'

    # def test_run(self):
    #     """

    #     """
    #     pass
