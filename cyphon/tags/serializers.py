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
Defines serializers for |Distilleries|.

====================================  ========================================
Class                                 Description
====================================  ========================================
:class:`~TagSerializer`               Serializer for |Tag| views.
:class:`~TopicSerializer`             Serializer for |Topic| views.
====================================  ========================================

"""

# third party
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType

# local
from articles.models import Article
from .models import Tag, Topic, TagRelation


class ArticleSerializer(serializers.ModelSerializer):
    """Serializer for a |Article| objects."""

    class Meta(object):
        """Metadata options."""

        model = Article
        fields = (
            'id',
            'title',
            'url',
        )


class TopicSerializer(serializers.ModelSerializer):
    """Serializer for |Topic| objects."""

    class Meta(object):
        """Metadata options."""

        model = Topic
        fields = (
            'id',
            'name',
            'url'
        )


class TagDetailSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for a |Tag| object."""

    topic = TopicSerializer()
    article = ArticleSerializer()

    class Meta(object):
        """Metadata options."""

        model = Tag
        fields = (
            'id',
            'name',
            'topic',
            'article',
        )


class TagListSerializer(serializers.ModelSerializer):
    """Serializer for a list of |Tag| objects."""

    topic = TopicSerializer()

    class Meta(object):
        """Metadata options."""

        model = Tag
        fields = (
            'id',
            'name',
            'topic',
        )


class TagRelationContentTypeField(serializers.ChoiceField):
    """Field type for |TagRelation| content_type field."""

    ALERT = 'alert'
    ANALYSIS = 'analysis'
    COMMENT = 'comment'
    CHOICES = (
        (ALERT, 'Alert'),
        (ANALYSIS, 'Analysis'),
        (COMMENT, 'Comment'),
    )

    def __init__(self):
        super().__init__(choices=self.CHOICES)

    def to_representation(self, value):
        return str(value)

    def to_internal_value(self, data):
        model = super().to_internal_value(data)

        return ContentType.objects.get(app_label='alerts', model=model)


class TagRelationSerializer(serializers.ModelSerializer):
    """Serializer for a list of |TagRelation| objects."""

    content_type = TagRelationContentTypeField()

    class Meta(object):
        """Metadata options."""

        model = TagRelation
        fields = (
            'id',
            'content_type',
            'object_id',
            'tag',
            'tag_date',
            'tagged_by',
        )
