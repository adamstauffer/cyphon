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

# standard library
import re

# local
from .search_parameter import SearchParameterType, SearchParameter
from .field_search_parameter import FieldSearchParameter
from .keyword_search_parameter import KeywordSearchParameter
from .distillery_filter_parameter import DistilleryFilterParameter


class UnknownParameter(SearchParameter):
    """
    SearchParameter that has an unknown type. This instance will always be
    an invalid parameter.
    """
    TYPE_UNKNOWN = 'Parameter type is unknown.'

    def __init__(self, index, parameter):
        """Constructor for UnknownParameter.

        Parameters
        ----------
        index: int
        parameter : str
        """
        super(UnknownParameter, self).__init__(index, parameter, None)

        self._add_error(UnknownParameter.TYPE_UNKNOWN)


class SearchQuery:
    """List of SearchQueryParameters used to search collections.

    Parses a string into a list of SearchQueryParameters that contain
    information used to search data collections.

    Attributes
    ----------
    errors : list of str
        Errors that occurred during the parsing of the query.
    invalid_parameters : list of SearchParameter
        Parameters that are not valid.
    keyword_parameters : list of KeywordSearchParameter
        Parameters that represent a keyword search.
    field_parameters : list of FieldSearchParameter
        Parameters that represent a field search.
    distillery_filter_parameter : DistilleryFilterParameter or None
        Parameters that are used to limit what distilleries are searched.
    unknown_parameters : list of UnknownParameter
        Parameters that have no known type.
    """

    PARAMETERS_REGEX = re.compile(
        r'\"(?:\"|\S.+?\")(?= |$)|\S+\"(?:\"|\S.+?\")|\S+'
    )
    """RegExp

    Regular expression object used to parse parameters from a search
    query string.
    """

    EMPTY_SEARCH_QUERY = 'Search query is empty.'
    """str
    
    Error message explaining that a search query is empty.
    """

    PARSING_ERROR = 'Could not parse parameters from query string `{}`.'
    """str
    
    Error message explaining that there was a problem parsing the query.
    """

    MULTIPLE_DISTILLERY_FILTERS = (
        'Only one distillery filter is only allowed to be used '
        'per search query. Parameter `{}` at index `{}` violates '
        'this rule.'
    )
    """str
    
    Error message explaining that there can only be one distillery filter
    per search query.
    """

    @staticmethod
    def _get_search_query_parameters(query):
        """Parses the query string into it's individual string parameters.

        Parameters
        ----------
        query: str

        Returns
        -------
        list of str
        """
        return SearchQuery.PARAMETERS_REGEX.findall(query)

    @staticmethod
    def _get_keywords(parameters):
        return [parameter.keyword for parameter in parameters]

    def __init__(self, query, ignored_parameter_types=None):
        """Constructor of a SearchQuery.

        Parameters
        ----------
        query : str
            Search query string
        """
        self._parameter_setters = {
            SearchParameterType.KEYWORD: self._add_keyword_parameter,
            SearchParameterType.FIELD: self._add_field_parameter,
            SearchParameterType.DISTILLERY: (
                self._set_distillery_filter_parameter
            ),
            None: self._add_unknown_parameter,
        }
        self.errors = []
        self.invalid_parameters = []
        self.keyword_parameters = []
        self.field_parameters = []
        self.distillery_filter_parameter = None
        self.unknown_parameters = []

        if not query:
            self._add_empty_query_error()
            return

        parameters = SearchQuery._get_search_query_parameters(query)

        if not parameters:
            self._add_parsing_error(query)
            return

        self._add_search_parameters(parameters, ignored_parameter_types)

    @property
    def distilleries(self):
        """Returns the distilleries specified in the distillery filter param.

        Returns
        -------
        list of Distillery or None
        """
        return (
            self.distillery_filter_parameter.distilleries
            if self.distillery_filter_parameter
            else None
        )

    @property
    def keywords(self):
        """Returns the keywords from the keyword parameters.

        Returns
        -------
        list of str or None
        """
        return (
            [parameter.keyword for parameter in self.keyword_parameters]
            if self.keyword_parameters
            else None
        )

    def as_dict(self):
        """Returns a JSON serializable representation of this object instance.

        Returns
        -------
        dict
        """
        return {
            'errors': self.errors,
            'keywords': self._get_keyword_parameters_as_dict(),
            'fields': self._get_field_parameters_as_dict(),
            'distilleries': self._get_distillery_filter_as_dict(),
        }

    def is_valid(self):
        """Determines if the SearchQuery is valid.

        Returns
        -------
        bool
        """
        return not self.errors and not self.invalid_parameters

    def _create_search_parameter(self, parameter_class, index, parameter):
        """Creates a search parameter using the given class.

        Checks for search parameter validity as well.

        Parameters
        ----------
        parameter_class : SearchParameter Class
        index : int
        parameter : str

        Returns
        -------
        SearchParameter
        """
        search_parameter = parameter_class(index, parameter)

        self._check_parameter_validity(search_parameter)

        return search_parameter

    def _get_distillery_filter_distilleries(self):
        """Returns the distilleries found from the distillery filter param.

        Returns
        -------
        list of Distillery or None
        """
        return (
            self.distillery_filter_parameter.distilleries
            if self.distillery_filter_parameter
            else None
        )

    def _get_keyword_parameters_as_dict(self):
        """Returns a the parameter info for each keyword parameter.

        Returns
        -------
        list of dict
        """
        return [keyword.as_dict() for keyword in self.keyword_parameters]

    def _get_field_parameters_as_dict(self):
        """Returns the parameter info for each field search parameter.

        Returns
        -------
        list of dict
        """
        return [field.as_dict() for field in self.field_parameters]

    def _get_distillery_filter_as_dict(self):
        """Returns the distillery filter parameter info.

        If the query does not have a distillery filter parameter, it
        returns None instead.

        Returns
        -------
        dict or None
        """
        return (
            self.distillery_filter_parameter.as_dict()
            if self.distillery_filter_parameter
            else None
        )

    def _add_empty_query_error(self):
        """Adds an EMPTY_SEARCH_QUERY error message to this instance."""
        self._add_error(SearchQuery.EMPTY_SEARCH_QUERY)

    def _add_parsing_error(self, query):
        """Adds a PARSING_ERROR error message to the query instance.

        Parameters
        ----------
        query: str
            Failed string that wasn't parsed.
        """
        self._add_error(SearchQuery.PARSING_ERROR.format(query))

    def _get_parameter_setter(self, parameter_type):
        """Returns the parameter type's setter function.

        Parameters
        ----------
        parameter_type : str

        Returns
        -------
        (int, str) -> None
        """
        return self._parameter_setters[parameter_type]

    def _add_search_parameters(self, parameters, ignored_parameter_types=None):
        """Adds the parsed query parameters as objects to the class.

        Parameters
        ----------
        parameters: list of str
        ignored_parameter_types : list of str or None
            Parameter types to ignore while parsing the parameters.
        """
        ignored_parameter_types = ignored_parameter_types or []

        for index, parameter in enumerate(parameters):
            parameter_type = SearchParameterType.get_parameter_type(parameter)

            if parameter_type in ignored_parameter_types:
                continue

            parameter_setter = self._get_parameter_setter(parameter_type)
            parameter_setter(index, parameter)

    def _add_parameter_error(self, parameter):
        """Adds a SearchParameter the the list of invalid parameters.

        Parameters
        ----------
        parameter : SearchParameter
        """
        self.invalid_parameters.append(parameter.as_dict())

    def _add_error(self, error):
        """Adds a search query error to the error list.

        Parameters
        ----------
        error : str
        """
        self.errors.append(error)

    def _add_multiple_distilleries_filters_error(self, parameter, index):
        """Adds a MULTIPLE_DISTILLERY_FILTERS error to the list of errors.

        Parameters
        ----------
        parameter : str
            Parameter string that violated the rule.
        index : int
            Index of the parameter in the search string.
        """
        self.errors.append(
            SearchQuery.MULTIPLE_DISTILLERY_FILTERS.format(parameter, index),
        )

    def _check_parameter_validity(self, parameter):
        """Checks if a search parameter is valid.

        If the parameter is invalid, it adds it to the list of
        invalid parameters.

        Parameters
        ----------
        parameter : SearchParameter
        """
        if not parameter.is_valid():
            self.invalid_parameters.append(parameter)

    def _add_keyword_parameter(self, index, parameter):
        """Adds a keyword search parameter to the list of keyword parameters.

        Parameters
        ----------
        index : int
            Index of the parameter in the search query.
        parameter : str
        """
        search_parameter = self._create_search_parameter(
            KeywordSearchParameter, index, parameter,
        )
        self.keyword_parameters.append(search_parameter)

    def _add_field_parameter(self, index, parameter):
        """Adds a field search parameter to the list of field search parameters.

        Parameters
        ----------
        index : int
            Index of the parameter in the search query.
        parameter : str
        """
        search_parameter = self._create_search_parameter(
            FieldSearchParameter, index, parameter,
        )
        self.field_parameters.append(search_parameter)

    def _set_distillery_filter_parameter(self, index, parameter):
        """Sets the queries distillery filter parameter.

        Parameters
        ----------
        index : int
            Index of the parameter in the search query.
        parameter : str
        """
        search_parameter = self._create_search_parameter(
            DistilleryFilterParameter, index, parameter,
        )

        if self.distillery_filter_parameter:
            self._add_multiple_distilleries_filters_error(parameter, index)
        else:
            self.distillery_filter_parameter = search_parameter

    def _add_unknown_parameter(self, index, parameter):
        """Adds an unknown parameter to the list of unknown parameters.

        Parameters
        ----------
        index : int
            Index of the parameter in the search query.
        parameter : str
        """
        search_parameter = self._create_search_parameter(
            UnknownParameter, index, parameter,
        )
        self.unknown_parameters.append(search_parameter)
