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

# third party
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q

# local
from alerts.models import Alert
from alerts.serializers import AlertDetailSerializer
from distilleries.models import Distillery
from utils.dbutils.dbutils import join_query
from .search_results import DEFAULT_PAGE_SIZE, SearchResults

ALERT_SEARCH_VIEW_NAME = 'search_alerts'


class AlertSearchResults(SearchResults):
    """

    """
    VIEW_NAME = 'search_alerts'

    def __init__(self, query, page=1, page_size=DEFAULT_PAGE_SIZE):
        """Find alerts that match a SearchQuery.

        Parameters
        ----------
        query : query.search.search_query.SearchQuery

        """
        super(AlertSearchResults, self).__init__(
            self.VIEW_NAME, query, page, page_size,
        )
        self.results = []

        queryset = self._get_alert_search_queryset(query)

        if queryset:
            self.results = self._get_results_page(
                queryset, page, page_size,
            )
            self.count = queryset.count()

    @staticmethod
    def _serialize_alert_object(alert, request):
        """Return a JSON serializable representation of an Alert.

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
    def _create_keyword_data_query(keywords, distilleries):
        """Create a search query that searches the alert data for keywords.

        Parameters
        ----------
        keywords : list of str
            Keywords to search for.

        Returns
        -------
        Q

        """
        text_field_names = AlertSearchResults._get_shared_text_fields(
            distilleries)
        queries = []

        for field_name in text_field_names:
            underscored_field_name = field_name.replace('.', '__')
            query_field = 'data__{}__icontains'.format(underscored_field_name)
            queries.extend([
                Q(**{query_field: keyword})
                for keyword
                in keywords
            ])

        return join_query(queries, 'OR')

    @staticmethod
    def _create_title_queries(keywords):
        """Create search queries that search alert titles for keywords.

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
        """Create search queries that search alert notes for keywords.

        Parameters
        ----------
        keywords : list of str

        Returns
        -------
        list of Q

        """
        return [Q(analysis__notes__icontains=keyword) for keyword in keywords]

    @staticmethod
    def _get_alert_comments_query(keywords):
        """Create search queries that search alert comments for keywords.

        Parameters
        ----------
        keywords : list of str

        Returns
        -------
        list of Q

        """
        return [Q(comments__content__icontains=keyword) for keyword in keywords]

    @staticmethod
    def _get_keyword_search_query(keywords, distilleries):
        """Create a search query that searches alerts for keywords.

        Parameters
        ----------
        keywords : list of str
            Keywords to search for.

        distilleries: list of distilleries.models.Distillery

        Returns
        -------
        Q

        """
        queries = []
        queries += [
            AlertSearchResults._create_keyword_data_query(
                keywords, distilleries,
            )
        ]
        queries += AlertSearchResults._create_title_queries(keywords)
        queries += AlertSearchResults._create_note_queries(keywords)
        queries += AlertSearchResults._get_alert_comments_query(keywords)

        return join_query(queries, 'OR')

    @staticmethod
    def _get_shared_text_fields(distilleries):
        """

        Parameters
        ----------
        distilleries

        Returns
        -------

        """
        grouped_text_fields = [
            distillery.get_text_fields() for distillery in distilleries]
        text_fields = [
            text_field for grouped_text_field in grouped_text_fields
            for text_field in grouped_text_field]
        field_names = [field.field_name for field in text_fields]

        return list(set(field_names))

    @staticmethod
    def _get_alert_search_queryset(query):
        """Return the queryset of alerts matching particular keywords.

        Parameters
        ----------
        query : query.search.search_query.SearchQuery
            Keywords to search for.

        Returns
        -------
        django.db.models.query.QuerySet

        """

        if not query.keywords:
            return Alert.objects.none()

        alert_qs = Alert.objects.filter_by_user(query.user)

        distillery_qs = Distillery.objects.all()

        if not query.user.is_staff:
            distillery_qs = distillery_qs.filter(company=query.user.company)

        if query.distilleries.count():
            distillery_qs = query.distilleries

        keyword_query = AlertSearchResults._get_keyword_search_query(
            query.keywords,
            distillery_qs,
        )
        alert_qs = alert_qs.filter(keyword_query)
        alert_qs = alert_qs.filter(distillery__in=distillery_qs)

        return alert_qs

    @staticmethod
    def _serialize_alert_queryset(queryset, request):
        """Create a JSON serializable representation of the alert queryset.

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
    def _get_results_page(queryset, page, page_size):
        """

        """
        paginator = Paginator(queryset, page_size)

        try:
            return paginator.page(page)
        except EmptyPage:
            return []

    def as_dict(self, request):
        """Return a JSON serializable representation of this object.

        Parameters
        ----------
        request : :class:`~django.http.HttpRequest`

        Returns
        -------
        |dict|

        """
        parent_dict = super(AlertSearchResults, self).as_dict(request)

        parent_dict['results'] = self._serialize_alert_queryset(
            self.results, request,
        )
        return parent_dict
