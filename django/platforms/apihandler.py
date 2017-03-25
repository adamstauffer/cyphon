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
# """
# Defines a base class for API handler classes.
# """

# # third party
# from django.utils.functional import cached_property

# # local
# from aggregator.funnels.models import Funnel
# from cyphon.baseclass import BaseClass
# from warehouses.models import Warehouse, Collection


# class ApiResponse(object):
#     """
#     Describes an API response.
#     """
#     def __init__(self, status_code=None, data=None):
#         self.status_code = status_code
#         self.data = data or []


# class ApiHandler(BaseClass):
#     """
#     Base class for handling social media APIs.

#     Attributes:
#         emissary: a Plumber object for providing a KeySet and Meter for the API
#         task: the task that should be performed

#         distillery: a Distillery object for saving data from the API

#     """

#     def __init__(self, emissary, porter):
#         self.emissary = emissary
#         # self.task = task
#         self.porter = None # handles result

#     # def __str__(self):
#     #     return 'distillery_%s__emissary_%s' % (self.distillery.pk,
#     #                                           self.emissary.pk)
#     # @cached_property
#     # def __keyset(self):
#     #     """
#     #     Returns the KeySet used to access the API.
#     #     """
#     #     return self.emissary.keyset

#     # @property
#     # def keyset(self):
#     #     """
#     #     Returns the Condenser used to store data from the API in the
#     #     Distillery's Bottle.
#     #     """
#     #     return self.__keyset

#     @cached_property
#     def __bottle(self):
#         """
#         Returns the Bottle used to store distilled data from the API.
#         """
#         return self.distillery.get_bottle()

#     @cached_property
#     def __distillery_warehouse(self):
#         """
#         Returns the Warehouse used to store distlled data from the API.
#         """
#         return self.distillery.warehouse

#     @cached_property
#     def __raw_data_warehouse(self):
#         """
#         Returns the Warehouse used to store raw data from the API.
#         """
#         # if fields with the same name can potentially store different
#         # data types, just store raw data in the same warehouse
#         # as distilled data
#         if self.__allow_multiple_mappings():
#             return self.__distillery_warehouse

#         # otherwise, raw data needs to be saved in a separate warehouse,
#         # to avoid potential mapping conflicts between raw data fields
#         # and distilled data fields
#         else:
#             kwargs = {
#                 'backend': self.__get_backend(),
#                 'name': self.data_source_label
#             }
#             try:
#                 warehouse = Warehouse.objects.get(**kwargs)
#             except Warehouse.DoesNotExist:
#                 warehouse = Warehouse(**kwargs)
#                 warehouse.save()
#             return warehouse

#     def __get_backend(self):
#         """
#         Returns the platform used to store data from the API. This could
#         be a database platform (such as MongoDB) or a search engine
#         (such as Elasticsearch).
#         """
#         return self.__distillery_warehouse.backend

#     def __allow_multiple_mappings(self):
#         """
#         Returns a Boolean indicating whether the Warehouse used to store
#         data can accomodate fields that have the same field name but a
#         different field type.
#         """
#         warehouse = self.__distillery_warehouse
#         engine_module = warehouse.get_module()
#         return engine_module.MULTIPLE_FIELD_NAME_MAPPINGS

#     @cached_property
#     def __condenser(self):
#         """
#         Returns the Condenser used to store data from the API in the
#         Distillery's Bottle.
#         """
#         pipe_natural_key = self.pipe_natural_key
#         bottle = self.__bottle
#         condenser = Funnel.objects.get_condenser(
#             bottle_id=bottle,
#             pipe_natural_key=pipe_natural_key
#         )
#         return condenser

#     @property
#     def condenser(self):
#         """
#         Returns the Condenser used to store data from the API in the
#         Distillery's Bottle.
#         """
#         return self.__condenser

#     def __get_emissary_name(self):
#         """
#         Returns the name of the Plumber used to access the API.
#         """
#         return self.emissary.name

#     @property
#     def pipe_natural_key(self):
#         """
#         Returns a tuple representing the natural key for a Pipe.

#         The key is assembled from the name of the class handling the API
#         request and the name of the module in which the class resides.
#         """
#         module_name = self.__module__
#         names = module_name.split('.')
#         package_name = names[-2]
#         class_name = type(self).__name__

#         return (package_name, class_name)

#     @property
#     def data_source_label(self):
#         """
#         Returns a string representing the platform package and class used
#         to access the API, formatted for use as the name of a database,
#         index, collection, or doctype.
#         """
#         keys = [self.pipe_natural_key[0], self.pipe_natural_key[1]]
#         name = '_'.join(keys)
#         return name.lower()

#     @property
#     def raw_data_collection(self):
#         """
#         Returns a Collection in which to save raw data from the API.
#         """
#         return Collection(
#             warehouse=self.__raw_data_warehouse,
#             name=self.data_source_label
#         )

#     def _format_query(self, query):
#         """
#         Takes a ReservoirQuery object and constructs a dictionary of
#         Twitter keyword arguments to use with the Twitter API.
#         """
#         return self._raise_method_not_implemented()

#     def __save_distilled_data(self, data, doc_id):
#         """
#         Takes a dictionary of data, the primary key of the Condenser
#         that should be used to distill the data, and the document id for
#         the document that contains the data, and a string representing
#         the Collection in which the raw data is stored. Adds the
#         document id and the name of the platform from which the data are
#         derived to the data dictionary. Saves the new dictiomary to a
#         database collection in a distilled form. The database collection
#         and the distilled form are determined by the ApiHandler's
#         Distillery.
#         """
#         return self.distillery.save_data(data, self.__condenser, doc_id,
#                                          str(self.raw_data_collection))

#     def __save_raw_data(self, data):
#         """
#         Takes a dictionary of data and saves it to the database collection
#         assigned to the API platform.
#         """
#         return self.raw_data_collection.insert(data)

#     def save_data(self, data):
#         """
#         Takes a dictionary and saves it in its raw form in the database
#         collection for the platform, and saves it in its distilled form
#         in the database collection used by the ApiHandler's Distillery.
#         Returns the document id of the saved distilled document.
#         """
#         # get DataChutes

#         doc_id = self.__save_raw_data(data)
#         return self.__save_distilled_data(data, doc_id)

#     def bulk_save_data(self, results):
#         """
#         Takes a list of dictionaries and saves them to database collections
#         in raw and distilled forms. Returns a list of document ids for the
#         distilled documents.
#         """
#         doc_ids = []

#         for data in results:
#             doc_id = self.save_data(data)
#             doc_ids.append(doc_id)

#         return doc_ids

#     def process_query(self, query):
#         """
#         Takes a ReservoirQuery and submits it to the API. If the handler is for
#         a non-streaming API, returns an ApiResponse object. This method needs to
#         be implemented in derived classes so it can be customized for specific
#         APIs.
#         """
#         return self.raise_method_not_implemented()

#     def process_response(self, results):
#         """

#         """
#         pass

