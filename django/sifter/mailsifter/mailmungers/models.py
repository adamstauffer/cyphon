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
from django.conf import settings
from django.db import models

# local
from cyphon.models import GetByNameManager
from sifter.mungers.models import Munger
from sifter.mailsifter.mailcondensers.models import MailCondenser

_MAILSIFTER_SETTINGS = settings.MAILSIFTER


class MailMunger(Munger):
    """
    Attributes:
        name : str

        distillery : Distillery

        condenser: MailCondenser
            a MailCondenser used to distill the message into the chosen
            Bottle

    """
    condenser = models.ForeignKey(MailCondenser)

    objects = GetByNameManager()

    def _get_company(self):
        """

        """
        return self.distillery.company

    def _process_data(self, data):
        """
        Takes a dictionary of data (e.g., of a social media post) and a
        Condenser. Returns a dictionary that distills the data
        using the crosswalk defined by the Condenser.
        """
        company = self._get_company()
        return self.condenser.process(data=data, company=company)

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
        collection = _MAILSIFTER_SETTINGS['MAIL_COLLECTION']
        doc_id = data['Message-ID']
        return self._save_data(doc, doc_id, collection, platform)
