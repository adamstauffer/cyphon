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


class SearchParameterType:
    """
    Contains values and helper functions to determine a search query
    parameter's type.
    """

    KEYWORD = 'keyword'
    """str

    String that indicates that a parameter is a keyword search.
    """

    FIELD = 'field'
    """str

    String indicating that a parameter is a field search.
    """

    DISTILLERY = 'distillery'
    """str

    String indicating that a parameter is a distillery filter.
    """

    TYPE_CHECK_REGEX_MAP = [
        (KEYWORD, r'^\".*\"$|^\w[\w.]*$'),
        (DISTILLERY, r'^source=(?:\*?[\w.]+\*?)?$'),
        (FIELD, r'^\w[\w.]*[=<>!]{1,2}(?:$|\".*\"$|[\w.]*$)')
    ]

    @staticmethod
    def get_parameter_type(parameter):
        """Returns the search query parameter type.

        Parameters
        ----------
        parameter : str
            Search query parameter to return the type of.

        Returns
        -------
        str or None
            Parameter type.
        """
        for type_check in SearchParameterType.TYPE_CHECK_REGEX_MAP:
            if re.match(type_check[1], parameter):
                return type_check[0]

        return None
