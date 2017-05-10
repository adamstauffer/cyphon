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
Tests the DataChute class.
"""

# standard library
import logging
from unittest.mock import Mock

# third party
from django.test import TestCase

# local
from cyphon.documents import DocumentObj
from sifter.datasifter.datachutes.models import DataChute
from tests.fixture_manager import get_fixtures


class DataChuteTestCase(TestCase):
    """
    Base class for testing the DataChute class.
    """
    fixtures = get_fixtures(['datachutes'])

    def setUp(self):
        logging.disable(logging.ERROR)

        # clear cached property
        try:
            del DataChute.objects._default_munger
        except AttributeError:
            pass

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_process_match(self):
        """
        Tests the process method for a matching data dictionary.
        """
        mock_doc_id = 1

        data = {'id': 123, 'subject': 'This is a Critical Alert'}
        doc_obj = DocumentObj(data=data)

        datachute = DataChute.objects.get(pk=3)
        datachute.munger.process = Mock(return_value=mock_doc_id)

        doc_id = datachute.process(doc_obj)

        datachute.munger.process.assert_called_once_with(doc_obj)
        self.assertEqual(doc_id, mock_doc_id)

    def test_process_nonmatch(self):
        """
        Tests the process method for a nonmatching data dictionary.
        """
        data = {'id': 123, 'Subject': 'This is an Urgent Alert'}
        doc_obj = DocumentObj(data=data)

        datachute = DataChute.objects.get(pk=3)
        datachute.munger.process = Mock(return_value=None)

        doc_id = datachute.process(doc_obj)

        self.assertEqual(doc_id, None)

    def test_process_no_sieve(self):
        """
        Tests the process method for a chute with no sieve.
        """
        mock_doc_id = 1

        data = {'id': 123, 'Subject': 'This is an Urgent Alert'}
        doc_obj = DocumentObj(data=data)

        datachute = DataChute.objects.get(pk=4)
        datachute.munger.process = Mock(return_value=mock_doc_id)

        doc_id = datachute.process(doc_obj)

        datachute.munger.process.assert_called_once_with(doc_obj)
        self.assertEqual(doc_id, mock_doc_id)
