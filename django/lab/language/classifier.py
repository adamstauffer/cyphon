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
from langdetect import detect_langs


def assign_language(text):
    """
    Uses Google's language detection algorithm to assign a language to a text
    string. If the language cannot be determined with at least 99% confidence,
    the function returns the string 'none'. In such cases, MongoDB's text index  
    will use simple tokenization with no list of stop words and no stemming.
    See http://docs.mongodb.org/manual/reference/text-search-languages/
    for more info.

    """
    # languages supported by MongoDB's text index
    supported_langs = ['da', 'nl', 'en', 'fi', 'fr', 'de', 'hu', 'it', 'nb',
                       'pt', 'ro', 'ru', 'es', 'sv', 'tr']

    langs = detect_langs(text)

    if langs[0].prob >= 0.99 and langs[0].lang in supported_langs:
        return langs[0].lang
    else:
        return 'none'

