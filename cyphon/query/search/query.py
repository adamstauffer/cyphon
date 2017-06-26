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
from .parameter import SearchParameter
from .parameter_type import SearchParameterType
from .parameter_value import (
    KeywordValue,
    FieldValue,
)
from cyphon.fieldsets import QueryFieldset
from distilleries.models import Distillery
from engines.queries import EngineQuery


class SearchQueryErrors:
    EMPTY_SEARCH_QUERY = 'Search query is empty.'

    MULTPIPLE_DISTILLERY_PARAMETERS = (
        'There can only be one instance of the `source=` parameter.'
    )
    """str

    Error message explaining that there can only be one
    SearchQueryParameter that has the SearchQueryParameterType.DISTILLERY
    type.
    """

    @staticmethod
    def _create_parameter_error_dict(parameter):
        """Creates a dictionary that explains a parameter's errors.

        Parameters
        ----------
        parameter : SearchParameter
            Parameter that contains errors.

        Returns
        -------
        dict
            Dictionary containing the original parameter, the index location
            of the parameter in the search query, the parameters type,
            and the list of errors associated with the parameter.
        """
        return {
            'parameter': parameter.parameter,
            'type': parameter.type,
            'index': parameter.index,
            'errors': parameter.errors,
        }

    def __init__(self, parameters):
        self.query = []
        self.parameters = []
        self._get_errors(parameters)

    def has_errors(self):
        return bool(self.query) or bool(self.parameters)

    def as_dict(self):
        """Creates a dictionary object based on the query parameters.

        Returns
        -------
        dict
        """
        errors = {}

        if self.query:
            errors['query'] = self.query

        if self.parameters:
            errors['parameters'] = ([
                SearchQueryErrors._create_parameter_error_dict(parameter)
                for parameter
                in self.parameters
            ])

        return errors

    def _get_errors(self, parameters):
        """Creates a dictionary explaining the search query's errors.

        Parameters
        ----------
        parameters : list of SearchParameter
            SearchQueryParameter instances that may have errors.
        """
        collection_parameter_count = 0

        if not parameters:
            self.query.append(SearchQueryErrors.EMPTY_SEARCH_QUERY)
            return

        for parameter in parameters:
            if not parameter.is_valid():
                self.parameters.append(parameter)
            if parameter.type is SearchParameterType.DISTILLERY:
                collection_parameter_count += 1

        if collection_parameter_count > 1:
            self.query.append(SearchQuery.MULTPIPLE_DISTILLERY_PARAMETERS)


class SearchQuery:
    """List of SearchQueryParameters used to search collections.

    Parses a string into a list of SearchQueryParameters that contain
    information used to search data collections.

    Attributes
    ----------
    parameters : list of SearchParameter
        Parsed parameter strings of the search query.
    """

    PARAMETERS_REGEX = re.compile(
        r'\"(?:\"|\S.+?\")(?=\ |$)|\S+\"(?:\"|\S.+?\")|\S+'
    )
    """RegExp

    Regular expression object used to parse parameters from a search
    query string.
    """

    MULTPIPLE_DISTILLERY_PARAMETERS = (
        'There can only be one instance of the `source=` parameter.'
    )
    """str

    Error message explaining that there can only be one
    SearchQueryParameter that has the SearchQueryParameterType.DISTILLERY
    type.
    """

    @staticmethod
    def _get_parameters(query):
        """Parses a string query into it's individual parameters.

        Parameters
        ----------
        query : str
            Query string to parse.

        Returns
        -------
        |list| of |SearchQueryParameter|
            List of parsed search parameters separated by their field name,
            operator, and value.
        """
        return [
            SearchParameter(index, parameter)
            for index, parameter
            in enumerate(re.findall(SearchQuery.PARAMETERS_REGEX, query))
            ]

    @staticmethod
    def _is_field_on_distillery(distillery, field_id):
        """Determines if a DataField is on a distillery.

        Parameters
        ----------
        distillery : Distillery
            Distillery to look for the DataField on.
        field_id : int
            ID of the DataField.

        Returns
        -------
        bool
            If the Distillery contains the DataField
        """
        bottle = distillery.container.bottle
        label = distillery.container.label

        if bottle.fields.all().exists(pk=field_id):
            return True
        if label and label.fields.all().exists(pk=field_id):
            return True

        return False

    @staticmethod
    def _sort_parameters_by_type(parameters):
        """Sorts SearchQueryParameters by their type.

        Parameters
        ----------
        parameters : list of SearchParameter
            Parameters to sort.

        Returns
        -------
        dict of SearchQueryParameter
            SearchQueryParameters indexed by their type property.
        """
        sorted_parameters = {}

        for parameter in parameters:
            if sorted_parameters[parameter.type]:
                sorted_parameters[parameter.type].append(parameter)
            else:
                sorted_parameters[parameter.type] = [parameter]

        return sorted_parameters

    @staticmethod
    def _get_keyword_fieldsets(distillery, parameter_values):
        """Creates QueryFieldsets from

        Parameters
        ----------
        distillery : Distillery
        parameter_values : list of KeywordValue

        Returns
        -------

        """
        keywords = ([
            parameter_value.keyword
            for parameter_value
            in parameter_values
        ])

        return ([
            QueryFieldset(
                field_name=field.field_name,
                field_type=field.field_type,
                operator='regex',
                value='|'.join(keywords)
            )
            for field
            in distillery.get_text_fields()
        ])

    @staticmethod
    def _get_field_fieldsets(distillery, fields):
        """

        Parameters
        ----------
        distillery : Distillery
        fields : list of FieldValue

        Returns
        -------

        """
        return ([
            QueryFieldset(
                field_name=field.field_name,
                field_type=field.field_type,
                operator=field.operator,
                value=field.value
            )
            for field
            in fields
            if SearchQuery._is_field_on_distillery(distillery, field.field_pk)
        ])

    @staticmethod
    def _get_fieldsets(distillery, fields, keywords):
        """Creates a list of QueryFieldsets based on a Distillery.

        Parameters
        ----------
        distillery : Distillery
        fields : list of SearchQueryFieldParameterValue
        keywords : list of KeywordValue

        Returns
        -------
        list of QueryFieldset
        """
        fieldsets = []

        if keywords:
            fieldsets += SearchQuery._get_keyword_fieldsets(
                distillery,
                keywords
            )

        if fields:
            fieldsets += SearchQuery._get_field_fieldsets(distillery, fields)

        return fieldsets

    def __init__(self, query):
        """Constructor of a SearchQuery.

        Parameters
        ----------
        query : str
            Search query string
        """
        self.parameters = SearchQuery._get_parameters(query)
        self._errors = SearchQueryErrors(self.parameters)

    def is_valid(self):
        """Determines if the SearchQuery is valid.

        Returns
        -------
        bool
            If the SearchQuery is valid.
        """
        return not self._errors.has_errors()

    @property
    def errors(self):
        return self._errors.as_dict()

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

        distilleries = Distillery.objects.all()
        results = {}
        sorted_parameters = SearchQuery._sort_parameters_by_type(
            self.parameters
        )

        for distillery in distilleries:
            fieldsets = SearchQuery._get_fieldsets(
                distillery,
                sorted_parameters[SearchParameterType.FIELD] or [],
                sorted_parameters[SearchParameterType.KEYWORD] or []
            )

            engine_query = EngineQuery(subqueries=fieldsets, joiner='OR')
            results[distillery.id] = distillery.find(engine_query)

        return results
