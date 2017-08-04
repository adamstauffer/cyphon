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
Settings for the Cyclops package.
"""

CYCLOPS_VERSION = '0.4.3'
"""str

Version number of Cyclops to use.
"""

CYCLOPS_JS_URL = (
    'https://cdn.rawgit.com/dunbarcyber/cyclops/{0}/dist/cyclops.js'.format(
        CYCLOPS_VERSION))
"""str

CDN URL of the cyclops JS file. Contains the main application.
"""

CYCLOPS_CSS_URL = (
    'https://cdn.rawgit.com/dunbarcyber/cyclops/{0}/dist/cyclops.css'.format(
        CYCLOPS_VERSION))
"""str

CDN URL of the cyclops CSS file. Contains all the styling.
"""
