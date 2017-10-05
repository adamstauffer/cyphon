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
from rest_framework.decorators import api_view
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.response import Response

# local
from distilleries.models import Distillery
from .search_query import SearchQuery
from .all_search_results import AllSearchResults
from .alert_search_results import AlertSearchResults
from .distillery_search_results import (
    DistillerySearchResultsList, DistillerySearchResults
)
from .search_parameter import SearchParameterType
from .search_results import DEFAULT_PAGE_SIZE

SEARCH_VIEW_NAME = 'search'
ALERT_SEARCH_VIEW_NAME = AlertSearchResults.VIEW_NAME
DISTILLERY_SEARCH_VIEW_NAME = DistillerySearchResults.VIEW_NAME
DISTILLERIES_SEARCH_VIEW_NAME = 'search_distilleries'


@api_view(['GET'])
def search(request):
    """View that searches both alerts and distilleries based on a search query.

    Parameters
    ----------
    request : rest_framework.request.Request

    Returns
    -------

    """
    query, page, page_size = _get_query_params(request.query_params)
    search_query = SearchQuery(query, request.user)
    response = _create_empty_response(search_query)

    if search_query.is_valid():
        search_results = AllSearchResults(
            search_query, page=page, page_size=page_size)
        response['results'] = search_results.as_dict(request)

        return Response(response)

    return Response(data=response, status=HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def search_alerts(request):
    """View that searches alerts based on a search query.

    Parameters
    ----------
    request : rest_framework.request.Request

    Returns
    -------
    Response
    """
    query, page, page_size = _get_query_params(request.query_params)
    search_query = SearchQuery(
        query, request.user,
        ignored_parameter_types=[SearchParameterType.FIELD],
    )
    response = _create_empty_response(search_query)

    if search_query.is_valid():
        search_results = AlertSearchResults(
            search_query, page=page, page_size=page_size)
        response['results'] = search_results.as_dict(request)

        return Response(response)

    return Response(data=response, status=HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def search_distilleries(request):
    """View that searches all distilleries based on a search query.

    Parameters
    ----------
    request : rest_framework.request.Request

    Returns
    -------
    Response
    """
    query, page, page_size = _get_query_params(request.query_params)
    search_query = SearchQuery(query, request.user)
    response = _create_empty_response(search_query)

    if search_query.is_valid():
        search_results = DistillerySearchResultsList(
            search_query, page=page, page_size=page_size,
        )
        response['results'] = search_results.as_dict(request)

        return Response(response)

    return Response(data=response, status=HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def search_distillery(request, pk):
    """View that searches a single distillery based on the search query.

    Parameters
    ----------
    request : rest_framework.request.Request
    pk: str
        Primary key of the distillery to search through.

    Returns
    -------
    Response
    """
    query, page, page_size = _get_query_params(request.query_params)
    search_query = SearchQuery(
        query, request.user,
        ignored_parameter_types=[SearchParameterType.DISTILLERY],
    )
    response = _create_empty_response(search_query)

    if search_query.is_valid():
        try:
            distillery = Distillery.objects.get(pk=int(pk))
        except Distillery.DoesNotExist:
            distillery = None

        if distillery:
            search_results = DistillerySearchResults(
                search_query, page=page, page_size=page_size,
                distillery=distillery,
            )
            response['results'] = search_results.as_dict(request)

        return Response(response)

    return Response(data=response, status=HTTP_400_BAD_REQUEST)


def _get_query_params(query_params):
    """Returns the GET parameters of a search view.

    Parameters
    ----------
    query_params : dict
        Dictionary of query parameters.

    Returns
    -------
    (str, int, int)
        The string query, page, and page size.
    """
    query = query_params.get('query', '')

    try:
        page = int(query_params.get('page', 1))
    except ValueError:
        page = 1

    try:
        page_size = int(query_params.get('page_size', DEFAULT_PAGE_SIZE))
    except ValueError:
        page_size = DEFAULT_PAGE_SIZE

    return query, page, page_size


def _create_empty_response(search_query):
    """Creates a search response without any results.

    Parameters
    ----------
    search_query : SearchQuery

    Returns
    -------
    dict
    """
    return {
        'query': search_query.as_dict(),
        'results': None,
    }
