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
Defines views for Actions.
"""

# third party
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated

# local
from alerts.models import Alert
from cyphon.views import CustomModelViewSet
from responder.dispatches.serializers import DispatchSerializer
from .models import Action
from .serializers import ActionSerializer, ActionRunSerializer


class ActionViewSet(CustomModelViewSet):
    """
    REST API for Contexts.
    """
    queryset = Action.objects.all()
    custom_filter_backends = ['responder.actions.filters.ActionFilterBackend']
    permission_classes = [IsAuthenticated, ]
    serializers = {
        'run': ActionRunSerializer,
        'default': ActionSerializer
    }

    @staticmethod
    def _get_alert(alert_id):
        """
        Takes an Alert primary key and returns the corresponding Alert
        object.
        """
        return Alert.objects.get(pk=alert_id)

    @staticmethod
    def _serialize_dispatch(dispatch, request):
        """
        Takes a Dispatch and an HttpRequest are returns a dictionary.
        """
        return DispatchSerializer(
            dispatch,
            context={'request': request}
        ).data

    def get_serializer_class(self):
        """
        Overrides the class method to get the serializer for the view.
        """
        return self.serializers.get(self.action, self.serializers['default'])

    @detail_route(methods=['post'], url_path='run')
    def run(self, request, pk=None):
        """

        """
        action = self.get_object()
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)

        if serializer.is_valid():
            alert_id = serializer.validated_data['alert']
            alert = self._get_alert(alert_id)
            dispatch = action.get_dispatch(user=request.user, alert=alert)
            result = self._serialize_dispatch(dispatch, request)
            return Response(result)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
