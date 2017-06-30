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
from cyphon.fieldsets import QueryFieldset
from distilleries.models import Distillery
from engines.queries import EngineQuery


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
    parameter_errors : list of SearchParameter
        Parameters that are not valid.
    keywords : list of KeywordSearchParameter
        Parameters that represent a keyword search.
    fields : list of FieldSearchParameter
        Parameters that represent a field search.
    distilleries : list of DistilleryFilterParameter
        Parameters that are used to limit what distilleries are searched.
    unknown : list of UnknownParameter
        Parameters that have no known type.
    """

    PARAMETERS_REGEX = re.compile(
        r'\"(?:\"|\S.+?\")(?=\ |$)|\S+\"(?:\"|\S.+?\")|\S+'
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

    MULTPIPLE_DISTILLERY_FILTERS = (
        'There can only be one instance of the `source=` parameter.'
    )
    """str

    Error message explaining that there can only be one
    SearchQueryParameter that has the SearchQueryParameterType.DISTILLERY
    type.
    """

    PARAMETER_TYPE_VALUES_MAP = dict([
        (SearchParameterType.KEYWORD, (KeywordSearchParameter, 'keywords')),
        (SearchParameterType.FIELD, (FieldSearchParameter, 'fields')),
        (SearchParameterType.DISTILLERY, (DistilleryFilterParameter, 'distilleries')),
        (None, (UnknownParameter, 'unknown')),
    ])

    @staticmethod
    def _is_data_field_on_distillery(data_field, distillery):
        """Determines if a distillery contains the data_field

        Parameters
        ----------
        data_field : DataField
        distillery : Distillery
            Distillery to look for the DataField on.

        Returns
        -------
        bool
            If the Distillery contains the DataField
        """
        if not data_field:
            return False

        bottle_fields = distillery.container.bottle.fields

        if bottle_fields.filter(pk=data_field.pk).exists():
            return True

        if not distillery.container.label:
            return False

        label_fields = distillery.container.label.fields

        return label_fields.filter(pk=data_field.pk).exists()

    def __init__(self, query):
        """Constructor of a SearchQuery.

        Parameters
        ----------
        query : str
            Search query string
        """
        self.errors = []
        self.parameter_errors = []
        self.keywords = []
        self.fields = []
        self.distilleries = []
        self.unknown = []

        if not query:
            self.errors.append(SearchQuery.EMPTY_SEARCH_QUERY)
            return

        parameters = SearchQuery.PARAMETERS_REGEX.findall(query)

        if not parameters:
            self.errors.append(SearchQuery.PARSING_ERROR.format(query))
            return

        for index, parameter in enumerate(parameters):
            parameter_type = SearchParameterType.get_parameter_type(parameter)
            parameter_type_values = SearchQuery.PARAMETER_TYPE_VALUES_MAP[
                parameter_type
            ]

            self._add_search_parameter(
                index,
                parameter,
                parameter_type_values[0],
                parameter_type_values[1],
            )

        if len(self.distilleries) > 1:
            self.errors.append(SearchQuery.MULTPIPLE_DISTILLERY_FILTERS)

    def is_valid(self):
        """Determines if the SearchQuery is valid.

        Returns
        -------
        bool
        """
        return not self.errors and not self.parameter_errors

    def get_error_dict(self):
        """ Returns a dictionary explaining the query errors.

        Returns
        -------
        dict
        """
        errors = {}

        if self.errors:
            errors['query'] = self.errors

        if self.parameter_errors:
            errors['parameters'] = self.parameter_errors

        return errors

    def get_results(self):
        """Returns search results for each Distillery indexed by Distillery.

        Returns
        -------
        dict of list of dict

        Raises
        ------
        AssertionError
            If the SearchQuery is not valid.
        """
        assert self.is_valid(), 'Can only get results of a valid SearchQuery.'

        distilleries = (
            self.distilleries[0].distilleries
            if len(self.distilleries) is 1
            else Distillery.objects.all()
        )
        results = []

        for distillery in distilleries:
            fieldsets = self._get_fieldsets(distillery)

            if not fieldsets:
                continue

            engine_query = EngineQuery(subqueries=fieldsets, joiner='OR')
            query_results = distillery.find(engine_query)

            if query_results:
                results.append({
                    'count': query_results['count'],
                    'distillery': distillery.pk,
                    'results': query_results['results'],
                })

        return results

    def _get_field_fieldsets(self, distillery):
        """ Returns the field search fieldsets for a certain distillery.

        Parameters
        ----------
        distillery : Distillery

        Returns
        -------
        list of QueryFieldset
        """
        if not self.fields:
            return []

        return [
            parameter.create_fieldset()
            for parameter
            in self.fields
            if parameter.is_related_to_distillery(distillery)
        ]

    def _get_keyword_fieldsets(self, distillery):
        """Returns the keyword fieldsets for a certain distillery.

        Parameters
        ----------
        distillery : Distillery

        Returns
        -------
        list of QueryFieldset
        """
        if not self.keywords:
            return []

        keywords = [parameter.keyword for parameter in self.keywords]

        return [
            QueryFieldset(
                field_name=field.field_name,
                field_type=field.field_type,
                operator='regex',
                value='|'.join(keywords),
            )
            for field
            in distillery.get_text_fields()
        ]

    def _get_fieldsets(self, distillery):
        """Returns the QueryFieldsets for a particular distillery.

        Parameters
        ----------
        distillery : Distillery
            Distillery to get the fieldsets for.

        Returns
        -------
        list of QueryFieldsets
        """
        return (
            self._get_field_fieldsets(distillery) +
            self._get_keyword_fieldsets(distillery)
        )

    def _add_parameter_error(self, parameter):
        """Adds a SearchParameter error to the current list of errors.

        Parameters
        ----------
        parameter : SearchParameter
        """
        self.parameter_errors.append(parameter.get_parameter_info())

    def _add_search_parameter(
            self, index, parameter, search_parameter_class, field):
        """Adds a search parameter to the instance.

        Parameters
        ----------
        index : int
            Index of the search parameter on the search query string.
        parameter : str
            String representation of the search parameter.
        search_parameter_class : SearchParameter Class
            Class that will parse the search parameter information.
        field : str
            Attribute of the SearchQuery that will store the created
            SearchParameter instance.
        """
        search_parameter = search_parameter_class(index, parameter)

        if not search_parameter.is_valid():
            self._add_parameter_error(search_parameter)

        getattr(self, field).append(search_parameter)
