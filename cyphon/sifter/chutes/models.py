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
from django.core.exceptions import ObjectDoesNotExist

# local
from cyphon.models import SelectRelatedManager, FindEnabledMixin

LOGGER = logging.getLogger(__name__)


class ChuteManager(SelectRelatedManager, FindEnabledMixin):
    """
    Adds methods to the default model manager.
    """

    def get_by_natural_key(self, sieve, munger):
        """
        Allow retrieval of a DataChute by its natural key instead of its
        primary key.
        """
        try:
            return self.get(sieve=sieve, munger=munger)
        except ObjectDoesNotExist:
            LOGGER.error('%s for sieve %s and munger %s does not exist',
                         self.model.__name__, sieve, munger)


class Chute(models.Model):
    """

    """
    enabled = models.BooleanField(default=True)

    class Meta:
        """
        Metadata options for a Django Model.
        """
        abstract = True
        unique_together = ('sieve', 'munger')
        ordering = ['sieve', 'munger']

    def __str__(self):
        if self.sieve:
            return '%s -> %s' % (self.sieve, self.munger)
        else:
            return '-> %s' % self.munger

    def _is_match(self, data):
        """
        Takes a data dictionary and returns True if the dictionary
        matches the rules defined by the Chute's sieve. Otherwise,
        returns False.
        """
        if self.sieve:
            return self.sieve.is_match(data)
        else:
            return True

    def _munge(self, data, doc_id=None, collection=None, platform=None):
        """
        Takes a data dictionary, a document id, and a string indicating the
        source of the data. Processes the data with the Chute's munger,
        and returns the document id of the distilled document.
        """
        return self.munger.process(data, doc_id, collection, platform)

    def process(self, data, doc_id=None, collection=None, platform=None):
        """
        Takes a data dictionary, a document id, and a string indicating
        the source of the data. Determines if the data is a match for the
        Chute's sieve. If it is, processes the data with the Chute's
        munger and returns the document id of the distilled document.
        Otherwise, returns None.
        """
        if self.enabled and self._is_match(data):
            return self._munge(data, doc_id, collection, platform)

    def thread_process(self, queue, **kwargs):
        """
        Takes a Queue, a data dictionary, a document id, and a string
        indicating the source of the data. Determines if the data is a
        match for the Chute's sieve. If it is, processes the data with
        the Chute's munger and returns the document id of the distilled
        document. Otherwise, returns None.
        """
        result = self.process(**kwargs)
        if result is not None:
            queue.put(True)

