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
from .parameter_type import SearchParameterType
from .parameter_value import FieldValue, KeywordValue
from bottler.datafields.models import DataField


class SearchParameter:
    """Represents an individual parameter of a search query.

    Attributes
    ----------
    parameter : str
        String value this parameter instance was created from.
    index : int
        Index position this parameter is in the search query.
    type : str
        Type of query parameter.
    _errors: str
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

    TYPE_TO_VALUE_CLASS = dict([
        (SearchParameterType.KEYWORD, KeywordValue),
        (SearchParameterType.FIELD, FieldValue),
    ])

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
        try:
            return SearchParameter.TYPE_TO_VALUE_CLASS[parameter_type](
                parameter
            )
        except KeyError:
            raise Exception(
                SearchParameter.MISSING_PARAMETER_CLASS.format(
                    parameter_type
                )
            )

    def __init__(self, index, parameter):
        """Search query parameter.

        Parameters
        ----------
        index : int
            Index position of this parameter in the search query.
        parameter : str
            Parsed parameter string from the search query.
        """
        self._errors = []
        self.parameter = parameter
        self.index = index
        self.type = SearchParameterType.get_parameter_type(self.parameter)

        if self.type is None:
            self._errors.append(SearchParameter.UNKNOWN_TYPE)
            self.value = None
        else:
            self.value = SearchParameter._get_parameter_value(
                self.parameter,
                self.type
            )

    @property
    def errors(self):
        """Returns the compiled errors of this instance and the value class.

        Returns
        -------
        list of str
        """
        if self.value:
            return self._errors + self.value.errors
        else:
            return self._errors

    def is_valid(self):
        """Determines of this parameter is valid.

        Returns
        -------
        bool
        """
        return not bool(self.errors)


class SearchParameterBase:
    def __init__(self, index, parameter, parameter_type):
        self.errors = []
        self.index = index
        self.parameter = parameter
        self.type = parameter_type

    def is_valid(self):
        return not bool(self.errors)


class KeywordSearchParameter(SearchParameterBase):
    def __init__(self, index, parameter):
        """

        Parameters
        ----------
        index : int
        parameter : str
        """
        super(KeywordSearchParameter, self).__init__(
            index,
            parameter,
            SearchParameterType.KEYWORD,
        )
        self.keyword = parameter.strip('"')

        if not self.keyword:
            self.errors.append('Keyword value is empty.')


class UnknownSearchParameter(SearchParameterBase):
    def __init__(self, index, parameter):
        super(UnknownSearchParameter, self).__init__(index, parameter, None)
        self.errors.append('Parameter type is unknown.')

class FieldSearchParameter(SearchParameterBase):
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

    def __init__(self, index, parameter):
        super(FieldSearchParameter, self).__init__(
            index,
            parameter,
            SearchParameterType.FIELD,
        )

        self._parse_parameter(parameter)

    def _parse_parameter(self, parameter):
        parsed_parameter = FieldSearchParameter.FIELD_REGEX.search(parameter)

        if parsed_parameter:
            self._assign_parsed_fields(parsed_parameter)
            self._check_operator()
            self._check_value()

            if self.is_valid():
                self._get_data_field()
        else:
            self.errors.append(FieldSearchParameter.INVALID_PARAMETER)

    def _get_data_field(self):
        try:
            self.data_field = DataField.objects.get(
                field_name__exact=self.field_name,
            )
        except DataField.DoesNotExist:
            self.errors.append(
                FieldSearchParameter.FIELD_DOES_NOT_EXIST.format(
                    self.field_name
                )
            )

    def _assign_parsed_fields(self, parsed_parameter):
        self.field_name, self.operator, self.value = (
            parsed_parameter.groups()
        )

    def _check_operator(self):
        """

        Returns
        -------

        """
        if self.operator not in FieldSearchParameter.OPERATORS:
            self.errors.append(
                FieldSearchParameter.INVALID_OPERATOR.format(self.operator)
            )

    def _check_value(self):
        if not self.value:
            self.errors.append(FieldSearchParameter.EMPTY_VALUE)

