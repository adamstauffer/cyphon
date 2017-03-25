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
Tests the MailChute class.
"""

# standard library
from unittest.mock import Mock

# third party
from django.test import TestCase

# local
from sifter.mailsifter.mailchutes.models import MailChute
from tests.fixture_manager import get_fixtures


class MailChuteTestCase(TestCase):
    """
    Base class for testing MailChutes.
    """
    fixtures = get_fixtures(['mailchutes'])

    def test_process_match(self):
        """
        Tests the process method for a matching email.
        """
        mock_doc_id = 1

        email = {'Message-ID': 'abc', 'Subject': 'This is a Critical Alert'}

        mailchute = MailChute.objects.get(pk=1)
        mailchute.munger.process = Mock(return_value=mock_doc_id)

        doc_id = mailchute.process(email)

        mailchute.munger.process.assert_called_once_with(email, None, None, None)
        self.assertEqual(doc_id, mock_doc_id), None

    def test_process_nonmatch(self):
        """
        Tests the process method for a nonmatching email.
        """
        email = {'Message-ID': 'abc', 'Subject': 'This is an Urgent Alert'}

        mailchute = MailChute.objects.get(pk=1)
        mailchute.munger.process = Mock(return_value=None)

        doc_id = mailchute.process(email)

        self.assertEqual(doc_id, None)

    def test_process_no_sieve(self):
        """
        Tests the process method for a chute with no sieve.
        """
        mock_doc_id = 1

        email = {'Message-ID': 'abc', 'Subject': 'This is an Urgent Alert'}

        mailchute = MailChute.objects.get(pk=3)
        mailchute.enabled = True
        mailchute.munger.process = Mock(return_value=mock_doc_id)

        doc_id = mailchute.process(email)

        mailchute.munger.process.assert_called_once_with(email, None, None, None)
        self.assertEqual(doc_id, mock_doc_id)

