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
Tests the receiver module.
"""

# standard library
from collections import OrderedDict
import json
import logging
from unittest.mock import Mock, patch, call

# third party
from django.test import TestCase, TransactionTestCase
from testfixtures import LogCapture

# local
from sifter.logsifter.logmungers.models import LogMunger
from receiver import get_default_munger, process_msg, LOGGER
from tests.fixture_manager import get_fixtures

LOGGER.removeHandler('console')


class GetDefaultChuteTestCase(TestCase):
    """
    Tests the get_default_munger function.
    """

    fixtures = get_fixtures(['logchutes'])

    def setUp(self):
        self.doc = {
            'message': 'foobar',
            '@uuid': '12345',
            'collection': 'elasticsearch.test_index.test_logs'
        }
        self.msg = bytes(json.dumps(self.doc), 'utf-8')

    def test_get_default_w_chute(self):
        """
        Tests the get_default_munger function when the default LogMunger
        does not exists.
        """
        mock_config = {'DEFAULT_LOG_MUNGER': 'default_log'}
        with patch.dict('receiver.LOGSIFTER', mock_config):
            actual = get_default_munger()
            expected = LogMunger.objects.get(name='default_log')
            self.assertEqual(actual, expected)

    def test_get_default_no_chute(self):
        """
        Tests the get_default_munger function when the default LogMunger
        does not exist.
        """
        mock_config = {'DEFAULT_LOG_MUNGER': 'dummy_munger'}
        with patch.dict('receiver.LOGSIFTER', mock_config):
            with patch('receiver.logging.getLogger', return_value=LOGGER):
                with LogCapture() as log_capture:
                    actual = get_default_munger()
                    expected = None
                    log_capture.check(
                        ('receiver',
                         'ERROR',
                         'Default LogMunger "dummy_munger" is not configured.'),
                    )
                    self.assertEqual(actual, expected)


class ProcessLogChuteTestCase(TransactionTestCase):
    """
    Tests the process_msg function.
    """

    fixtures = get_fixtures(['logchutes'])

    default_munger = 'default_log'

    def setUp(self):
        self.doc = {
            'message': 'foobar',
            '@uuid': '12345',
            'collection': 'elasticsearch.test_index.test_logs'
        }
        sorted_doc = OrderedDict(sorted(self.doc.items()))
        self.msg = bytes(json.dumps(sorted_doc), 'utf-8')

        logging.disable(logging.ERROR)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_saved_to_chute(self):
        """
        Tests the process_msg function when the log message is saved by
        an enabled LogChute and a default chute is enabled.
        """
        mock_config = {
            'DEFAULT_LOG_CHUTE_ENABLED': True,
            'DEFAULT_LOG_MUNGER': self.default_munger
        }
        with patch.dict('receiver.LOGSIFTER', mock_config):
            with patch('sifter.logsifter.logchutes.models.LogChute.process',
                       return_value=True) as mock_chute_process:
                with patch('receiver.get_default_munger') as mock_get_default:
                    self.doc['message'] = 'critical alert'
                    msg = bytes(json.dumps(self.doc), 'utf-8')
                    process_msg(
                        channel=None,
                        method=None,
                        properties=None,
                        body=msg
                    )
                    args = [
                        self.doc['message'],
                        self.doc['@uuid'],
                        self.doc['collection']
                    ]
                    mock_chute_process.assert_has_calls([call(*args), call(*args)])
                    mock_get_default.process.assert_not_called()

    def test_not_saved_default_disabled(self):
        """
        Tests the process_msg function when the log message is not
        saved by an enabled LogChute and a default chute is disabled.
        """
        mock_config = {
            'DEFAULT_LOG_CHUTE_ENABLED': False,
            'DEFAULT_LOG_MUNGER': self.default_munger
        }
        with patch.dict('receiver.LOGSIFTER', mock_config):
            with patch('sifter.logsifter.logchutes.models.LogChute.process',
                       return_value=False) as mock_chute_process:
                with patch('receiver.get_default_munger') as mock_get_default:
                    process_msg(
                        channel=None,
                        method=None,
                        properties=None,
                        body=self.msg
                    )
                    args = [
                        self.doc['message'],
                        self.doc['@uuid'],
                        self.doc['collection']
                    ]
                    mock_chute_process.assert_has_calls([call(*args), call(*args)])
                    mock_get_default.assert_not_called()

    def test_not_saved_default_enabled(self):
        """
        Tests the process_msg function when the log message is not
        saved by an enabled LogChute and a default chute is enabled.
        """
        mock_config = {
            'DEFAULT_LOG_CHUTE_ENABLED': True,
            'DEFAULT_LOG_MUNGER': self.default_munger
        }
        mock_munger = Mock()
        mock_munger.process = Mock()
        with patch.dict('receiver.LOGSIFTER', mock_config):
            with patch('sifter.logsifter.logchutes.models.LogChute.process',
                       return_value=False) as mock_chute_process:
                with patch('receiver.get_default_munger',
                           return_value=mock_munger) as mock_get_default:
                    process_msg(
                        channel=None,
                        method=None,
                        properties=None,
                        body=self.msg
                    )
                    args = [
                        self.doc['message'],
                        self.doc['@uuid'],
                        self.doc['collection']
                    ]
                    mock_chute_process.assert_has_calls([call(*args), call(*args)])
                    self.assertEqual(mock_get_default.call_count, 1)
                    mock_munger.process.assert_called_once_with(
                        self.doc['message'],
                        self.doc['@uuid'],
                        self.doc['collection']
                    )

    def test_exception(self):
        """
        Tests the process_msg function when an exception is raised.
        """
        logging.disable(logging.NOTSET)
        with patch('receiver.logging.getLogger', return_value=LOGGER):
            with patch('receiver.json.loads', side_effect=Exception('foo')):
                with LogCapture() as log_capture:
                    process_msg(
                        channel=None,
                        method=None,
                        properties=None,
                        body=self.msg
                    )
                    log_capture.check(
                        ('receiver',
                         'ERROR',
                         ('An error occurred while processing the message:\n'
                          '  {"@uuid": "12345", '
                          '"collection": "elasticsearch.test_index.test_logs", '
                          '"message": "foobar"}')),
                    )

