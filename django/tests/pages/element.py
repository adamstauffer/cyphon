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
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

TIMEOUT = 1


class HtmlElement(object):
    """
    Base element class.
    """

    def __init__(self):
        self.timeout = TIMEOUT


class StyledElement(HtmlElement):
    """
    Represents an HTML element that is located by CSS selector.
    """

    def __get__(self, obj, owner):
        """
        Gets the text of the specified object.
        """
        driver = obj.driver
        WebDriverWait(driver, self.timeout).until(
            lambda driver: driver.find_element_by_css_selector(self.locator))
        element = driver.find_element_by_css_selector(self.locator)
        return element.get_attribute('innerHTML')


class NamedElement(HtmlElement):
    """
    Represents an HTML input element that is located by name.
    """

    def __get__(self, obj, owner):
        """
        Gets the text of the specified object.
        """
        driver = obj.driver
        WebDriverWait(driver, self.timeout).until(
            lambda driver: driver.find_element_by_name(self.locator))
        element = driver.find_element_by_name(self.locator)
        return element.get_attribute('value')


class TextInputElement(NamedElement):
    """
    Represents an HTML input element that is located by name.
    """

    def __set__(self, obj, value):
        """
        Sets the text to the value supplied.
        """
        driver = obj.driver
        WebDriverWait(driver, self.timeout).until(
            lambda driver: driver.find_element_by_name(self.locator))
        element = driver.find_element_by_name(self.locator)
        element.clear()
        element.send_keys(value)


class SelectElement(HtmlElement):
    """
    Represents an HTML select element that is located by name. Selections
    set and retrve

    """

    def __get__(self, obj, owner):
        """
        Gets the text of the specified object.
        """
        driver = obj.driver
        WebDriverWait(driver, self.timeout).until(
            lambda driver: driver.find_element_by_name(self.locator))
        element = driver.find_element_by_name(self.locator)
        select = Select(element)
        return select.first_selected_option.text

    def __set__(self, obj, value):
        """
        Sets the select element to the value supplied.
        """
        driver = obj.driver
        WebDriverWait(driver, self.timeout).until(
            lambda driver: driver.find_element_by_name(self.locator))
        element = driver.find_element_by_name(self.locator)
        for option in element.find_elements_by_tag_name('option'):
            if option.text == value:
                option.click()
                break


class LinkElement(HtmlElement):
    """
    Represents a link element that is located by ID.
    """

    def __get__(self, obj, owner):
        """
        Gets the text of the specified object.
        """
        driver = obj.driver
        WebDriverWait(driver, self.timeout).until(
            lambda driver: driver.find_element_by_id(self.locator))
        element = driver.find_element_by_id(self.locator)
        return element.get_attribute('href')


class AutocompleteElement(HtmlElement):
    """

    """
    def __init__(self, driver):
        super(AutocompleteElement, self).__init__()
        self.driver = driver
        self.path = '//span[@data-input-id="id_%s-autocomplete"]' % self.locator
        self.name = self.locator + '-autocomplete'

    def click(self):
        """

        """
        WebDriverWait(self.driver, self.timeout).until(
            lambda driver: driver.find_element_by_name(self.name))
        self.driver.find_element_by_name(self.name).click()

    def delete(self):
        """

        """
        btn_path = '//span[@id="id_%s-deck"]//span[@class="remove"]' \
                   % self.locator
        driver = self.driver
        WebDriverWait(driver, self.timeout).until(
            lambda driver: driver.find_element_by_xpath(btn_path))
        driver.find_element_by_xpath(btn_path).click()

    def _get_option(self, value):
        """

        """
        driver = self.driver
        option_path = '%s/span[@data-value="%s"]' % (self.path, value)
        WebDriverWait(driver, self.timeout).until(
            lambda driver: driver.find_element_by_xpath(option_path))
        return driver.find_element_by_xpath(option_path)

    def exists(self, value):
        """
        Takes an index of an inline form and the name of a target_field, and
        returns a Boolean indicating whether the option exists.
        """
        try:
            self._get_option(value)
            return True
        except NoSuchElementException:
            return False

    def select(self, value):
        """

        """
        self.click()
        time.sleep(0.5)
        option = self._get_option(value)
        option.click()

    def count(self):
        """

        """
        time.sleep(0.5)
        self.click()
        time.sleep(0.5) # wait for server response
        option_path = self.path + '/span[@data-value]'
        try:
            WebDriverWait(self.driver, self.timeout).until(
                lambda driver: driver.find_element_by_xpath(option_path))
            options = self.driver.find_elements_by_xpath(option_path)
            return len(options)
        except TimeoutException:
            return 0

    def get_value(self):
        """
        Gets the current value of the autocomplete.
        """
        WebDriverWait(self.driver, self.timeout).until(
            lambda driver: driver.find_element_by_name(self.locator))
        element = self.driver.find_element_by_name(self.locator)
        return element.get_attribute('value')

