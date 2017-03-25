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

# third party
from django.db import models

# local
from aggregator.pipes.models import Pipe
from sifter.chutes.models import Chute, ChuteManager
from sifter.datasifter.datasieves.models import DataSieve
from sifter.datasifter.datamungers.models import DataMunger

LOGGER = logging.getLogger(__name__)


class DataChuteManager(ChuteManager):
    """
    Adds methods to the default model manager.
    """

    def find_by_endpoint(self, endpoint):
        """
        Returns a QuerySet object containing only enabled Chutes
        for the gievn endpoint.
        """
        enabled_chutes = super(DataChuteManager, self).find_enabled()
        return enabled_chutes.filter(endpoint=endpoint)


class DataChute(Chute):
    """

    """
    sieve = models.ForeignKey(
        DataSieve,
        null=True,
        blank=True,
        default=None,
        related_name='chutes',
        related_query_name='chute'
    )
    munger = models.ForeignKey(DataMunger)
    endpoint = models.ForeignKey(Pipe)

    objects = DataChuteManager()

    def _get_platform_name(self):
        """

        """
        return self.endpoint.platform.name

    def bulk_process(self, data):
        """

        """
        for doc in data:
            self.process(doc)

    def process(self, data):
        """
        Overrides the parent method to add platform info to the data.
        """
        platform = self._get_platform_name()
        return super(DataChute, self).process(data, platform=platform)

