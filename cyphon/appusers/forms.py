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
Django forms for AppUser app.
"""

# third party
from django import forms
from django.contrib.auth import forms as auth_forms
from django.utils.translation import ugettext_lazy as _

# local
from appusers.models import AppUser


class CustomUserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username.
    Password is automatically set as unusable until the user responds
    to a confirmation email.
    """
    class Meta:
        model = AppUser
        fields = ('email', )


class CustomUserChangeForm(auth_forms.UserChangeForm):
    """
    A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """

    def __init__(self, *args, **kargs):
        super(CustomUserChangeForm, self).__init__(*args, **kargs)

    class Meta:
        model = AppUser
        fields = '__all__'


class UserRegistrationForm(auth_forms.SetPasswordForm):
    """
    The form used for the initial registration of a user.
    """
    new_password2 = forms.CharField(widget=forms.PasswordInput(),
                                    label=_("Password Confirmation"))
    first_name = forms.CharField(label=_("First Name"),
                                 required=True, widget=forms.TextInput,
                                 max_length=30)
    last_name = forms.CharField(label=_("Last Name"),
                                required=True, widget=forms.TextInput,
                                max_length=30)

    def save(self, commit=True):
        """
        Saves the user to the database.
        """
        self.user.set_password(self.cleaned_data['new_password1'])
        self.user.first_name = self.cleaned_data['first_name']
        self.user.last_name = self.cleaned_data['last_name']
        self.user.is_active = True
        if commit:
            self.user.save()
        return self.user


class CustomSetPasswordForm(auth_forms.SetPasswordForm):
    """
    Custom form for setting passwords.
    """
    error_messages = dict(auth_forms.SetPasswordForm.error_messages, **{
        'same_password_as_old': _("You entered the same password as your "
                                  "current password. Please enter a new "
                                  "password."),
    })
    new_password1 = forms.CharField(widget=forms.PasswordInput(),
                                    label=_("New Password"))

    def clean_new_password1(self):
        """
        Checks to make sure that the new password isn't the same as
        the old one.
        """
        password1 = self.cleaned_data.get('new_password1')
        if self.user.check_password(password1):
            raise forms.ValidationError(
                self.error_messages['same_password_as_old'],
                code='same_password_as_old',
            )
        return password1


class CustomPasswordChangeForm(auth_forms.PasswordChangeForm):
    """
    Custom form for changing passwords by an admin panel.
    """
    error_messages = dict(auth_forms.PasswordChangeForm.error_messages, **{
        'same_password_as_old': _("You entered the same password as your "
                                  "current password. Please enter a new "
                                  "password."),
    })
    new_password1 = forms.CharField(widget=forms.PasswordInput(),
                                    label=_("New Password"))

    def clean_new_password1(self):
        """
        Checks to make sure that the new password isn't the same as
        the old one.
        """
        password1 = self.cleaned_data.get('new_password1')
        if self.user.check_password(password1):
            raise forms.ValidationError(
                self.error_messages['same_password_as_old'],
                code='same_password_as_old',
            )
        return password1

