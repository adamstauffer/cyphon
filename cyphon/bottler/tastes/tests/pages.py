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

# local
from tests.pages.element import AutocompleteElement, SelectElement
from tests.pages.modeladmin import ModelAdminPage


class BottleField(SelectElement):
    locator = 'bottle'

class LabelField(SelectElement):
    locator = 'label'

class ContainerField(SelectElement):
    locator = 'container'

class LocationField(AutocompleteElement):
    locator = 'location'

class ContentField(AutocompleteElement):
    locator = 'content'

class TitleField(AutocompleteElement):
    locator = 'title'

class AuthorField(AutocompleteElement):
    locator = 'author'

class DateField(AutocompleteElement):
    locator = 'datetime'


class TastePage(ModelAdminPage):
    """
    Page class for a Taste admin page.
    """
    container = ContainerField()

    def __init__(self, *args, **kwargs):
        """

        """
        super(TastePage, self).__init__(*args, **kwargs)
        self.datetime = DateField(self.driver)
        self.location = LocationField(self.driver)
        self.content = ContentField(self.driver)
        self.title = TitleField(self.driver)
        self.author = AuthorField(self.driver)


class InlineLocationField(AutocompleteElement):
    locator = 'taste-0-location'

class InlineContentField(AutocompleteElement):
    locator = 'taste-0-content'

class InlineTitleField(AutocompleteElement):
    locator = 'taste-0-title'

class InlineAuthorField(AutocompleteElement):
    locator = 'taste-0-author'

class InlineDateField(AutocompleteElement):
    locator = 'taste-0-datetime'


class InlineTastePage(ModelAdminPage):
    """
    Page class for a Fitting admin page.
    """
    bottle = BottleField()
    label = LabelField()

    def __init__(self, *args, **kwargs):
        """

        """
        super(InlineTastePage, self).__init__(*args, **kwargs)
        self.datetime = InlineDateField(self.driver)
        self.location = InlineLocationField(self.driver)
        self.content = InlineContentField(self.driver)
        self.title = InlineTitleField(self.driver)
        self.author = InlineAuthorField(self.driver)

