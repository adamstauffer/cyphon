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
[`source`_]

Default Django settings for Cyphon when running tests or compiling docs.

For more information on this Django file, see:
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of Django settings and their values, see:
https://docs.djangoproject.com/en/1.9/ref/settings/

.. _source: ../_modules/cyphon/settings/dev.html

"""

from .default import *


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}
