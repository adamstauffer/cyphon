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
Tests the StreamController class.
"""

# standard library
from unittest.mock import Mock, patch

# third party
from django.contrib.auth import get_user_model

# local
from aggregator.pipes.models import Pipe
from aggregator.pumproom.faucet import Faucet
from aggregator.pumproom.streamcontroller import StreamController
from aggregator.pumproom.tests.test_pump import PumpBaseTestCase
from aggregator.streams.models import Stream

User = get_user_model()

# pylint: disable=W0212
# allow use of protected members in tests


class StreamControllerTestCase(PumpBaseTestCase):
    """
    Base class for testing the StreamController class.
    """

    @staticmethod
    def _create_faucet():
        """
        Helper method that returns an example ApiHandler.
        """
        pipe = Pipe.objects.get_by_natural_key('twitter', 'SearchAPI')
        user = User.objects.get(pk=1)
        return Faucet(
            endpoint=pipe,
            user=user,
            task='BKGD_SRCH'
        )

    def setUp(self):
        super(StreamControllerTestCase, self).setUp()
        self.faucet = self._create_faucet()
        self.faucet.process_request = Mock()  # avoid NotImplementedError
        self.faucet.stop = Mock()
        self.controller = StreamController(
            faucet=self.faucet,
            query=self.query
        )


class GetStreamTestCase(StreamControllerTestCase):
    """
    Tests the _get_stream method of the StreamController class.
    """

    def setUp(self):
        super(GetStreamTestCase, self).setUp()
        self.auth = self.controller.faucet.emissary.passport
        self.pipe = self.controller.faucet.endpoint

    def test_when_no_stream(self):
        """
        Tests the _get_stream method when a Stream does not already exist.
        """
        Stream.objects.all().delete()
        self.assertEqual(Stream.objects.all().count(), 0)
        stream = self.controller.stream
        self.assertEqual(Stream.objects.all().count(), 1)
        saved_stream = Stream.objects.get(pk=stream.pk)
        self.assertEqual(saved_stream.auth, self.auth)
        self.assertEqual(saved_stream.pipe, self.pipe)

    def test_when_stream_exists(self):
        """
        Tests the _get_stream method when a Stream already exists.
        """
        Stream.objects.all().delete()
        new_stream = Stream(pipe=self.pipe, auth=self.auth)
        new_stream.save()
        saved_stream = self.controller.stream
        actual = saved_stream.pk
        expected = new_stream.pk
        self.assertEqual(actual, expected)


class StartThreadTestCase(StreamControllerTestCase):
    """
    Tests the _start_stream method of the StreamController class.
    """

    def test_start_thread(self):
        """
        Tests the _start_stream method.
        """
        self.controller.faucet.start = Mock()
        self.controller.faucet.stop = Mock()
        self.controller.stream.save_as_closed = Mock()
        with patch('threading.Thread.start') as mock_start:
            thread = self.controller._start_stream()
            self.assertIs(thread.daemon, True)
            self.assertEqual(mock_start.call_count, 1)


class QueryIsRunningTestCase(StreamControllerTestCase):
    """
    Tests the _query_is_running method of the StreamController class.
    """

    def test_streaming_and_query_same(self):
        """
        Tests the _query_is_running method when the stream is running and the
        query is unchanged.
        """
        self.controller.stream.active = True
        self.controller.stream.record.query = self.controller.query.to_dict()
        actual = self.controller._query_is_running()
        self.assertIs(actual, True)

    def test_streaming_but_query_diff(self):
        """
        Tests the _query_is_running method when the stream is running but the
        query has changed.
        """
        self.controller.stream.active = True
        actual = self.controller._query_is_running()
        self.assertIs(actual, False)

    def test_no_stream_and_query_same(self):
        """
        Tests the _query_is_running method when the query is unchanged but
        the stream is no longer running.
        """
        self.controller.stream.active = False
        self.controller.query = self.controller.stream.record.query
        actual = self.controller._query_is_running()
        self.assertIs(actual, False)

    def test_no_stream_and_query_diff(self):
        """
        Tests the _query_is_running method when the stream is no longer running
        and the query has changed.
        """
        self.controller.stream.active = False
        self.controller.query = {'new': 'query'}
        actual = self.controller._query_is_running()
        self.assertIs(actual, False)


class ProcessQueryTestCase(StreamControllerTestCase):
    """
    Tests the process_query method of the StreamController class.
    """

    def test_when_query_runnning(self):
        """
        Tests the process_query method when the query is already running.
        """
        self.controller._query_is_running = Mock(return_value=True)
        self.controller._start_thread = Mock()
        actual = self.controller.process_query()
        self.assertIs(actual, False)
        self.controller._start_thread.assert_not_called()

    def test_when_query_not_runnning(self):
        """
        Tests the process_query method when the query is not already running.
        """
        self.controller._query_is_running = Mock(return_value=False)
        self.controller._start_stream = Mock()

        # avoid exception in thread when test db destroyed
        self.controller.stream.save = Mock()

        actual = self.controller.process_query()
        self.assertIs(actual, True)
        self.assertEqual(self.controller._start_stream.call_count, 1)

