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
    LinkElement,
    TextInputElement,
)
from tests.pages.modeladmin import ModelAdminPage
from tests.pages.configtool import ConfigToolPage
from tests.pages.generic import GenericRelationMixin


class CondenserField(SelectElement):
    locator = 'condenser'

class TargetField(AutocompleteElement):
    locator = 'target_field'


class FittingPage(ModelAdminPage, GenericRelationMixin):
    """
    Page class for a Fitting admin page.
    """
    condenser = CondenserField()

    def __init__(self, *args, **kwargs):
        super(FittingPage, self).__init__(*args, **kwargs)
        self.target_field = TargetField(self.driver)


class NameField(TextInputElement):
    locator = 'name'

class BottleField(SelectElement):
    locator = 'bottle'


class InlineTargetField(AutocompleteElement):
    """
    An target_field for an inline Fitting.
    """

    def __init__(self, driver, index):
        self.locator = 'fittings-%s-target_field' % index
        super(InlineTargetField, self).__init__(driver)


class InlineContentTypeField(SelectElement):
    """
    A content_type for an inline Fitting.
    """

    def __init__(self, index):
        super(InlineContentTypeField, self).__init__()
        self.locator = 'fittings-%s-content_type' % index


class InlineObjectIdField(TextInputElement):
    """
    An object_id for an inline Fitting.
    """

    def __init__(self, index):
        super(InlineObjectIdField, self).__init__()
        self.locator = 'fittings-%s-object_id' % index


class InlineLookupField(LinkElement):
    """
    A lookup link for an inline Fitting.
    """

    def __init__(self, index):
        super(InlineLookupField, self).__init__()
        self.locator = 'lookup_id_fittings-%s-object_id' % index


class CondenserPageLocators(object):
    """
    A base class for page locators.
    """
    ADD_FITTING = (By.CSS_SELECTOR, '.grp-add-handler')
    REMOVE_FITTING = (By.CSS_SELECTOR, '.grp-remove-handler')
    DELETE_FITTING_0 = (By.CSS_SELECTOR, '#fittings0 .grp-delete-handler')


class CondenserPage(ConfigToolPage):
    """
    Page class for a Condenser admin page.
    """
    name = NameField()
    bottle = BottleField()

    content_type_0 = InlineContentTypeField(index=0)
    object_id_0 = InlineObjectIdField(index=0)
    lookup_0 = InlineLookupField(index=0)

    content_type_1 = InlineContentTypeField(index=1)
    object_id_1 = InlineObjectIdField(index=1)
    lookup_1 = InlineLookupField(index=0)

    def __init__(self, driver):
        super(CondenserPage, self).__init__(driver)
        self.target_field_0 = InlineTargetField(self.driver, index=0)
        self.target_field_1 = InlineTargetField(self.driver, index=1)

    def add_fitting(self):
        """
        Clicks the 'add fitting' button.
        """
        element = self.driver.find_element(*CondenserPageLocators.ADD_FITTING)
        element.click()

    def remove_fitting(self):
        """
        Clicks the 'remove fitting' button.
        """
        self.scroll_to_bottom()
        element = self.driver.find_element(*CondenserPageLocators.REMOVE_FITTING)
        element.click()

    def delete_fitting(self):
        """
        Deletes the first inline fitting.
        """
        element = self.driver.find_element(*CondenserPageLocators.DELETE_FITTING_0)
        element.click()
