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
Defines classes for Mattermost actions.
"""

# standard library
import json

# third party
from django.conf import settings
import requests

# local
from ambassador.transport import Cargo
from responder.carrier import Carrier

_MATTERMOST_SETTINGS = settings.MATTERMOST

# message colors mapped to alert levels
COLOR_LEVEL = {
    'CRITICAL': '#c168a6',
    'HIGH': '#d6705c',
    'MEDIUM': '#ffc578',
    'LOW': '#6ca887',
    'INFO': '#80b8d6'
}


class WebHookHandler(Carrier):
    """
    Base class for interacting with Mattermost Web Hooks.
    """

    def __init__(self, *args, **kwargs):
        super(WebHookHandler, self).__init__(*args, **kwargs)
        self.server = '{server}/hooks/{hook}'.format(
            server=_MATTERMOST_SETTINGS['SERVER'],
            hook=_MATTERMOST_SETTINGS['GENERATED_KEY'])
        self.display_username = _MATTERMOST_SETTINGS['DISPLAYED_USERNAME']

    def process_request(self, obj):
        """Post a Mattermost message for an Alert.

        Parameters
        ----------
        obj : |Alert|
            The |Alert| used to create the Mattermost message.

        Returns
        -------
        |Cargo|
            The results of the API call to Mattermost.

        """
        response = requests.post(
            self.server,
            headers={
                'Content-type': 'application/json'
            },
            data=json.dumps({
                'username': self.display_username,
                'attachments': [
                    {
                        'fallback': '#### New Cyphon Alert! \nTitle: '
                                    '{}\nLink: {}'.format(obj.title, obj.link),
                        'color': '{}'.format(COLOR_LEVEL.get(obj.level)),
                        'text': 'A new alert was created in Cyphon',
                        'author_name': 'Cyphon',
                        'title': '{}'.format(obj.title),
                        'title_link': '{}'.format(obj.link),
                        'fields': [
                            {
                                'short': True,
                                'title': 'Source',
                                'value': '{}'.format(obj.distillery)
                            },
                            {
                                'short': True,
                                'title': 'Level',
                                'value': '{}'.format(obj.level)
                            },
                            {
                                'short': True,
                                'title': 'Status',
                                'value': '{}'.format(obj.status)
                            },
                            {
                                'short': True,
                                'title': 'Incidents',
                                'value': '{}'.format(obj.incidents)
                            }]
                    }
                ]
            })
        )

        return Cargo(
            status_code=response.status_code,
            data={'response': response.text}
        )
