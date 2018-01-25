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
Tests functions in the dbutils package.
"""

# standard library
from unittest import TestCase
try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

# local
from utils.dbutils import dbutils


class CountByGroupTestCase(TestCase):
    """
    Tests the count_by_group function.
    """

    @patch('django.db.models.query.QuerySet', autospec=True)
    def test_count_by_group(self, mock_queryset):
        """
        Tests the count_by_group function.
        """

        options = (
            ('high', 'High'),
            ('medium', 'Medium'),
            ('low', 'Low'),
        )

        # mock_queryset.count = Mock(return_value=3)
        mock_queryset.values = Mock(return_value=mock_queryset)
        mock_queryset.order_by = Mock(return_value=mock_queryset)
        mock_queryset.annotate = Mock(return_value=[Mock() for _ in range(3)])

        for i in range(3):
            mock_queryset.annotate.return_value[i].level = options[i][0]
            mock_queryset.annotate.return_value[i].level__count = 1

        actual = dbutils.count_by_group(mock_queryset, 'level', options)
        expected = {
            'level': {
                'high': 1,
                'medium': 1,
                'low': 1
            }
        }
        self.assertEqual(actual, expected)

        mock_queryset.annotate.return_value.clear()
        for value, _ in options:
            expected['level'][value] = 0
        actual = dbutils.count_by_group(mock_queryset, 'level', options)
        self.assertEqual(actual, expected)

