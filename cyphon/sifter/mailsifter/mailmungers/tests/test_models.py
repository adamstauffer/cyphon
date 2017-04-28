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

"""

# standard library
from unittest.mock import Mock

# third party
from django.test import TestCase

# local
from sifter.mailsifter.mailmungers.models import MailMunger
from tests.fixture_manager import get_fixtures


class MailMungerTestCase(TestCase):
    """
    Base class for testing the MailMunger class.
    """

    fixtures = get_fixtures(['mailmungers'])

    def test_process(self):
        """
        Tests the process method.
        """
        mock_doc = Mock()
        mock_doc_id = 1

        email = {'Message-ID': 'abc'}

        msg_id = email['Message-ID']
        mailmunger = MailMunger.objects.get_by_natural_key('mail')
        mailmunger.condenser.process = Mock(return_value=mock_doc)
        mailmunger.distillery.save_data = Mock(return_value=mock_doc_id)

        doc_id = mailmunger.process(email)

        mailmunger.condenser.process.assert_called_once_with(
            data=email,
            company=mailmunger.distillery.company
        )

        mailmunger.distillery.save_data.assert_called_once_with(
            mock_doc,
            msg_id,
            'postgresql.django_cyphon.django_mailbox_message',
            None
        )
        self.assertEqual(doc_id, mock_doc_id)

