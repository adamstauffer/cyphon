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
A collection of classes and functions that help register a user.
"""

# third party
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template import loader
from django.core.mail import EmailMultiAlternatives


def send_registration_email(
        user, domain_override=None, use_https=False, from_email=None,
        subject_template_name='appuser/user_registration_subject.txt',
        email_template_name='appuser/user_registration_email.html',
        token_generator=default_token_generator,
        html_email_template_name=None):
    """
    Generates a one-use only link for a user to register their profile.

    Args:
        domain_override (str, optional):
            **Default**: None

            The domain url. If given, this will override the default domain 
            url thatwill be placed in the registration link given to the user.

        use_https (bool, optional):
            **Default**: False

            Use https in registration link.
            If true, will place https:// at the beginning of the 
            registration url.

        from_email (str, optional):
            **Default**: None

            The return email address. 

        subject_template_name (str, optional): 
            **Default**: 'appuser/user_registration_subject.txt'

            The template that will be used to create the subject line.

        email_template_name (str, optional): 
            **Default**: 'appuser/user_registration_email.html'

            The template that will be used to create the email content.

        token_generator (module, optional): 
            **Default**: django.contrib.auth.tokens.default_token_generator

            Generator used to create custom tokens for the registration
            email.

        html_email_template_name (str, optional):
            **Default**: None

            The template to use to display the information in an html email.
    """
    if not domain_override:
        site_name = domain = settings.HOSTNAME
    else:
        site_name = domain = domain_override

    context = {
        'email': user.email,
        'domain': domain,
        'site_name': site_name,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'user': user,
        'registration_path': settings.REGISTRATION_PATH,
        'token': token_generator.make_token(user),
        'protocol': 'https' if use_https else 'http',
    }

    subject = loader.render_to_string(subject_template_name, context)
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    body = loader.render_to_string(email_template_name, context)

    email_message = EmailMultiAlternatives(subject, body,
                                           from_email, [user.email])
    if html_email_template_name is not None:
        html_email = loader.render_to_string(html_email_template_name, context)
        email_message.attach_alternative(html_email, 'text/html')

    email_message.send()
