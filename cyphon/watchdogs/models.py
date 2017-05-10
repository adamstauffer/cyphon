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
Defines Watchdog, Trigger, and Muzzle classes for generating Alerts.
"""

# standard library
import datetime
import logging

# third party
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

# local
from alarms.models import Alarm, AlarmManager
from alerts.models import Alert
from categories.models import Category
from cyphon.choices import ALERT_LEVEL_CHOICES, TIME_UNIT_CHOICES
from cyphon.transaction import require_lock
from utils.dateutils.dateutils import convert_time_to_whole_minutes
from utils.parserutils.parserutils import get_dict_value
from sifter.datasifter.datasieves.models import DataSieve

_LOGGER = logging.getLogger(__name__)


class WatchdogManager(AlarmManager):
    """
    Adds methods to the default model manager.
    """

    def find_relevant(self, distillery):
        """

        """
        enabled_watchdogs = super(WatchdogManager, self).find_enabled()
        categories = distillery.categories.all()
        queryset = enabled_watchdogs.annotate(
            categories_cnt=models.Count('categories')
        )
        no_categories_q = models.Q(categories_cnt=0)
        shared_categories_q = models.Q(categories__in=categories)

        if categories:
            queryset = queryset.filter(no_categories_q | shared_categories_q)
        else:
            queryset = queryset.filter(no_categories_q)

        return queryset.distinct()


class Watchdog(Alarm):
    """
    Defines a class for inspecting data produced by a Distillery. Used
    to create Alerts when appropriate.

    Attributes
    ----------
    name : str
        A |str| representing the name of the Watchdog.

    enabled : bool
        A |bool| indicating whether the Watchdog is active.

    categories : `QuerySet` of `Categories`

    groups : `QuerySet` of `Groups`

    """
    categories = models.ManyToManyField(
        Category,
        related_name='watchdogs',
        related_query_name='watchdog',
        blank=True,
        help_text=_('Restrict coverage to Distilleries with these Categories. '
                    'If no Categories are selected, all Distilleries will '
                    'be covered.')
    )

    objects = WatchdogManager()

    def __str__(self):
        return self.name

    def _is_muzzled(self, alert):
        """
        Takes an Alert and returns True if it should be suppressed.
        Otherwise, returns False.
        """
        if hasattr(self, 'muzzle') and self.muzzle.enabled:
            return self.muzzle.is_match(alert)
        else:
            return False

    def _create_alert(self, level, distillery, doc_id):
        """
        Takes an alert level, a distillery, and a document id. Returns
        an Alert object.
        """
        return Alert(
            level=level,
            alarm=self,
            distillery=distillery,
            doc_id=doc_id,
        )

    @transaction.atomic
    @require_lock(Alert, 'ACCESS EXCLUSIVE')
    def _process_alert(self, alert):
        """

        """
        if not self._is_muzzled(alert):
            alert.save()
            return alert

    def inspect(self, data):
        """Return an Alert level for a document.

        Parameters
        ----------
        data: dict
            The document to be inspected.

        Returns
        -------
        |str| or |None|
            If the data matches one of the Watchdog's |triggers|,
            returns the :attr:`~Trigger.alert_level` for that Ttrigger|.
            Otherwise, returns |None|.

        """
        triggers = self.triggers.all()
        for trigger in triggers:
            if trigger.is_match(data):
                return trigger.alert_level

    def process(self, doc_obj):
        """Generate an |Alert| for a document if appropriate.

        Parameters
        ----------
        doc_obj: |DocumentObj|
            Data and related information about the document to be
            inspected.

        Returns
        -------
        |Alert| or |None|
            Returns an |Alert| if the Watchdog is enabled and the
            document matches one of the Watchdog's |Triggers|.
            Otherwise, returns |None|.

        """
        if self.enabled:
            alert_level = self.inspect(doc_obj.data)
            if alert_level is not None:
                alert = self._create_alert(alert_level, doc_obj.distillery,
                                           doc_obj.doc_id)
                return self._process_alert(alert)


class TriggerManager(models.Manager):
    """Manage |Trigger| objects.

    Adds methods to the default Django model manager.
    """

    def get_by_natural_key(self, watchdog_name, sieve_name):
        """Get a |Trigger| by its natural key.

        Allows retrieval of a |Warehouse| by its natural key instead of
        its primary key.

        Parameters
        ----------
        watchdog_name : str
            The name of the |Watchdog| to which the Trigger belongs.

        sieve_name : str
            The name of the |DataSieve| associated with the Trigger.

        Returns
        -------
        |Trigger|
            The |Trigger| associated with the natural key.

        """
        try:
            watchdog = Watchdog.objects.get_by_natural_key(watchdog_name)
            sieve = DataSieve.objects.get_by_natural_key(sieve_name)
            return self.get(watchdog=watchdog, sieve=sieve)
        except ObjectDoesNotExist:
            _LOGGER.error('%s %s:%s does not exist',
                          self.model.__name__, watchdog_name, sieve_name)


class Trigger(models.Model):
    """
    Defines conditions under which a |Watchdog| will generate an |Alert|.

    Attributes
    ----------
    watchdog : Watchdog
        The |Watchdog| associated with the Trigger.

    sieve : DataSieve
        A |DataSieve| for examining data.

    alert_level : str
        A |str| representing an |Alert| level to be returned if the
        Trigger's sieve returns ``True`` for the data examined. Options are
        constrained to |ALERT_LEVEL_CHOICES|.

    rank : int
        An |int| representing the order of the Trigger in a |Watchdog|
        inspection. Triggers are evaluated in ascending order (the lowest
        rank first)

    """
    watchdog = models.ForeignKey(
        Watchdog,
        related_name='triggers',
        related_query_name='trigger',
        verbose_name=_('watchdog'),
        help_text=_('The Watchdog with which this trigger is associated.')
    )
    sieve = models.ForeignKey(
        DataSieve,
        related_name='sieves',
        related_query_name='sieve',
        help_text=_('The DataSieve used to inspect the data during this step.')
    )
    alert_level = models.CharField(
        max_length=255,
        choices=ALERT_LEVEL_CHOICES,
        help_text=_('The Alert level to be returned if the DataSieve returns True '
                    'for the data examined.')
    )
    rank = models.IntegerField(
        default=0,
        help_text=_('An integer representing the order of this step in the '
                    'Inspection. Steps are performed in ascending order, '
                    'with the lowest number examined first.')
    )

    objects = TriggerManager()

    class Meta:
        ordering = ['rank']
        unique_together = [('watchdog', 'sieve'), ('watchdog', 'rank')]

    def __str__(self):
        try:
            return '%s <- %s (rank: %s)' % \
                   (self.sieve, self.alert_level, self.rank)
        except ObjectDoesNotExist:
            return super(Trigger, self).__str__()

    def is_match(self, data):
        """
        Takes a data dictionary and returns a Boolean indicating whether
        it matches the Trigger's DataSieve.
        """
        return self.sieve.is_match(data)


class Muzzle(models.Model):
    """
    Defines parameters for throttling the rate at which a |Watchdog|
    generates |Alerts|.

    Attributes
    ----------
    watchdog : Watchdog
        The |Watchdog| to be muzzled.

    matching_fields : str
        A comma-separated string of field names. Defines fields in an
        Alert's |Alert.data| whose values should be used to identify duplicate
        |Alerts|.

    time_interval : int
        A positive |int| that defines the length of time within which
        generation of duplicate |Alerts| should be supressed.

    time_unit : str
        The time units for the ``time_interval``. Options are
        constrained to |TIME_UNIT_CHOICES|.

    enabled : bool
        A |bool| indicating whether the Muzzle is enabled.

    """
    watchdog = models.OneToOneField(Watchdog, primary_key=True,
                                    help_text=_('The Watchdog to be muzzled.'))
    matching_fields = models.CharField(
        max_length=255,
        help_text=_('A comma-separated string of field names. Defines '
                    'data fields whose values should be used to identify '
                    'duplicate Alerts.')
    )
    time_interval = models.PositiveIntegerField(
        help_text=_('The length of time within which generation of '
                    'duplicate Alerts should be supressed.')
    )
    time_unit = models.CharField(
        max_length=3,
        choices=TIME_UNIT_CHOICES,
        help_text=_('The units of the time interval.')
    )
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return str(self.watchdog)

    def _get_fields(self):
        """
        Returns a list of field names created from the Muzzle's
        matching_fields.
        """
        fields = self.matching_fields.split(',')
        cleaned_fields = []

        for field in fields:
            cleaned_field = field.strip()
            if cleaned_field != '':
                cleaned_fields.append(cleaned_field)

        return cleaned_fields

    def _get_start_time(self):
        """
        Returns a DateTime object equal to the current time minus the
        Muzzle's time_interval.
        """
        minutes = convert_time_to_whole_minutes(self.time_interval,
                                                self.time_unit)
        return timezone.now() - datetime.timedelta(minutes=minutes)

    def _get_filtered_alerts(self, alert):
        """
        Takes an Alert and returns a queryset of Alerts with the same
        level and distillery that were generated within the Muzzle's
        time frame.
        """
        time = self._get_start_time()
        return Alert.objects.filter(
            created_date__gte=time,
            level=alert.level,
            distillery=alert.distillery,
            alarm_type=alert.alarm_type,
            alarm_id=alert.alarm_id
        ).order_by('created_date')

    def is_match(self, alert):
        """
        Takes an Alert and returns a Boolean indicating whether the
        Alert duplicates a previous Alert within the Muzzle's time frame.
        """
        fields = self._get_fields()
        alerts = self._get_filtered_alerts(alert)
        new_data = alert.saved_data
        for old_alert in alerts:
            match = True
            old_data = old_alert.data
            for field in fields:
                new_data_val = get_dict_value(field, new_data)
                old_data_val = get_dict_value(field, old_data)
                if new_data_val != old_data_val:
                    match = False
                    break
            if match:
                old_alert.add_incident()
                return True

        return False
