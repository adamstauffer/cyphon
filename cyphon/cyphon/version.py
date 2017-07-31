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

# standard library
from subprocess import check_output
import re

VERSION_REGEX = re.compile(b'\d+\.\d+\.\d+')
"""RegExp

Regular express used to pull the version number of Cyphon from the most
recent git commit tag.
"""


def get_version():
    """Returns the current version of Cyphon according to it's tag on git.

    Returns
    -------
    string or None
    """

    raw_version = check_output(['git', 'describe', '--tags'])

    if not raw_version:
        return None

    version = VERSION_REGEX.match(raw_version)

    if not version:
        return None

    return version.group(0).decode('utf-8')


class VersionMiddleware(object):
    """
    Middleware that adds version information to response headers.
    """

    VERSION_HEADER = 'Cyphon-Version'
    """str

    Name of the header that contains the cyphon version number.
    """

    VERSION_REGEX = re.compile(b'\d+\.\d+\.\d+')
    """RegExp

    Regular express used to pull the version number of Cyphon from the most
    recent git commit tag.
    """

    def __init__(self, get_response=None):
        self.get_response = get_response
        self.current_version = get_version() or ''

    def __call__(self, request):
        """Adds the Cyphon version number into a header on every response.

        Parameters
        ----------
        request : :class: `~django.http.HttpRequest`

        Returns
        -------
        :class: `~django.http.HttpResponse`
        """
        response = self.get_response(request)
        response[self.VERSION_HEADER] = self.current_version
        request.cyphon_version = self.current_version

        return response

    def process_response(self, request, response):
        response[self.VERSION_HEADER] = self.current_version

        return response

    def process_request(self, request):
        request.cyphon_version = self.current_version
        return None
