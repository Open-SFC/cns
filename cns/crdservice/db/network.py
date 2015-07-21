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
from sqlalchemy.orm import exc
from nscs.crdservice.common import exceptions as q_exc
from nscs.crdservice.db import model_base
from nscs.crdservice.openstack.common import log as logging
from nscs.crdservice.openstack.common import uuidutils


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
    

class CrdNetwork(model_base.BASEV2, HasId, HasTenant):
    """Represents a v2 neutron network."""
    __tablename__ = "cns_networks"

    name = sa.Column(sa.String(255))
    network_id = sa.Column(sa.String(36), nullable=False)
    network_type = sa.Column(sa.String(255))
    segmentation_id = sa.Column(sa.Integer())
    physical_network = sa.Column(sa.String(255))
    router_external = sa.Column(sa.Boolean)
    status = sa.Column(sa.String(16))
    admin_state_up = sa.Column(sa.Boolean)
    vxlan_service_port = sa.Column(sa.String(10))


class CrdSubnet(model_base.BASEV2, HasId, HasTenant):
    __tablename__ = "cns_subnets"

    name = sa.Column(sa.String(255))
    subnet_id = sa.Column(sa.String(36), nullable=False)
    network_id = sa.Column(sa.String(36), nullable=False)
    ip_version = sa.Column(sa.Integer, nullable=False)
    cidr = sa.Column(sa.String(64), nullable=False)
    gateway_ip = sa.Column(sa.String(64))
    dns_nameservers = sa.Column(sa.String(255))
    allocation_pools = sa.Column(sa.String(255))
    host_routes = sa.Column(sa.String(255))


class CrdPort(model_base.BASEV2, HasId):
    __tablename__ = "cns_ports"

    tenant_id = sa.Column(sa.String(255))
    name = sa.Column(sa.String(255))
    port_id = sa.Column(sa.String(36), nullable=False)
    network_id = sa.Column(sa.String(36), nullable=False)
    subnet_id = sa.Column(sa.String(36), nullable=False)
    mac_address = sa.Column(sa.String(32), nullable=False)
    device_id = sa.Column(sa.String(255), nullable=False)
    ip_address = sa.Column(sa.String(64), nullable=False)
    admin_state_up = sa.Column(sa.Boolean(), nullable=False)
    status = sa.Column(sa.String(16), nullable=False)
    device_owner = sa.Column(sa.String(255))
    security_groups = sa.Column(sa.String(255))


class CrdNetworkDb(db_base_plugin_v2.CrdDbPluginV2):
    #################### Network Start######################################
    def _make_network_dict(self, network, fields=None):
        res = {'id': network['id'],
               'name': network['name'],
               'network_type': network['network_type'],
               'tenant_id': network['tenant_id'],
               'segmentation_id': network['segmentation_id'],
               'physical_network': network['physical_network'],
               'router_external': network['router_external'],
               'network_id': network['network_id'],
               'status': network['status'],
               'admin_state_up': network['admin_state_up'],
               'vxlan_service_port': network['vxlan_service_port']}
        return self._fields(res, fields)
        
    def create_network(self, context, network):
        n = network['network']
        with context.session.begin(subtransactions=True):
            network = CrdNetwork(id=n['network_id'],
                                 tenant_id=n['tenant_id'],
                                 name=n['name'],
                                 network_type=n['network_type'],
                                 segmentation_id=n['segmentation_id'],
                                 physical_network=n['physical_network'],
                                 router_external=n['router_external'],
                                 vxlan_service_port=n['vxlan_service_port'],
                                 network_id=n['network_id'],
                                 status=n['status'],
                                 admin_state_up=n['admin_state_up'])
            context.session.add(network)
        return self._make_network_dict(network)
        
    def get_network(self, context, id, fields=None):
        network = self._get_network(context, id)
        return self._make_network_dict(network, fields)

    def get_networks(self, context, filters=None, fields=None):
        return self._get_collection(context, CrdNetwork,
                                    self._make_network_dict,
                                    filters=filters, fields=fields)
    @staticmethod
    def _get_network(context, id):
        try:
            query = context.session.query(CrdNetwork)
            network = query.filter(CrdNetwork.network_id == id).one()
        except exc.NoResultFound:
            raise q_exc.NetworkNotFound(net_id=id)
            #return False
        except exc.MultipleResultsFound:
            LOG.error('Multiple Networks match for %s' % id)
            raise q_exc.NetworkNotFound(net_id=id)
        return network
    
    def update_network(self, context, id, network):
        n = network['network']
        with context.session.begin(subtransactions=True):
            network = self._get_network(context, id)
            network.update(n)
        return self._make_network_dict(network)
        
    def delete_network(self, context, id):
        network = self._get_network(context, id)
        with context.session.begin(subtransactions=True):
            context.session.delete(network)
    ################## Network End #######################################

    #################### Subnet Start######################################
    def _make_subnet_dict(self, subnet, fields=None):
        res = {'id': subnet['id'],
               'name': subnet['name'],
               'tenant_id': subnet['tenant_id'],
               'network_id': subnet['network_id'],
               'subnet_id': subnet['subnet_id'],
               'ip_version': subnet['ip_version'],
               'cidr': subnet['cidr'],
               'gateway_ip': subnet['gateway_ip'],
               'dns_nameservers': subnet['dns_nameservers'],
               'allocation_pools': subnet['allocation_pools'],
               'host_routes': subnet['host_routes']}
        return self._fields(res, fields)
        
    def create_subnet(self, context, subnet):
        n = subnet['subnet']
        with context.session.begin(subtransactions=True):
            subnet = CrdSubnet(id=n['subnet_id'],
                               tenant_id=n['tenant_id'],
                               name=n['name'],
                               network_id=n['network_id'],
                               subnet_id=n['subnet_id'],
                               ip_version=n['ip_version'],
                               cidr=n['cidr'],
                               gateway_ip=n['gateway_ip'],
                               dns_nameservers=n['dns_nameservers'],
                               allocation_pools=n['allocation_pools'],
                               host_routes=n['host_routes'])
            context.session.add(subnet)
        return self._make_subnet_dict(subnet)
        
    def get_subnet(self, context, id, fields=None):
        subnet = self._get_subnet(context, id)
        return self._make_subnet_dict(subnet, fields)

    def get_subnets(self, context, filters=None, fields=None):
        return self._get_collection(context, CrdSubnet,
                                    self._make_subnet_dict,
                                    filters=filters, fields=fields)

    @staticmethod
    def _get_subnet(context, id):
        try:
            query = context.session.query(CrdSubnet)
            subnet = query.filter(CrdSubnet.subnet_id == id).one()
        except exc.NoResultFound:
            raise q_exc.SubnetNotFound(subnet_id=id)
            #return False
        except exc.MultipleResultsFound:
            LOG.error('Multiple Subnets match for %s' % id)
            raise q_exc.SubnetNotFound(subnet_id=id)
        return subnet
    
    def update_subnet(self, context, id, subnet):
        n = subnet['subnet']
        with context.session.begin(subtransactions=True):
            subnet = self._get_subnet(context, id)
            subnet.update(n)
        return self._make_subnet_dict(subnet)
        
    def delete_subnet(self, context, id):
        subnet = self._get_subnet(context, id)
        with context.session.begin(subtransactions=True):
            context.session.delete(subnet)
    ################## Subnet End #######################################
           
    #################### Port Start######################################
    def _make_port_dict(self, port, fields=None):
        res = {'id': port['id'],
               'name': port['name'],
               'tenant_id': port['tenant_id'],
               'network_id': port['network_id'],
               'port_id': port['port_id'],
               'subnet_id': port['subnet_id'],
               'mac_address': port['mac_address'],
               'device_id': port['device_id'],
               'ip_address': port['ip_address'],
               'device_owner': port['device_owner'],
               'security_groups': port['security_groups'],
               'status': port['status'],
               'admin_state_up': port['admin_state_up']}
        return self._fields(res, fields)
        
    def create_port(self, context, port):
        n = port['port']
        with context.session.begin(subtransactions=True):
            port = CrdPort(id=n['port_id'],
                           name=n['name'],
                           tenant_id=n['tenant_id'],
                           network_id=n['network_id'],
                           port_id=n['port_id'],
                           subnet_id=n['subnet_id'],
                           mac_address=n['mac_address'],
                           device_id=n['device_id'],
                           ip_address=n['ip_address'],
                           device_owner=n['device_owner'],
                           security_groups=n['security_groups'],
                           status=n['status'],
                           admin_state_up=n['admin_state_up'])
            context.session.add(port)
        return self._make_port_dict(port)
        
    def get_port(self, context, id, fields=None):
        port = self._get_port(context, id)
        return self._make_port_dict(port, fields)

    def get_ports(self, context, filters=None, fields=None):
        return self._get_collection(context, CrdPort,
                                    self._make_port_dict,
                                    filters=filters, fields=fields)

    @staticmethod
    def _get_port(context, id):
        try:
            query = context.session.query(CrdPort)
            port = query.filter(CrdPort.port_id == id).one()
        except exc.NoResultFound:
            raise q_exc.PortNotFound(port_id=id)
            #return False
        except exc.MultipleResultsFound:
            LOG.error('Multiple Ports match for %s' % id)
            raise q_exc.PortNotFound(port_id=id)
        return port
    
    def update_port(self, context, id, port):
        n = port['port']
        with context.session.begin(subtransactions=True):
            port = self._get_port(context, id)
            port.update(n)
        return self._make_port_dict(port)
        
    def delete_port(self, context, id):
        port = self._get_port(context, id)
        with context.session.begin(subtransactions=True):
            context.session.delete(port)
    ################## Port End #######################################
