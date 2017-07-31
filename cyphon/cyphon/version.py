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

# third party
from django.utils.deprecation import MiddlewareMixin

GIT_TAG_COMMANDS = ['git', 'describe', '--tags', '--abbrev=0']

SEMANTIC_VERSION_REGEX = re.compile(b'\d+\.\d+\.\d+')


def get_version():
    """Returns the current version of Cyphon according to it's tag on git.

    Returns
    -------
    string or None
    """

    version = check_output(GIT_TAG_COMMANDS)

    if not version or not SEMANTIC_VERSION_REGEX.match(version):
        return None

    return version.decode('utf-8')


class VersionMiddleware(MiddlewareMixin):
    """
    Middleware that adds version information to response headers.
    """

    VERSION_HEADER = 'Cyphon-Version'
    """str

    Name of the header that contains the cyphon version number.
    """

    def __init__(self, get_response=None):
        self.current_version = get_version() or ''
        super(VersionMiddleware, self).__init__(get_response)

    def process_response(self, request, response):
        response[self.VERSION_HEADER] = self.current_version

        return response

    def process_request(self, request):
        request.cyphon_version = self.current_version

