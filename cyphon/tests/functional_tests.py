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
import os
import unittest

# third party
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver import Chrome, Firefox, Remote
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


def _add_travis_info(capabilities):
    """

    """
    capabilities['tunnel-identifier'] = os.getenv('TRAVIS_JOB_NUMBER')
    capabilities['build'] = os.getenv('TRAVIS_BUILD_NUMBER')
    capabilities['tags'] = [os.getenv('TRAVIS_PYTHON_VERSION'), 'CI']
    return capabilities


def _get_desired_capabilities():
    """
    Return a dictionary of browser settings for a Selenium web driver.
    """
    platform = _TEST_SETTINGS['PLATFORM']
    browser = _TEST_SETTINGS['BROWSER']
    version = _TEST_SETTINGS['VERSION']

    if platform and browser and version:
        capabilities = {
            'platform': _TEST_SETTINGS['PLATFORM'],
            'browserName': _TEST_SETTINGS['BROWSER'],
            'version': _TEST_SETTINGS['VERSION'],
        }
    elif browser.lower() == 'firefox':
        capabilities = DesiredCapabilities.FIREFOX
    else:
        capabilities = DesiredCapabilities.CHROME

    return _add_travis_info(capabilities)


def _get_remote_driver(capabilities):
    """
    Get a Docker Selenium web driver.
    """
    host = _TEST_SETTINGS['HOST']
    port = _TEST_SETTINGS['PORT']
    url = 'http://%s:%s/wd/hub' % (host, port)
    return Remote(
        command_executor=url,
        desired_capabilities=capabilities
    )


def _get_saucelabs_driver(capabilities):
    """
    Get a SauceLabs Selenium web driver.
    """
    username = _SAUCE_SETTINGS['USERNAME']
    access_key = _SAUCE_SETTINGS['ACCESS_KEY']
    hub_url = '%s:%s@localhost:4445' % (username, access_key)
    return Remote(
        command_executor='http://%s/wd/hub' % hub_url,
        desired_capabilities=capabilities
    )


def _get_local_driver(browser):
    """
    Get a local Selenium web driver.
    """
    if browser.lower() == 'firefox':
        return Firefox()
    else:
        return Chrome()


def get_web_driver():
    """
    Get a Selenium web driver. Try to get a local driver first. If that
    fails, try to get a remote driver.
    """
    driver = _TEST_SETTINGS['DRIVER'].lower()
    capabilities = _get_desired_capabilities()

    if driver == 'docker':
        return _get_remote_driver(capabilities)
    elif driver == 'saucelabs':
        return _get_saucelabs_driver(capabilities)
    else:
        browser = _TEST_SETTINGS['BROWSER']
        return _get_local_driver(browser)


def _web_driver_available():
    """
    Return a Boolean indicating whether a Selenium web driver is
    available.
    """
    try:
        driver = get_web_driver()
        driver.quit()
        return True
    except (ConnectionRefusedError, NameError, RuntimeError,
            WebDriverException) as error:
        _LOGGER.warning('No WebDriver available for functional tests, '
                        'so those tests will be skipped.')
        return False


if _TEST_SETTINGS['ENABLED']:
    FUNCTIONAL_TESTS_ENABLED = _web_driver_available()
else:
    FUNCTIONAL_TESTS_ENABLED = True
    _LOGGER.warning('Functional tests are disabled, '
                    'so those tests will be skipped.')


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
        cls.driver.implicitly_wait(10)
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
