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

from .parameter import SearchQueryParameter
from .parameter_type import SearchQueryParameterType
from cyphon.choices import TEXT_FIELDS
from cyphon.fieldsets import QueryFieldset
from distilleries.models import Distillery
from engines.queries import EngineQuery

class SearchQuery:
    """List of SearchQueryParameters used to search collections.

    Parses a string into a list of SearchQueryParameters that contain
    information used to search data collections.

    Attributes
    ----------
    parameters : list of SearchQueryParameter
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
            SearchQueryParameter(index, parameter)
            for index, parameter
            in enumerate(re.findall(SearchQuery.PARAMETERS_REGEX, query))
        ]

    @staticmethod
    def _create_parameter_error(parameter):
        """Creates a dictionary that explains a parameter's errors.

        Parameters
        ----------
        parameter : SearchQueryParameter
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

    @staticmethod
    def _get_errors(parameters):
        """Creates a dictionary explaining the search query's errors.

        Parameters
        ----------
        parameters : list of SearchQueryParameter
            SearchQueryParameter instances that may have errors.

        Returns
        -------
        dict
            Dictionary containing the overall query errors and the
            individual parameter errors.
        """
        collection_parameter_count = 0
        parameter_errors = []
        query_errors = []
        errors = {}

        if not parameters:
            errors['query'] = ['Search query is empty.']
            return errors

        for parameter in parameters:
            if not parameter.is_valid():
                parameter_errors += SearchQuery._create_parameter_error(
                    parameter
                )
            if parameter.type is SearchQueryParameterType.DISTILLERY:
                collection_parameter_count += 1

        if collection_parameter_count > 1:
            query_errors.append(SearchQuery.MULTPIPLE_DISTILLERY_PARAMETERS)

        if parameter_errors:
            errors['parameters'] = parameter_errors

        if query_errors:
            errors['query'] = query_errors

        return errors

    @staticmethod
    def _is_field_on_distillery(distillery, field_id):
        if distillery.container.bottle.fields.all().exists(pk=field_id):
            return True
        if distillery.container.label.fields.all().exists(pk=field_id):
            return True

        return False

    @staticmethod
    def _sort_parameters_by_type(parameters):
        """Sorts SearchQueryParameters by their type.

        Parameters
        ----------
        parameters : list of SearchQueryParameter

        Returns
        -------
        dict of SearchQueryParameter
        """
        sorted_parameters = {}

        for parameter in parameters:
            if sorted_parameters[parameter.type]:
                sorted_parameters[parameter.type].append(parameter)
            else:
                sorted_parameters[parameter.type] = [parameter]

        return sorted_parameters

    @staticmethod
    def _get_keyword_fieldsets(distillery, keywords):
        """

        Parameters
        ----------
        distillery : Distillery
        keywords : SearchQueryParameterKeywordValue

        Returns
        -------

        """
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
        fields : SearchQueryParameterFieldValue

        Returns
        -------

        """
        return ([
            QueryFieldset(
                field_name=field.name,
                field_type=field.type,
                operator=field.operator,
                value=field.value
            )
            for field
            in fields
            if SearchQuery._is_field_on_distillery(distillery, field.pk)
        ])

    @staticmethod
    def _get_fieldsets(distillery, fields, keywords):
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
        self.errors = SearchQuery._get_errors(self.parameters)

    def is_valid(self):
        """Determines if the SearchQuery is valid.

        Returns
        -------
        bool
            If the SearchQuery is valid.
        """
        return not bool(self.errors)

    def get_results(self):
        assert self.is_valid(), (
            'Can only call `.get_results()` on a valid query.'
        )

        distilleries = Distillery.objects.all()
        results = {}
        sorted_parameters = SearchQuery._sort_parameters_by_type(
            self.parameters
        )

        for distillery in distilleries:
            fieldsets = SearchQuery._get_fieldsets(
                distillery,
                sorted_parameters[SearchQueryParameterType.FIELD] or [],
                sorted_parameters[SearchQueryParameterType.KEYWORD] or []
            )

            engine_query = EngineQuery(subqueries=fieldsets, joiner='OR')
            results[distillery.id] = distillery.find(engine_query)

        return results
