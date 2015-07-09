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

from nscs.crdserver.openstack.common import log as logging

from cns.crdserver.db import network as network_db
from cns.crdserver.extensions.network import NetworkBase
from cns.crdserver.dispatcher.ofcontroller.network import NetworkDispatcher
from cns.crdserver.plugins import delta
LOG = logging.getLogger(__name__)
import time


class NetworkPlugin(NetworkBase,
                    NetworkDispatcher):
    """
    Implementation of the Crd Core Plugin.
    DB related work is implemented in class NetworkPluginDb
    """
    supported_extension_aliases = ["network"]
    
    def __init__(self):
        self.networkdb = network_db.CrdNetworkDb()
        self.cnsdelta = delta.CnsDelta()
    
    ################ Network API Start ############################
    def create_network(self, context, network):
        segments = network['network']['segments']
        if segments:
            network_type = segments[0]['network_type']
            physical_network = segments[0]['physical_network']
            segmentation_id = segments[0]['segmentation_id']
            network['network']['network_type'] = network_type
            network['network']['physical_network'] = physical_network
            network['network']['segmentation_id'] = segmentation_id
            network['network']['segments'] = ''
        v = self.networkdb.create_network(context, network)
        data = v
        v.update({'operation' : 'create'})
        delta={}
        delta.update({'network_delta':v})
        networkdelta = self.cnsdelta.create_network_delta(context,delta)
        fanoutmsg = {}
        fanoutmsg.update({'method':'create_virtual_network','payload':networkdelta})
        delta={}
        version = networkdelta['version_id']
        delta[version] = fanoutmsg
        self.send_fanout(context,'call_consumer',delta)
        return data

    def update_network(self, context, network_id, network):
        v = self.networkdb.update_network(context, network_id, network)
        data = v
        
        v.update({'operation' : 'update'})
        delta={}
        delta.update({'network_delta':v})
        networkdelta = self.cnsdelta.create_network_delta(context,delta)
        fanoutmsg = {}
        fanoutmsg.update({'method':'update_virtual_network','payload':networkdelta})
        delta={}
        version = networkdelta['version_id']
        delta[version] = fanoutmsg
        #self.send_fanout(context,'call_consumer',delta)
        
        return data

    def delete_network(self, context, network_id):
        v = self.get_network(context,network_id)
        self.networkdb.delete_network(context, network_id)
        v.update({'operation' : 'delete'})
        delta={}
        delta.update({'network_delta':v})
        networkdelta = self.cnsdelta.create_network_delta(context,delta)
        fanoutmsg = {}
        fanoutmsg.update({'method':'delete_virtual_network','payload':networkdelta})
        delta={}
        version = networkdelta['version_id']
        delta[version] = fanoutmsg
        self.send_fanout(context,'call_consumer',delta)

    def get_network(self, context, network_id, fields=None):
        #LOG.debug(_('Get network %s'), network_id)
        return self.networkdb.get_network(context, network_id, fields)

    def get_networks(self, context, filters=None, fields=None):
        #LOG.debug(_('Get networks'))
        return self.networkdb.get_networks(context, filters, fields)
    ################ Network API Start ############################
    
    ################ Subnet API Start ############################
    def create_subnet(self, context, subnet):
        v = self.networkdb.create_subnet(context, subnet)
        data = v
        v.update({'operation' : 'create'})
        delta={}
        delta.update({'subnet_delta':v})
        subnetdelta = self.cnsdelta.create_subnet_delta(context,delta)
        fanoutmsg = {}
        fanoutmsg.update({'method':'create_subnet','payload':subnetdelta})
        delta={}
        version = subnetdelta['version_id']
        delta[version] = fanoutmsg
        self.send_fanout(context,'call_consumer',delta)
        return data

    def update_subnet(self, context, subnet_id, subnet):
        v = self.networkdb.update_subnet(context, subnet_id, subnet)
        data = v
        v.update({'operation' : 'update'})
        delta={}
        delta.update({'subnet_delta':v})
        subnetdelta = self.cnsdelta.create_subnet_delta(context,delta)
        fanoutmsg = {}
        fanoutmsg.update({'method':'update_subnet','payload':subnetdelta})
        delta={}
        version = subnetdelta['version_id']
        delta[version] = fanoutmsg
        self.send_fanout(context,'call_consumer',delta)
        return data

    def delete_subnet(self, context, subnet_id):
        v = self.get_subnet(context, subnet_id)
        self.networkdb.delete_subnet(context, subnet_id)
        v.update({'operation' : 'delete'})
        delta={}
        delta.update({'subnet_delta':v})
        subnetdelta = self.cnsdelta.create_subnet_delta(context,delta)
        fanoutmsg = {}
        fanoutmsg.update({'method':'delete_subnet','payload':subnetdelta})
        delta={}
        version = subnetdelta['version_id']
        delta[version] = fanoutmsg
        self.send_fanout(context,'call_consumer',delta)

    def get_subnet(self, context, subnet_id, fields=None):
        #LOG.debug(_('Get subnet %s'), subnet_id)
        return self.networkdb.get_subnet(context, subnet_id, fields)

    def get_subnets(self, context, filters=None, fields=None):
        #LOG.debug(_('Get subnets'))
        return self.networkdb.get_subnets(context, filters, fields)
    ################ Subnet API Start ############################

    ################ Port API Start ############################
    def create_port(self, context, port):
        time.sleep(2)
        v = self.networkdb.create_port(context, port)
        data = v
        v.update({'operation' : 'create'})
        delta={}
        delta.update({'port_delta':v})
        portdelta = self.cnsdelta.create_port_delta(context,delta)
        fanoutmsg = {}
        fanoutmsg.update({'method':'create_port','payload':portdelta})
        delta={}
        version = portdelta['version_id']
        delta[version] = fanoutmsg
        self.send_fanout(context,'call_consumer',delta)
        
        return data

    def update_port(self, context, port_id, port):
        v = self.networkdb.update_port(context, port_id, port)
        data = v
        v.update({'operation' : 'update'})
        delta={}
        delta.update({'port_delta':v})
        portdelta = self.cnsdelta.create_port_delta(context,delta)
        fanoutmsg = {}
        fanoutmsg.update({'method':'update_port','payload':portdelta})
        delta={}
        version = portdelta['version_id']
        delta[version] = fanoutmsg
        self.send_fanout(context,'call_consumer',delta)
        return data

    def delete_port(self, context, port_id):
        v = self.get_port(context, port_id)
        self.networkdb.delete_port(context, port_id)
        v.update({'operation' : 'delete'})
        delta={}
        delta.update({'port_delta':v})
        portdelta = self.cnsdelta.create_port_delta(context,delta)
        fanoutmsg = {}
        fanoutmsg.update({'method':'delete_port','payload':portdelta})
        delta={}
        version = portdelta['version_id']
        delta[version] = fanoutmsg
        self.send_fanout(context,'call_consumer',delta)

    def get_port(self, context, port_id, fields=None):
        #LOG.debug(_('Get port %s'), port_id)
        return self.networkdb.get_port(context, port_id, fields)

    def get_ports(self, context, filters=None, fields=None):
        #LOG.debug(_('Get ports'))
        return self.networkdb.get_ports(context, filters, fields)
    ################ Port API Start ############################
