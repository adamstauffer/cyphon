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
from unittest import skip

# third party
from django.test import TestCase
from django.core import mail
from django.contrib.auth import get_user_model


class UserSignalCase(TestCase):

    def setUp(self):
        self.email = 'chase.brewer@dunbarcyber.com'
        self.password = 'password'
        self.first_name = 'Chase'
        self.last_name = 'Brewer'
        self.User = get_user_model()
        user = self.User.objects.create_user(self.email, self.password)
        user.first_name = self.first_name
        user.last_name = self.last_name
        user.save()

    @skip
    def test_mail_was_sent_upon_user_creation(self):
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.email, mail.outbox[0].to)

