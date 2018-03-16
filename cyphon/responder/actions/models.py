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
Defines an |Action| class for an API endpoint.
"""

# third party
from django.db import models
from django.utils.translation import ugettext_lazy as _

# local
from ambassador.endpoints.models import Endpoint, EndpointManager
from cyphon.models import FindEnabledMixin
from responder.destinations.models import Destination
from sifter.datasifter.datasieves.models import DataSieve
from cyphon.transaction import close_old_connections


class Action(Endpoint):
    """
    Specifies the module and |Carrier| class that should be used to
    access an API endpoint of a |Destination|, such as JIRA. An |Action|
    can pass an |Alert| to the |Carrier|, which uses it to construct and
    send a request to the API endpoint. The |Action| then retrieves a
    |Dispatch| of the API response from the |Carrier|.

    Attributes
    ----------
    api_module : str
        The name of the module that will handle the API request
        (i.e., the name of the Python file without the extension,
        e.g., 'handlers').

    api_class : str
        The name of the class that will handle the API request
        (e.g., 'SearchAPI').

    visa_required : bool
        Whether requests to the API endpoint are rate limited.
        If |True|, an |Emissary| must have a |Visa| to access the
        |Endpoint|. The |Visa| defines the rate limit that should
        apply to the |Emissary|'s |Passport| (API key).

    platform : Destination
        The |Destination| representing the data platform which the API
        endpoint accesses.

    title : str
        A short description of the |Action|'s result' (e.g. "JIRA Issue").

    description : str
        A short description of the |Action| (e.g. "Create a JIRA Issue").

    """
    platform = models.ForeignKey(
        Destination,
        help_text=_('The package that will handle the API request.')
    )
    title = models.CharField(
        max_length=40,
        unique=True,
        null=True,
        help_text=_('A short description of the Action\'s result '
                    '(e.g., JIRA Issue). This is used to describe the '
                    'Dispatch returned by a completed Action.')
    )
    description = models.CharField(
        max_length=40,
        unique=True,
        null=True,
        help_text=_('A short description of the Action in active tense '
                    '(e.g., "Create a JIRA Issue"). This is used to '
                    'describe the Action in a list of options.')
    )

    objects = EndpointManager()

    class Meta:
        ordering = ['title']
        unique_together = ('platform', 'api_class')

    def save(self, *args, **kwargs):
        """
        Overrides the save() method to assign a default description to
        a new Action using its other attributes.
        """
        if self.description is None:
            self.description = str(self)
        super(Action, self).save(*args, **kwargs)

    def get_dispatch(self, user, alert):
        """Take action on an |Alert| and get a |Dispatch| of the API
        response.

        Parameters
        ----------
        user : |AppUser|
            The user making the API request.

        alert : |Alert|
            The |Alert| on which the action is being taken and to which
            the API request relates.

        Returns
        -------
        |Dispatch|
            A record of the API response.

        """
        transport = self.create_request_handler(user=user)
        transport.run(alert)
        return transport.record


class AutoActionManager(models.Manager, FindEnabledMixin):
    """
    Adds methods to the default model manager.
    """

    @close_old_connections
    def process(self, alert):
        """Performs applicable |AutoActions| on an |Alert|.

        Parameters
        ----------
        alert : |Alert|
            The |Alert| to process.

        Returns
        -------
        None

        """
        autoactions = self.find_enabled()
        for autoaction in autoactions:
            autoaction.process(alert)


class AutoAction(models.Model):
    """
    Specifies an |Action| that is performed on every alert creation.
    Optionally references a |DataSieve| that can examine alert data
    before performing the action.

    Attributes
    ----------
    action : Action
        The |Action| that is performed at each alert creation.

    sieve : DataSieve
        The |DataSieve| to use to determine if the action should be
        performed.

    enabled : bool
        Global switch for the |AutoAction|.

    """

    action = models.ForeignKey(
        Action,
        on_delete=models.PROTECT,
        help_text=_('The Action to perform.')
    )
    sieve = models.ForeignKey(
        DataSieve,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        help_text=_('The DataSieve used to inspect the data during this step.')
    )
    enabled = models.BooleanField(
        default=True
    )

    objects = AutoActionManager()

    def __str__(self):
        return '{} - {}'.format(self.id, self.action)

    def _is_applicable(self, alert):
        """
        Takes an Alert and returns a Boolean indicating whether the
        AutoAction is applicable.
        """
        return not self.sieve or self.sieve.is_match(alert.data)

    def _create_request_handler(self):
        """
        Returns a Carrier to handle the API request for the AutoAction.
        """
        return self.action.create_request_handler(user=None)

    def process(self, alert):
        """Process the given |Alert| if the |AutoAction| is applicable.

        Parameters
        ----------
        alert : |Alert|
            The |Alert| which the AutoAction should process.

        Returns
        -------
        None

        """
        if self._is_applicable(alert):
            transport = self._create_request_handler()
            transport.run(alert)
