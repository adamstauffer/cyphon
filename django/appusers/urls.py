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

# third party
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.core.urlresolvers import reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required, user_passes_test

# local
from appusers import forms
from . import views


# Helper function that brings up a 404 page if a user attempts to access it
# when logged in.
login_forbidden = user_passes_test(lambda u: u.is_anonymous(), '/')


urlpatterns = [
    # url(r'^login/$',
    #     'appusers.views.custom_login',
    #     {
    #         'template_name': 'appuser/login.html'
    #     },
    #     name='login'),
    # url(r'^logout/$',
    #     'django.contrib.auth.views.logout',
    #     {
    #         'template_name': 'appuser/logout.html'
    #     },
    #     name='logout'),
    # url(r'^logout_then_login/$',
    #     'django.contrib.auth.views.logout_then_login',
    #     {
    #         'extra_context': {
    #             'logged_out': True,
    #         },
    #     },
    #     name='logout_then_login'),
    # url(r'^password_change/$',
    #     'django.contrib.auth.views.password_change',
    #     {
    #         'template_name': 'appuser/password_change.html',
    #         'password_change_form': forms.CustomPasswordChangeForm,
    #         'post_change_redirect': reverse_lazy(
    #             'password_change_done'),
    #     },
    #     name='password_change'),
    # url(r'^password_change_done/$',
    #     'django.contrib.auth.views.password_change_done',
    #     {
    #         'template_name': 'appuser/password_change_done.html',
    #     },
    #     name='password_change_done'),
    # url(r'^password_reset/$',
    #     login_forbidden(auth_views.password_reset),
    #     {
    #         'template_name': 'appuser/password_reset.html',
    #         'email_template_name': 'appuser/password_reset_email.html',
    #         'subject_template_name': 'appuser/password_reset_subject.txt',
    #         'current_app': 'appusers',
    #         'post_reset_redirect': reverse_lazy('password_reset_done'),
    #     },
    #     name='password_reset'),
    # url(r'^password_reset_done/$',
    #     'django.contrib.auth.views.password_reset_done',
    #     {
    #         'template_name': 'appuser/password_reset_done.html',
    #     },
    #     name='password_reset_done'),
    # url(r'^password_reset_confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/'
    #     '(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    #     'appusers.views.password_reset_confirm',
    #     {
    #         'template_name': 'appuser/password_reset_confirm.html',
    #         'set_password_form': forms.CustomSetPasswordForm,
    #         'post_reset_redirect': reverse_lazy(
    #             'password_reset_complete'),
    #         'current_app': 'appusers',
    #     },
    #     name='password_reset_confirm'),
    # url(r'^password_reset_complete/$',
    #     login_forbidden(auth_views.password_reset_complete),
    #     {
    #         'template_name': 'appuser/password_reset_complete.html',
    #     },
    #     name='password_reset_complete'),
    # url(r'^user_registration/(?P<uidb64>[0-9A-Za-z_\-]+)/'
    #     '(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    #     'appusers.views.user_registration',
    #     {
    #         'template_name': 'appuser/user_registration.html',
    #         'user_registration_form': forms.UserRegistrationForm,
    #         'post_reset_redirect': reverse_lazy(
    #             'user_registration_complete'),
    #         'current_app': 'appusers',
    #     },
    #     name='user_registration'),
    # url(r'^user_registration_complete/$',
    #     TemplateView.as_view(
    #         template_name='appuser/user_registration_complete.html'),
    #     name='user_registration_complete'),
    # url(r'^profile/$',
    #     login_required(TemplateView.as_view(
    #         template_name='appuser/profile.html')),
    #     name='profile'),
    url(r'^token-authenticated/$', views.UserTokenAuthenticatedFor.as_view(),
        name='user_token_authentication'),
    url(r'^registration/$', views.UserRegistration.as_view(),
        name='user_registration'),
]
