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
Defines views for |Distilleries| using the Django REST framework.

==============================  ===========================================
Class                           Description
==============================  ===========================================
:class:`~TagPagination`            Pagination for |Tag| views.
:class:`~TagViewSet`            `ReadOnlyModelViewSet`_ for |Tags|.
==============================  ===========================================

"""

# third party
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

# local
from .models import Tag
from .serializers import TagSerializer


class TagPagination(PageNumberPagination):
    """Pagination for |Tag| views.

    Paginates |Tags| using Django REST framework's
    `PageNumberPagination`_.
    """

    page_size = 50


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """REST API views for Tags."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = TagPagination
