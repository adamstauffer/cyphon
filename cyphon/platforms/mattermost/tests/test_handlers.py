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
Tests the Mattermost WebHookHandler class.
"""

# standard library
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

# third party
from django.db.models.signals import post_save
from django.test import TransactionTestCase
from httmock import urlmatch, HTTMock

# local
from alerts.models import Alert
from distilleries.models import Distillery
from responder.actions.signals import process_autoactions
from responder.dispatches.models import Dispatch
from tests.fixture_manager import get_fixtures
from tests.mock import patch_find_by_id
from watchdogs.models import Watchdog


@urlmatch(netloc='mattermost.example.com')
def mattermost_mock(url, request):
    return {
        'status_code': 200,
        'content': 'Test response'
    }


class MattermostTestCase(TransactionTestCase):
    """
    Base class for testing the Mattermost handler classes.
    """

    fixtures = get_fixtures(['autoactions', 'distilleries', 'watchdogs'])

    def setUp(self):
        self.alert = Alert(
            level='HIGH',
            status=0,
            distillery=Distillery.objects.get(pk=1),
            doc_id=1,
            alarm=Watchdog.objects.get(pk=1)
        )
        self.mock_settings = {
            'SERVER': 'https://mattermost.example.com',
            'GENERATED_KEY': 'xxx-mattermost-xxx',
            'DISPLAYED_USERNAME': 'Test Username'
        }
        post_save.connect(process_autoactions, sender=Alert)

    def tearDown(self):
        super(MattermostTestCase, self).tearDown()
        post_save.disconnect(process_autoactions, sender=Alert)

    @patch_find_by_id()
    def test_run_autoaction(self):
        """
        Tests the Mattermost AutoAction.
        """
        with patch.dict('platforms.mattermost.handlers.settings.MATTERMOST',
                        self.mock_settings):
            with HTTMock(mattermost_mock):
                dispatch_count = Dispatch.objects.count()
                self.alert.save()
                self.assertEqual(Dispatch.objects.count(), dispatch_count + 1)
                dispatch = Dispatch.objects.all()[0]
                self.assertEqual(dispatch.data, {'response': 'Test response'})
