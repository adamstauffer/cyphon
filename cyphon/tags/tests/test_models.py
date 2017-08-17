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

# third party
from django.core.exceptions import ValidationError
from django.test import TestCase
import six
from testfixtures import LogCapture

# local
from alerts.models import Alert
from bottler.containers.models import Container
from tags.models import DataTagger, Tag, TagRelation
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


class DataTaggerTestCase(TestCase):
    """
    Base class for testing the DataTagger class.
    """
    fixtures = get_fixtures(['datataggers', 'tags'])

    def setUp(self):
        self.alert = Alert.objects.get(pk=2)
        self.container = Container.objects.get_by_natural_key('post')
        self.datatagger = DataTagger.objects.get(pk=1)


class CleanDataTaggerTestCase(DataTaggerTestCase):
    """
    Test cases for the clean method the DataTagger class.
    """

    def test_invalid_field_name(self):
        """
        Tests that a validation error is thrown for an invalid
        field_name value.
        """
        datatagger = DataTagger(
            container=self.container,
            field_name='foobar',
            exact_match=False,
            create_tags=False
        )
        msg = ('The given field name does not '
               'appear in the selected Container.')
        with six.assertRaisesRegex(self, ValidationError, msg):
            datatagger.clean()

    def test_invalid_create_tags(self):
        """
        Tests that a validation error is thrown for an invalid
        create_tags value.
        """
        datatagger = DataTagger(
            container=self.container,
            field_name='user.name',
            exact_match=False,
            create_tags=True
        )
        msg = ('The "create tags" feature is only '
               'available for exact matches.')
        with six.assertRaisesRegex(self, ValidationError, msg):
            datatagger.clean()


class GetValueTestCase(DataTaggerTestCase):
    """
    Test cases for the _get_value method the DataTagger class.
    """

    def test_string(self):
        """
        Tests that a lowercase string is returned if a value is found.
        """
        datatagger = DataTagger(
            container=self.container,
            field_name='content.text'
        )
        actual = datatagger._get_value(self.alert)
        expected = 'this is some text about cats.'
        self.assertEqual(actual, expected)

    def test_non_string(self):
        """
        Tests that None is returned if the field does not exist in the
        Alert data.
        """
        datatagger = DataTagger(
            container=self.container,
            field_name='foobar'
        )
        actual = datatagger._get_value(self.alert)
        expected = None
        self.assertEqual(actual, expected)


class CreateTagTestCase(DataTaggerTestCase):
    """
    Test cases for the _create_tag method the DataTagger class.
    """

    def test_duplicate(self):
        """
        Test case for when the Tag already exists.
        """
        Tag.objects.create(name='piedpiper')
        with LogCapture() as log_capture:
            self.datatagger._create_tag('piedpiper')
            log_capture.check(
                ('tags.models',
                 'ERROR',
                 'An error occurred while creating a new tag "piedpiper": '
                 'duplicate key value violates unique constraint '
                 '"tags_tag_name_key"\n'
                 'DETAIL:  Key (name)=(piedpiper) already exists.\n')
            )

    def test_new_tag(self):
        """
        Test case for when the Tag does not already exist.
        """
        self.assertFalse(Tag.objects.filter(name='piedpiper').exists())
        self.datatagger._create_tag('piedpiper')
        self.assertTrue(Tag.objects.filter(name='piedpiper').exists())


class GetTagTestCase(DataTaggerTestCase):
    """
    Test cases for the _get_tag method the DataTagger class.
    """

    def test_tag_exists(self):
        """
        Test case for when the Tag already exists.
        """
        actual = self.datatagger._get_tag('cat')
        expected = Tag.objects.get_by_natural_key('cat')
        self.assertEqual(actual, expected)

    def test_no_tag_create_tag_true(self):
        """
        Test case for when the Tag does not already exist and
        create_tags is True.
        """
        self.assertFalse(Tag.objects.filter(name='newtag').exists())
        actual = self.datatagger._get_tag('newtag')
        expected = Tag.objects.get_by_natural_key('newtag')
        self.assertEqual(actual, expected)

    def test_no_tag_create_tag_false(self):
        """
        Test case for when the Tag does not already exist and
        create_tags is False.
        """
        datatagger = DataTagger.objects.get(pk=2)
        actual = datatagger._get_tag('newtag')
        expected = None
        self.assertEqual(actual, expected)
        self.assertFalse(Tag.objects.filter(name='newtag').exists())


class GetTokensTestCase(DataTaggerTestCase):
    """
    Test cases for the _get_tokens method the DataTagger class.
    """

    def test_get_tokens(self):
        """
        Tests that strings with plural words generate tokens that
        include the singular form.
        """
        text = 'this is some text about wild cats.'
        tokens = self.datatagger._get_tokens(text)
        self.assertTrue('cat' in tokens)
        self.assertTrue('cats' in tokens)


class TagExactMatchTestCase(DataTaggerTestCase):
    """
    Test cases for the _tag_exact_match method the DataTagger class.
    """

    def test_tag_exists(self):
        """
        Test case for when an appropriate Tag exists or is created.
        """
        self.assertFalse(Tag.objects.filter(name='piedpiper').exists())
        self.datatagger._tag_exact_match(self.alert, 'piedpiper')
        actual = self.alert.associated_tags[0]
        expected = Tag.objects.get(name='piedpiper')
        self.assertEqual(actual, expected)

    def test_tag_does_not_exist(self):
        """
        Test case for when an appropriate Tag does not exist.
        """
        self.datatagger.create_tags = False
        self.datatagger._tag_exact_match(self.alert, 'piedpiper')
        self.assertEqual(len(self.alert.associated_tags), 0)
        self.assertFalse(Tag.objects.filter(name='pied piper').exists())


class TagPartialMatchTestCase(DataTaggerTestCase):
    """
    Test cases for the _tag_partial_match method the DataTagger class.
    """

    def test_single_token_tag(self):
        """
        Test case for Tags containing a single token.
        """
        datatagger = DataTagger.objects.get(pk=3)
        self.datatagger._tag_partial_match(self.alert,
                                           'this is some text about wild cats.')
        actual = self.alert.associated_tags[0]
        expected = Tag.objects.get(name='cat')
        self.assertEqual(actual, expected)

    def test_multi_token_tag(self):
        """
        Test case for Tags containing omultiple tokens.
        """
        pass

    def test_no_tags(self):
        """
        Test case when teh string matches no Tags.
        """
        pass


class ProcessTestCase(DataTaggerTestCase):
    """
    Test cases for the process method the DataTagger class.
    """

    def test_exact_match_true(self):
        """
        Test case for when exact_match is True.
        """
        pass

    def test_exact_match_false(self):
        """
        Test case for when exact_match is False.
        """
        pass
