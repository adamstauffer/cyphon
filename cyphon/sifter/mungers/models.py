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
from django.db import models

# local
from distilleries.models import Distillery


class Munger(models.Model):
    """

    Attributes:
        name: a string representing the name of the DataReader
        distillery: a Distillery used to save the distilled message to a Warehouse

    Define in subclasses:
        condenser: a Condenser used to distill the message into the chosen
                   Bottle

    """
    name = models.CharField(max_length=40, unique=True)
    distillery = models.ForeignKey(Distillery)

    class Meta:
        """
        Metadata options for a Django Model.
        """
        abstract = True
        unique_together = ('condenser', 'distillery')
        ordering = ['name']

    def __str__(self):
        return self.name

    def _save_data(self, data, doc_id=None, collection=None, platform=None):
        """

        """
        return self.distillery.save_data(data, doc_id, collection, platform)

    def _process_data(self, data):
        """
        Takes a dictionary of data (e.g., of a social media post) and a
        Condenser. Returns a dictionary that distills the data
        using the crosswalk defined by the Condenser.
        """
        return self.condenser.process(data)

    def process(self, data, doc_id=None, collection=None, platform=None):
        """
        Condenses data into the Distillery's Bottle, adds the doc_id and
        source to the data, saves it in the Distillery's Collection
        (database collection), and sends a signal that the document has been
        saved.

        Parameters:
            data: a dictionary of raw data
            condenser: a Condenser that should be used to distill the data
            doc_id: the id of the document that contains the data
            collection: a string representing the Collection in which the raw
                    data is stored (e.g., 'elasticsearch.cyphon.twitter')
        """
        doc = self._process_data(data)
        doc_id = self._save_data(doc, doc_id, collection, platform)
        return doc_id

