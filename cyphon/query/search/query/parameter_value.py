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

# local
from bottler.datafields.models import DataField


class SearchQueryParameterValue:
    """Base class for parsing parameter values.

    Attributes
    ----------
    errors : list of str
        Problems that occurred while parsing the parameter value.
    """
    def __init__(self):
        self.errors = []

    def is_valid(self):
        """Determines if the parameter value is valid.

        Returns
        -------
        bool
            If the parameter value is valid.
        """
        return not bool(self.errors)

    def _add_error(self, error):
        """Adds an error to the current list of value errors.

        Parameters
        ----------
        error : str
            Error message to add.
        """
        self.errors.append(error)


class SearchQueryParameterKeywordValue(SearchQueryParameterValue):
    EMPTY_VALUE = 'Keyword value is empty.'
    """str

    Error message explaining that the keyword value is empty
    """

    def __init__(self, parameter):
        """

        Parameters
        ----------
        parameter : str
            Search query parameter to pull keyword value from.
        """
        super().__init__()
        self.keyword = parameter.strip('"')

        if not self.keyword:
            self._add_error(SearchQueryParameterKeywordValue.EMPTY_VALUE)


class SearchQueryParameterFieldValue(SearchQueryParameterValue):
    FIELD_REGEX = re.compile(
        r'(?P<field_name>^\w[\w.]*)'  # Name of the field
        r'(?P<operator>[=<>!]{1,2})'  # Operator to compare value with
        r'(?P<value>$|\".*\"$|[\w.]*$)'  # Value to match on the field
    )
    """RegExp

    Regex object used to parse the field search properties from the
    parameter string.
    """

    OPERATORS = ['=', '<', '>', '<=', '>=', '!=']
    """list of str

    All the possible operator values.
    """

    FIELD_DOES_NOT_EXIST = 'Field `{}` does not exist.'
    """str

    Error message explaining that the requested field to be searched does
    not exist.
    """

    INVALID_OPERATOR = 'Operator `{}` is not a valid operator.'
    """str

    Error message explaining that the given operator is invalid.
    """

    INVALID_PARAMETER = 'Could not parse parameter into field properties.'
    """str

    Error message explaining that the given parameter could not be parsed
    by the regex object.
    """

    EMPTY_VALUE = 'Value is empty.'
    """str

    Error message explaining that the value to compare against is empty.
    """

    @staticmethod
    def _parse_parameter(parameter):
        """Parses the parameter string into the field search properties.

        Parameters
        ----------
        parameter : str
            Parameter string to parse.

        Returns
        -------
        MatchObject or None
        """
        return SearchQueryParameterFieldValue.FIELD_REGEX.search(parameter)

    @staticmethod
    def _get_bottle_field(field_name):
        """Returns the matching bottle field of the given field_name.

        Parameters
        ----------
        field_name : str
            Name of the field to search.

        Returns
        -------
        DataField or None
            The matching DataField object or None.
        """
        try:
            return DataField.objects.get(field_name__exact=field_name)
        except DataField.DoesNotExist:
            return None

    def __init__(self, parameter):
        """Constructor for SearchQueryParameterFieldValue.

        Parameters
        ----------
        parameter : str
            Query parameter string to parse the value of.
        """
        super().__init__()

        parsed = SearchQueryParameterFieldValue._parse_parameter(parameter)

        if parsed:
            field_name, self.operator, self.value = parsed.groups()

            self.field = SearchQueryParameterFieldValue._get_bottle_field(
                field_name
            )

            if self.field is None:
                self._add_field_does_not_exist_error(field_name)

            if self.operator not in SearchQueryParameterFieldValue.OPERATORS:
                self._add_invalid_operator_error(self.operator)

            if not self.value:
                self._add_error(SearchQueryParameterFieldValue.EMPTY_VALUE)
        else:
            self._add_error(SearchQueryParameterFieldValue.INVALID_PARAMETER)

    @property
    def name(self):
        return self.field.field_name

    @property
    def type(self):
        return self.field.field_type

    @property
    def pk(self):
        return self.field.pk

    def _add_field_does_not_exist_error(self, field_name):
        """Adds a FIELD_DOES_NOT_EXIST error to the current list of errors.

        Parameters
        ----------
        field_name : str
            Name of the field that doesn't exist.

        """
        self._add_error(
            SearchQueryParameterFieldValue.FIELD_DOES_NOT_EXIST.format(
                field_name
            )
        )

    def _add_invalid_operator_error(self, operator):
        """Adds an INVALID_OPERATOR error to the current list of errors.

        Parameters
        ----------
        operator : str
            String that was attempted to be used as an operator.

        """
        self._add_error(
            SearchQueryParameterFieldValue.INVALID_OPERATOR.format(operator)
        )
