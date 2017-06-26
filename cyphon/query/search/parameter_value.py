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


class SearchParameterValue:
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


class KeywordValue(SearchParameterValue):
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
            self.errors.append(KeywordValue.EMPTY_VALUE)

class FieldOperators:
    EQUALS = '='
    GREATER_THAN = '>'
    LESS_THAN = '<'
    GREATER_THAN_OR_EQUAL = '>='
    LESS_THAN_OR_EQUAL = '<='
    NOT_EQUAL = '!='
    ALL = [
        EQUALS,
        GREATER_THAN,
        LESS_THAN,
        GREATER_THAN_OR_EQUAL,
        LESS_THAN_OR_EQUAL,
        NOT_EQUAL,
    ]
    BOOLEAN_OPERATORS = dict([(EQUALS, 'eq')])
    TEXT_OPERATORS = dict([(EQUALS, 'regex')])
    DATE_OPERATORS = dict([
        (GREATER_THAN, 'gt'),
        (LESS_THAN, 'lt'),
        (GREATER_THAN_OR_EQUAL, 'gte'),
        (LESS_THAN_OR_EQUAL, 'lte'),
    ])
    NUMBER_FIELDS = ['FloatField', 'IntegerField']
    NUMBER_OPERATORS = [ALL]



class FieldValue(SearchParameterValue):
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
        return FieldValue.FIELD_REGEX.search(parameter)

    @staticmethod
    def _get_data_field(field_name):
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

        parsed = FieldValue._parse_parameter(parameter)

        if parsed:
            field_name, self.operator, self.value = parsed.groups()

            self.field = FieldValue._get_data_field(
                field_name
            )

            if self.field is None:
                self._add_field_does_not_exist_error(field_name)

            if self.operator not in FieldValue.OPERATORS:
                self._add_invalid_operator_error(self.operator)

            if not self.value:
                self.errors.append(FieldValue.EMPTY_VALUE)
        else:
            self.errors.append(FieldValue.INVALID_PARAMETER)

    @property
    def field_name(self):
        """Returns the field_name of the matching DataField.

        Returns
        -------
        str
        """
        if self.field:
            return self.field.field_name
        else:
            return None

    @property
    def field_type(self):
        """Returns the field_type of the matching DataField.

        Returns
        -------
        str
        """
        if self.field:
            return self.field.field_type
        else:
            return None

    @property
    def field_pk(self):
        """Returns the primary key of the matching DataField.

        Returns
        -------
        int
        """
        if self.field:
            return self.field.pk
        else:
            return None

    def _add_field_does_not_exist_error(self, field_name):
        """Adds a FIELD_DOES_NOT_EXIST error to the current list of errors.

        Parameters
        ----------
        field_name : str
            Name of the field that doesn't exist.

        """
        self.errors.append(
            FieldValue.FIELD_DOES_NOT_EXIST.format(
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
        self.errors.append(
            FieldValue.INVALID_OPERATOR.format(operator)
        )
