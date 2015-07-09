# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Cisco Systems, Inc.
# Copyright 2012 NEC Corporation
# Copyright 2013 Freescale Semiconductor, Inc.
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

from __future__ import absolute_import

import logging

from cns.crdclient.v2_0 import client as cns_client
from django.utils.datastructures import SortedDict

from horizon.conf import HORIZON_CONFIG

from openstack_dashboard.api import base

LOG = logging.getLogger(__name__)



class CrdAPIDictWrapper(base.APIDictWrapper):

    def set_id_as_name_if_empty(self, length=8):
        try:
            if not self._apidict['name']:
                id = self._apidict['id']
                if length:
                    id = id[:length]
                self._apidict['name'] = '(%s)' % id
        except KeyError:
            pass

    def items(self):
        return self._apidict.items()
        
def crdclient(request):
    LOG.debug('crdcnsclient connection created using token "%s" and url "%s"'
              % (request.user.token.id, base.url_for(request, 'crd')))
    LOG.debug('user_id=%(user)s, tenant_id=%(tenant)s' %
              {'user': request.user.id, 'tenant': request.user.tenant_id})
    c = cns_client.Client(token=request.user.token.id,
                              endpoint_url=base.url_for(request, 'crd'))
    return c

###OF Clusters

class OFCluster(CrdAPIDictWrapper):
    """Wrapper for CRD Openflow Clusters"""
    _attrs = ['name', 'id', 'ca_cert_pem',
              'private_key_pem', 'root_cert_pem',
              'inter_cert_pem', 'created_at', 'deleted_at',
              'updated_at']

    def __init__(self, apiresource):
        super(OFCluster, self).__init__(apiresource)

class OFController(CrdAPIDictWrapper):
    """Wrapper for CRD Openflow Controllers"""
    _attrs = ['name', 'id', 'ip_address',
              'port', 'cell',
              'cluster_id', 'status', 'created_at', 'deleted_at',
              'updated_at']

    def __init__(self, apiresource):
        super(OFController, self).__init__(apiresource)

class LogicalSwitches(CrdAPIDictWrapper):
    """Wrapper for CRD Openflow Logical Switches"""
    _attrs = ['name', 'id', 'ip_address',
              'port', 'certificate_pem', 'private_key_pem',
              'cluster_id', 'cluster_id', 'datapath_id', 'created_at', 'deleted_at',
              'updated_at']

    def __init__(self, apiresource):
        super(LogicalSwitches, self).__init__(apiresource)

def of_cluster_list(request, **params):
    LOG.debug("of_cluster_list(): params=%s" % (params))
    clusters = crdclient(request).list_ofclusters(**params).get('ofclusters')
    return [OFCluster(n) for n in clusters]

def of_cluster_create(request, **kwargs):
    """
    Create a OF Cluster
    """
    LOG.debug("of_cluster_create(): kwargs = %s" % kwargs)
    body = {'ofcluster': kwargs}
    cluster = crdclient(request).create_ofcluster(body=body).get('ofcluster')
    return OFCluster(cluster)

def of_cluster_delete(request, cluster_id):
    LOG.debug("of_cluster_delete(): cluster_id=%s" % cluster_id)
    crdclient(request).delete_ofcluster(cluster_id)

def of_cluster_get(request, cluster_id, **params):
    LOG.debug("of_cluster_get(): cluster_id=%s, params=%s" % (cluster_id, params))
    cluster = crdclient(request).show_ofcluster(cluster_id, **params).get('ofcluster')
    return OFCluster(cluster)

def of_cluster_modify(request, cluster_id, **kwargs):
    LOG.debug("of_cluster_modify(): cluster_id=%s, kwargs=%s" % (cluster_id, kwargs))
    body = {'ofcluster': kwargs}
    cluster = crdclient(request).update_ofcluster(cluster_id,
                                                  body=body).get('ofcluster')
    return OFCluster(cluster)

def of_controller_list(request, **params):
    LOG.debug("of_controller_list(): params=%s" % (params))
    controllers = crdclient(request).list_ofcontrollers(**params).get('ofcontrollers')
    return [OFController(n) for n in controllers]

def of_controller_create(request, **kwargs):
    """
    Create a OF Controller
    """
    LOG.debug("of_controller_create(): kwargs = %s" % kwargs)
    body = {'ofcontroller': kwargs}
    controller = crdclient(request).create_ofcontroller(body=body).get('ofcontroller')
    return OFController(controller)

def of_controller_get(request, controller_id, cluster_id, **params):
    LOG.debug("of_controller_get(): controller_id=%s, params=%s" % (controller_id, params))
    body = {'cluster_id': cluster_id}
    controller = crdclient(request).show_ofcontroller(controller_id, body=body).get('ofcontroller')
    return OFController(controller)

def of_controller_delete(request, cluster_id, controller_id):
    LOG.debug("of_controller_delete(): cluster_id=%s, controller_id=%s" % (cluster_id, controller_id))
    body = {'body':{'cluster_id': cluster_id, 'id': controller_id}}
    crdclient(request).delete_ofcontroller(controller_id, body=body)

def of_switches_list(request, cluster_id, controller_id, **params):
    LOG.debug("of_switches_list(): params=%s" % (params))
    switches = crdclient(request).list_logicalswitchs(cluster_id, controller_id, **params).get('logicalswitchs')
    return [LogicalSwitches(n) for n in switches]

def of_switch_delete(request, cluster_id, controller_id, switch_id):
    LOG.debug("of_switch_delete(): cluster_id=%s, controller_id=%s, switch_id=%s" % (cluster_id, controller_id, switch_id))
    body = {'body':{'cluster_id': cluster_id, 'controller_id': controller_id, 'id': switch_id}}
    crdclient(request).delete_logicalswitch(switch_id, body=body)

def of_switch_create(request, **kwargs):
    """
    Create a OF Logical Switch
    """
    LOG.debug("of_switch_create(): kwargs = %s" % kwargs)
    body = {'logicalswitch': kwargs}
    switch = crdclient(request).create_logicalswitch(body=body).get('logicalswitchs')
    return LogicalSwitches(switch)