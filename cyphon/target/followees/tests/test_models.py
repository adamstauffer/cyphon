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
Tests the Followee class and its related classes.
"""

# third party
from django.test import TestCase
from django.core.exceptions import ValidationError

# local
from aggregator.reservoirs.models import Reservoir
from target.followees.models import Followee, LegalName, Account, Alias
from tests.fixture_manager import get_fixtures


class FolloweeModelsTestCase(TestCase):
    """
    Base class for testing the Followee class and its related classes.
    """
    fixtures = get_fixtures(['followees'])


class FolloweeTestCase(FolloweeModelsTestCase):
    """
    Tests the Followee class.
    """

    def test_find_accounts(self):
        """
        Tests method for finding a Followee's Accounts for a given Reservoir.
        """
        john = Followee.objects.get(pk=1)
        jane = Followee.objects.get(pk=2)

        self.assertEqual(len(john.find_accounts('twitter')), 2)
        self.assertEqual(len(john.find_accounts('facebook')), 1)

        # test case for no accounts for a given platform
        self.assertEqual(len(john.find_accounts('instagram')), 0)

        # test case for no accounts at all
        self.assertEqual(len(jane.find_accounts('twitter')), 0)

    def test_can_add_associate(self):
        """
        Tests method for adding an associate to a Followee record.
        """


class LegalNameTestCase(FolloweeModelsTestCase):
    """
    Tests the LegalName class.
    """

    def test_get_full_name_if_middle(self):
        """
        Tests method for getting a full name, when a middle name exists.
        """
        name = LegalName.objects.get(pk=1)
        self.assertEqual(name.get_full_name(), 'John Adam Smith')

    def test_get_full_name_if_no_middle(self):
        """
        Tests method for getting a full name, when no middle name exists.
        """
        jane = LegalName.objects.get(pk=2)
        self.assertEqual(jane.get_full_name(), 'Jane Smith')

    def test_get_last_first_with_middle(self):
        """
        Tests method for getting a last name followed by a first name
        and middle initial, when a middle name exists.
        """
        john = LegalName.objects.get(pk=1)
        self.assertEqual(john.get_last_name_first_name(), 'Smith, John A')

    def test_get_last_first_no_middle(self):
        """
        Tests method for getting a last name followed by a first name, when no
        middle name exists.
        """
        john = LegalName.objects.get(pk=2)
        self.assertEqual(john.get_last_name_first_name(), 'Smith, Jane')


class AccountTestCase(FolloweeModelsTestCase):
    """
    Tests the Account class.
    """

    def test_dup_account_same_followee(self):
        """
        Tests that an Account having the same platform and user id of another
        account under the same followee can't be saved.
        """
        john = Followee.objects.get(pk=1)
        twitter = Reservoir.objects.get_by_natural_key('twitter')

        with self.assertRaises(ValidationError):
            dup = Account(followee=john, platform=twitter, user_id='jad')
            dup.full_clean()

    def test_dup_account_diff_followee(self):
        """
        Tests that an Account having the same platform and user id of an
        account under a different followee can't be saved.
        """
        jack = Followee.objects.get(nickname='Jack')
        twitter = Reservoir.objects.get_by_natural_key('twitter')

        with self.assertRaises(ValidationError):
            dup = Account(followee=jack, platform=twitter, user_id='jad')
            dup.full_clean()


class AliasTestCase(FolloweeModelsTestCase):
    """
    Tests the Alias class.
    """

    def test_dup_alias_is_invalid(self):
        """
        Tests that duplicate Aliases can't be saved.
        """
        twitter = Account.objects.get(pk=1)
        with self.assertRaises(ValidationError):
            dup = Alias(account=twitter, handle='John Smith', role='name')
            dup.full_clean()

    def test_same_handle_diff_role(self):
        """
        Tests that the same handle with a different role is okay.
        """
        twitter = Account.objects.get(pk=1)
        try:
            dup = Alias(account=twitter, handle='John Smith', role='username')
            dup.full_clean()
        except ValidationError:
            self.fail("Nonduplicate raised ValidationError unexpectedly")

    def test_same_handle_diff_acct(self):
        """
        Tests that the same handle with a different account is okay.
        """
        facebook = Account.objects.get(pk=2)
        try:
            dup = Alias(account=facebook, handle='John Smith', role='name')
            dup.full_clean()
        except ValidationError:
            self.fail("Nonduplicate raised ValidationError unexpectedly")


