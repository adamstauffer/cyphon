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
import re
from subprocess import check_output

# third party
from django.utils.deprecation import MiddlewareMixin

_GIT_TAG_COMMANDS = ['git', 'describe', '--tags', '--abbrev=0']

_SEMANTIC_VERSION_REGEX = re.compile(b'\d+\.\d+\.\d+')


def get_version():
    """Return the current version of Cyphon according to its tag on git.

    Returns
    -------
    |str| or |None|

    """
    version = check_output(_GIT_TAG_COMMANDS)

    if not version or not _SEMANTIC_VERSION_REGEX.match(version):
        return None

    return version.decode('utf-8').strip('\n')


class VersionMiddleware(MiddlewareMixin):
    """Middleware that adds version information to response headers."""

    VERSION_HEADER = 'Cyphon-Version'
    """|str|

    Name of the header that contains the Cyphon version number.
    """

    def __init__(self, get_response=None):
        """Initialize a VersionMiddleware instance."""
        self.current_version = get_version() or ''
        super(VersionMiddleware, self).__init__(get_response)

    def process_response(self, request, response):
        """Add the current Cyphon version to an HTTP response header.

        Parameters
        ----------
        request : :class:`~django.core.handlers.wsgi.WSGIRequest`

        response : :class:`~django.template.response.TemplateResponse`

        Returns
        -------
        response : :class:`~django.template.response.TemplateResponse`
            The reponse containing the Cyphon version header.

        """
        response[self.VERSION_HEADER] = self.current_version

        return response

    def process_request(self, request):
        """Set the Cyphon version in a WSGIRequest.

        Parameters
        ----------
        request : :class:`~django.core.handlers.wsgi.WSGIRequest`

        Returns
        -------
        None

        """
        request.cyphon_version = self.current_version
