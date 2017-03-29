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

# third party
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

# local
from appusers import registration
from appusers.models import AppUser


@receiver(post_save, sender=AppUser)
def email_user_confirmation(sender, **kwargs):
    """ 
    Email a user when they're created the first time so they can
    set up their password and change their first/last name if
    they need to.
    """
    pass
    # if kwargs['created'] and kwargs['instance'].last_login is None:
    #     registration.send_registration_email(
    #         kwargs['instance'],
    #         html_email_template_name='appuser/user_registration_html_email.html')

