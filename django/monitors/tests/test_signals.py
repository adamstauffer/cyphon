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
Tests signal recievers in the Monitors package.
"""

# third party
from django.test import TransactionTestCase

# local
from distilleries.models import Distillery
from distilleries.signals import document_saved
from monitors.models import Monitor
from tests.fixture_manager import get_fixtures


class UpdateMonitorsTestCase(TransactionTestCase):
    """
    Tests the update_monitors signal receiver.
    """
    fixtures = get_fixtures(['monitors'])

    def test_update_monitors(self):
        """
        Tests the update_monitors signal receiver.
        """
        assert Monitor.objects.get(pk=3).status == 'RED'
        assert Monitor.objects.get(pk=4).status == 'RED'

        distillery = Distillery.objects.get(pk=1)
        document_saved.send(sender='document_saved', doc={},
                            distillery=distillery, doc_id='1')

        self.assertEqual(Monitor.objects.get(pk=3).status, 'GREEN')
        self.assertEqual(Monitor.objects.get(pk=4).status, 'RED')
