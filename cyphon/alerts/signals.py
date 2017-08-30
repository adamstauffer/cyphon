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
import smtplib

# third party
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

# local
from tags.models import DataTagger, Tag
from utils.emailutils.emailutils import emails_enabled
from .models import Alert, Analysis, Comment
from .services import compose_comment_email

_LOGGER = logging.getLogger(__name__)


@receiver(post_save, sender=Comment)
def send_comment_notification(sender, instance, created, **kwargs):
    """Email relevant users when a new |Comment| is saved."""

    # email relevant users if a comment is created
    if created and emails_enabled():
        for user in instance.get_other_contributors():
            email_message = compose_comment_email(instance, user)
            try:
                email_message.send()
            except smtplib.SMTPAuthenticationError as error:
                _LOGGER.error('An error occurred when sending an '
                              'email notification: %s', error)


def tag_alert(sender, instance, created, **kwargs):
    """Tag a new |Alert|."""
    if created:
        DataTagger.objects.process(instance)


def tag_analysis(sender, instance, created, **kwargs):
    """Tag an |Analysis|."""
    Tag.objects.process(value=instance.notes, obj=instance)


def tag_comment(sender, instance, created, **kwargs):
    """Tag a |Comment|."""
    Tag.objects.process(value=instance.content, obj=instance)


if not settings.TEST:
    post_save.connect(tag_alert, sender=Alert)
    post_save.connect(tag_analysis, sender=Analysis)
    post_save.connect(tag_comment, sender=Comment)
