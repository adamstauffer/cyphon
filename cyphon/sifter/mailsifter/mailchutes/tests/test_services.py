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
Tests services for the MailSifter package.
"""

# standard library
from email.mime.text import MIMEText
from unittest.mock import patch

# third party
from django.test import TransactionTestCase
from testfixtures import LogCapture

# local
from sifter.mailsifter.mailchutes.services import process_email
from tests.fixture_manager import get_fixtures

# NOTE: use TransactionTestCase to handle threading

class ProcessEmailTestCase(TransactionTestCase):
    """
    Tests the process_email receiver.
    """
    fixtures = get_fixtures(['mailchutes'])

    text = 'critical alert test'
    html = '<html><head></head><body><p>critical alert test</p></html>'
    count = 0

    def setUp(self):
        super(ProcessEmailTestCase, self).setUp()
        self.msg = MIMEText('example text', 'plain')
        self.msg['Message-ID'] = 'NM615AA6A517B60AA16@email.com'
        self.msg['Date'] = 'Tue, 8 Sep 2015 16:08:59 -0400'

    def test_match_with_default(self):
        """
        Tests the process_email receiver for an email that matches an
        existing MailChute.
        """
        self.msg['Subject'] = 'critical alert'
        mock_config = {
            'DEFAULT_MAIL_MUNGER': 'default_mail',
            'DEFAULT_MAIL_CHUTE_ENABLED': True
        }
        with patch('distilleries.models.Distillery.save_data',
                   return_value='id_123') as mock_save:
            with patch('sifter.mailsifter.mailchutes.services.catch_email') \
                    as mock_catch_email:
                with patch.dict('sifter.mailsifter.mailchutes.services.settings.MAILSIFTER',
                                mock_config):
                    process_email(self.msg)
                    self.assertIs(mock_save.called, True)
                    self.assertIs(mock_catch_email.called, False)

    def test_no_match_without_default(self):
        """
        Tests the process_email receiver for an email that doesn't match
        an existing MailChute when a default MailMunger is not enabled.
        """
        self.msg['Subject'] = 'nothing to see here'
        mock_config = {
            'DEFAULT_MAIL_MUNGER': 'default_mail',
            'DEFAULT_MAIL_CHUTE_ENABLED': False
        }
        with patch('distilleries.models.Distillery.save_data',
                   return_value='id_123') as mock_save:
            with patch('sifter.mailsifter.mailchutes.services.catch_email') \
                    as mock_catch_email:
                with patch.dict('sifter.mailsifter.mailchutes.services.settings.MAILSIFTER',
                                mock_config):
                    process_email(self.msg)
                    self.assertIs(mock_save.called, False)
                    self.assertIs(mock_catch_email.called, False)

    def test_no_match_with_default(self):
        """
        Tests the process_email receiver for an email that doesn't match
        an existing MailChute when a default MailMunger is enabled.
        """
        self.msg['Subject'] = 'nothing to see here'
        mock_config = {
            'DEFAULT_MAIL_MUNGER': 'default_mail',
            'DEFAULT_MAIL_CHUTE_ENABLED': True
        }
        with patch('distilleries.models.Distillery.save_data',
                   return_value='id_123') as mock_save:
            with patch.dict('sifter.mailsifter.mailchutes.services.settings.MAILSIFTER',
                            mock_config):
                process_email(self.msg)
                self.assertIs(mock_save.called, True)

    def test_no_match_missing_munger(self):
        """
        Tests the process_email receiver for an email that doesn't match
        an existing MailChute when a default MailChute is enabled but
        the defaul MailMunger can't be found.
        """
        self.msg['Subject'] = 'nothing to see here'
        mock_config = {
            'DEFAULT_MAIL_MUNGER': 'missing_munger',
            'DEFAULT_MAIL_CHUTE_ENABLED': True
        }
        with patch.dict('sifter.mailsifter.mailchutes.services.settings.MAILSIFTER',
                        mock_config):
            with LogCapture() as log_capture:
                msg = ('Default MailMunger "missing_munger" is not configured. '
                       'Could not save message %s' % self.msg['Message-ID'])
                process_email(self.msg)
                log_capture.check(
                    ('sifter.mailsifter.mailchutes.services', 'ERROR', msg),
                )

