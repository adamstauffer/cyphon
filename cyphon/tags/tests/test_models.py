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
Tests the Company class.
"""

# standard library
from django.test import TestCase

# local
from alerts.models import Alert
from tags.models import Tag, TagRelation
from tests.fixture_manager import get_fixtures


class TagTestCase(TestCase):
    """
    Base class for testing the Tag class.
    """
    fixtures = get_fixtures(['tags'])

    def test_str(self):
        """
        Tests the __str__ method.
        """
        tag = Tag.objects.get_by_natural_key('cat')
        self.assertEqual(str(tag), 'cat')

    def test_assign_tag(self):
        """
        Tests the assign_tag method.
        """
        tag = Tag.objects.get(pk=3)
        alert = Alert.objects.get(pk=1)
        tag_relation = tag.assign_tag(alert)
        self.assertEqual(tag_relation.tagged_object, alert)


class TagRelationTestCase(TestCase):
    """
    Base class for testing the TagRelation class.
    """
    fixtures = get_fixtures(['tags'])

    def test_str(self):
        """
        Tests the __str__ method.
        """
        tag_relation = TagRelation.objects.get(pk=1)
        self.assertEqual(str(tag_relation), 'cat <Alert: PK 1: Acme Supply Co>')
