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
Tests the settings utility module.
"""
import os
try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch
from unittest import TestCase

import botocore.exceptions

import utils.settings


class GetParametersTestCase(TestCase):
    """
    Tests get_param and get_ssm_param utility functions.
    """

    @patch('boto3.client')
    def test_get_ssm_param(self, mock_boto_client):
        """
        Tests the get_ssm_param function.
        """
        mock_ssm = MagicMock()
        mock_ssm.get_parameter.return_value = {'Parameter': {'Value': 'bar'}}
        mock_boto_client.return_value = mock_ssm
        self.assertEqual(utils.settings.get_ssm_param('foo'), 'bar')

        mock_ssm.get_parameter.side_effect = KeyError
        self.assertEqual(utils.settings.get_ssm_param('foo'), None)

        mock_ssm.get_parameter.side_effect = botocore.exceptions.ClientError(
            {'Error': {'Code': 'ParameterNotFound'}}, 'GetParameter')
        self.assertEqual(utils.settings.get_ssm_param('foo'), None)


        mock_ssm.get_parameter.side_effect = botocore.exceptions.ClientError(
            {'Error': {'Code': 'InvalidAction'}}, 'GetParameter')
        self.assertRaises(
            botocore.exceptions.ClientError,
            utils.settings.get_ssm_param,
            'foo'
        )

    @patch('boto3.client')
    def test_get_param(self, mock_boto_client):
        """
        Tests the get_param function.
        """
        utils.settings.ON_EC2 = False
        os.environ['FOO'] = os.environ['BAR'] = 'bar'
        self.assertEqual(utils.settings.get_param('foo'), 'bar')
        self.assertEqual(utils.settings.get_param('foo', envvar='BAR'), 'bar')
        self.assertEqual(
            utils.settings.get_param('foo', envvar='QUX', default='bar'),
            'bar'
        )

        utils.settings.ON_EC2 = True
        mock_ssm = MagicMock()
        mock_ssm.get_parameter.return_value = {'Parameter': {'Value': 'bar'}}
        mock_boto_client.return_value = mock_ssm
        self.assertEqual(utils.settings.get_param('qux'), 'bar')

        mock_ssm.get_parameter.side_effect = botocore.exceptions.ClientError(
            {'Error': {'Code': 'ParameterNotFound'}}, 'GetParameter')
        self.assertEqual(utils.settings.get_param('qux'), None)
        self.assertEqual(utils.settings.get_param('qux', default='bar'), 'bar')
        self.assertEqual(utils.settings.get_param('qux', envvar='FOO'), 'bar')

        with patch('utils.settings.get_ssm_param') as patched_get_ssm_param:
            patched_get_ssm_param.return_value = 'bar'
            utils.settings.get_param('foo')
            patched_get_ssm_param.assert_called_with('cyphon.foo', True)

            utils.settings.get_param('bar', prefix='foo')
            patched_get_ssm_param.assert_called_with('foobar', True)
