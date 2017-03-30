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
import logging
from unittest import skip

# third party
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.core import mail
from rest_framework import status

# local
from appusers.models import AppUser
from appusers.tests import helpers
from tests.api_tests import CyphonAPITestCase
from tests.fixture_manager import get_fixtures


class AppUserViewTestCase(CyphonAPITestCase):
    """
    Base class for testing the AppUser views.
    """

    fixtures = get_fixtures(['users'])

    model_url = 'users/'

    def test_get_users_for_nonstaff(self):
        """
        Tests the AppUsers REST API endpoint for user who is not staff.
        """
        response = self.get_api_response(is_staff=False)
        count = AppUser.objects.count()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), count)


@skip
class ViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.email = 'chase.brewer@dunbarcyber.com'
        self.password = 'password'
        self.User = get_user_model()
        self.user = self.User.objects.create_user(self.email, self.password)

    def test_authorization_when_not_logged_in(self):
        login_response = self.client.get(reverse('login'))
        self.assertEqual(login_response.status_code, 200)

        logout_response = self.client.get(reverse('logout'))
        self.assertEqual(logout_response.status_code, 200)

        logout_login_response = self.client.get(reverse('logout_then_login'))
        self.assertEqual(logout_login_response.status_code, 302)

        password_change_response = self.client.get(reverse('password_change'))
        self.assertEqual(password_change_response.status_code, 302)

        password_change_done = self.client.get(reverse('password_change_done'))
        self.assertEqual(password_change_done.status_code, 302)

        password_reset = self.client.get(reverse('password_reset'))
        self.assertEqual(password_reset.status_code, 200)

        password_reset_done = self.client.get(reverse('password_reset_done'))
        self.assertEqual(password_reset_done.status_code, 200)

        password_reset_confirm = self.client.get(reverse(
                'password_reset_confirm', kwargs={
                    'uidb64': 'NYG',
                    'token': 'fijeaofjei-fijfieaeaf',
                }))
        self.assertEqual(password_reset_confirm.status_code, 404)

        password_reset_complete = self.client.get(reverse(
                'password_reset_complete'))
        self.assertEqual(password_reset_complete.status_code, 200)

        user_registration = self.client.get(reverse(
                'user_registration', kwargs={
                    'uidb64': 'NYG',
                    'token': 'fijeaofjei-fijfieaeaf',
                }))
        self.assertEqual(user_registration.status_code, 404)

        user_registration_complete = self.client.get(reverse(
                'user_registration_complete'))
        self.assertEqual(user_registration_complete.status_code, 200)

        profile = self.client.get(reverse('profile'))
        self.assertEqual(profile.status_code, 302)

    def test_user_registration(self):

        # Make sure the email was sent and that it was sent to the right person
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.email, mail.outbox[0].to)

        # Find the email that the user has to click to register their account
        email_urls = helpers.get_urls_from_text(mail.outbox[0].body)
        matched_urls = [x for x in email_urls if 'user_registration' in x]
        if matched_urls:
            response = self.client.get(matched_urls[0])
            self.assertEqual(response.status_code, 200)
            response_post = self.client.post(
                    matched_urls[0], 
                    {
                        'new_password1': 'NewPassword',
                        'new_password2': 'NewPassword',
                        'first_name': 'Chase',
                        'last_name': 'Brewer',
                    },
                    follow=True)
            self.assertEqual(response_post.status_code, 200)

            # After posting to the link, the link should now fail with a 404
            response_fail = self.client.get(matched_urls[0])
            self.assertEqual(response_fail.status_code, 404)
        else:
            self.fail('Registration link not found in email')


    def test_password_reset(self):

        # Check that there is currently a registration email sent out
        self.assertEqual(len(mail.outbox), 1)

        # Register the user so that they can actually reset their password
        self.test_user_registration()

        # Send the reset link
        response = self.client.post(reverse('password_reset'), 
                                    {'email': self.email},
                                    follow=True)
        self.assertEqual(response.status_code, 200)

        # Check that there is a reset link sent out
        self.assertEqual(len(mail.outbox), 2)
        self.assertIn(self.email, mail.outbox[1].to)

        # Find the email that the user has to click to reset their password
        email_urls = helpers.get_urls_from_text(mail.outbox[1].body)
        matched_urls = [x for x in email_urls if 'password_reset' in x]
        if matched_urls:
            response = self.client.get(matched_urls[0])
            self.assertEqual(response.status_code, 200)
            response_post = self.client.post(
                    matched_urls[0], 
                    {
                        'new_password1': 'NewPassword2',
                        'new_password2': 'NewPassword2',
                    },
                    follow=True)
            self.assertEqual(response_post.status_code, 200)

            # After posting to the link, the link should now fail with a 404
            response_fail = self.client.get(matched_urls[0])
            self.assertEqual(response_fail.status_code, 404)
        else:
            self.fail('Registration link not found in email')

    """ client.login isn't working """
    def test_authorization_when_logged_in(self):
        self.client.login(username=self.email, password=self.password)

        login_response = self.client.get(reverse('login'))
        self.assertEqual(login_response.status_code, 302)

        password_change_response = self.client.get(reverse('password_change'))
        self.assertEqual(password_change_response.status_code, 200)

        password_change_done = self.client.get(reverse('password_change_done'))
        self.assertEqual(password_change_done.status_code, 200)

        password_reset = self.client.get(reverse('password_reset'))
        self.assertEqual(password_reset.status_code, 404)

        password_reset_done = self.client.get(reverse('password_reset_done'))
        self.assertEqual(password_reset_done.status_code, 404)

        password_reset_confirm = self.client.get(reverse(
                'password_reset_confirm', kwargs={
                    'uidb64': 'NYG',
                    'token': 'fijeaofjei-fijfieaeaf',
                }))
        self.assertEqual(password_reset_confirm.status_code, 404)

        password_reset_complete = self.client.get(reverse(
                'password_reset_complete'))
        self.assertEqual(password_reset_complete.status_code, 404)

        user_registration = self.client.get(reverse(
                'user_registration', kwargs={
                    'uidb64': 'NYG',
                    'token': 'fijeaofjei-fijfieaeaf',
                }))
        self.assertEqual(user_registration.status_code, 404)

        user_registration_complete = self.client.get(reverse(
                'user_registration_complete'))
        self.assertEqual(user_registration_complete.status_code, 404)

        profile = self.client.get(reverse('profile'))
        self.assertEqual(profile.status_code, 200)

        logout_response = self.client.get(reverse('logout'))
        self.assertEqual(logout_response.status_code, 200)

        logout_login_response = self.client.get(reverse('logout_then_login'))
        self.assertEqual(logout_login_response.status_code, 302)

