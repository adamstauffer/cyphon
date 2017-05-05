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
from django.core.exceptions import ObjectDoesNotExist
import pika

# local
from cyphon.transaction import close_connection, close_old_connections
from sifter.logsifter.datachutes.models import DataChute
from sifter.logsifter.datamungers.models import DataMunger
from sifter.logsifter.logchutes.models import LogChute
from sifter.logsifter.logmungers.models import LogMunger

LOGGER = logging.getLogger('receiver')

DATASIFTER = settings.DATASIFTER
BROKER = settings.RABBITMQ
LOGSIFTER = settings.LOGSIFTER


def get_consumer(queue_type=None):
    """

    Parameters
    ----------
    queue_type : str
        Options are 'DATACHUTES', 'LOGCHUTES', 'MONITORS', 'WATCHDOGS'.

    Returns
    -------
    func
        A function for processing a queue of the given type.

    """
    consumers = {
        'DATACHUTES': process_json,
        'LOGCHUTES': process_log,
        'MONITORS': call_monitors,
        'WATCHDOGS': call_watchdogs,
    }
    return consumers.get(queue_type, 'WATCHDOGS')


def consume_queue(queue_type='ALARMS'):
    """
    Creates a queue consumer for RabbitMQ.

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

        consumer_func = get_consumer(queue_type)

        channel.basic_consume(consumer_func,
                              queue=queue_name,
                              no_ack=True)

        channel.start_consuming()

    except Exception as error:
        LOGGER.exception('An error occurred while consuming logs:\n  %s', error)


def process_json(data):
    """

    """
    doc_id = data.get('@uuid')
    collection = data.get('collection')
    saved = False
    enabled_chutes = DataChute.objects.find_enabled()

    LOGGER.info('Processing JSON message %s in %s', doc_id, collection)

    for chute in enabled_chutes:
        result = chute.process(data, doc_id, collection)
        if result:
            saved = True

    if not saved and DATASIFTER['DEFAULT_DATA_CHUTE_ENABLED']:
        default_munger = get_default_munger()
        if default_munger:
            default_munger.process(data, doc_id, collection)


def process_log(data):
    """

    """
    doc_id = data.get('@uuid')
    collection = data.get('collection')
    saved = False
    enabled_chutes = LogChute.objects.find_enabled()

    LOGGER.info('Processing log message %s in %s', doc_id, collection)

    for chute in enabled_chutes:
        result = chute.process(data, doc_id, collection)
        if result:
            saved = True

    if not saved and LOGSIFTER['DEFAULT_LOG_CHUTE_ENABLED']:
        default_munger = get_default_munger()
        if default_munger:
            default_munger.process(data, doc_id, collection)


def call_monitors(data):
    """

    """
    pass


def call_watchdogs(data):
    """

    """
    pass


@close_connection
def process_msg(channel, method, properties, body):
    """
    Callback function for a queue consumer.

    Parameters:
        channel: pika.Channel
        method: pika.spec.Basic.Return
        properties: pika.spec.BasicProperties
        body: str, unicode, or bytes (python 3.x)

    """
    try:
        if not isinstance(body, str):
            body = body.decode('utf-8')

        data = json.loads(body)

        if 'message' in data:
            process_log(data)
        else:
            process_json(data)

    except Exception as error:
        LOGGER.exception('An error occurred while processing the message:\n  %s',
                         body)


def get_default_munger():
    """
    Returns the default LogMunger specified in the site configuration.
    """
    munger_name = LOGSIFTER['DEFAULT_LOG_MUNGER']
    try:
        return LogMunger.objects.get(name=munger_name)
    except ObjectDoesNotExist:
        LOGGER.error('Default LogMunger "%s" is not configured.', munger_name)


@close_old_connections
def create_consumers(queue_type, num):
    """

    """
    kwargs = {'queue_type': queue_type}
    for dummy_num in range(num):
        process = Process(target=consume_queue, kwargs=kwargs)
        process.start()


if __name__ == '__main__':
    try:
        QUEUE_TYPE = sys.argv[1]
    except (IndexError, ValueError):
        QUEUE_TYPE = 'ALARMS'
    try:
        NUM = int(sys.argv[2])
    except (IndexError, ValueError):
        NUM = 1

    create_consumers(QUEUE_TYPE, NUM)
