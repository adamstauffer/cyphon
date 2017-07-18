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

# third party
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q

# local
from alerts.models import Alert
from alerts.serializers import AlertDetailSerializer
from distilleries.models import Distillery
from utils.dbutils.dbutils import join_query
from .search_results import SearchResults, DEFAULT_PAGE_SIZE

ALERT_SEARCH_VIEW_NAME = 'search_alerts'


class AlertSearchResults(SearchResults):
    """
    """
    VIEW_NAME = 'search_alerts'

    @staticmethod
    def _serialize_alert_object(alert, request):
        """Returns a JSON serializable representation of an Alert.

        Parameters
        ----------
        alert : Alert
            Alert object to serialize.
        request : django.http.HttpRequest
            Request from the view that wants the serializable data.

        Returns
        -------
        dict
        """
        return AlertDetailSerializer(alert, context={'request': request}).data

    @staticmethod
    def _get_alert_data_query(distillery, keywords):
        """Returns a Q object that searches an alert's JSON data for keywords.

        Parameters
        ----------
        distillery : Distillery
            Distillery that created an alert.
        keywords : list of str
            Keywords to search for in the alert data.

        Returns
        -------
        Q
        """
        text_fields = distillery.get_text_fields()
        field_names = [field.field_name for field in text_fields]
        field_keys = [name.replace('.', '__') for name in field_names]
        queries = []

        for key in field_keys:
            query_field = 'data__{}__icontains'.format(key)
            keyword_queries = [
                Q(**{query_field: keyword})
                for keyword
                in keywords
            ]
            queries.extend(keyword_queries)

        field_query = join_query(queries, 'OR')

        return Q(distillery=distillery) & field_query

    @staticmethod
    def _get_distilleries_with_alerts(user):
        """Returns the distilleries that created alerts.

        Parameters
        ----------
        user : appusers.models.AppUser
            User requesting the distillery list.

        Returns
        -------
        list of Distillery
        """
        return Distillery.objects.filter(
            alerts__in=Alert.objects.filter_by_user(user)
        ).distinct()

    @staticmethod
    def _create_data_query(user, keywords):
        """Creates a search query that searches the alert data for keywords.

        Parameters
        ----------
        user : appusers.models.AppUser
            User making the search request.
        keywords : list of str
            Keywords to search for.

        Returns
        -------
        Q
        """
        distilleries = AlertSearchResults._get_distilleries_with_alerts(user)

        if distilleries:
            data_queries = [
                AlertSearchResults._get_alert_data_query(distillery, keywords)
                for distillery in distilleries
            ]
            return join_query(data_queries, 'OR')

        return Q()

    @staticmethod
    def _create_title_queries(keywords):
        """Creates search queries that search alert titles for keywords.

        Parameters
        ----------
        keywords : list of str

        Returns
        -------
        list of Q
        """
        return [Q(title__icontains=keyword) for keyword in keywords]

    @staticmethod
    def _create_note_queries(keywords):
        """Creates search queries that search alert notes for keywords.

        Parameters
        ----------
        keywords : list of str

        Returns
        -------
        list of Q
        """
        return [Q(notes__icontains=keyword) for keyword in keywords]

    @staticmethod
    def _get_alert_comments_query(keywords):
        """Creates search queries that search alert comments for keywords.

        Parameters
        ----------
        keywords : list of str

        Returns
        -------
        list of Q
        """
        return [Q(comment__content__icontains=keyword) for keyword in keywords]

    @staticmethod
    def _get_alert_search_query(user, keywords):
        """Creates a search query that searches alerts for keywords.

        Parameters
        ----------
        user : appuser.models.AppUser
            User requesting the search query.
        keywords : list of str
            Keywords to search for.

        Returns
        -------
        Q
        """
        queries = []
        queries += [AlertSearchResults._create_data_query(user, keywords)]
        queries += AlertSearchResults._create_title_queries(keywords)
        queries += AlertSearchResults._create_note_queries(keywords)
        queries += AlertSearchResults._get_alert_comments_query(keywords)

        return join_query(queries, 'OR')

    @staticmethod
    def _get_alert_search_queryset(user, keywords):
        """Returns the queryset of alerts matching particular keywords.

        Parameters
        ----------
        user : appuser.models.AppUser
            User requesting the queryset.
        keywords : list of str
            Keywords to search for.

        Returns
        -------
        django.db.models.query.QuerySet
        """
        query = AlertSearchResults._get_alert_search_query(user, keywords)

        return Alert.objects.filter_by_user(user).filter(query)

    @staticmethod
    def _serialize_alert_queryset(queryset, request):
        """Creates a JSON serializable representation of the alert queryset.

        Parameters
        ----------
        queryset : django.db.models.query.QuerySet
            Alert queryset.
        request : django.http.HttpRequest
            Request from the view making the request.

        Returns
        -------
        list of dict
        """
        return [
            AlertSearchResults._serialize_alert_object(alert, request)
            for alert in queryset
        ]

    @staticmethod
    def _get_alert_results_page(queryset, page, page_size):
        paginator = Paginator(queryset, page_size)

        try:
            alerts = paginator.page(page)
        except EmptyPage:
            alerts = []

        return alerts

    def __init__(self, user, query, page=1, page_size=DEFAULT_PAGE_SIZE):
        """Finds alerts that match a SearchQuery.

        Parameters
        ----------
        user : appusers.models.AppUser
        query : query.search.search_query.SearchQuery
        """
        super(AlertSearchResults, self).__init__(
            self.VIEW_NAME, query, page, page_size,
        )
        self.results = []

        if query.keywords:
            queryset = self._get_alert_search_queryset(user, query.keywords)

            if queryset:
                self.results = self._get_alert_results_page(
                    queryset, page, page_size,
                )
                self.count = queryset.count()

    def as_dict(self, request):
        """Returns a JSON serializable representation of this object.

        Parameters
        ----------
        request : django.http.HttpRequest

        Returns
        -------
        dict
        """
        parent_dict = super(AlertSearchResults, self).as_dict(request)

        parent_dict['results'] = self._serialize_alert_queryset(
            self.results, request,
        )
        return parent_dict
