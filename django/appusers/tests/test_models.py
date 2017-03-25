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


class UserTestCase(TestCase):

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

    def test_user_is_there(self):
        user = self.User.objects.get(email=self.email)
        self.assertIsNotNone(user)
        self.assertEqual(user.email, self.email)

    def test_user_credentials_are_correct(self):
        user = self.User.objects.get(email=self.email)
        self.assertEqual(user.email, self.email)
        self.assertEqual(user.email, self.email)
        self.assertEqual(user.first_name, self.first_name)
        self.assertEqual(user.last_name, self.last_name)

    def test_user_password_is_correct(self):
        user = self.User.objects.get(email=self.email)
        try:
            user.check_password(self.password)
        except Exception:
            self.fail('Password did not match')

    def test_user_password_change(self):
        user = self.User.objects.get(email=self.email)
        new_password = 'newpassword'

        # Change password to new password
        user.set_password(new_password)
        user.save()
        user = self.User.objects.get(email=self.email)
        self.assertTrue(user.check_password(new_password))

        # Change password back to original password
        user.set_password(self.password)
        user.save()
        user = self.User.objects.get(email=self.email)
        self.assertTrue(user.check_password(self.password))

    def test_get_absolute_url(self):
        user = self.User.objects.get(email=self.email)
        self.assertEqual(user.get_absolute_url(), 
                         '/users/chase.brewer%40dunbarcyber.com/')

    def test_get_full_name(self):
        user = self.User.objects.get(email=self.email)
        self.assertEqual(user.get_full_name(), 'Chase Brewer')

    def test_get_short_name(self):
        user = self.User.objects.get(email=self.email)
        self.assertEqual(user.get_short_name(), 'Chase')

    @skip
    def test_email_user(self):
        user = self.User.objects.get(email=self.email)
        from_email = 'donotreply@test.com'
        subject = 'Subject'
        message = 'Message'
        user.email_user(subject, message, from_email=from_email)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[1].subject, subject)
        self.assertEqual(mail.outbox[1].from_email, from_email)

