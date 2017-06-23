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

Base Django settings for Cyphon.

For more information on this Django file, see:
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of Django settings and their values, see:
https://docs.djangoproject.com/en/1.9/ref/settings/

.. _source: ../_modules/cyphon/settings/base.html

"""

# standard library
from collections import OrderedDict
from datetime import timedelta
import os
import sys

# local
from .conf import *


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# change this to the directory where Cyphon's dependencies are installed
REQUIREMENTS = os.path.join(os.path.dirname(BASE_DIR),
                            'virtualenv/lib/python3.4/site-packages')

ALLOWED_HOSTS = HOST_SETTINGS['ALLOWED_HOSTS']
CORS_ORIGIN_WHITELIST = HOST_SETTINGS['CORS_ORIGIN_WHITELIST']
LOGIN_REDIRECT_URL = '/app/'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': POSTGRES['NAME'],
        'USER': POSTGRES['USER'],
        'PASSWORD': POSTGRES['PASSWORD'],
        'HOST': POSTGRES['HOST'],
        'PORT': POSTGRES['PORT'],
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            '/templates/'
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

TEST = 'test' in sys.argv

#: Application definition
INSTALLED_APPS = (
    'cyphon',  # must come before django.contrib.admin to override templates
    'autocomplete_light',  # must come before django.contrib.admin
    # 'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.gis',
    'django.contrib.messages',
    'django.contrib.postgres',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    # 'debug_toolbar',
    'constance',
    'constance.backends.database',
    'grappelli.dashboard',  # must come after contenttypes and before grappelli
    'grappelli',  # must come before django.contrib.admin
    'django.contrib.admin',
    'django_extensions',
    'django_filters',
    'django_mailbox',
    # 'corsheaders',  # Cross Origin Resource Sharing (local dev)
    'rest_framework',
    'rest_framework_docs',
    'rest_framework_jwt',  # Auth tokens
    'aggregator.filters',
    'aggregator.funnels',
    'aggregator.invoices',
    'aggregator.pipes',
    'aggregator.plumbers',
    'aggregator.pumproom',
    'aggregator.reservoirs',
    'aggregator.samples',
    'aggregator.streams',
    'alerts',
    'ambassador.passports',
    'ambassador.stamps',
    'ambassador.visas',
    'appusers',
    'bottler.containers',
    'bottler.bottles',
    'bottler.labels',
    'bottler.tastes',
    'categories',
    'codebooks',
    'companies',
    'contexts',
    'cyclops',
    'cyphon.settings',
    'distilleries',
    'httmock',
    'inspections',
    'lab.procedures',
    'monitors',
    'notifications',
    'query',
    'query.collectionqueries',
    'query.reservoirqueries',
    'responder.actions',
    'responder.couriers',
    'responder.destinations',
    'responder.dispatches',
    'sifter.datasifter.datachutes',
    'sifter.datasifter.datacondensers',
    'sifter.datasifter.datamungers',
    'sifter.datasifter.datasieves',
    'sifter.logsifter.logchutes',
    'sifter.logsifter.logcondensers',
    'sifter.logsifter.logmungers',
    'sifter.logsifter.logsieves',
    'sifter.mailsifter.mailchutes',
    'sifter.mailsifter.mailcondensers',
    'sifter.mailsifter.mailmungers',
    'sifter.mailsifter.mailsieves',
    'tags',
    'target.followees',
    'target.locations',
    'target.searchterms',
    'target.timeframes',
    'utils.dateutils',
    'utils.geometry',
    'utils.parserutils',
    'utils.validators',
    'warehouses',
    'watchdogs',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
)

ROOT_URLCONF = 'cyphon.urls'

WSGI_APPLICATION = 'cyphon.wsgi.application'

#: Authentication backend classes to use when attempting to authenticate a user
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend', # this is default
)

#: The model to use to represent a User.=
AUTH_USER_MODEL = 'appusers.AppUser'

#: Link Creation for Emails sent from the server
TRANSFER_PROTOCOL = 'http'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 9,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

#: Path for user registration
REGISTRATION_PATH = '#/user/registration'

#: Path for password reset
PASSWORD_RESET_PATH = '#/user/reset-password'

#: How many days until a unique user url is not valid
PASSWORD_RESET_TIMEOUT_DAYS = 3

#: Password strength variables
PASSWORD_MIN_LENGTH = 6
PASSWORD_MAX_LENGTH = 30

# This section is for sending email to users. This example is a gmail account.
EMAIL_NAME = EMAIL['NAME']
EMAIL_HOST = EMAIL['HOST']
EMAIL_HOST_USER = EMAIL['HOST_USER']
EMAIL_HOST_PASSWORD = EMAIL['HOST_PASSWORD']
EMAIL_PORT = EMAIL['PORT']
EMAIL_USE_TLS = EMAIL['USE_TLS']

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'US/Eastern'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/
STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(HOME_DIR, 'static')

STATICFILES_DIRS = []

if CYCLOPS['LOCAL_ASSETS_ENABLED']:
    STATICFILES_DIRS += [
        (CYCLOPS['LOCAL_FOLDER_NAME'], CYCLOPS['LOCAL_ASSETS_PATH']),
    ]

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(HOME_DIR, 'media')

API_URL = '/api/v1/'

# REST Framework
# http://www.django-rest-framework.org/api-guide/settings/
REST_FRAMEWORK = {
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_METADATA_CLASS': 'rest_framework.metadata.SimpleMetadata',
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
        # 'rest_framework.permissions.DjangoModelPermissions',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ),
}

# This is for the messaging system that celery will use to operate. This is
# for rabbitMQ.
BROKER_URL = 'amqp://{username}:{password}@{host}:5672/{vhost}'.format(
    username=RABBITMQ['USERNAME'],
    password=RABBITMQ['PASSWORD'],
    host=RABBITMQ['HOST'],
    vhost=RABBITMQ['VHOST']
)

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

#: Schedule for Celery tasks
CELERYBEAT_SCHEDULE = {
    'get-new-mail': {
        'task': 'tasks.get_new_mail',
        'schedule': timedelta(seconds=30)
    },
    'run-health-check': {
        'task': 'tasks.run_health_check',
        'schedule': timedelta(seconds=60)
    },
    'run-bkgd-search': {
        'task': 'tasks.run_bkgd_search',
        'schedule': timedelta(seconds=60)
    },
}

CELERYD_POOL_RESTARTS = True

GRAPPELLI_ADMIN_TITLE = 'Cyphon'
GRAPPELLI_INDEX_DASHBOARD = 'cyphon.dashboard.CyphonIndexDashboard'

JASMINE_TEST_DIRECTORY = 'tests'

JWT_AUTH = {
    'JWT_ALLOW_REFRESH': True,
    'JWT_RESPONSE_PAYLOAD_HANDLER': 'appusers.views.jwt_response_payload_handler',
    'JWT_EXPIRATION_DELTA': timedelta(weeks=52),
    'JWT_REFRESH_EXPIRATION_DELTA': timedelta(weeks=52)
}

CONSTANCE_IGNORE_ADMIN_VERSION_CHECK = True
CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'
CONSTANCE_CONFIG = OrderedDict([
    ('PUSH_NOTIFICATIONS_ENABLED', (False, 'Turn on push notifications')),
])

DJANGO_MAILBOX_ATTACHMENT_UPLOAD_TO = os.path.join(MEDIA_ROOT,
                                                   'mailbox_attachments/%Y/%m/%d/')

REST_FRAMEWORK_DOCS = {
    'HIDE_DOCS': os.environ.get('HIDE_DRFDOCS', False)
}
