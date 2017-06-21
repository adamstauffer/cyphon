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

# local
from .parameter_type import SearchQueryParameterType
from .parameter_value import SearchQueryParameterFieldValue, SearchQueryParameterKeywordValue


class SearchQueryParameter:
    """Represents an individual parameter of a search query.

    Attributes
    ----------
    parameter : str
        String value this parameter instance was created from.
    index : int
        Index position this parameter is in the search query.
    type : str
        Type of query parameter.
    errors: str
        Problems with this search query parameter.
    """
    UNKNOWN_TYPE = 'Parameter type is unknown.'
    """`str`

    Error message explaining that the type of the given parameter cannot
    be identified.
    """

    MISSING_PARAMETER_CLASS = (
        'There is no SearchQueryParameterValue class created to deal with '
        'parameter type `{}`.'
    )
    """`str`

    Error message explaining that a SearchQueryParameterValue class was
    not created to deal with this parameters type.
    """

    PARAMETER_TYPE_TO_VALUE_CLASS = dict([
        (SearchQueryParameterType.KEYWORD, SearchQueryParameterKeywordValue),
        (SearchQueryParameterType.FIELD, SearchQueryParameterFieldValue),
    ])

    @staticmethod
    def _get_parameter_value_class(parameter_type):
        try:
            return (
                SearchQueryParameter.PARAMETER_TYPE_TO_VALUE_CLASS[parameter_type]
            )
        except KeyError:
            raise Exception(
                SearchQueryParameter.MISSING_PARAMETER_CLASS.format(
                    parameter_type
                )
            )

    @staticmethod
    def _get_parameter_value(parameter, parameter_type):
        """Returns a SearchQueryParameterValue class.

        Returns the SearchQueryParameterValue class associated with the
        given parameter type that translates the parameter string into
        values.

        Parameters
        ----------
        parameter : str
            Search query parameter string.
        parameter_type: str
            Search query parameter type.

        Returns
        -------
        SearchQueryParameterValue
            Class instance that translates the parameter string into values.
        """
        return SearchQueryParameter._get_parameter_value_class(parameter_type)(
            parameter
        )

    def __init__(self, index, parameter):
        """Search query parameter.

        Parameters
        ----------
        index : int
            Index position of this parameter in the search query.
        parameter: str
            Parsed parameter string from the search query.
        """
        self.errors = []
        self.parameter = parameter
        self.index = index
        self.type = SearchQueryParameterType.get_parameter_type(self.parameter)

        if self.type is None:
            self._add_error(SearchQueryParameter.UNKNOWN_TYPE)
            self.value = None
        else:
            self.value = SearchQueryParameter._get_parameter_value(
                self.parameter,
                self.type
            )

            if not self.value.is_valid():
                self._add_errors(self.value.errors)

    def is_valid(self):
        """Determines of this parameter is valid.

        Returns
        -------
        bool
            If this search query parameter is valid.
        """
        return not bool(self.errors)

    def _add_error(self, error):
        """Adds an error to this parameters current error list.

        Parameters
        ----------
        error : str
            Error message to add.
        """
        self.errors.append(error)

    def _add_errors(self, errors):
        """Adds a list of errors to this parameter's current error list.

        Parameters
        ----------
        errors : list of str

        Returns
        -------

        """
        self.errors += errors
