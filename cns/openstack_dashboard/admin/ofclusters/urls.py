# Copyright 2013 Freescale Semiconductor, Inc.
# All rights reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


from django.conf.urls import patterns, url, include

from .views import IndexView, CreateClusterView, UpdateClusterView, DetailClusterView, DetailSwitchView, CreateControllerView, CreateSwitchView

CLUSTERS = r'^(?P<cluster_id>[^/]+)/%s$'

urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^create/$', CreateClusterView.as_view(), name='create'),
    url(CLUSTERS % 'update', UpdateClusterView.as_view(), name='update'),
    url(CLUSTERS % 'detail', DetailClusterView.as_view(), name='detail'),
    url(r'^(?P<cluster_id>[^/]+)/switches/(?P<controller_id>[^/]+)$', DetailSwitchView.as_view(), name='switches'),
    url(CLUSTERS % 'createofc', CreateControllerView.as_view(), name='createofc'),
    url(r'^(?P<cluster_id>[^/]+)/switches/(?P<controller_id>[^/]+)/createswitch$', CreateSwitchView.as_view(), name='createswitch'),
    )
