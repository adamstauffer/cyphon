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
from django.test import TestCase, TransactionTestCase

# local
from alerts.models import Alert
import platforms.jira.handlers as jira_module
from responder.actions.models import Action, AutoAction
from sifter.datasifter.datasieves.models import DataSieve
from tests.fixture_manager import get_fixtures
from tests.mock import patch_find_by_id


class ActionsBaseTestCase(TestCase):
    """
    Base class for testing Actions.
    """

    fixtures = get_fixtures(['actions', 'dispatches'])

    def setUp(self):
        self.action = Action.objects.get(pk=1)


class ActionTestCase(ActionsBaseTestCase):
    """
    Tests the Action class.
    """

    def test_str(self):
        """
        Tests the string representation of an Action.
        """
        self.assertEqual(str(self.action), 'Jira IssueAPI')

    def test_get_module(self):
        """
        Tests the _get_module method for getting the module for an
        Action's Destination.
        """
        self.assertEqual(self.action._get_module(), jira_module)

    def test_create_request_handler(self):
        """
        Tests the create_request_handler method for getting a request
        handler for an Action.
        """
        mock_user = Mock()
        mock_handler = Mock()
        with patch('platforms.jira.handlers.IssueAPI',
                   return_value=mock_handler) as mock_api:
            kwargs = {
                'user': mock_user,
            }
            result = self.action.create_request_handler(**kwargs)
            mock_api.assert_called_once_with(endpoint=self.action,
                                             user=mock_user)
            self.assertEqual(result, mock_handler)

    def test_save_w_no_descr(self):
        """
        Test the save method of an Action with the Action has no
        description.
        """
        self.assertEqual(self.action.description, None)
        self.action.save()
        self.assertEqual(self.action.description, 'Jira IssueAPI')

    def test_save_w_descr(self):
        """
        Test the save method of an Action with the Action has a
        description.
        """
        self.action.description = 'Create a JIRA Issue'
        self.action.save()
        self.assertEqual(self.action.description, 'Create a JIRA Issue')

    def test_get_dispatch(self):
        """
        Test the get_dispatch method of an Action.
        """
        mock_alert = Mock()
        mock_user = Mock()
        mock_record = Mock()
        mock_handler = Mock()

        mock_handler.run = Mock(return_value=mock_record)
        mock_handler.record = mock_record

        with patch('platforms.jira.handlers.IssueAPI',
                   return_value=mock_handler) as mock_api:
            kwargs = {
                'alert': mock_alert,
                'user': mock_user,
            }
            result = self.action.get_dispatch(**kwargs)
            mock_api.assert_called_once_with(endpoint=self.action,
                                             user=mock_user)
            mock_handler.run.assert_called_once_with(mock_alert)
            self.assertEqual(result, mock_record)


class AutoActionManagerTestCase(TransactionTestCase):
    """
    Tests the AutoActionManager class.
    """

    fixtures = get_fixtures(['alerts', 'autoactions'])

    def setUp(self):
        self.autoaction = AutoAction.objects.get(pk=1)
        self.alert = Alert.objects.get(pk=1)

    def test_find_enabled(self):
        """
        Tests the find_enabled method.
        """
        self.assertEqual(AutoAction.objects.find_enabled().count(), 1)
        self.autoaction.enabled = False
        self.autoaction.save()
        self.assertEqual(AutoAction.objects.find_enabled().count(), 0)

    @patch('responder.actions.models.AutoAction.process')
    def test_process(self, mock_process):
        """
        Tests the process method.
        """
        AutoAction.objects.process(self.alert)
        enabled_autoactions = AutoAction.objects.find_enabled().count()
        self.assertEqual(enabled_autoactions, mock_process.call_count)
        self.autoaction.process.assert_called_once_with(self.alert)


class AutoActionTestCase(TestCase):
    """
    Tests the AutoAction class.
    """

    fixtures = get_fixtures(['alerts', 'autoactions'])

    def setUp(self):
        self.alert = Alert.objects.get(pk=1)
        self.sieve = DataSieve.objects.get(pk=4)  # loaded from watchdogs.json
        self.autoaction = AutoAction.objects.get(pk=1)
        self.autoaction.sieve = self.sieve
        self.mock_handler = Mock()

    def test_str(self):
        """
        Tests the string representation of an AutoAction.
        """
        self.assertEqual(str(self.autoaction), '1 - Mattermost WebHookHandler')

    @patch_find_by_id()
    def test_matching_sieve(self):
        """
        Tests the process method for an AutoAction with a DataSieve that
        matches the Alert data.
        """
        with patch('responder.actions.models.Action.create_request_handler',
                   return_value=self.mock_handler):
            self.alert.data = {'message': 'CRIT-'}
            self.autoaction.process(self.alert)
            self.mock_handler.run.assert_called_once_with(self.alert)

    @patch_find_by_id()
    def test_nonmatching_sieve(self):
        """
        Tests the process method for an AutoAction with a DataSieve that
        doesn't match the Alert data.
        """
        with patch('responder.actions.models.Action.create_request_handler',
                   return_value=self.mock_handler):
            self.autoaction.process(self.alert)
            self.mock_handler.run.assert_not_called()

    @patch_find_by_id()
    def test_no_sieve(self):
        """
        Tests the process method for an AutoAction without a DataSieve.
        """
        with patch('responder.actions.models.Action.create_request_handler',
                   return_value=self.mock_handler):
            self.autoaction.sieve = None
            self.autoaction.process(self.alert)
            self.mock_handler.run.assert_called_once_with(self.alert)
