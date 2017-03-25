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

_FUNCTIONAL_TESTS_ENABLED = settings.FUNCTIONAL_TESTS_ENABLED

_LOGGER = logging.getLogger(__name__)

if not _FUNCTIONAL_TESTS_ENABLED:
    _LOGGER.warning('Functional tests are disabled, '
                   'so those tests will be skipped.')


@unittest.skipUnless(_FUNCTIONAL_TESTS_ENABLED, 'functional tests disabled')
class FunctionalTest(StaticLiveServerTestCase):
    """
    Base class for a functional test case.
    """

    def __init__(self, *args, **kwargs):
        super(FunctionalTest, self).__init__(*args, **kwargs)

    @classmethod
    def setUpClass(cls):
        super(FunctionalTest, cls).setUpClass()
        try:
            cls.driver = Firefox()
        except WebDriverException as error:
            cls.driver = Remote(
                command_executor='http://selenium:4444/wd/hub',
                desired_capabilities=DesiredCapabilities.FIREFOX
            )
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
