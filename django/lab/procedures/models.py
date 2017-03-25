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
import importlib
import logging

# third party
from django.db import models
from django.core.exceptions import ObjectDoesNotExist

# local
from lab.registry import LAB_CHOICES
from utils.parserutils import parserutils
from utils.validators.validators import IDENTIFIER_VALIDATOR


LOGGER = logging.getLogger(__name__)


class ProtocolManager(models.Manager):
    """
    Adds methods to the default model manager.
    """

    def get_by_natural_key(self, package, module, function):
        """
        Allows retrieval of a Lab by its natural key instead of its
        primary key.
        """
        try:
            return self.get(package=package, module=module, function=function)
        except ObjectDoesNotExist:
            LOGGER.error('%s "%s.%s.%s" does not exist',
                         self.model.__name__, package, module, function)


class Protocol(models.Model):
    """

    Attributes:
        name: a string representing the name of the Protocol
        package: the name of a subpackage within the labs package that will
            analyze the data
        module: the name of the module the package that will analyze the data
        function: the name of the function that will analyze the data

    """
    name = models.CharField(max_length=255, unique=True)
    package = models.CharField(
        max_length=32,
        validators=[IDENTIFIER_VALIDATOR],
        choices=LAB_CHOICES
    )
    module = models.CharField(
        max_length=32,
        validators=[IDENTIFIER_VALIDATOR]
    )
    function = models.CharField(
        max_length=32,
        validators=[IDENTIFIER_VALIDATOR]
    )

    objects = ProtocolManager()

    class Meta:
        """
        Metadata options.
        """
        unique_together = ('package', 'module', 'function')

    def __str__(self):
        return self.name

    def _get_module(self):
        """
        Returns the module for analyzing the data.
        """
        module_full_name = 'lab.%s.%s' % (self.package, self.module)

        # load the module (will raise ImportError if module cannot be loaded)
        module = importlib.import_module(module_full_name)

        return module

    def process(self, data):
        """
        Passes the data to the classfying function and returns the result.
        """
        module = self._get_module()

        # get the classifier function (will raise AttributeError if function cannot be found)
        func = getattr(module, self.function)

        return func(data)


class Procedure(models.Model):
    """

    Attributes:
        name: a string representing the name of the procedure
        protocol: a Protocol used to analyze
        field_name: the name of the field containing the data to analyze. If no
            field_name is provide, the entire data dictionary is analyzed.
    """
    name = models.CharField(max_length=255, unique=True)
    protocol = models.ForeignKey(Protocol)
    field_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

    def _analyze(self, data):
        return self.protocol.process(data)

    def get_result(self, data):
        """
        Takes a data dictionary and analyzes it using the Procedure's protocol.
        If the Procedure has a field_name, only the corresponding field within
        the data dictionary is analyzed. Otherwise, the entire data dictionary
        is analyzed with the protocol.

        Notes
        -----
        This method should have the same name as the corresponding
        method in an Inspection.
        """
        if self.field_name:
            value = parserutils.get_dict_value(self.field_name, data)
            return self._analyze(value)
        else:
            return self._analyze(data)
