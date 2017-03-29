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
Provides services for handling email messages.
"""

# standard library
import logging

# third party
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

# local
from sifter.mailsifter.mailchutes.models import MailChute
from sifter.mailsifter.mailmungers.models import MailMunger

_MAILSIFTER_SETTINGS = settings.MAILSIFTER

_LOGGER = logging.getLogger(__name__)


def process_email(email):
    """
    Takes an email.message.Message object and processes it through
    enabled MailChutes.

    """
    enabled_chutes = MailChute.objects.find_enabled()
    saved = False

    for chute in enabled_chutes:
        result = chute.process(data=email)
        if result:
            saved = True
    if not saved and _MAILSIFTER_SETTINGS['DEFAULT_MAIL_CHUTE_ENABLED']:
        catch_email(email)


def catch_email(email):
    """
    Takes an email.message.Message object and saves it using the default
    MailMunger.
    """
    munger_name = _MAILSIFTER_SETTINGS['DEFAULT_MAIL_MUNGER']

    try:
        default_munger = MailMunger.objects.get(name=munger_name)
        default_munger.process(email)
    except ObjectDoesNotExist:
        _LOGGER.error('Default MailMunger "%s" is not configured. '
                      'Could not save message %s',
                      munger_name, email['Message-ID'])
