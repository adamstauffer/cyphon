# -*- coding: utf-8 -*-
# Copyright 2017-2018 Dunbar Security Solutions, Inc.
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
from django_filters import rest_framework as filters
from django.contrib.contenttypes.models import ContentType

# local
from .models import Tag, Topic, TagRelation
from .serializers import (
    TagDetailSerializer,
    TagListSerializer,
    TopicSerializer,
    TagRelationSerializer,
)


class TagPagination(PageNumberPagination):
    """Pagination for |Tag| views.

    Paginates |Tags| using Django REST framework's
    `PageNumberPagination`_.
    """

    page_size = 50


class TagViewSet(viewsets.ModelViewSet):
    """REST API views for Tags."""

    queryset = Tag.objects.all()
    serializer_class = TagDetailSerializer
    pagination_class = TagPagination

    def get_serializer_class(self):
        """
        Overrides the default method for returning the ViewSet's
        serializer.
        """
        if self.serializer_class is None:  # pragma: no cover
            msg = ("'%s' should either include a `serializer_class` attribute,"
                   " or override the `get_serializer_class()` method."
                   % type(self).__name__)
            raise RuntimeError(msg)

        if self.action is 'list':
            return TagListSerializer
        else:
            return self.serializer_class


class TagRelationFilter(filters.FilterSet):
    content_type = filters.ModelChoiceFilter(
        queryset=ContentType.objects.filter(app_label='alerts'),
        to_field_name='model')

    class Meta:
        model = TagRelation
        fields = ['content_type', 'object_id', 'tag']


class TagRelationViewSet(viewsets.ModelViewSet):
    """REST API views for TagRelations."""

    queryset = TagRelation.objects.all()
    serializer_class = TagRelationSerializer
    filter_class = TagRelationFilter


class TopicViewSet(viewsets.ModelViewSet):
    """REST API views for Tags."""

    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    pagination_class = TagPagination
