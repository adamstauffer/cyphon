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
Defines classes for tagging objects.

======================  ================================================
Class                   Description
======================  ================================================
:class:`~Tag`           Term for describing objects.
:class:`~TagRelation`   Association between a |Tag| and an object.
======================  ================================================

"""

# third party
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models

# local
from taxonomies.models import Taxonomy, TaxonomyManager


class Tag(Taxonomy):
    """A term for describing objects.

    Attributes
    ----------
    name : |str|
        The name of the Tag.

    """

    objects = TaxonomyManager()

    class Meta(object):
        """Metadata options."""

        ordering = ['name']

    def __str__(self):
        return self.name

    def assign_tag(self, obj, user=None):
        """Associate a tag with an object.

        Parameters
        ----------
        obj : |Alert| or |Comment|
            The object to to be tagged.

        user : |AppUser|
            The user tagging the object.

        Returns
        -------
        |TagRelation|

        """
        model_type = ContentType.objects.get_for_model(obj)
        return TagRelation.objects.create(
            content_type=model_type,
            object_id=obj.id,
            tag=self,
            tagged_by=user
        )


class TagRelation(models.Model):
    """Association between a |Tag| and an object.

    Attributes
    ----------
    content_type : ContentType
        The |ContentType| of object that was tagged.

    object_id : int
        The id of the :attr:`~TagRelation.tagged_object`.

    tagged_object : `Alert` or `Comment`
        The object that was tagged, which can be an |Alert| or |Comment|.

    tag : Tag
        The |Tag| associated with the :attr:`~TagRelation.tagged_object`.

    tag_date : datetime
        The |datetime| when the TagRelation was created.

    tagged_by : AppUser
        The |AppUser| who created the TagRelation.

    """

    _ALERT = models.Q(app_label='alerts', model='alert')
    _COMMENT = models.Q(app_label='alerts', model='comment')
    _TAGGED = _ALERT | _COMMENT

    content_type = models.ForeignKey(
        ContentType,
        limit_choices_to=_TAGGED,
        blank=True,
        null=True,
        on_delete=models.PROTECT
    )
    object_id = models.PositiveIntegerField(blank=True, null=True)
    tagged_object = GenericForeignKey('content_type', 'object_id')
    tag = models.ForeignKey(Tag)
    tag_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    tagged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.PROTECT
    )

    class Meta(object):
        """Metadata options."""

        unique_together = ('content_type', 'object_id', 'tag')

    def __str__(self):
        return '%s <%s: %s>' % (self.tag, str(self.content_type).title(),
                                self.tagged_object)
