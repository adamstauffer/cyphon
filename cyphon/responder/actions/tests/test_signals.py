# -*- coding: utf-8 -*-
# Copyright 2017-2018 Dunbar Security Solutions, Inc.
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

"""

# standard library
try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

# third party
from django.db.models.signals import post_save
from django.db.utils import IntegrityError
from django.test import TestCase, TransactionTestCase

# local
from alerts.models import Alert
from distilleries.models import Distillery
import platforms.jira.handlers as jira_module
from responder.actions.models import Action, AutoAction
from responder.actions.signals import process_autoactions
from sifter.datasifter.datasieves.models import DataSieve
from tests.fixture_manager import get_fixtures
from tests.mock import patch_find_by_id
from watchdogs.models import Watchdog


class ProcessAutoActionsTestCase(TransactionTestCase):
    """
    Tests the process_autoactions signal receiver.
    """

    fixtures = get_fixtures(['autoactions', 'distilleries', 'watchdogs'])

    def setUp(self):
        self.autoaction = AutoAction.objects.get(pk=1)
        post_save.connect(process_autoactions, sender=Alert)
        self.sieve = DataSieve.objects.get(pk=4)  # loaded from watchdogs.json
        self.alert = Alert(
            level='HIGH',
            status=0,
            distillery=Distillery.objects.get(pk=1),
            alarm=Watchdog.objects.get(pk=1)
        )
        post_save.connect(process_autoactions, sender=Alert)

    def tearDown(self):
        super(ProcessAutoActionsTestCase, self).tearDown()
        post_save.disconnect(process_autoactions, sender=Alert)

    @patch_find_by_id()
    @patch('responder.actions.models.AutoActionManager.process')
    def test_new_alert(self, mock_process):
        """
        Tests that AutoActions are processed when a new Alert is saved.
        """
        self.alert.save()
        mock_process.assert_called_once_with(self.alert)

    @patch_find_by_id()
    @patch('responder.actions.models.AutoActionManager.process')
    def test_duplicate_alert(self, mock_process):
        """
        Tests that AutoActions are not processed for a duplicate Alert.
        """
        self.alert.save()
        self.alert.pk = None
        with self.assertRaises(IntegrityError):
            self.alert.save()
            mock_process.assert_not_called()

    @patch_find_by_id()
    @patch('responder.actions.models.AutoActionManager.process')
    def test_old_alert(self, mock_process):
        """
        Tests that AutoActions are not processed when an existing Alert
        is updated.
        """
        self.alert.save()
        self.alert.save()
        self.assertEqual(mock_process.call_count, 1)
