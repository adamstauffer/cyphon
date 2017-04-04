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
from sifter.logsifter.logchutes.models import LogChute
from sifter.logsifter.logmungers.models import LogMunger

LOGGER = logging.getLogger('receiver')

LOGSIFTER = settings.LOGSIFTER
BROKER = settings.RABBITMQ


def consume_logs():
    """
    Creates a queue consumer for RabbitMQ.
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
        routing_key = BROKER['ROUTING_KEY']
        durable = BROKER['DURABLE']
        queue_name = BROKER['QUEUE_NAME']

        channel.exchange_declare(exchange=exchange,
                                 type=exchange_type,
                                 durable=durable)

        channel.queue_declare(queue=queue_name)

        channel.queue_bind(exchange=exchange,
                           queue=queue_name,
                           routing_key=routing_key)

        LOGGER.info('Waiting for logs')
        # print(' [*] Waiting for logs. To exit press CTRL+C')

        channel.basic_consume(process_msg,
                              queue=queue_name,
                              no_ack=True)

        channel.start_consuming()

    except Exception as error:
        LOGGER.exception('An error occurred while consuming logs:\n  %s', error)


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

        doc = json.loads(body)
        data = doc.get('message')
        doc_id = doc.get('@uuid')
        collection = doc.get('collection')
        saved = False
        enabled_chutes = LogChute.objects.find_enabled()

        LOGGER.info('Processing message %s in %s', doc_id, collection)

        for chute in enabled_chutes:
            result = chute.process(data, doc_id, collection)
            if result:
                saved = True

        if not saved and LOGSIFTER['DEFAULT_LOG_CHUTE_ENABLED']:
            default_munger = get_default_munger()
            if default_munger:
                default_munger.process(data, doc_id, collection)

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
def create_consumers(num):
    """

    """
    for dummy_num in range(num):
        process = Process(target=consume_logs)
        process.start()


if __name__ == '__main__':
    try:
        NUM = int(sys.argv[1])
    except (IndexError, ValueError):
        NUM = 1

    create_consumers(NUM)
