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
Defines a DashboardPage and its elements.
"""

# local
from tests.pages.page import Page
from tests.pages.element import StyledElement


class Module1(StyledElement):
    locator = 'div[id="module_1"] h2'

class Module2(StyledElement):
    locator = 'div[id="module_2"] h2'

class Module3(StyledElement):
    locator = 'div[id="module_3"] h2'

class Module4(StyledElement):
    locator = 'div[id="module_4"] h2'

class Module5(StyledElement):
    locator = 'div[id="module_5"] h2'

class Module6(StyledElement):
    locator = 'div[id="module_6"] h2'

class Module7(StyledElement):
    locator = 'div[id="module_7"] h2'

class Module8(StyledElement):
    locator = 'div[id="module_8"] h2'

class Module9(StyledElement):
    locator = 'div[id="module_9"] h2'

class Module10(StyledElement):
    locator = 'div[id="module_10"] h2'

class Module11(StyledElement):
    locator = 'div[id="module_11"] h2'

class Module12(StyledElement):
    locator = 'div[id="module_12"] h2'

class Module13(StyledElement):
    locator = 'div[id="module_13"] h2'

class Module14(StyledElement):
    locator = 'div[id="module_14"] h2'

class Module15(StyledElement):
    locator = 'div[id="module_15"] h2'

class DashboardPage(Page):
    """
    Page class for the admin dashboard.
    """
    module_1 = Module1()
    module_2 = Module2()
    module_3 = Module3()
    module_4 = Module4()
    module_5 = Module5()
    module_6 = Module6()
    module_7 = Module7()
    module_8 = Module8()
    module_9 = Module9()
    module_10 = Module10()
    module_11 = Module11()
    module_12 = Module12()
    module_13 = Module13()
    module_14 = Module14()
    module_15 = Module15()
