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
Defines classes used for following people across social media platforms.
"""

# third party
from django.db import models

# local
from aggregator.reservoirs.models import Reservoir


class Followee(models.Model):
    """
    A person being followed on social media. The person may be followed across
    multiple social media platforms.

    The followee's accounts are associated using a 'nickname', a general handle
    by which the followee can be identified. A nickname is used because the
    followee's legal name may not be known. However, a legal name can also be
    associated with the followee to clarify his or her identity.

    A followee can be linked to other followees through a symmetrical
    'associates' relationship.
    """
    nickname = models.CharField(max_length=255, unique=True, null=False)
    associates = models.ManyToManyField('self', symmetrical=True, blank=true)

    def __str__(self):
        return self.nickname

    def find_accounts(self, reservoir):
        """
        Returns the Followee's Accounts for a particular social media platform,
        as defined by a Reservoir.
        """
        return self.accounts.filter(platform__name=reservoir)

    def add_associate(self, associate):
        """
        Links the Followee to another Followee.
        """
        self.associates.add(associate)

    def get_associates(self):
        """
        Gets Followees linked to this Followee.
        """
        return self.associates


class LegalName(models.Model):
    """
    The legal name associated with a person being followed (followee).
    """
    followee = models.OneToOneField(Followee, primary_key=True)
    first = models.CharField(max_length=255)
    middle = models.CharField(max_length=255, default='')
    last = models.CharField(max_length=255)

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        """
        If a middle name or initial exists, returns the first name, middle name,
        and last name. Otherwise, returns the first and last name.
        """
        if self.middle:
            return '%s %s %s' % (self.first, self.middle, self.last)
        else:
            return '%s %s' % (self.first, self.last)

    def get_last_name_first_name(self):
        """
        Returns the last name followed by the first name and, if available,
        a middle initial.
        """
        if self.middle:
            return '%s, %s %s' % (self.last, self.first, self.middle[0])
        else:
            return '%s, %s' % (self.last, self.first)


class Account(models.Model):
    """
    A social media account associated with a person being followed (followee).
    Consists of a social media platform, a followee's userid on that platform,
    and the followee's username (screen name).

    This is a many-to-one relationship; it is possible for a followee to be
    associated with multiple accounts on the same platform, but only one
    followee can be associated with a particular social media account account.
    """
    followee = models.ForeignKey(Followee, related_name='accounts')
    platform = models.ForeignKey(Reservoir)
    user_id = models.CharField(max_length=255)
    username = models.CharField(max_length=255)

    class Meta:
        """
        Metadata options.
        """
        unique_together = ('platform', 'user_id')


class Alias(models.Model):
    """
    Contains the record for a social media handle, such as a name or username
    (screen name) associated with a social media account. This class serves to
    keep track of the handles associated with an account over time (in case a
    followee changes his or her screen name, for example).
    """
    ROLE_CHOICES = (
        ('name', 'Name'),
        ('username', 'Username'),
    )

    account = models.ForeignKey(Account)
    handle = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        Metadata options.
        """
        unique_together = ('account', 'handle', 'role')
