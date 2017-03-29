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
Tests the Watchdog and Triigger classes.
"""

# standard library
import logging
from unittest.mock import Mock, patch
import threading

# third party
from django.test import TestCase, TransactionTestCase 

# local
from alerts.models import Alert
from distilleries.models import Distillery
from tests.fixture_manager import get_fixtures
from watchdogs.models import Watchdog, Trigger, Muzzle


DOC_ID = '666f6f2d6261722d71757578'

DATA = {
    '_meta': {
        'priority': 'HIGH',
    },
    '_raw_data': {
        'backend': 'mongodb',
        'distillery': 'test',
        'doc_id': DOC_ID
    },
    'subject': '[CRIT-111]'
}


class WatchdogBaseTestCase(TestCase):
    """
    Tests the Watchdog class.
    """
    fixtures = get_fixtures(['watchdogs', 'distilleries'])

    doc_id = DOC_ID
    data = DATA

    @classmethod
    def setUpClass(cls):
        super(WatchdogBaseTestCase, cls).setUpClass()
        logging.disable(logging.ERROR)

    @classmethod
    def tearDownClass(cls):
        logging.disable(logging.NOTSET)
        super(WatchdogBaseTestCase, cls).tearDownClass()

    def setUp(self):
        self.distillery = Distillery.objects.get_by_natural_key('mongodb',
                                                                'test_database',
                                                                'test_docs')
        self.email_wdog = Watchdog.objects.get_by_natural_key('inspect_emails')
        self.log_wdog = Watchdog.objects.get_by_natural_key('inspect_logs')


class WatchdogManagerTestCase(WatchdogBaseTestCase):
    """
    Tests the WatchdogManager class.
    """

    def test_find_relvnt_no_category(self):
        """
        Tests the find_relevant method for a Distillery that is not
        associated with any categories.
        """
        distillery = Distillery.objects.get_by_natural_key('mongodb',
                                                           'test_database',
                                                           'test_posts')
        relevant_watchdogs = Watchdog.objects.find_relevant(distillery)
        self.assertEqual(relevant_watchdogs.count(), 1)
        self.assertEqual(relevant_watchdogs[0].name, 'inspect_logs')
        self.assertEqual(relevant_watchdogs[0].categories.count(), 0)

    def test_find_rlvnt_one_category(self):
        """
        Tests the find_relevant method for a Distillery that is
        associated with one category.
        """
        distillery = Distillery.objects.get_by_natural_key('elasticsearch',
                                                           'test_index',
                                                           'test_docs')
        relevant_watchdogs = Watchdog.objects.find_relevant(distillery)
        self.assertEqual(relevant_watchdogs.count(), 2)
        self.assertEqual(relevant_watchdogs[0].name, 'inspect_emails')
        self.assertTrue(relevant_watchdogs[0].categories.count() > 0)

    def test_find_rlvnt_mult_category(self):
        """
        Tests the find_relevant method for a Distillery that is
        associated with multiple categories.
        """
        distillery = Distillery.objects.get_by_natural_key('elasticsearch',
                                                           'test_index',
                                                           'test_mail')
        relevant_watchdogs = Watchdog.objects.find_relevant(distillery)
        self.assertEqual(relevant_watchdogs.count(), 2)


class WatchdogTestCase(WatchdogBaseTestCase):
    """
    Tests the Watchdog class.
    """

    def test_str(self):
        """
        Tests the __str__ method for the Watchdog class.
        """
        self.assertEqual(str(self.email_wdog), 'inspect_emails')

    def test_inspect_true(self):
        """
        Tests the inspect method for a case that matches a ruleset.
        """
        actual = self.email_wdog.inspect(self.data)
        expected = 'HIGH'
        self.assertEqual(actual, expected)

    def test_inspect_false(self):
        """
        Tests the inspect method for a case that doesn't match a ruleset.
        """
        actual = self.log_wdog.inspect(self.data)
        expected = None
        self.assertEqual(actual, expected)

    def test_create_alert(self):
        """
        Tests the _create_alert method.
        """
        alert = self.email_wdog._create_alert(
            level='HIGH',
            distillery=self.distillery,
            doc_id=self.doc_id
        )
        self.assertEqual(alert.level, 'HIGH')
        self.assertEqual(alert.alarm_type.name, 'watchdog')
        self.assertEqual(alert.alarm_id, self.email_wdog.pk)
        self.assertEqual(alert.alarm, self.email_wdog)
        self.assertEqual(alert.distillery, self.distillery)
        self.assertEqual(alert.doc_id, self.doc_id)

    def test_process_true(self):
        """
        Tests the process method for a case that matches a ruleset.
        """
        with patch('distilleries.models.Distillery.find_by_id',
                   return_value=self.data):
            alert_count = Alert.objects.count()
            actual = self.email_wdog.process(self.data, self.distillery,
                                             self.doc_id)
            self.assertEqual(actual, Alert.objects.get(doc_id=self.doc_id))
            self.assertEqual(actual.level, 'HIGH')
            self.assertEqual(actual.alarm_type.name, 'watchdog')
            self.assertEqual(actual.alarm_id, self.email_wdog.pk)
            self.assertEqual(actual.alarm, self.email_wdog)
            self.assertEqual(actual.distillery, self.distillery)
            self.assertEqual(Alert.objects.count(), alert_count + 1)

    def test_process_muzzled(self):
        """
        Tests the process method for a case that matches a ruleset but
        duplicates a previous Alert when the Watchdog is muzzled.
        """
        with patch('distilleries.models.Distillery.find_by_id',
                   return_value=self.data):
            alert_count = Alert.objects.count()
            alert = self.email_wdog.process(self.data, self.distillery,
                                            self.doc_id)
            # check that a new Alert was created
            self.assertEqual(Alert.objects.count(), alert_count + 1)

            # try to create a duplicate Alert
            results = self.email_wdog.process(self.data, self.distillery,
                                              self.doc_id)

            # make sure no new Alert has been created
            self.assertEqual(Alert.objects.count(), alert_count + 1)
            self.assertEqual(results, None)

            # check that the previous Alert was incremented
            alert = Alert.objects.get(pk=alert.pk)
            self.assertEqual(alert.incidents, 2)

    def test_process_muzzled_disabled(self):
        """
        Tests the process method for a case that matches a ruleset but
        duplicates a previous Alert when the Watchdog is muzzled but the
        is disabled.
        """
        self.email_wdog.muzzle.enabled = False

        with patch('distilleries.models.Distillery.find_by_id',
                   return_value=self.data):
            alert_count = Alert.objects.count()
            alert = self.email_wdog.process(self.data, self.distillery,
                                            self.doc_id)
            # check that a new Alert was created
            self.assertEqual(Alert.objects.count(), alert_count + 1)

            # try to create a duplicate Alert
            self.email_wdog.process(self.data, self.distillery,
                                    self.doc_id)

            # make sure another Alert has been created
            self.assertEqual(Alert.objects.count(), alert_count + 2)

            # check that the previous Alert was not incremented
            alert = Alert.objects.get(pk=alert.pk)
            self.assertEqual(alert.incidents, 1)

    def test_process_not_muzzled(self):
        """
        Tests the process method for a case that matches a ruleset but
        duplicates a previous Alert when the Watchdog is not muzzled.
        """
        watchdog = Watchdog.objects.get(pk=2)
        data = {'message': 'CRIT-400'}
        with patch('distilleries.models.Distillery.find_by_id',
                   return_value=data):
            alert_count = Alert.objects.count()
            alert = watchdog.process(data, self.distillery, self.doc_id)

            # check that a new Alert was created
            self.assertEqual(Alert.objects.count(), alert_count + 1)

            # try to create a duplicate Alert
            watchdog.process(data, self.distillery, self.doc_id)

            # make sure another Alert has been created
            self.assertEqual(Alert.objects.count(), alert_count + 2)

            # check that the previous Alert was not incremented
            alert = Alert.objects.get(pk=alert.pk)
            self.assertEqual(alert.incidents, 1)

    def test_disabled(self):
        """
        Tests the process method for a Watchdog that is disabled.
        """
        self.email_wdog.enabled = False
        result = self.email_wdog.process(self.data, self.distillery,
                                         self.doc_id)
        self.assertEqual(result, None)

    def test_process_false(self):
        """
        Tests the process method for a case that doesn't match a ruleset.
        """
        actual = self.log_wdog.process(self.data, self.distillery,
                                        self.doc_id)
        self.assertEqual(actual, None)
        alerts = Alert.objects.all()
        self.assertEqual(alerts.count(), 0)


class TriggerTestCase(TestCase):
    """
    Tests the Trigger class.
    """

    fixtures = get_fixtures(['watchdogs'])

    @classmethod
    def setUpClass(cls):
        super(TriggerTestCase, cls).setUpClass()
        cls.trigger = Trigger.objects.get(pk=1)

    def test_str(self):
        """
        Tests the __str__ method for a Trigger with a sieve.
        """
        self.assertEqual(str(self.trigger), 'high_priority_email <- HIGH (rank: 0)')

    def test_str_no_sieve(self):
        """
        Tests the __str__ method for a Trigger without a sieve.
        """
        self.assertEqual(str(Trigger()), 'Trigger object')

    def test_is_match(self):
        """
        Tests the is_match method.
        """
        with patch('watchdogs.models.Trigger.sieve') as mock_sieve:
            mock_sieve.is_match = Mock(return_value=True)
            data = {'title': 'test'}
            result = self.trigger.is_match(data)
            mock_sieve.is_match.assert_called_once_with(data)
            self.assertIs(result, True)


class MuzzleTestCase(TestCase):
    """
    Tests the Muzzle class.
    """

    fixtures = get_fixtures(['watchdogs', 'alerts'])

    mock_data = {
        'subject': 'foo',
        'to': 'bar'
    }

    @classmethod
    def setUpClass(cls):
        super(MuzzleTestCase, cls).setUpClass()
        cls.watchdog = Watchdog.objects.get(pk=1)

    def setUp(self):
        self.muzzle = Muzzle.objects.get(pk=1)

    def test_str(self):
        """
        Tests the __str__ method of a Muzzle.
        """
        self.assertEqual(str(self.muzzle), 'inspect_emails')

    def test_get_fields_wo_spaces(self):
        """
        Tests the _get_fields method when no spaces separate the fields.
        """
        actual = self.muzzle._get_fields()
        expected = ['subject', 'to']
        self.assertEqual(actual, expected)

    def test_get_fields_w_spaces(self):
        """
        Tests the _get_fields method when spaces separate the fields.
        """
        self.muzzle.matching_fields = ' message, source_ip '
        actual = self.muzzle._get_fields()
        expected = ['message', 'source_ip']
        self.assertEqual(actual, expected)

    def test_get_fields_single_field(self):
        """
        Tests the _get_fields method for a single field.
        """
        self.muzzle.matching_fields = ' message, '
        actual = self.muzzle._get_fields()
        expected = ['message']
        self.assertEqual(actual, expected)

    def test_is_match_w_no_alerts(self):
        """
        Tests the is_match method when no previous Alerts are in the
        Muzzle's time frame.
        """
        with patch('distilleries.models.Distillery.find_by_id',
                   return_value=self.mock_data):
            alert = Alert.objects.get(pk=1)
            self.assertIs(self.muzzle.is_match(alert), False)

    def test_is_match_w_no_matches(self):
        """
        Tests the is_match method when there are no matching Alerts in
        the Muzzle's time frame.
        """
        alert5 = Alert.objects.get(pk=5)
        alert6 = Alert.objects.get(pk=6)
        alert7 = Alert.objects.get(pk=7)
        alert5.data = {'subject': 'foo', 'to': 'bar1'}
        alert6.data = {'subject': 'foo', 'to': 'bar2'}
        alert7.data = {'subject': 'foo', 'to': 'bar3'}
        with patch('distilleries.models.Distillery.find_by_id'):
            alert8 = Alert.objects.get(pk=8)
            alert8.saved_data = {'subject': 'foo', 'to': 'bar4'}
            with patch('watchdogs.models.timezone.now',
                       return_value=alert8.created_date):
                self.assertIs(self.muzzle.is_match(alert8), False)

    def test_is_match_w_matches(self):
        """
        Tests the is_match method when there is a matching Alert in
        the Muzzle's time frame.
        """
        dup_doc = {'subject': 'foo', 'to': 'bar1'}
        alert5 = Alert.objects.get(pk=5)
        alert6 = Alert.objects.get(pk=6)
        alert5.data = dup_doc
        alert6.data = dup_doc
        alert5.save()
        alert6.save()

        old_alert5_incidents = alert5.incidents
        old_alert6_incidents = alert6.incidents
        with patch('distilleries.models.Distillery.find_by_id'):
            with patch('watchdogs.models.timezone.now',
                       return_value=alert6.created_date):
                new_alert = Alert.objects.get(pk=6)
                new_alert.pk = None
                new_alert.saved_data = dup_doc
                self.assertIs(self.muzzle.is_match(new_alert), True)

        # get fresh instances of Alerts and check that the oldest
        # one was incremented
        alert5 = Alert.objects.get(pk=5)
        alert6 = Alert.objects.get(pk=6)
        self.assertEqual(alert5.incidents, old_alert5_incidents + 1)
        self.assertEqual(alert6.incidents, old_alert6_incidents)


class WatchdogTransactionTestCase(TransactionTestCase):
    """
    Tests the Watchdog class.
    """
    fixtures = get_fixtures(['watchdogs', 'distilleries'])

    doc_id = DOC_ID
    data = DATA

    def setUp(self):
        self.distillery = Distillery.objects.get_by_natural_key('mongodb',
                                                                'test_database',
                                                                'test_docs')
        self.email_wdog = Watchdog.objects.get_by_natural_key('inspect_emails')

    def test_multiprocess_muzzled(self):
        """
        Tests muzzling when multiple duplicate Alerts are being processed
        concurrently.
        """
        with patch('distilleries.models.Distillery.find_by_id',
                   return_value=self.data):
            with patch('alerts.models.Alert._format_title',
                       return_value=self.data['subject']):
                incident_num = 20

                alert_count = Alert.objects.count()

                args = (self.data, self.distillery, self.doc_id)

                alert = self.email_wdog.process(*args)

                # check that a new Alert was created
                self.assertEqual(Alert.objects.count(), alert_count + 1)

                # NOTE: we can't use multiprocessing with Mocks,
                # so we have to settle for using threading to mimic concurrency

                threads = []
                for dummy_index in range(incident_num):
                    new_thread = threading.Thread(target=self.email_wdog.process,
                                                  args=args)
                    threads.append(new_thread)
                    new_thread.start()

                for thread in threads:
                    thread.join()

                # NOTE: we can't check Alert counts because saved Alerts
                # won't be committed in the TransactionTestCase

                # but we can check that the previous Alert was incremented
                alert = Alert.objects.get(pk=alert.pk)
                self.assertEqual(alert.incidents, incident_num + 1)
