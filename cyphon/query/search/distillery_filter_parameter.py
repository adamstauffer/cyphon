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

# standard library
import re

# local
from distilleries.models import Distillery
from warehouses.models import Collection, Warehouse
from .search_parameter import SearchParameter, SearchParameterType


class DistilleryFilterParameter(SearchParameter):
    """
    Class representing a search query parameter that wants to filter
    the distilleries it searches through.

    Attributes
    ----------
    filter : str
        String representation of distilleries to filter.

    collection : str
        Name of a collection(s) to search for related distilleries.

    warehouse : str
        Name of the warehouse(s) to search for related distilleries.

    distilleries : django.db.models.query.QuerySet
        Matching distillery objects.

    """

    FILTER_REGEX = re.compile(r'^@source=(?P<filter>[\w.*]+)?$')
    """RegExp

    Regex used to get the distillery filter value from the parameter string.
    """

    FILTER_GROUPS_REGEX = re.compile(
        r'^(?P<warehouse>\*|\w+)\.(?P<collection>\*|\w+)$',
    )
    """RegExp

    Regex used to separate the warehouse name search from the collection
    name search.
    """

    INVALID_PARAMETER = 'Invalid parameter string.'
    """str

    Errors message explaining that the given parameter string is invalid.
    """

    FILTER_VALUE_IS_EMPTY = 'Distillery filter value is empty.'
    """str

    Error message explaining that the string value to filter distilleries
    with is an empty string.
    """

    INVALID_FILTER = 'Invalid filter value.'
    """str

    Error message explaining that the parsed string value to filter
    distilleries with is invalid.
    """

    CANNOT_FIND_WAREHOUSE = 'Cannot find warehouse that matches name `{}`.'
    """str

    Error message explaining that the given warehouse name does not exist.
    """

    CANNOT_FIND_COLLECTION = 'Cannot find collection that matches name `{}`.'
    """str

    Error message explaining that the given collection name does not exist.
    """

    NO_MATCHING_DISTILLERIES = 'There were no matching distilleries for `{}`.'
    """str

    Error message explaining that the distillery filter returned
    no distilleries.
    """

    WILDCARD = '*'
    """str

    String representation explaining that all warehouse/collection names
    should be included in the search.
    """

    def __init__(self, index, parameter, user):
        """Constructor for DistilleryFilterParameter.

        Parameters
        ----------
        index : int
            Index of this search parameter in the search query string.
        parameter : str
            String representation of this parameter.
        user : appusers.models.AppUser
        """
        super(DistilleryFilterParameter, self).__init__(
            index,
            parameter,
            SearchParameterType.DISTILLERY,
        )
        self.filter = self._get_filter(parameter)

        if not self.is_valid():
            return

        filter_match = self._get_filter_match(self.filter)

        if not self.is_valid():
            return

        self.collection = filter_match.group('collection')
        self.warehouse = filter_match.group('warehouse')
        self.distilleries = self._get_distilleries(
            self.warehouse,
            self.collection,
            user,
        )

    def _get_filter(self, parameter):
        """Return the distillery filter value from the parameter string.

        If parameter or distillery filter value is invalid, it also adds
        those errors to the parameter.

        Parameters
        ----------
        parameter : str
            String representation of this parameter.

        Returns
        -------
        str
            String representation of the distilleries to filter.

        """
        match_object = DistilleryFilterParameter.FILTER_REGEX.match(parameter)

        if match_object is None:
            self._add_error(DistilleryFilterParameter.INVALID_PARAMETER)
            return None

        distillery_filter = match_object.group('filter')

        if distillery_filter is None:
            self._add_error(DistilleryFilterParameter.FILTER_VALUE_IS_EMPTY)
            return None

        return distillery_filter

    def _get_filter_match(self, distillery_filter):
        """Return the match object of the distillery filter value.

        Parameters
        ----------
        distillery_filter : str
            String representation of the distilleries to filter.

        Returns
        -------
        MatchObject
            Regex match object that contains the collection and warehouse
            names to retrieve related distilleries from.

        """
        match_object = DistilleryFilterParameter.FILTER_GROUPS_REGEX.match(
            distillery_filter,
        )

        if match_object is None:
            self._add_error(DistilleryFilterParameter.INVALID_FILTER)
            return None

        return match_object

    def _get_collections_by_warehouse(self, warehouse):
        """Return the pks of the collections related to the warehouse name.

        If the warehouse value is a wildcard it returns an empty array.
        If the warehouse name cannot be found, it adds a
        CANNOT_FIND_WAREHOUSE error the the parameter errors.

        Parameters
        ----------
        warehouse : str
            Name of the warehouse(s) to get related collections of.

        Returns
        -------
        list of int
            List of collection primary keys related to the warehouse name.

        """
        if warehouse == DistilleryFilterParameter.WILDCARD:
            return Collection.objects.all()

        warehouses = Warehouse.objects.filter(name=warehouse)

        if not warehouses.count():
            self._add_error(
                DistilleryFilterParameter.CANNOT_FIND_WAREHOUSE.format(
                    warehouse
                )
            )
            return Collection.objects.none()

        return Collection.objects.filter(warehouse__in=warehouses)

    def _get_collections_by_name(self, collection):
        """Return the pks of collections with the given name.

        If the collection is a wildcard, it returns an empty string.
        If the collection cannot be found, it adds a
        CANNOT_FIND_COLLECTION error to the parameter.

        Parameters
        ----------
        collection : str
            Name of the collection(s) to find.

        Returns
        -------
        list of int
            Collection primary keys that match the collection name.

        """
        if collection == DistilleryFilterParameter.WILDCARD:
            return Collection.objects.all()

        collections = Collection.objects.filter(name=collection)

        if not collections.count():
            self._add_error(
                DistilleryFilterParameter.CANNOT_FIND_COLLECTION.format(
                    collection
                )
            )

        return collections

    def _get_collections(self, warehouse, collection):
        collections_by_warehouse = self._get_collections_by_warehouse(warehouse)
        collections_by_name = self._get_collections_by_name(collection)

        return collections_by_warehouse & collections_by_name

    def _get_distilleries(self, warehouse, collection, user):
        """Return the distillery objects related to warehouse/collection names.

        If a related distillery cannot be found, adds a
        NO_MATCHING_DISTILLERIES error to the parameter.

        Parameters
        ----------
        warehouse : str
            Warehouse name to get related distilleries with.

        collection : str
            Collection name to get related distilleries with.

        user: appusers.models.AppUser

        Returns
        -------
        list of Distillery
            Distilleries related to the given warehouse/collection names.

        """
        collections = self._get_collections(warehouse, collection)

        if not self.is_valid():
            return Distillery.objects.none()

        distillery_qs = Distillery.objects.all()

        if not user.is_staff:
            distillery_qs = distillery_qs.filter(company=user.company)

        distilleries_qs = distillery_qs.filter(
            collection__in=collections.values_list('id', flat=True),
        )

        if not distilleries_qs.count():
            self._add_error(DistilleryFilterParameter.NO_MATCHING_DISTILLERIES)

        return distilleries_qs

    def as_dict(self):
        """Return a JSON serializable representation of this object.

        Returns
        -------
        dict

        """
        info = super(DistilleryFilterParameter, self).as_dict()
        distillery_names = [
            str(distillery)
            for distillery
            in self.distilleries
        ]
        info.update({
            'filter': self.filter,
            'collection': self.collection,
            'warehouse': self.warehouse,
            'distilleries': distillery_names,
        })

        return info
