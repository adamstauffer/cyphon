# -*- coding: utf-8 -*-
# Copyright 2017-2018 Dunbar Security Solutions, Inc.
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
Defines a reciever for the Distillery app's document_saved signal.
"""

# third party
from django.db.models.signals import post_save
from django.dispatch import receiver

# local
from alerts.models import Alert
from distilleries.signals import document_saved
from .models import AutoAction


@receiver(post_save, sender=Alert)
def process_autoaction(sender, instance, created, **kwargs):
    """Perform applicable |AutoActions| when a new |alert| is saved."""

    if created:
        AutoAction.objects.process(instance)
