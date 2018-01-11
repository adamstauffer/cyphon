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
Tests the Stream class.
"""

# third party
from django.test import TestCase

# local
from aggregator.invoices.models import Invoice
from aggregator.streams.models import Stream
from tests.fixture_manager import get_fixtures


class StreamManagerTestCase(TestCase):
    """
    Class for StreamManager test cases.
    """
    fixtures = get_fixtures(['streams'])

    def close_all(self):
        """
        Tests the __str__ method of the Stream class.
        """
        stream = Stream.objects.get(pk=2)
        assert stream.active
        Stream.objects.close_all()
        stream = Stream.objects.get(pk=2)
        self.assertFalse(stream.active)


class StreamTestCase(TestCase):
    """
    Class for Stream test cases.
    """
    fixtures = get_fixtures(['streams'])

    def test_str(self):
        """
        Tests the __str__ method of the Stream class.
        """
        stream = Stream.objects.get(auth=1)
        actual = str(stream)
        expected = 'Twitter SearchAPI: twitter_1'
        self.assertEqual(actual, expected)

    def test_save_as_open(self):
        """
        Tests the save_as_open method of the Stream class.
        """
        record = Invoice.objects.get(pk=2)
        stream = Stream.objects.get(auth=1)
        self.assertIs(stream.active, False)
        stream.save_as_open(record)
        saved_stream = Stream.objects.get(auth=1)
        self.assertIs(saved_stream.active, True)
        self.assertEqual(saved_stream.record, record)

    def test_save_as_closed(self):
        """
        Tests the save_as_closed method of the Stream class.
        """
        stream = Stream.objects.get(auth=2)
        self.assertIs(stream.active, True)
        stream.save_as_closed()
        saved_stream = Stream.objects.get(auth=2)
        self.assertIs(saved_stream.active, False)

