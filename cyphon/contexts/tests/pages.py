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
from selenium.webdriver.common.by import By

# local
from tests.pages.element import (
    AutocompleteElement,
    SelectElement,
    TextInputElement,
)
from tests.pages.modeladmin import ModelAdminPage


class ContextField(SelectElement):
    locator = 'context'

class SearchField(AutocompleteElement):
    locator = 'search_field'

class OperatorField(AutocompleteElement):
    locator = 'operator'

class ValueField(AutocompleteElement):
    locator = 'value_field'


class ContextFilterPage(ModelAdminPage):
    """
    Page class for a ContextFilter admin page.
    """
    context = ContextField()

    def __init__(self, *args, **kwargs):
        super(ContextFilterPage, self).__init__(*args, **kwargs)
        self.search_field = SearchField(self.driver)
        self.operator = OperatorField(self.driver)
        self.value_field = ValueField(self.driver)


class NameField(TextInputElement):
    locator = 'name'

class FocalDistilleryField(SelectElement):
    locator = 'primary_distillery'

class RelatedDistilleryField(SelectElement):
    locator = 'related_distillery'


class InlineSearchField(AutocompleteElement):
    """
    A search_field field for an inline ContextFilter.
    """
    def __init__(self, driver, index):
        self.locator = 'filters-%s-search_field' % index
        super(InlineSearchField, self).__init__(driver)


class InlineOperatorField(AutocompleteElement):
    """
    An operator field for an inline ContextFilter.
    """

    def __init__(self, driver, index):
        self.locator = 'filters-%s-operator' % index
        super(InlineOperatorField, self).__init__(driver)


class InlineValueField(AutocompleteElement):
    """
    A value_field field for an inline ContextFilter.
    """

    def __init__(self, driver, index):
        self.locator = 'filters-%s-value_field' % index
        super(InlineValueField, self).__init__(driver)


class ContextPageLocators(object):
    """
    A base class for page locators.
    """
    ADD_FILTER = (By.CSS_SELECTOR, '.grp-add-handler')
    REMOVE_FILTER = (By.CSS_SELECTOR, '.grp-remove-handler')
    DELETE_FILTER_0 = (By.CSS_SELECTOR, '#filters0 .grp-delete-handler')


class ContextPage(ModelAdminPage):
    """
    Page class for a Context admin page.
    """
    name = NameField()
    primary_distillery = FocalDistilleryField()
    related_distillery = RelatedDistilleryField()

    def __init__(self, driver):
        super(ContextPage, self).__init__(driver)
        self.search_field_0 = InlineSearchField(self.driver, index=0)
        self.operator_0 = InlineOperatorField(self.driver, index=0)
        self.value_field_0 = InlineValueField(self.driver, index=0)

        self.search_field_1 = InlineSearchField(self.driver, index=1)
        self.operator_1 = InlineOperatorField(self.driver, index=1)
        self.value_field_1 = InlineValueField(self.driver, index=1)

    def add_filter(self):
        """
        Clicks the 'add filter' button.
        """
        element = self.driver.find_element(*ContextPageLocators.ADD_FILTER)
        element.click()

    def remove_fitting(self):
        """
        Clicks the 'remove filter' button.
        """
        element = self.driver.find_element(*ContextPageLocators.REMOVE_FILTER)
        element.click()

    def delete_fitting(self):
        """
        Deletes the first inline filter.
        """
        element = self.driver.find_element(*ContextPageLocators.DELETE_FILTER_0)
        element.click()

