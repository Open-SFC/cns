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
from nscs.crdservice.db import db_base_plugin_v2
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.orm import exc, relationship, backref
import netaddr
from nscs.crdservice.db import sqlalchemyutils
from nscs.crdservice.api.v2 import attributes
from nscs.crdservice.common import exceptions as q_exc
from nscs.crdservice.db import model_base
from nscs.crdservice.openstack.common import log as logging
from nscs.crdservice.openstack.common import uuidutils
from nscs.crdservice.common import utils
from nscs.crdservice.openstack.common import timeutils
from nscs.crdservice.db import api as db
from oslo.config import cfg
import datetime
import uuid




LOG = logging.getLogger(__name__)

class HasTenant(object):
    """Tenant mixin, add to subclasses that have a tenant."""

    # NOTE(jkoelker) tenant_id is just a free form string ;(
    tenant_id = sa.Column(sa.String(255))


class HasId(object):
    """id mixin, add to subclasses that have an id."""

    id = sa.Column(sa.String(36),
                   primary_key=True,
                   default=uuidutils.generate_uuid)
    

    
class cns_compute_delta(model_base.BASEV2, HasId):
    compute_id = sa.Column(sa.Integer, nullable=False)
    hostname = sa.Column(sa.String(255), nullable=False)
    ip_address = sa.Column(sa.String(64))
    created_at = sa.Column(sa.DateTime)
    ovs_port = sa.Column(sa.String(64))
    datapath_id = sa.Column(sa.String(255))
    datapath_name = sa.Column(sa.String(255))
    data_ip = sa.Column(sa.String(255))
    switch = sa.Column(sa.String(255))
    domain = sa.Column(sa.String(255))
    subject_name = sa.Column(sa.String(255))
    status = sa.Column(sa.String(16))
    operation = sa.Column(sa.String(255), nullable=False)
    logged_at = sa.Column(sa.DateTime, default=datetime.datetime.now, nullable=False)
    version_id = sa.Column(sa.Integer, sa.ForeignKey('crd_versions.runtime_version'), nullable=False)
    
class cns_network_delta(model_base.BASEV2, HasId, HasTenant):
    """Represents a v2 neutron network."""
    name = sa.Column(sa.String(255))
    network_id = sa.Column(sa.String(36), nullable=False)
    network_type = sa.Column(sa.String(255))
    segmentation_id = sa.Column(sa.Integer())
    physical_network = sa.Column(sa.String(255))
    router_external = sa.Column(sa.Boolean)
    status = sa.Column(sa.String(16))
    admin_state_up = sa.Column(sa.Boolean)
    vxlan_service_port = sa.Column(sa.String(10))
    operation = sa.Column(sa.String(255), nullable=False)
    user_id = sa.Column(sa.String(36),nullable=False)
    logged_at = sa.Column(sa.DateTime, default=datetime.datetime.now, nullable=False)
    version_id = sa.Column(sa.Integer, sa.ForeignKey('crd_versions.runtime_version'), nullable=False)
    
    
class cns_subnet_delta(model_base.BASEV2, HasId, HasTenant):
    name = sa.Column(sa.String(255))
    subnet_id = sa.Column(sa.String(36), nullable=False)
    network_id = sa.Column(sa.String(36))
    ip_version = sa.Column(sa.Integer)
    cidr = sa.Column(sa.String(64))
    gateway_ip = sa.Column(sa.String(64))
    dns_nameservers = sa.Column(sa.String(255))
    allocation_pools = sa.Column(sa.String(255))
    host_routes = sa.Column(sa.String(255))
    operation = sa.Column(sa.String(255), nullable=False)
    user_id = sa.Column(sa.String(36),nullable=False)
    logged_at = sa.Column(sa.DateTime, default=datetime.datetime.now, nullable=False)
    version_id = sa.Column(sa.Integer, sa.ForeignKey('crd_versions.runtime_version'), nullable=False)
    
class cns_port_delta(model_base.BASEV2, HasId, HasTenant):
    name = sa.Column(sa.String(255))
    port_id = sa.Column(sa.String(36), nullable=False)
    network_id = sa.Column(sa.String(36))
    subnet_id = sa.Column(sa.String(36))
    mac_address = sa.Column(sa.String(32))
    device_id = sa.Column(sa.String(255))
    ip_address = sa.Column(sa.String(64))
    admin_state_up = sa.Column(sa.Boolean())
    status = sa.Column(sa.String(16))
    device_owner = sa.Column(sa.String(255))
    security_groups = sa.Column(sa.String(255))
    operation = sa.Column(sa.String(255), nullable=False)
    user_id = sa.Column(sa.String(36),nullable=False)
    logged_at = sa.Column(sa.DateTime, default=datetime.datetime.now, nullable=False)
    version_id = sa.Column(sa.Integer, sa.ForeignKey('crd_versions.runtime_version'), nullable=False)
    
class cns_instance_delta(model_base.BASEV2, HasId, HasTenant):
    display_name = sa.Column(sa.String(255))
    instance_id = sa.Column(sa.String(36))
    user_id = sa.Column(sa.String(36))
    state_description = sa.Column(sa.String(255))
    state = sa.Column(sa.String(255))
    created_at = sa.Column(sa.DateTime)
    launched_at = sa.Column(sa.String(50))
    host = sa.Column(sa.String(50))
    type = sa.Column(sa.String(50))
    reservation_id = sa.Column(sa.String(50))
    operation = sa.Column(sa.String(255), nullable=False)
    logged_at = sa.Column(sa.DateTime, default=datetime.datetime.now, nullable=False)
    version_id = sa.Column(sa.Integer, sa.ForeignKey('crd_versions.runtime_version'), nullable=False)
    
class cns_nwport_delta(model_base.BASEV2, HasId):
    nwport_id = sa.Column(sa.String(36))
    name = sa.Column(sa.String(255), nullable=False)
    network_type = sa.Column(sa.String(64))
    ip_address = sa.Column(sa.String(64))
    data_ip = sa.Column(sa.String(64))
    bridge = sa.Column(sa.String(64))
    vxlan_vni = sa.Column(sa.String(3))
    vxlan_udpport = sa.Column(sa.String(5))
    vlan_id = sa.Column(sa.String(5))
    ovs_port = sa.Column(sa.String(5))
    flow_type = sa.Column(sa.String(64))
    local_data_ip = sa.Column(sa.String(64))
    host = sa.Column(sa.String(64))
    operation = sa.Column(sa.String(255), nullable=False)
    logged_at = sa.Column(sa.DateTime, default=datetime.datetime.now, nullable=False)
    version_id = sa.Column(sa.Integer, sa.ForeignKey('crd_versions.runtime_version'), nullable=False) 
   
class CnsDeltaDb(db_base_plugin_v2.CrdDbPluginV2):
    
    
    def _make_network_delta_dict(self, networkdelta, fields=None):
        res = {'tenant_id': networkdelta['tenant_id'],
               'id': networkdelta['id'],
               'name': networkdelta['name'],
               'network_id': networkdelta['network_id'],
               'network_type': networkdelta['network_type'],
               'segmentation_id': networkdelta['segmentation_id'],
               'router_external': networkdelta['router_external'],
               'vxlan_service_port': networkdelta['vxlan_service_port'],
               'status': networkdelta['status'],
               'admin_state_up': networkdelta['admin_state_up'],
               'operation': networkdelta['operation'],
               'user_id': networkdelta['user_id'],
               'logged_at': networkdelta['logged_at'],
               'version_id': networkdelta['version_id']}
        return self._fields(res, fields)
        
        
    def get_network_deltas(self, context, filters=None, fields=None):
        return self._get_collection(context, cns_network_delta,
                                    self._make_network_delta_dict,
                                    filters=filters, fields=fields)
        
            
    def create_network_delta(self, context, network):
        networkdelta = network['network_delta']
        LOG.debug(_('create_network_delta db %s'), str(networkdelta))
        user_id = context.user_id
        tenant_id=networkdelta['tenant_id']
        with context.session.begin(subtransactions=True):
            version_id = self.create_version(context, tenant_id)
            network_delta = cns_network_delta(id=str(uuid.uuid4()),
                                        tenant_id=networkdelta['tenant_id'],
                                        name=networkdelta['name'],
                                        network_type=networkdelta['network_type'],
                                        router_external=networkdelta['router_external'],
                                        vxlan_service_port=networkdelta['vxlan_service_port'],
                                        segmentation_id=networkdelta['segmentation_id'],
                                        network_id=networkdelta['network_id'],
                                        operation=networkdelta['operation'],
                                        status=networkdelta['status'],
                                        admin_state_up=networkdelta['admin_state_up'],
                                        user_id=user_id,
                                        logged_at=datetime.datetime.now(),
                                        version_id=version_id)
            context.session.add(network_delta)
            
        return self._make_network_delta_dict(network_delta)
    
    def _make_subnet_delta_dict(self, subnetdelta, fields=None):
        res = {'tenant_id': subnetdelta['tenant_id'],
               'id': subnetdelta['id'],
               'name': subnetdelta['name'],
               'subnet_id': subnetdelta['subnet_id'],
               'network_id': subnetdelta['network_id'],
               'ip_version': subnetdelta['ip_version'],
               'cidr': subnetdelta['cidr'],
               'gateway_ip': subnetdelta['gateway_ip'],
               'dns_nameservers': subnetdelta['dns_nameservers'],
               'allocation_pools': subnetdelta['allocation_pools'],
               'host_routes': subnetdelta['host_routes'],
               'operation': subnetdelta['operation'],
               'user_id': subnetdelta['user_id'],
               'logged_at': subnetdelta['logged_at'],
               'version_id': subnetdelta['version_id']}
        return self._fields(res, fields)
        
        
    def get_subnet_deltas(self, context, filters=None, fields=None):
        return self._get_collection(context, cns_subnet_delta,
                                    self._make_subnet_delta_dict,
                                    filters=filters, fields=fields)
    def create_subnet_delta(self, context, subnet):
        subnetdelta = subnet['subnet_delta']
        LOG.debug(_('create_subnet_delta db %s'), str(subnetdelta))
        user_id = context.user_id
        tenant_id=subnetdelta['tenant_id']
        with context.session.begin(subtransactions=True):
            version_id = self.create_version(context, tenant_id)
            subnet_delta = cns_subnet_delta(id=str(uuid.uuid4()),
                                        tenant_id=subnetdelta['tenant_id'],
                                        name=subnetdelta['name'],
                                        subnet_id=subnetdelta['subnet_id'],
                                        network_id=subnetdelta['network_id'],
                                        ip_version=subnetdelta['ip_version'],
                                        cidr=subnetdelta['cidr'],
                                        gateway_ip=subnetdelta['gateway_ip'],
                                        dns_nameservers=subnetdelta['dns_nameservers'],
                                        allocation_pools=subnetdelta['allocation_pools'],
                                        host_routes=subnetdelta['host_routes'],
                                        operation=subnetdelta['operation'],
                                        user_id=user_id,
                                        logged_at=datetime.datetime.now(),
                                        version_id=version_id)
            context.session.add(subnet_delta)
    
        return self._make_subnet_delta_dict(subnet_delta)
    
    
    def _make_port_delta_dict(self, portdelta, fields=None):
        res = {'tenant_id': portdelta['tenant_id'],
               'id': portdelta['id'],
               'name': portdelta['name'],
               'port_id': portdelta['port_id'],
               'network_id': portdelta['network_id'],
               'subnet_id': portdelta['subnet_id'],
               'mac_address': portdelta['mac_address'],
               'device_id': portdelta['device_id'],
               'ip_address': portdelta['ip_address'],
               'admin_state_up': portdelta['admin_state_up'],
               'status': portdelta['status'],
               'device_owner': portdelta['device_owner'],
               'security_groups': portdelta['security_groups'],
               'operation': portdelta['operation'],
               'user_id': portdelta['user_id'],
               'logged_at': portdelta['logged_at'],
               'version_id': portdelta['version_id']}
        return self._fields(res, fields)
        
        
    def get_port_deltas(self, context, filters=None, fields=None):
        return self._get_collection(context, cns_port_delta,
                                    self._make_port_delta_dict,
                                    filters=filters, fields=fields)
    def create_port_delta(self, context, port):
        portdelta = port['port_delta']
        LOG.debug(_('create_port_delta db %s'), str(portdelta))
        user_id = context.user_id
        tenant_id=portdelta['tenant_id']
        with context.session.begin(subtransactions=True):
            version_id = self.create_version(context, tenant_id)
            port_delta = cns_port_delta(id=str(uuid.uuid4()),
                                        tenant_id=portdelta['tenant_id'],
                                        name=portdelta['name'],
                                        port_id=portdelta['port_id'],
                                        network_id=portdelta['network_id'],
                                        subnet_id=portdelta['subnet_id'],
                                        ip_address=portdelta['ip_address'],
                                        mac_address=portdelta['mac_address'],
                                        device_id=portdelta['device_id'],
                                        status=portdelta['status'],
                                        admin_state_up=portdelta['admin_state_up'],
                                        device_owner=portdelta['device_owner'],
                                        security_groups=portdelta['security_groups'],
                                        operation=portdelta['operation'],
                                        user_id=user_id,
                                        logged_at=datetime.datetime.now(),
                                        version_id=version_id)
            context.session.add(port_delta)
        return self._make_port_delta_dict(port_delta)
    
    
    def _make_compute_delta_dict(self, computedelta, fields=None):
        res = {'compute_id': computedelta['compute_id'],
               'id': computedelta['id'],
               'hostname': computedelta['hostname'],
               'ip_address': computedelta['ip_address'],
               'data_ip': computedelta['data_ip'],
               'created_at': computedelta['created_at'],
               'ovs_port': computedelta['ovs_port'],
               'datapath_id': computedelta['datapath_id'],
               'datapath_name': computedelta['datapath_name'],
               'switch': computedelta['switch'],
               'domain': computedelta['domain'],
               'subject_name': computedelta['subject_name'],
               'status': computedelta['status'],
               'operation': computedelta['operation'],
               'logged_at': computedelta['logged_at'],
               'version_id': computedelta['version_id']}
        return self._fields(res, fields)
        
        
    def get_compute_deltas(self, context, filters=None, fields=None):
        return self._get_collection(context, cns_compute_delta,
                                    self._make_compute_delta_dict,
                                    filters=filters, fields=fields)
    
    def create_compute_delta(self, context, compute):
        computedelta = compute['compute_delta']
        LOG.debug(_('create_compute_delta db %s'), str(computedelta))
        with context.session.begin(subtransactions=True):
            version_id = self.create_version(context, 'Nova')
            compute_delta = cns_compute_delta(id=str(uuid.uuid4()),
                                        compute_id = computedelta['compute_id'],
                                        hostname = computedelta['hostname'],
                                        ip_address = computedelta['ip_address'],
                                        data_ip = computedelta['data_ip'],
                                        created_at = computedelta['created_at'],
                                        ovs_port = computedelta['ovs_port'],
                                        datapath_id = computedelta['datapath_id'],
                                        datapath_name = computedelta['datapath_name'],
                                        switch = computedelta['switch'],
                                        domain = computedelta['domain'],
                                        subject_name = computedelta['subject_name'],
                                        status = computedelta['status'],
                                        operation = computedelta['operation'],
                                        logged_at=datetime.datetime.now(),
                                        version_id=version_id)
            context.session.add(compute_delta)
            
        return self._make_compute_delta_dict(compute_delta)
        
    def _make_instance_delta_dict(self, instancedelta, fields=None):
        res = {'tenant_id': instancedelta['tenant_id'],
               'id': instancedelta['id'],
               'display_name': instancedelta['display_name'],
               'instance_id': instancedelta['instance_id'],
               'user_id': instancedelta['user_id'],
               'state_description': instancedelta['state_description'],
               'state': instancedelta['state'],
               'created_at': instancedelta['created_at'],
               'launched_at': instancedelta['launched_at'],
               'host': instancedelta['host'],
               'type': instancedelta['type'],
               'reservation_id': instancedelta['reservation_id'],
               'operation': instancedelta['operation'],
               'logged_at': instancedelta['logged_at'],
               'version_id': instancedelta['version_id']}
        return self._fields(res, fields)
        
        
    def get_instance_deltas(self, context, filters=None, fields=None):
        return self._get_collection(context, cns_instance_delta,
                                    self._make_instance_delta_dict,
                                    filters=filters, fields=fields)
    
    def create_instance_delta(self, context, instance):
        instancedelta = instance['instance_delta']
        LOG.debug(_('create_instance_delta db %s'), str(instancedelta))
        user_id = context.user_id
        tenant_id=instancedelta['tenant_id']
        with context.session.begin(subtransactions=True):
            version_id = self.create_version(context, tenant_id)
            instance_delta = cns_instance_delta(id=str(uuid.uuid4()),
                                        tenant_id = instancedelta['tenant_id'],
                                        display_name = instancedelta['display_name'],
                                        instance_id = instancedelta['instance_id'],
                                        user_id = instancedelta['user_id'],
                                        state_description = instancedelta['state_description'],
                                        state = instancedelta['state'],
                                        created_at = instancedelta['created_at'],
                                        launched_at = instancedelta['launched_at'],
                                        host = instancedelta['host'],
                                        type = instancedelta['type'],
                                        reservation_id = instancedelta['reservation_id'],
                                        operation = instancedelta['operation'],
                                        logged_at = datetime.datetime.now(),
                                        version_id = version_id)
            context.session.add(instance_delta)
            
        return self._make_instance_delta_dict(instance_delta)
        
    
    
    def _make_nwport_delta_dict(self, nwportdelta, fields=None):
        res = {'nwport_id': nwportdelta['nwport_id'],
               'id': nwportdelta['id'],
               'name': nwportdelta['name'],
               'network_type': nwportdelta['network_type'],
               'ip_address': nwportdelta['ip_address'],
               'data_ip': nwportdelta['data_ip'],
               'bridge': nwportdelta['bridge'],
               'vxlan_vni': nwportdelta['vxlan_vni'],
               'vxlan_udpport': nwportdelta['vxlan_udpport'],
               'vlan_id': nwportdelta['vlan_id'],
               'flow_type': nwportdelta['flow_type'],
               'ovs_port': nwportdelta['ovs_port'],
               'local_data_ip': nwportdelta['local_data_ip'],
               'host': nwportdelta['host'],
               'operation': nwportdelta['operation'],
               'logged_at': nwportdelta['logged_at'],
               'version_id': nwportdelta['version_id']}
        return self._fields(res, fields)
        
        
    def get_nwport_deltas(self, context, filters=None, fields=None):
        return self._get_collection(context, cns_nwport_delta,
                                    self._make_nwport_delta_dict,
                                    filters=filters, fields=fields)
    
    def create_nwport_delta(self, context, nwport):
        nwportdelta = nwport['nwport_delta']
        LOG.debug(_('create_nwport_delta db %s'), str(nwportdelta))
        with context.session.begin(subtransactions=True):
            version_id = self.create_version(context, 'Nova')
            nwport_delta = cns_nwport_delta(id=str(uuid.uuid4()),
                                        nwport_id = nwportdelta['id'],
                                        name = nwportdelta['name'],
                                        network_type = nwportdelta['network_type'],
                                        ip_address = nwportdelta['ip_address'],
                                        data_ip = nwportdelta['data_ip'],
                                        bridge = nwportdelta['bridge'],
                                        vxlan_vni = nwportdelta['vxlan_vni'],
                                        vxlan_udpport = nwportdelta['vxlan_udpport'],
                                        vlan_id = nwportdelta['vlan_id'],
                                        flow_type = nwportdelta['flow_type'],
                                        ovs_port = nwportdelta['ovs_port'],
                                        local_data_ip = nwportdelta['local_data_ip'],
                                        host = nwportdelta['host'],
                                        operation = nwportdelta['operation'],
                                        logged_at=datetime.datetime.now(),
                                        version_id=version_id)
            context.session.add(nwport_delta)
            
        return self._make_nwport_delta_dict(nwport_delta)
