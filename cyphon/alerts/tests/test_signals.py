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
Tests Alert views.
"""

# standard library
try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

# third party
from django.test import TestCase

# local
from appusers.models import AppUser
from alerts.models import Comment
from tests.fixture_manager import get_fixtures


class CommentReceiverTestCase(TestCase):
    """
    Tests the handle_comment_post_save_signal receiver.
    """
    fixtures = get_fixtures(['comments'])

    def setUp(self):
        self.comment = Comment.objects.get(pk=1)

    def test_old_alert(self):
        """
        Tests that the handle_comment_post_save_signal receiver doesn't
        send an email when an existing alert is updated.
        """
        with patch('alerts.signals.compose_comment_email') as mock_compose:

            comment = Comment.objects.get(pk=1)
            comment.save()
            mock_compose.assert_not_called()

    def test_new_alert(self):
        """
        Tests that the handle_comment_post_save_signal receiver doesn't
        send an email when a new alert is updated.
        """
        mock_email = Mock()
        mock_email.send = Mock()
        with patch('alerts.signals.compose_comment_email',
                   return_value=mock_email) as mock_compose:

            comment = Comment.objects.get(pk=1)
            user = AppUser.objects.get(pk=2)
            comment.pk = None
            comment.save()
            mock_compose.assert_called_with(comment, user)
            self.assertEqual(mock_compose.call_count, 1)
            self.assertEqual(mock_email.send.call_count, 1)
