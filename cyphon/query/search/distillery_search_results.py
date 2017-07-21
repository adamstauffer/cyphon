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
from functools import reduce

# third party
from django.urls import reverse

# local
from cyphon.fieldsets import QueryFieldset
from distilleries.models import Distillery
from distilleries.serializers import DistilleryListSerializer
from engines.queries import EngineQuery
from .search_results import SearchResults, DEFAULT_PAGE_SIZE


class DistillerySearchResults(SearchResults):
    VIEW_NAME = 'search_distillery'
    @staticmethod
    def _serialize_distillery_object(distillery, request):
        """Returns a JSON serializable representation of a distillery object.

        Parameters
        ----------
        distillery : Distillery
            Distillery object to serialize.
        request : django.http.HttpRequest
            Request object from the view requesting the serialized object.

        Returns
        -------
        dict
        """
        return DistilleryListSerializer(
            distillery,
            context={'request': request}
        ).data

    @staticmethod
    def _get_field_fieldsets(distillery, field_parameters):
        """Returns QueryFieldsets of FieldSearchParameters based on Distillery.

        Parameters
        ----------
        distillery : Distillery
        field_parameters : list of query.search.field_search_parameter.FieldSearchParameter

        Returns
        -------
        list of QueryFieldset
        """
        if not field_parameters:
            return []

        return [
            parameter.create_fieldset() for parameter in field_parameters
            if parameter.is_related_to_distillery(distillery)
        ]

    @staticmethod
    def _create_keyword_fieldset(text_field, keywords):
        """Returns QueryFieldset of a DataField that takes keywords.

        Parameters
        ----------
        text_field : bottler.datafields.models.DataField
        keywords : list of str

        Returns
        -------
        QueryFieldset
        """
        return QueryFieldset(
            field_name=text_field.field_name,
            field_type=text_field.field_type,
            operator='regex',
            value='|'.join(keywords),
        )

    @staticmethod
    def _get_keyword_fieldsets(distillery, keywords):
        """Returns QueryFieldsets for all text fields of a distillery.

        Parameters
        ----------
        distillery : Distillery
            Distillery to get the text fields from.
        keywords : list of str
            Keywords to search for in the text fields.

        Returns
        -------
        list of QueryFieldset
        """
        if not keywords:
            return []

        text_fields = distillery.get_text_fields()

        return [
            DistillerySearchResults._create_keyword_fieldset(field, keywords)
            for field in text_fields
        ]

    @staticmethod
    def _get_fieldsets(distillery, query):
        """Returns QueryFieldsets of keyword and field searches for a distillery.

        Parameters
        ----------
        distillery : Distillery
        query: query.search.search_query.SearchQuery

        Returns
        -------
        list of QueryFieldset
        """
        fieldsets = []
        fieldsets += DistillerySearchResults._get_field_fieldsets(
            distillery, query.field_parameters,
        )
        fieldsets += DistillerySearchResults._get_keyword_fieldsets(
            distillery, query.keywords,
        )

        return fieldsets

    @staticmethod
    def _get_distillery(distillery):
        """

        Parameters
        ----------
        distillery : Distillery or int

        Returns
        -------
        Distillery or None
        """
        try:
            return Distillery.objects.get(pk=distillery)
        except Distillery.DoesNotExist:
            return None

    def __init__(self, query, distillery, page=1, page_size=DEFAULT_PAGE_SIZE):
        """Creates a DistillerySearchResults instance.

        Parameters
        ----------
        query: query.search.search_query.SearchQuery
        distillery : Distillery
        """
        super(DistillerySearchResults, self).__init__(
            self.VIEW_NAME, query, page, page_size,
        )
        self.results = []
        self.distillery = distillery
        self.fieldsets = []
        self.engine_query = None
        self.fieldsets = self._get_fieldsets(distillery, query)

        if not self.fieldsets:
            return

        self.engine_query = EngineQuery(subqueries=self.fieldsets, joiner='OR')

        results = self.distillery.find(
            self.engine_query, page=page, page_size=page_size,
        )

        if results and results['count']:
            self.count += results['count']
            self.results = results['results']

    def as_dict(self, request):
        """Returns a JSON serializable representation of this instance.

        Parameters
        ----------
        request : django.http.HttpRequest

        Returns
        -------
        dict
        """
        parent_dict = super(DistillerySearchResults, self).as_dict(request)

        parent_dict['results'] = self.results
        parent_dict['distillery'] = self._serialize_distillery_object(
            self.distillery, request,
        )

        return parent_dict

    def _get_path(self):
        return reverse(self.view_name, args=[self.distillery.pk])


class DistillerySearchResultsList:
    @staticmethod
    def _get_result_count(results):
        """Returns the result count of all DistillerySearchResults.

        Parameters
        ----------
        results : list of DistillerySearchResult

        Returns
        -------
        int
        """
        return reduce((lambda count, result: count + result.count), results, 0)

    @staticmethod
    def _get_distillery_search_results(distilleries, query, page, page_size):
        """

        Parameters
        ----------
        distilleries : list of Distillery
        query : query.search.search_query.SearchQuery

        Returns
        -------

        """
        if query.keywords or query.field_parameters:
            return [
                DistillerySearchResults(query, distillery, page, page_size)
                for distillery in distilleries
            ]

        return []

    def __init__(self, query, page=1, page_size=DEFAULT_PAGE_SIZE):
        """Creates a DistillerySearchResultsList instance.

        Parameters
        ----------
        query: query.search.search_query.SearchQuery
        """
        self.count = 0
        self.distilleries = (
            query.distilleries or Distillery.objects.all()
        )
        self.results = self._get_distillery_search_results(
            self.distilleries, query, page, page_size,
        )
        self.count = self._get_result_count(self.results)

    def as_dict(self, request):
        """
        Returns a JSON serializable representation of this instance.

        Parameters
        ----------
        request : rest_framework.request.Request

        Returns
        -------
        dict
        """
        return {
            'count': self.count,
            'results': self._get_results_as_dict(request)
        }

    def _get_results_as_dict(self, request):
        """
        Returns a JSON serializable representation of the
        related DistillerySearchResults

        Parameters
        ----------
        request : django.http.HttpRequest

        Returns
        -------
        list of dict
        """
        return [
            result.as_dict(request) for result in self.results
            if result.count
        ]

