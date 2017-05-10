#!/usr/bin/env python
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

# local
from monitors.models import Monitor
from sifter.datasifter.datachutes.models import DataChute
from sifter.logsifter.logchutes.models import LogChute
from watchdogs.models import Watchdog


def _process_json(doc_obj):
    """

    """
    DataChute.objects.process(doc_obj)


def _process_log(doc_obj):
    """

    """
    LogChute.objects.process(doc_obj)


def _call_monitors(doc_obj):
    """

    """
    Monitor.objects.process(doc_obj)


def _call_watchdogs(doc_obj):
    """

    """
    Watchdog.objects.process(doc_obj)


CONSUMERS = {
    'DATACHUTES': _process_json,
    'LOGCHUTES': _process_log,
    'MONITORS': _call_monitors,
    'WATCHDOGS': _call_watchdogs,
}
