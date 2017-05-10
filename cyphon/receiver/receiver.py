#!/usr/bin/env python
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
Provides a queue consumer for RabbitMQ.
"""

# standard library
import json
import logging
import os
import sys
from multiprocessing import Process

# add path to the Cyphon project folder so Cyphon packages can be found
CYPHON_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CYPHON_PATH)
sys.path.append(os.path.dirname(os.path.dirname(CYPHON_PATH)))

# set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cyphon.settings.default')

# add path to virtualenv site packages so required packages can be found
from django.conf import settings
sys.path.append(settings.REQUIREMENTS)

# load models so this module can be called from the command line
import django
django.setup()

# third party
import pika

# local
from cyphon.documents import DocumentObj
from cyphon.transaction import close_connection, close_old_connections
from .consumers import CONSUMERS

LOGGER = logging.getLogger('receiver')

BROKER = settings.RABBITMQ


def _create_doc_obj(body):
    """

    """
    data = json.loads(body)
    doc_id = data.get('@uuid')
    collection = data.get('collection')
    return DocumentObj(data=data, doc_id=doc_id, collection=collection)


@close_connection
def process_msg(channel, method, properties, body, queue_type):
    """Process a message.

    Callback function for a queue consumer.

    Parameters
    ----------
    channel : pika.Channel

    method : pika.spec.Basic.Return

    properties : pika.spec.BasicProperties

    body : str, unicode, or bytes (python 3.x)

    queue_type : str
        Indicates the type of consumer to use. Options are 'DATACHUTES',
        'LOGCHUTES', 'MONITORS', 'WATCHDOGS'.

    """
    try:
        if not isinstance(body, str):
            body = body.decode('utf-8')

        doc_obj = _create_doc_obj(body)
        consumer_func = CONSUMERS[queue_type]
        consumer_func(doc_obj)

    except Exception as error:
        LOGGER.exception('An error occurred while processing the message '
                         '\'%s\':\n  %s', body, error)


def consume_queue(queue_type='WATCHDOGS'):
    """Create a queue consumer for RabbitMQ.

    Parameters
    ----------
    queue_type : str
        Options are 'DATACHUTES', 'LOGCHUTES', 'MONITORS', 'WATCHDOGS'.

    """
    try:
        credentials = pika.PlainCredentials(username=BROKER['USERNAME'],
                                            password=BROKER['PASSWORD'])

        parameters = pika.ConnectionParameters(host=BROKER['HOST'],
                                               virtual_host=BROKER['VHOST'],
                                               credentials=credentials,
                                               connection_attempts=6,
                                               retry_delay=10)

        conn = pika.BlockingConnection(parameters)

        channel = conn.channel()
        exchange = BROKER['EXCHANGE']
        exchange_type = BROKER['EXCHANGE_TYPE']
        durable = BROKER['DURABLE']

        routing_key = BROKER[queue_type]['ROUTING_KEY']
        queue_name = BROKER[queue_type]['QUEUE_NAME']

        channel.exchange_declare(exchange=exchange,
                                 type=exchange_type,
                                 durable=durable)

        channel.queue_declare(queue=queue_name)

        channel.queue_bind(exchange=exchange,
                           queue=queue_name,
                           routing_key=routing_key)

        LOGGER.info('Waiting for messages')
        # print(' [*] Waiting for messages. To exit press CTRL+C')

        channel.basic_consume(process_msg,
                              queue=queue_name,
                              no_ack=True,
                              arguments={'queue_type': queue_type})

        channel.start_consuming()

    except Exception as error:
        LOGGER.exception('An error occurred while consuming messages:\n  %s',
                         error)


@close_old_connections
def create_consumers(queue_type, num):
    """Create one or more queue consumers.

    Parameters
    ----------
    queue_type : str
        Indicates how the messages will be processed. Options are
        'DATACHUTES', 'LOGCHUTES', 'MONITORS', 'WATCHDOGS'.

    num : str
        A string representation of an integer representing the number of
        consumers to spawn.

    """
    kwargs = {'queue_type': queue_type}
    for dummy_num in range(num):
        process = Process(target=consume_queue, kwargs=kwargs)
        process.start()


if __name__ == '__main__':
    try:
        if sys.argv[1] in CONSUMERS:
            _QUEUE_TYPE = sys.argv[1]
    except IndexError:
        _QUEUE_TYPE = 'WATCHDOGS'
    try:
        _NUM = int(sys.argv[2])
    except (IndexError, ValueError):
        _NUM = 1

    create_consumers(_QUEUE_TYPE, _NUM)
