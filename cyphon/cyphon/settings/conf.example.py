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


.. _source: ../_modules/cyphon/settings/conf.html

"""

# standard library
import os
import sys

# third party
from django.core.management.utils import get_random_secret_key
from ec2_metadata import ec2_metadata

# local
from utils.settings import get_param, ON_EC2


SECRET_KEY = get_param('secret_key', get_random_secret_key())

HOST_SETTINGS = {
    'ALLOWED_HOSTS': [addr.strip() for addr in os.getenv(
        'ALLOWED_HOSTS', 'localhost').split(',')],
    'CORS_ORIGIN_WHITELIST': [addr.strip() for addr in os.getenv(
        'CORS_ORIGIN_WHITELIST', 'localhost:8000').split(',')],
}

if ON_EC2:
    HOST_SETTINGS['ALLOWED_HOSTS'].append(ec2_metadata.private_ipv4)

TEST = 'test' in sys.argv

FUNCTIONAL_TESTS = {
    'ENABLED': os.getenv('FUNCTIONAL_TESTS_ENABLED', False),
    'DRIVER': os.getenv('FUNCTIONAL_TESTS_DRIVER', 'LOCALHOST'),  # 'DOCKER', 'SAUCELABS'
    'HOST': os.getenv('FUNCTIONAL_TESTS_HOST', 'localhost'),
    'PORT': os.getenv('FUNCTIONAL_TESTS_PORT', '4444'),
    'PLATFORM': os.getenv('FUNCTIONAL_TESTS_PLATFORM', 'ANY'),
    'BROWSER': os.getenv('FUNCTIONAL_TESTS_BROWSER', 'chrome'),
    'VERSION': os.getenv('FUNCTIONAL_TESTS_VERSION', ''),
}

PAGE_SIZE = 10

PROJ_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
HOME_DIR = os.path.dirname(PROJ_DIR)
KEYS_DIR = os.path.join(HOME_DIR, 'keys')

APPUSERS = {
    'CUSTOM_FILTER_BACKENDS': []
}

CODEBOOKS = {
    'CODENAME_PREFIX': '**',  # prefix for displayed CodeNames
    'CODENAME_SUFFIX': '**',  # suffix for displayed CodeNames
}

CYCLOPS = {
    'ENABLED': True,
    'MAPBOX_ACCESS_TOKEN': '',
    'LOCAL_ASSETS_ENABLED': False,
    'LOCAL_ASSETS_PATH': os.path.abspath(os.path.join(PROJ_DIR, '../../cyclops/dist')),
    'LOCAL_FOLDER_NAME': 'cyclops',
    'LOCAL_CSS_FILENAME': 'cyclops.css',
    'LOCAL_JS_FILENAME': 'cyclops.js',
}

DATASIFTER = {
    'DEFAULT_MUNGER': 'default',
    'DEFAULT_MUNGER_ENABLED': True,
}

DISTILLERIES = {

    # dictionary key for recording the date record was saved
    'DATE_KEY': '_saved_date',

    # dictionary key for saving the primary key of the distillery associated with a
    # distilled document
    'DISTILLERY_KEY': '_distillery',

    # dictionary key for saving fields relating to the location of the raw data on
    # which the distilled data is based
    'RAW_DATA_KEY': '_raw_data',

    # dictionary key for adding a label to a document
    'LABEL_KEY': '_metadata',

    # dictionary key for saving the name of the backend where the raw data is stored
    'BACKEND_KEY': 'backend',

    # dictionary key for saving the name of the database where the raw data is stored
    'WAREHOUSE_KEY': 'database',

    # dictionary key for saving the name of the collection where the raw data is stored
    'COLLECTION_KEY': 'collection',

    # dictionary key for saving the document id for the raw data
    'DOC_ID_KEY': 'doc_id',

    # dictionary key for saving the name of the platform associated with a document
    'PLATFORM_KEY': '_platform',

}

ELASTICSEARCH = {
    'HOSTS': [
        {
            'host': get_param('elasticsearch_host', 'elasticsearch'),
            'port': int(get_param('elasticsearch_port', '9200')),
            'http_auth': get_param('elasticsearch_http_auth'),
            'use_ssl': bool(int(get_param('elasticsearch_use_ssl', False))),
        },
    ],
    # Note: the keyword arguments provided below are passed to the
    # *Elasticsearch* constructor, and should not contain host-specific
    # keyword arguments for individual connections, which are instead
    # configured in the 'HOSTS' list above.
    'KWARGS': {
        'timeout': 30,
    },
}

EMAIL = {
    'DEFAULT_FROM': 'webmaster@localhost',
    'HOST': get_param('email_host', 'smtp.gmail.com'),
    'HOST_USER': get_param('email_user', ''),
    'HOST_PASSWORD': get_param('email_password', ''),
    'PORT': int(get_param('email_port', '587')),
    'SUBJECT_PREFIX': '[Cyphon] ',
    'USE_TLS': get_param('email_use_tls', 'true').lower() in ('true', '1'),
}

GEOIP = {
    'GEOIP_PATH': os.getenv('GEOIP_PATH', '/usr/share/GeoIP/'),
    'CITY_DB': 'GeoLite2-City.mmdb',
}

JIRA = {
    'SERVER': get_param('jira_host'),
    'PROJECT_KEY': get_param('jira_project_key'),
    'ISSUE_TYPE': get_param('jira_issue_type'),
    'CUSTOM_FIELDS': {},                           # custom fields
    'PRIORITIES': {
        'CRITICAL': 'Critical',
        'HIGH': 'High',
        'MEDIUM': 'Medium',
        'LOW': 'Low',
        'INFO': 'Low'
    },
    'DEFAULT_PRIORITY': 'Medium',
    'STYLE_PARAMS': {
        'title': 'Cyphon Alert',
        'titleBGColor': '#dcdcdc',
        'bgColor': '#f5f5f5',
    },
    'INCLUDE_FULL_DESCRIPTION': False,
    'INCLUDE_EMPTY_FIELDS': False,
    'INCLUDE_ALERT_COMMENTS': False,
    'INCLUDE_ALERT_LINK': True,
    'COMMENT_VISIBILITY': {
        'type': 'role',
        'value': ''                     # JIRA role
    },
}

LOGSIFTER = {
    'DEFAULT_MUNGER': 'default',
    'DEFAULT_MUNGER_ENABLED': True,
}

MAILSIFTER = {
    'DEFAULT_MUNGER': 'default',
    'DEFAULT_MUNGER_ENABLED': True,
    'MAIL_COLLECTION': 'postgresql.django_cyphon.django_mailbox_message',
    'EMAIL_CONTENT_PREFERENCES': ('text/plain', 'text/html'),
    'ALLOWED_EMAIL_ATTACHMENTS': ('text/plain', 'application/pdf', 'image/jpeg', 'image/png'),
    'ALLOWED_FILE_EXTENSIONS': ('.txt', '.pdf', '.jpeg', '.jpg', '.png'),
    'ATTACHMENTS_FOLDER': 'attachments/%Y/%m/%d/',
}

MONGODB = {
    'HOST': '{0}:{1}'.format(
        get_param('mongodb_host', 'mongo'),  # e.g., 'localhost'
        get_param('mongodb_port', '27017')),
    'TIMEOUT': 20,
}

NOTIFICATIONS = {
    'PUSH_NOTIFICATION_KEY': '',
    'GCM_SENDER_ID': '',
    'IGNORED_ALERT_LEVELS': ['INFO'],
}

POSTGRES = {
    'NAME': get_param('postgres_db', 'postgres'),
    'USER': get_param('postgres_username', 'postgres'),
    'PASSWORD': get_param('postgres_password', 'postgres'),
    'HOST': get_param('postgres_host', 'postgres'),  # e.g., 'localhost'
    'PORT': get_param('postgres_port', '5432'),
}

PRIVATE_FIELDS = [
    DISTILLERIES['DISTILLERY_KEY'],
    DISTILLERIES['RAW_DATA_KEY'],
    DISTILLERIES['DATE_KEY'],
]

RABBITMQ = {
    'HOST': get_param('rabbitmq_default_host', 'rabbit'),
    'VHOST': get_param('rabbitmq_default_vhost', 'cyphon'),
    'USERNAME': get_param('rabbitmq_default_user', 'guest'),
    'PASSWORD': get_param('rabbitmq_default_pass', 'guest'),
    'EXCHANGE': get_param('rabbitmq_exchange', 'cyphon'),
    'EXCHANGE_TYPE': get_param('rabbitmq_exchange_type', 'direct'),
    'DURABLE': True,
}

SAUCELABS = {
    'USERNAME': get_param('sauce_username'),
    'ACCESS_KEY': get_param('sauce_access_key'),
}

TEASERS = {
    'CHAR_LIMIT': 1000  # Character limit for teaser fields
}

#: Twitter authentication credentials for use in tests
TWITTER = {
    'KEY': get_param('twitter_key'),
    'SECRET': get_param('twitter_secret'),
    'ACCESS_TOKEN': get_param('twitter_access_token'),
    'ACCESS_TOKEN_SECRET': get_param('twitter_access_token_secret'),
}

WAREHOUSES = {
    'DEFAULT_STORAGE_ENGINE': 'elasticsearch'
}
