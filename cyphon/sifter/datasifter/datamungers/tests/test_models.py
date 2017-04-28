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
Tests the DataMunger class.
"""

# standard library
from unittest.mock import Mock

# third party
from django.test import TestCase

# local
from sifter.datasifter.datamungers.models import DataMunger
from tests.fixture_manager import get_fixtures


class DataMungerTestCase(TestCase):
    """
    Base class for testing the DataMunger class.
    """
    fixtures = get_fixtures(['datamungers', 'distilleries'])

    def test_process(self):
        """
        Tests the process method.
        """
        mock_doc = Mock()
        mock_doc_id = 1

        data = {'id': 123, 'subject': 'This is a Critical Alert'}

        datamunger = DataMunger.objects.get(pk=1)
        datamunger.condenser.process = Mock(return_value=mock_doc)
        datamunger.distillery.save_data = Mock(return_value=mock_doc_id)

        doc_id = datamunger.process(data, 'twitter')

        datamunger.condenser.process.assert_called_once_with(data)

        datamunger.distillery.save_data.assert_called_once_with(
            mock_doc,
            'twitter',
            None,
            None
        )
        self.assertEqual(doc_id, mock_doc_id)

