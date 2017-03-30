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
import time

# third party
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

# local
from cyphon.forms import CONFIG_TEST_VALUE_FIELD, CONFIG_TEST_RESULT_FIELD
from .element import TextInputElement
from .modeladmin import ModelAdminPage


class ConfigToolLocators(object):
    """
    Page class for a ConfigToolAdmin page.
    """
    CONFIG_TOOL = (By.CSS_SELECTOR, '.config-tool')
    RUN_TEST_BUTTON = (By.NAME, '_test')


class ConfigTestStringField(TextInputElement):
    """
    A username input field.
    """
    locator = CONFIG_TEST_VALUE_FIELD


class ConfigTestResultField(TextInputElement):
    """
    A password input field.
    """
    locator = CONFIG_TEST_RESULT_FIELD


class ConfigToolPage(ModelAdminPage):
    """
    Mixin class for a ConfigToolAdmin page.
    """
    config_test_value = ConfigTestStringField()
    config_test_result = ConfigTestResultField()

    def open_tool(self):
        """
        Opens the config test panel.
        """
        element = self.driver.find_element(*ConfigToolLocators.CONFIG_TOOL)
        element.click()

    def run_test(self):
        """
        Clicks the "run test" button and returns the test result.
        """
        element = self.driver.find_element(*ConfigToolLocators.RUN_TEST_BUTTON)
        element.click()
        time.sleep(0.5)  # wait for server response

        driver = self.driver
        WebDriverWait(driver, self.timeout).until(
            lambda driver: self.config_test_result)
        return self.config_test_result

