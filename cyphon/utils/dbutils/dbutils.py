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
import json

# third party
from django.core.serializers.json import DjangoJSONEncoder


def count_by_group(queryset, column, options):
    """
    Takes a QuerySet, a column name, and an options list (tuple of 2-tuples).
    Returns a dictionary containing the number of records for each option.
    """
    counts = {}

    for option in options:
        value = option[0]
        kwargs = {column: value}
        counts[value] = queryset.filter(**kwargs).count()

    return {column: counts}


def json_encodeable(data):
    """

    """
    serialized_data = json.dumps(data, cls=DjangoJSONEncoder)
    return json.loads(serialized_data)


def join_query(queries, logic):
    """

    """
    assert logic in ['AND', 'OR']

    joined_query = queries.pop()

    if logic == 'OR':
        for query in queries:
            joined_query |= query

    elif logic == 'AND':
        for query in queries:
            joined_query &= query

    return joined_query
