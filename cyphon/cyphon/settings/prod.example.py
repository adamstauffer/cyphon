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
[`source`_]

Production Django settings for Cyphon.

For more information on this Django file, see:
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of Django settings and their values, see:
https://docs.djangoproject.com/en/1.9/ref/settings/

.. _source: ../_modules/cyphon/settings/prod.html

"""

# standard library
import email.utils
import logging
import os

# local
from .base import *


if ON_EC2 or os.getenv('AWS_ACCESS_KEY'):
    INSTALLED_APPS.insert(1, 'django_s3_storage')

LOGGER = logging.getLogger(__name__)
DEBUG = False

ADMINS = []
if 'DJANGO_ADMIN' in os.environ:
    ADMINS.append(email.utils.parseaddr(os.getenv('DJANGO_ADMIN')))

# Store media and static content in S3
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_KEY')
AWS_S3_BUCKET_NAME = os.getenv('AWS_S3_BUCKET_NAME')
AWS_S3_BUCKET_NAME_STATIC = AWS_S3_BUCKET_NAME
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_S3_BUCKET_NAME
AWS_S3_ENDPOINT_URL_STATIC = 'https://s3.amazonaws.com'
if ON_EC2:
    AWS_REGION = ec2_metadata.region
else:
    AWS_REGION = os.getenv('AWS_REGION_NAME', 'us-east-1')

DEFAULT_FILE_STORAGE = 'django_s3_storage.storage.S3Storage'
STATICFILES_LOCATION = 'static'
STATICFILES_STORAGE = 'django_s3_storage.storage.StaticS3Storage'

AWS_S3_KEY_PREFIX_STATIC = 'static/'

if AWS_S3_BUCKET_NAME:
    STATIC_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, STATICFILES_LOCATION)

AWS_S3_BUCKET_AUTH = False

MEDIAFILES_LOCATION = 'media'
if AWS_S3_BUCKET_NAME:
    MEDIA_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, MEDIAFILES_LOCATION)
    MEDIA_ROOT = 'media'

#: URL for constructing link with MEDIA_URL, e.g. https://www.example.com
BASE_URL = os.getenv('BASE_URL_PROD', 'http://localhost:8000')

CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOW_CREDENTIALS = True

LOG_DIR = BASE_DIR

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(name)s '
                      '%(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'django.log'),
            'when': 'midnight',
            'interval': 1,
            'backupCount': 7,
            'formatter': 'verbose',
        },
        'receiver_file': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'receiver.log'),
            'when': 'midnight',
            'interval': 1,
            'backupCount': 7,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
    },
    'loggers': {
        'django.server': {
            'handlers': ['console', 'file', 'mail_admins'],
            'propagate': True,
            'level': 'WARNING'
        },
        'django.request': {
            'handlers': ['console', 'file', 'mail_admins'],
            'propagate': True,
            'level': 'WARNING'
        },
        'django': {
            'handlers': ['console', 'file', 'mail_admins'],
            'propagate': True,
            'level': 'WARNING',
        },
        'receiver': {
            'handlers': ['console', 'receiver_file', 'mail_admins'],
            'propagate': True,
            'level': 'INFO',
        },
    }
}
