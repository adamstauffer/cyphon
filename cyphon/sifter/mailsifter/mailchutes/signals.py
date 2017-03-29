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
Defines a signal reciever for incoming emails.
"""

# third party
from django.db import close_old_connections
from django.dispatch import receiver
from django_mailbox.signals import message_received

# local
from .services import process_email


@receiver(message_received)
def handle_message(sender, message, **args):
    """
    Takes a signal sender and a Django Mailbox Message and processes
    the message.
    """
    # get the Python email.message.Message object
    email = message.get_email_object()

    # process the email through enabled MailChutes
    process_email(email)

    close_old_connections()

