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
Views for the appuser package
"""

# third party
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import login
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text
from django.shortcuts import resolve_url
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import viewsets

# local
from cyphon.views import CustomModelViewSet
from . import forms
from . import serializers

_USER_SETTINGS = settings.APPUSERS


def custom_login(request, **kwargs):
    if request.user.is_authenticated:
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
    else:
        return login(request, **kwargs)


# @sensitive_post_parameters()
# @never_cache
# def user_registration(request, uidb64=None, token=None,
#                       template_name='appuser/user_registration.html',
#                       token_generator=default_token_generator,
#                       user_registration_form=forms.UserRegistrationForm,
#                       post_reset_redirect=None,
#                       current_app=None, extra_context=None):
#     """
#     Presents the user with a form to register if the given token and
#     uid are correct. If not, it returns a 404.

#     This view is copied from django.contrib.auth.views.password_reset_confirm.
#     There are some slight variable changes, and most of them can
#     be passed in as optional parameters to the original view.
#     I have the actual URL pointing to the the original view, but I have
#     this here in case there is an update to django breaks the original
#     view.
#     """
#     user_model = get_user_model()
#     assert uidb64 is not None and token is not None  # checked by URLconf
#     if post_reset_redirect is None:
#         post_reset_redirect = reverse('user_registration_complete')
#     else:
#         post_reset_redirect = resolve_url(post_reset_redirect)
#     try:
#         # urlsafe_base64_decode() decodes to bytestring on Python 3
#         uid = force_text(urlsafe_base64_decode(uidb64))
#         user = user_model._default_manager.get(pk=uid)
#     except (TypeError, ValueError, OverflowError, user_model.DoesNotExist):
#         user = None

#     if user is not None and token_generator.check_token(user, token):
#         if user.is_active:
#             raise Http404

#         validlink = True
#         title = _('Enter new password')
#         if request.method == 'POST':
#             form = user_registration_form(user, request.POST)
#             if form.is_valid():
#                 form.save()
#                 return HttpResponseRedirect(post_reset_redirect)
#         else:
#             form = user_registration_form(user)
#     else:
#         raise Http404
        
#     context = {
#         'form': form,
#         'title': title,
#         'validlink': validlink,
#         'user': user,
#     }

#     if extra_context is not None:
#         context.update(extra_context)

#     if current_app is not None:
#         request.current_app = current_app

#     return TemplateResponse(request, template_name, context)


@sensitive_post_parameters()
@never_cache
def password_reset_confirm(request, uidb64=None, token=None,
                           template_name='registration/password_reset_confirm.html',
                           token_generator=default_token_generator,
                           set_password_form=forms.CustomSetPasswordForm,
                           post_reset_redirect=None,
                           current_app=None, extra_context=None):
    """
    This view is copied from django.contrib.auth.views.password_reset_confirm.
    I wasn't too fond of how it showed a page without the form if
    the person guessed the token and the uid. I changed it so that
    it raises an 404 error instead.
    """
    UserModel = get_user_model()
    assert uidb64 is not None and token is not None  # checked by URLconf
    if post_reset_redirect is None:
        post_reset_redirect = reverse('password_reset_complete')
    else:
        post_reset_redirect = resolve_url(post_reset_redirect)
    try:
        # urlsafe_base64_decode() decodes to bytestring on Python 3
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = UserModel._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        if not user.is_active:
            raise Http404

        validlink = True
        title = _('Enter new password')
        if request.method == 'POST':
            form = set_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(post_reset_redirect)
        else:
            form = set_password_form(user)
    else:
        raise Http404

    context = {
        'form': form,
        'title': title,
        'validlink': validlink,
    }

    if extra_context is not None:
        context.update(extra_context)

    if current_app is not None:
        request.current_app = current_app

    return TemplateResponse(request, template_name, context)


class UserTokenAuthenticatedFor(APIView):
    """
    View that determines if a user is able to perform a one time link action,
    such as registering for the first time, or resetting their password.
    """
    serializer_class = serializers.UserTokenAuthentication
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        """
        Determines if a user token is associated with a the given user id
        that has been encoded in base 64.
        """
        token_auth = serializers.UserTokenAuthentication(data=request.data)

        if token_auth.is_valid():
            return Response(True)
        else:
            return Response(token_auth.errors,
                            status=status.HTTP_400_BAD_REQUEST)


# class SendPasswordResetEmail(APIView):
#     """
#     Sends the user a password reset email
#     """

#     def post(self, request):
#         user_email = serializers.UserEmailSerializer(data=request.data)
#         if user_email.is_valid():
#             user_model = get_user_model()
#             user = user_model.objects.get(email=user_email)

#             if user:


class UserRegistration(APIView):
    """
    View that registers a user that has been added into the system by a
    cyphon admin.
    """
    serializer_class = serializers.UserRegistrationSerializer
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        """
        Update a user.
        """
        user_registration = serializers.UserRegistrationSerializer(
            data=request.data)

        if user_registration.is_valid():
            uid = force_text(urlsafe_base64_decode(
                user_registration.validated_data['uidb64']))
            user = get_user_model().objects.get(pk=uid)
            user.first_name = user_registration.validated_data['first_name']
            user.last_name = user_registration.validated_data['last_name']
            user.set_password(user_registration.validated_data['password2'])
            user.is_active = True
            user.save()
            return Response(serializers.AppUserSerializer(user).data)
        else:
            return Response(user_registration.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class AppUserPagination(PageNumberPagination):
    """
    Pagination class for appusers
    """
    page_size = 50


class AppUserViewSet(CustomModelViewSet):
    """
    A simple ViewSet for viewing and editing alerts.
    """
    queryset = get_user_model().objects.all()
    serializer_class = serializers.AppUserSerializer
    pagination_class = AppUserPagination

    def __init__(self, *args, **kwargs):

        # configure filter backends here so we can mock APPUSERS in tests
        self.custom_filter_backends = _USER_SETTINGS['CUSTOM_FILTER_BACKENDS']
        super(AppUserViewSet, self).__init__(*args, **kwargs)


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'user': serializers.AppUserSerializer(user).data
    }
