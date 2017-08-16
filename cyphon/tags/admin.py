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
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

# local
from tags.models import TagRelation
from taxonomies.admin import TaxonomyAdmin
from .forms import TagForm
from .models import Tag


@admin.register(Tag)
class TagAdmin(TaxonomyAdmin):
    """
    Customizes inline admin forms for |Tags|.
    """

    form = TagForm


class TagRelationInlineAdmin(GenericTabularInline):
    """
    Customizes inline admin forms for |TagRelations|.
    """

    model = TagRelation
    fields = (
        'tag',
    )
    extra = 1


@admin.register(TagRelation)
class TagRelationAdmin(admin.ModelAdmin):
    """Customizes admin pages for |TagRelations|."""

    list_display = [
        'tagged_object',
        'content_type',
        'tag',
        'tagged_by',
        'tag_date',
    ]
    list_display_links = ['tagged_object', ]
    related_lookup_fields = {
        'generic': [['content_type', 'object_id'], ],
    }
    readonly_fields = ['tagged_by', 'tag_date']
