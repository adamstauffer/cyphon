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
Functional test case classes.
"""

# standard library
import logging
import unittest

# third party
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver import Firefox, Remote
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import WebDriverException

# local
from tests.pages.login import LoginPage
from tests.pages.configtool import ConfigToolPage
from tests.pages.modeladmin import ModelAdminPage
from tests.pages.preview import ModelPreviewPage

_TEST_SETTINGS = settings.FUNCTIONAL_TESTS
_SAUCE_SETTINGS = settings.SAUCELABS

_LOGGER = logging.getLogger(__name__)


def _get_desired_capabilities():
    """
    Return a dictionary of browser settings for a Selenium web driver.
    """
    platform = _TEST_SETTINGS['PLATFORM']
    browser = _TEST_SETTINGS['BROWSER']
    version = _TEST_SETTINGS['VERSION']

    if platform and browser and version:
        return {
            'platform': _TEST_SETTINGS['PLATFORM'],
            'browserName': _TEST_SETTINGS['BROWSER'],
            'version': _TEST_SETTINGS['VERSION'],
        }
    else:
        return DesiredCapabilities.FIREFOX


def _get_remote_driver():
    """
    Get a SauceLabs Selenium web driver.
    """
    username = _SAUCE_SETTINGS['USERNAME']
    access_key = _SAUCE_SETTINGS['ACCESS_KEY']
    url = 'ondemand.saucelabs.com:80/wd/hub'
    command = 'http://%s:%s@%s' % (username, access_key, url)
    desired_cap = _get_desired_capabilities()
    return Remote(
        command_executor=command,
        desired_capabilities=desired_cap
    )


def get_web_driver():
    """
    Get a Selenium web driver. Try to get a local driver first. If that
    fails, try to get a remote driver.
    """
    try:
        return Firefox()
    except (NameError, WebDriverException):
        return _get_remote_driver()


def _web_driver_available():
    """
    Return a Boolean indicating whether a Selenium web driver is
    available.
    """
    try:
        driver = get_web_driver()
        driver.quit()
        return True
    except WebDriverException:
        return False


def _enable_functional_tests():
    """
    Return a Boolean indicating whether functional tests should be run.
    """
    if _TEST_SETTINGS['ENABLED']:
        return _web_driver_available()
    return False


if not _enable_functional_tests():
    FUNCTIONAL_TESTS_ENABLED = False
    _LOGGER.warning('Functional tests are disabled, '
                    'so those tests will be skipped.')
else:
    FUNCTIONAL_TESTS_ENABLED = True


@unittest.skipUnless(FUNCTIONAL_TESTS_ENABLED, 'functional tests disabled')
class FunctionalTest(StaticLiveServerTestCase):
    """
    Base class for a functional test case.
    """

    def __init__(self, *args, **kwargs):
        super(FunctionalTest, self).__init__(*args, **kwargs)

    @classmethod
    def setUpClass(cls):
        super(FunctionalTest, cls).setUpClass()
        cls.driver = get_web_driver()
        cls.driver.implicitly_wait(1)
        cls.driver.maximize_window()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super(FunctionalTest, cls).tearDownClass()


class AdminFunctionalTest(FunctionalTest):
    """
    Base class for a functional test case for admin pages.
    """
    url = '/admin/'  # override in derived classes
    username = 'admin@example.com'
    password = 'Ic01nYL!WEc0&l*'

    def _create_superuser(self):
        """
        Helper method to create a superuser for test cases.
        """
        user_model = get_user_model()
        return user_model.objects.create_superuser(
            email=self.username,
            password=self.password
        )

    def setUp(self):
        self._create_superuser()
        self.driver.get(self.live_server_url + self.url)
        self.page = LoginPage(self.driver)
        self.page.login(self.username, self.password)


class ModelAdminFunctionalTest(AdminFunctionalTest):
    """
    Class for functional tests for a ModelAdmin page.
    """

    def setUp(self):
        super(ModelAdminFunctionalTest, self).setUp()
        self.page = ModelAdminPage(self.driver)


class ModelPreviewFunctionalTest(AdminFunctionalTest):
    """
    Class for functional tests for a ModelAdmin page with a preview field.
    """

    def setUp(self):
        super(ModelPreviewFunctionalTest, self).setUp()
        self.page = ModelPreviewPage(self.driver)


class ConfigToolFunctionalTest(AdminFunctionalTest):
    """
    Class for functional tests for a ModelAdmin page with a config
    test tool.
    """

    def setUp(self):
        super(ConfigToolFunctionalTest, self).setUp()
        self.page = ConfigToolPage(self.driver)
        self.page.open_tool()
