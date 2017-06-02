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

# third party
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render



@login_required(login_url='/login/')
def application(request):
    """
    Returns an html template for Cyphon with the necessary variables and
    resources to make it run.
    """
    css_url = settings.CYCLOPS['CDN_FORMAT'].format(
        settings.CYCLOPS['VERSION'],
        'css',
    )
    js_url = settings.CYCLOPS['CDN_FORMAT'].format(
        settings.CYCLOPS['VERSION'],
        'js',
    )
    css_file = '{0}/{1}'.format(
        settings.CYCLOPS['LOCAL_FOLDER_NAME'],
        settings.CYCLOPS['LOCAL_CSS_FILENAME'],
    )
    js_file = '{0}/{1}'.format(
        settings.CYCLOPS['LOCAL_FOLDER_NAME'],
        settings.CYCLOPS['LOCAL_JS_FILENAME'],
    )

    return render(request, 'cyclops/app.html', {
        'notifications_enabled': settings.NOTIFICATIONS['ENABLED'],
        'mapbox_access_token': settings.CYCLOPS['MAPBOX_ACCESS_TOKEN'],
        'local_assets_enabled': settings.CYCLOPS['LOCAL_ASSETS_ENABLED'],
        'cyclops_version': settings.CYCLOPS['VERSION'],
        'css_file': css_file,
        'js_file': js_file,
        'css_url': css_url,
        'js_url': js_url,
    })

def manifest(request):
    """
    Returns the manifest.json necessary for push notifications.
    """
    return JsonResponse({
        'gcm_sender_id': settings.NOTIFICATIONS['GCM_SENDER_ID'],
        'manifest_version': 2,
        'name': 'Cyphon Push Notifications',
        'version': '0.2',
    })
