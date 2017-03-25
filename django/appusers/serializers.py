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
Serializers related to the custom user object
"""

# third party
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import ugettext as _
from rest_framework import serializers

# local
from . import models


class AppUserSerializer(serializers.ModelSerializer):
    """
    Serializer for the AppUser object
    """

    class Meta:
        model = models.AppUser
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'is_staff',
            'company'
        )
        write_only_fields = ('password',)
        read_only_fields = (
            'is_staff',
            'is_superuser',
            'is_active',
            'date_joined',
        )


class UserEmailSerializer(serializers.Serializer):
    """
    Serializes an email associated with a User account
    """
    email = serializers.EmailField(
        label=_('User Email'),
        help_text=_('Enter the email associated with your account'))


def valid_uidb64(value):
    """
    Determines if a uidb64 value is valid.
    """
    try:
        force_text(urlsafe_base64_decode(value))
    except (DjangoUnicodeDecodeError, ValueError) as error:
        raise serializers.ValidationError(str(error))
    return value


class UserTokenAuthentication(serializers.Serializer):
    """
    Serializes a token and uidb64 associated with a user and validates if an
    intended action is possible base on their current user status.
    """
    token = serializers.CharField(
        label=_('Token'),
        help_text=_('Temporary token associated with a user account.'))
    uidb64 = serializers.CharField(
        label=_('uidb64'),
        help_text=_('Encoded user id associated with a user account.'),
        validators=[valid_uidb64])
    action = serializers.ChoiceField(
        choices=[_("password-reset"), _("register")],
        label=_("User Action"),
        help_text=_("The action the user wishes to perform on their account."))

    def action_authorized(self, action, user):
        """
        Determines if an action is authorized for a certain user
        """
        authorized = False

        if not user.has_usable_password():
            if action is 'password-reset':
                authorized = user.is_active
            if action is 'register':
                authorized = not user.is_active

        return authorized

    def validate(self, data):
        """
        Check that the user token matches the decoded user id
        """
        user_model = get_user_model()

        uid = force_text(urlsafe_base64_decode(data['uidb64']))

        try:
            user = user_model.objects.get(pk=uid)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                "Not a valid token and uidb64 combination")

        if user is not None:
            if not default_token_generator.check_token(user, data['token']):
                raise serializers.ValidationError(
                    "Not a valid token and uidb64 combination")
            if not self.action_authorized(data['action'], user):
                raise serializers.ValidationError(
                    "User not authorized for {0}".format(data['action']))

        return data


class UserRegistrationSerializer(serializers.Serializer):
    """
    Serializer for user registration.
    """
    token = serializers.CharField(
        label=_('Token'),
        help_text=_('Temporary token associated with a user account.'))
    uidb64 = serializers.CharField(
        label=_('uidb64'),
        help_text=_('Encoded user id associated with a user account.'),
        validators=[valid_uidb64])
    password1 = serializers.CharField(
        min_length=8, max_length=20, label=_("Password"),
        style={'input_type': 'password'})
    password2 = serializers.CharField(
        min_length=8, max_length=20, label=_("Repeat Password"),
        style={'input_type': 'password'})
    first_name = serializers.CharField(label=_("First Name"), max_length=30)
    last_name = serializers.CharField(label=_("Last Name"), max_length=30)

    def validate(self, data):
        """
        Validates multiple field errors
        """
        tokenData = {
            'token': data['token'],
            'uidb64': data['uidb64'],
            'action': 'register'
        }

        if data['password1'] != data['password2']:
            raise serializers.ValidationError(
                "The passwords you entered did not match.")
        if not UserTokenAuthentication(data=tokenData).is_valid():
            raise serializers.ValidationError(
                "User token not valid.")

        return data

