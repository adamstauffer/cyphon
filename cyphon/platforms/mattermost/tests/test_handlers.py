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
from django.test import TransactionTestCase
from httmock import urlmatch, HTTMock

# local
from cyphon.documents import DocumentObj
from responder.dispatches.models import Dispatch
from tests.fixture_manager import get_fixtures
from watchdogs.models import Watchdog


DOC_ID = '666f6f2d6261722d71757578'

DATA = {
    '_meta': {
        'priority': 'HIGH',
    },
    '_raw_data': {
        'backend': 'mongodb',
        'distillery': 'test',
        'doc_id': DOC_ID
    },
    'content': {
        'subject': '[CRIT-111]'
    }
}


@urlmatch(netloc='mattermost.example.com')
def mattermost_mock(url, request):
    return {'status_code': 200,
            'content': 'Test response'}


class MattermostTestCase(TransactionTestCase):
    """
    Base class for testing the Mattermost handler classes.
    """

    fixtures = get_fixtures([
        'watchdogs', 'distilleries', 'autoactions'])

    doc_id = DOC_ID
    data = DATA
    doc_obj = DocumentObj(
        data=DATA,
        doc_id=DOC_ID,
        collection='mongodb.test_database.test_docs'
    )

    def setUp(self):
        self.email_wdog = Watchdog.objects.get_by_natural_key('inspect_emails')
        self.mock_settings = {
            'SERVER': 'https://mattermost.example.com',
            'GENERATED_KEY': 'xxx-mattermost-xxx',
            'DISPLAYED_USERNAME': 'Test Username'
        }

    def test_run_autoaction(self):
        """
        Tests the Watchdog's process method runs autoactions.
        """
        with patch.dict('platforms.mattermost.handlers.settings.MATTERMOST',
                        self.mock_settings):
            with HTTMock(mattermost_mock):
                dispatch_count = Dispatch.objects.count()
                self.email_wdog.process(self.doc_obj)
                self.assertEqual(Dispatch.objects.count(), dispatch_count + 1)
