# -*- encoding: utf-8 -*-
#
# Author: Purandhar Sairam Mannidi <sairam.mp@freescale.com>
#
"""
SQLAlchemy models for OCAS data.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
import uuid

from oslo_log._i18n import _

from . import model as api_model
from nscs.nscsas.storage.sqlalchemy.models import Base, get_session


class VirtualNetworks(Base):
    """OCAS Networks"""
    __tablename__ = 'cns_virtualnetworks'
    __table_args__ = {'useexisting': True}

    id = Column(String(36), primary_key=True, unique=True)
    name = Column(String(128), nullable=False)
    tenant = Column(String(36), nullable=False)
    type = Column(String(10), nullable=False)
    segmentation_id = Column(Integer)
    vxlan_service_port = Column(Integer)
    status = Column(String(10), nullable=False)
    state = Column(Boolean)
    external = Column(Boolean)


class Subnets(Base):
    """OCAS Subnets"""
    __tablename__ = 'cns_subnets'
    __table_args__ = {'useexisting': True}

    id = Column(String(36), primary_key=True, unique=True)
    name = Column(String(128), nullable=False)
    dhcp = Column(Boolean)
    ip_version = Column(String(4), nullable=False)
    gateway_ip = Column(String(50))
    cidr = Column(String(50))
    nw_id = Column(String(36), ForeignKey('cns_virtualnetworks.id'))


class IPAllocationPools(Base):
    """OCAS Ip Allocation Pools of a Subnet"""
    __tablename__ = 'cns_ipallocationpools'
    __table_args__ = {'useexisting': True}

    id = Column(String(36), primary_key=True)
    start = Column(String(50), nullable=False)
    end = Column(String(50), nullable=False)
    subnet_id = Column(String(36), ForeignKey('cns_subnets.id'))


class DNSServers(Base):
    """OCAS DNS Servers of a Subnet"""
    __tablename__ = 'cns_dnsservers'
    __table_args__ = {'useexisting': True}

    id = Column(String(36), primary_key=True)
    address = Column(String(50), nullable=False)
    subnet_id = Column(String(36), ForeignKey('cns_subnets.id'))


class VirtualMachines(Base):
    """OCAS Virtual Instances"""
    __tablename__ = 'cns_virtualmachines'
    __table_args__ = {'useexisting': True}

    id = Column(String(36), primary_key=True, unique=True)
    name = Column(String(128), nullable=False)
    type = Column(String(50))
    tenant = Column(String(36), nullable=False)
    host = Column(String(50), nullable=False)
    created_at = Column(DateTime)
    launched_at = Column(DateTime)
    state_description = Column(String(255))
    state = Column(String(255))
    user_id = Column(String(36))
    reservation_id = Column(String(50))
    zone = Column(String(50))


class Ports(Base):
    """OCAS Ports"""
    __tablename__ = 'cns_ports'
    __table_args__ = {'useexisting': True}

    id = Column(String(36), primary_key=True, unique=True)
    name = Column(String(128), nullable=False)
    tenant = Column(String(36), nullable=False)
    type = Column(String(50), nullable=False)
    bridge = Column(String(50))
    mac_address = Column(String(255), nullable=False)
    ip_address = Column(String(50))
    state = Column(Boolean)
    status = Column(String(10))
    device_owner = Column(String(255))
    device_id = Column(String(255))
    subnet_id = Column(String(36), ForeignKey('cns_subnets.id'))
    nw_id = Column(String(36), ForeignKey('cns_virtualnetworks.id'))


class SecurityGroups(Base):
    """OCAS Security Groups of a Port"""
    __tablename__ = 'cns_securitygroups'
    __table_args__ = {'useexisting': True}

    id = Column(String(36), primary_key=True)
    port_id = Column(String(36), ForeignKey('cns_ports.id'))


class Switches(Base):
    """OCAS DPRM Switch database"""
    __tablename__ = 'cns_switches'
    __table_args__ = {'useexisting': True}

    id = Column(String(36), primary_key=True, unique=True)
    name = Column(String(16), nullable=False)
    type = Column(Boolean)
    fqdn = Column(String(96))
    baddr = Column(Boolean)
    ip_address = Column(String(50))


class Domains(Base):
    """OCAS DPRM Domain database"""
    __tablename__ = 'cns_domains'
    __table_args__ = {'useexisting': True}

    id = Column(String(36), primary_key=True, unique=True)
    name = Column(String(16), nullable=False)
    subject = Column(String(256))
    ttp_name = Column(String(256))


class Datapaths(Base):
    """OCAS Datapath"""
    __tablename__ = 'cns_datapaths'
    __table_args__ = {'useexisting': True}

    id = Column(String(16), primary_key=True, unique=True)
    name = Column(String(256), nullable=False)
    subject = Column(String(256), nullable=False)
    switch = Column(String(36), ForeignKey('cns_switches.id'))
    domain = Column(String(36), ForeignKey('cns_domains.id'))


class Attributes(Base):
    """Common table for OCAS Attributes of Networks/Subnets/Ports/VirtualMachines"""
    __tablename__ = 'cns_attributes'
    __table_args__ = {'useexisting': True}

    id = Column(String(36), primary_key=True)
    type = Column(String(16), nullable=False)
    reference_id = Column(String(36), nullable=False)
    name = Column(String(255), nullable=False)
    value = Column(String(255))


class Versions(Base):
    """OCAS Versions"""
    __tablename__ = 'cns_versions'
    __table_args__ = {'useexisting': True}

    runtime_version = Column(Integer, nullable=False, primary_key=True)


class NWPorts(Base):
    """OCAS Network Side Ports"""
    __tablename__ = 'cns_nwports'
    __table_args__ = {'useexisting': True}

    id = Column(String(36), primary_key=True, unique=True)
    name = Column(String(128), nullable=False)
    network_type = Column(String(50), nullable=False)
    data_ip = Column(String(50), nullable=False)
    bridge = Column(String(50), nullable=False)
    ip_address = Column(String(50), nullable=False)
    vxlan_vni = Column(Integer)
    vxlan_port = Column(Integer)
    flow_type = Column(String(255))
    ovs_port = Column(Integer)
    local_data_ip = Column(String(50))
    host = Column(String(255))


class CNSDBMixin(object):
    @staticmethod
    def _row_to_vnetwork(row):
        return api_model.VirtualNetwork(id=row.id,
                                        type=row.type,
                                        name=row.name,
                                        state=row.state,
                                        tenant=row.tenant,
                                        segmentation_id=row.segmentation_id,
                                        vxlan_service_port=row.vxlan_service_port,
                                        status=row.status,
                                        external=row.external)

    def create_virtualnetwork(self, network):
        """
        Insert Network record into database

        :param network:
                {
                    'id' :                '5af62b10-e589-430c-9731-426a24f54df9',
                    'name':               'os-5af62b10-e589',
                    'tenant':             'os-12345678-9abc',
                    'type':               'vxlan',
                    'segmentation_id':    '1024',
                    'vxlan_service_port': '4789',
                    'status':             'active',
                    'state':              'up',
                    'external':           'false',
                }
        :return:
                Network data if the insertion is successful
                revoke transaction and raise exception
        """
        session = get_session()
        with session.begin():
            nw_row = VirtualNetworks(id=network.id)
            nw_row.update(network.as_dict())
            session.add(nw_row)
            session.flush()
        return self._row_to_vnetwork(nw_row)

    def get_virtualnetworks(self, nw_id=None, name=None, pagination=None):
        """Yields a lists of alarms that match filters
        :param name: Optional name to return one virtual network.
        :param nw_id: Optional nw_id to return one virtual network.
        :param pagination: Optional pagination query.
        """

        if pagination:
            raise NotImplementedError(_('Pagination not implemented'))

        session = get_session()
        query = session.query(VirtualNetworks)
        if name is not None:
            query = query.filter(VirtualNetworks.name == name)
        if nw_id is not None:
            query = query.filter(VirtualNetworks.id == nw_id)

        return (self._row_to_vnetwork(x) for x in query.all())

    def update_virtualnetwork(self, network):
        """Update an virtual network.

        :param network: the virtual network to update
        """
        session = get_session()
        with session.begin():
            nw_row = session.merge(VirtualNetworks(id=network.id))
            nw_row.update(network.as_dict())
            session.flush()

        return self._row_to_vnetwork(nw_row)

    @staticmethod
    def delete_virtualnetwork(nw_id):
        """Delete a Virtual Network

        :param nw_id: ID of the Virtual Network to delete
        """
        session = get_session()
        with session.begin():
            session.query(VirtualNetworks).filter(VirtualNetworks.id == nw_id).delete()
            session.flush()

    @staticmethod
    def _row_to_subnet(row):
        return api_model.Subnet(id=row.id,
                                name=row.name,
                                nw_id=row.nw_id,
                                dhcp=row.dhcp,
                                ip_version=row.ip_version,
                                gateway_ip=row.gateway_ip,
                                cidr=row.cidr,
                                pools=[],
                                dns_servers=[])

    @staticmethod
    def _row_to_pool(row):
        return api_model.Pool(start=row.start,
                              end=row.end,
                              id=None,
                              subnet_id=None)

    def create_subnet(self, subnet):
        """
        Insert Subnet record into database

        :param subnet:
                {
                    'id' :                '5af62b10-e589-430c-9731-426a24f54df9',
                    'name':               'os-5af62b10-e589',
                    'nw_id':              '5af62b10-e589-430c-9731-426a24f54df9',
                    'vnname':             'os-5af62b10-e589',
                    'dhcp':               'enable',
                    'ip_version':         '4',
                    'cidr':               '1.1.1.0/24',
                    'gateway_ip':         '1.1.1.1',
                    'pools':              [{'start':'1.1.1.1','end':'1.1.1.10'},
                                           {'start':'1.1.1.50','end':'1.1.1.100'}],
                    'dns_servers':        ['1.1.1.1','1.1.1.45'],
                }
        :return:
                Subnet data if the insertion is successful
                revoke transaction and raise exception
        """
        session = get_session()
        with session.begin():
            sub_row = Subnets(id=subnet.id)
            sub_row.update(subnet.as_dict())
            session.add(sub_row)
            session.flush()
            p_rows = []
            for pool in subnet.pools:
                pool_row = IPAllocationPools(id=pool.id)
                pool_row.update(pool.as_dict())
                session.add(pool_row)
                session.flush()
                p_rows.append(pool_row)
            serv = len(subnet.dns_servers) if len(subnet.dns_servers) < 4 else 4
            dns_rows = []
            for s in range(0, serv):
                serv_row = DNSServers(id=uuid.uuid4(), subnet_id=subnet.id, address=subnet.dns_servers[s])
                session.add(serv_row)
                session.flush()
                dns_rows.append(subnet.dns_servers[s])
        subnet = self._row_to_subnet(sub_row)
        subnet.pools = [self._row_to_pool(pool_row) for pool_row in p_rows]
        subnet.dns_servers = dns_rows
        return subnet

    def update_subnet(self, subnet):
        """
        Update Subnet record into database

        :param subnet:
                {
                    'id' :                '5af62b10-e589-430c-9731-426a24f54df9',
                    'name':               'os-5af62b10-e589',
                    'nw_id':              '5af62b10-e589-430c-9731-426a24f54df9',
                    'vnname':             'os-5af62b10-e589',
                    'dhcp':               'enable',
                    'ip_version':         '4',
                    'cidr':               '1.1.1.0/24',
                    'gateway_ip':         '1.1.1.1',
                    'dns_servers':        ['1.1.1.1','1.1.1.45'],
                }
        :return:
                Subnet data if the insertion is successful
                revoke transaction and raise exception
        """
        session = get_session()
        with session.begin():
            sub_row = session.merge(Subnets(id=subnet.id))
            sub_row.update(subnet.as_dict())
            session.add(sub_row)
            session.flush()
            serv = len(subnet.dns_servers) if len(subnet.dns_servers) < 4 else 4
            dns_rows = []
            session.query(DNSServers).filter(DNSServers.subnet_id == subnet.id).delete()
            for s in range(0, serv):
                serv_row = DNSServers(id=uuid.uuid4(), subnet_id=subnet.id, address=subnet.dns_servers[s])
                session.add(serv_row)
                session.flush()
                dns_rows.append(subnet.dns_servers[s])
        subnet = self._row_to_subnet(sub_row)
        query = session.query(IPAllocationPools)
        query.filter(IPAllocationPools.subnet_id == subnet.id)
        subnet.pools = [self._row_to_pool(pool_row) for pool_row in query.all()]
        subnet.dns_servers = dns_rows
        return subnet

    def get_subnets(self, nw_id=None, sub_id=None, name=None, pagination=None):
        """Yields a lists of subnets that match filters
        :param name: Optional name to return one subnet.
        :param sub_id: Optional sub_id to return one subnet.
        :param nw_id: Optional nw_id to return subnets for this network.
        :param pagination: Optional pagination query.
        """

        if pagination:
            raise NotImplementedError(_('Pagination not implemented'))

        session = get_session()
        query = session.query(Subnets)

        if name is not None:
            query = query.filter(Subnets.name == name)
        if sub_id is not None:
            query = query.filter(Subnets.id == sub_id)
        if nw_id is not None:
            query = query.filter(Subnets.nw_id == nw_id)

        subnets = [self._row_to_subnet(x) for x in query.all()]

        for sub in subnets:
            pool_query = session.query(IPAllocationPools).filter(IPAllocationPools.subnet_id == sub.id)
            sub.pools = [self._row_to_pool(pool_row) for pool_row in pool_query.all()]

            dns_query = session.query(DNSServers).filter(DNSServers.subnet_id == sub.id)
            sub.dns_servers = [x.address for x in dns_query.all()]
        return subnets

    @staticmethod
    def delete_subnet(sub_id):
        """Delete a Virtual Network

        :param sub_id: ID of the Subnet to delete
        """
        session = get_session()
        with session.begin():
            session.query(IPAllocationPools).filter(IPAllocationPools.subnet_id == sub_id).delete()
            session.query(DNSServers).filter(DNSServers.subnet_id == sub_id).delete()
            session.query(Subnets).filter(Subnets.id == sub_id).delete()
            session.flush()

    @staticmethod
    def _row_to_vmachine(row):
        return api_model.VirtualMachine(id=row.id,
                                        name=row.name,
                                        state=row.state,
                                        state_description=row.state_description,
                                        tenant=row.tenant,
                                        created_at=row.created_at,
                                        launched_at=row.launched_at,
                                        host=row.host,
                                        user_id=row.user_id,
                                        reservation_id=row.reservation_id,
                                        type=row.type,
                                        zone=row.zone)

    def create_virtualmachine(self, vm):
        """
        Insert Virtual Machine record into database

        :param vm:
                {
                    'id' :                '5af62b10-e589-430c-9731-426a24f54df9',
                    'name':               'os-5af62b10-e589',
                    'tenant':             'os-12345678-9abc',
                    'state':              'Active',
                    'state_description':  'Active',
                    'created_at':         '2013-11-28 15:10:40',
                    'launched_at':        '2013-11-28 15:10:40',
                    'host':               'p4080ds',
                    'user_id':            '5af62b10-e589-430c-9731-426a24f54df9',
                    'reservation_id':     'r-os66o900',
                    'type':               'VM_TYPE_NORMAL_APPLICATION'
                }
        :return:
                Virtual Machine data if the insertion is successful
                revoke transaction and raise exception
        """
        session = get_session()
        with session.begin():
            vm_row = VirtualMachines(id=vm.id)
            vm_row.update(vm.as_dict())
            session.add(vm_row)
            session.flush()
        return self._row_to_vmachine(vm_row)

    def get_virtualmachines(self, vm_id=None, name=None, pagination=None):
        """Yields a lists of virtual machines that match filters
        :param name: Optional name to return one virtual machine.
        :param vm_id: Optional vm_id to return one virtual machine.
        :param pagination: Optional pagination query.
        """

        if pagination:
            raise NotImplementedError(_('Pagination not implemented'))

        session = get_session()
        query = session.query(VirtualMachines)
        if name is not None:
            query = query.filter(VirtualMachines.name == name)
        if vm_id is not None:
            query = query.filter(VirtualMachines.id == vm_id)

        return (self._row_to_vmachine(x) for x in query.all())

    def update_virtualmachine(self, vm):
        """Update an virtual machine.

        :param vm: the virtual machine to update
        """
        session = get_session()
        with session.begin():
            vm_row = session.merge(VirtualMachines(id=vm.id))
            vm_row.update(vm.as_dict())
            session.flush()

        return self._row_to_vmachine(vm_row)

    @staticmethod
    def delete_virtualmachine(vm_id):
        """Delete a Virtual Machine

        :param vm_id: ID of the Virtual Machine to delete
        """
        session = get_session()
        with session.begin():
            session.query(VirtualMachines).filter(VirtualMachines.id == vm_id).delete()
            session.flush()

    @staticmethod
    def _row_to_port(row):
        return api_model.Port(id=row.id,
                              name=row.name,
                              state=row.state,
                              tenant=row.tenant,
                              bridge=row.bridge,
                              type=row.type,
                              mac_address=row.mac_address,
                              ip_address=row.ip_address,
                              status=row.status,
                              device_owner=row.device_owner,
                              device_id=row.device_id,
                              security_groups=[],
                              subnet_id=row.subnet_id,
                              nw_id=row.nw_id)

    def create_port(self, port):
        """
        Insert port record into database

        :param port:
                {
                    id: '',
                    name: '',
                    state: '',
                    tenant: '',
                    host: '',
                    type: '',
                    mac_address: '',
                    ip_address: '',
                    status: '',
                    device_owner: '',
                    device_id: '',
                    security_groups: [],
                    subnet_id: '',
                    nw_id: ''
                }

        :return:
                Port data if the insertion is successful
                revoke transaction and raise exception
        """
        session = get_session()
        with session.begin():
            port_row = Ports(id=port.id)
            port_row.update(port.as_dict())
            session.add(port_row)
            session.flush()
            sg_rows = []
            for sg in port.security_groups:
                sg_row = SecurityGroups(id=sg, port_id=port.id)
                session.add(sg_row)
                session.flush()
                sg_rows.append(sg_row)
        port_out = self._row_to_port(port_row)
        port_out.security_groups = [sg.id for sg in sg_rows]
        return port_out

    def update_port(self, port):
        """Update an Port.

        :param port: the port to update
        """
        session = get_session()
        with session.begin():
            port_row = session.merge(Ports(id=port.id))
            port_row.update(port.as_dict())
            session.flush()
            sg_rows = []
            session.query(SecurityGroups).filter(SecurityGroups.port_id == port.id).delete()
            for sg in port.security_groups:
                sg_row = SecurityGroups(id=sg, port_id=port.id)
                session.add(sg_row)
                session.flush()
                sg_rows.append(sg_row)

        port_out = self._row_to_port(port_row)
        port_out.security_groups = [sg.id for sg in sg_rows]

        return port_out

    def get_ports(self, port_id=None, name=None, pagination=None):
        """Yields a lists of ports that match filters
        :param name: Optional name to return one virtual machine.
        :param port_id: Optional port_id to return one port details.
        :param pagination: Optional pagination query.
        """

        if pagination:
            raise NotImplementedError(_('Pagination not implemented'))

        session = get_session()
        query = session.query(Ports)
        if name is not None:
            query = query.filter(Ports.name == name)
        if port_id is not None:
            query = query.filter(Ports.id == port_id)

        ports = [self._row_to_port(x) for x in query.all()]
        for port in ports:
            sg_query = session.query(SecurityGroups).filter(SecurityGroups.port_id == port.id)
            port.security_groups = [sg.id for sg in sg_query.all()]

        return ports

    @staticmethod
    def delete_port(port_id):
        """Delete a Port

        :param port_id: ID of the Virtual Port to delete
        """
        session = get_session()
        with session.begin():
            session.query(SecurityGroups).filter(SecurityGroups.port_id == port_id).delete()
            session.query(Ports).filter(Ports.id == port_id).delete()
            session.flush()

    @staticmethod
    def _row_to_domain(row):
        return api_model.Domain(id=row.id,
                                name=row.name,
                                subject=row.subject,
                                ttp_name=row.ttp_name)

    def create_domain(self, domain):
        """
        Insert domain record into database

        :param domain:
                {
                    id: '5af62b10-e589-430c-9731-426a24f54df9',
                    name: 'test_domain',
                    subject: '/CN=ofcontroller.freescale.com/'
                }

        :return:
                Domain data if the insertion is successful
                revoke transaction and raise exception
        """
        session = get_session()
        with session.begin():
            dom_row = Domains(id=domain.id, name=domain.name, subject=domain.subject, ttp_name=domain.ttp_name)
            session.add(dom_row)
            session.flush()

        return self._row_to_domain(dom_row)

    def update_domain(self, domain):
        """Update an Domain.

        :param domain: the domain to update
        """
        session = get_session()
        with session.begin():
            dom_row = session.merge(Domains(id=domain.id))
            dom_row.update(domain.as_dict())
            session.flush()

        return self._row_to_domain(dom_row)

    def get_domains(self, domain_id=None, name=None, pagination=None):
        """Yields a lists of ports that match filters
        :param name: Optional name to return one domain.
        :param domain_id: Optional domain_id to return one domain details.
        :param pagination: Optional pagination query.
        """

        if pagination:
            raise NotImplementedError(_('Pagination not implemented'))

        session = get_session()
        query = session.query(Domains)
        if name is not None:
            query = query.filter(Domains.name == name)
        if domain_id is not None:
            query = query.filter(Domains.id == domain_id)

        return [self._row_to_domain(x) for x in query.all()]

    @staticmethod
    def delete_domain(domain_id):
        """Delete a Domain

        :param domain_id: ID of the Domain to delete
        """
        session = get_session()
        with session.begin():
            session.query(Domains).filter(Domains.id == domain_id).delete()
            session.flush()

    @staticmethod
    def _row_to_switch(row):
        return api_model.Switch(id=row.id,
                                name=row.name,
                                fqdn=row.fqdn,
                                type=row.type,
                                baddr=row.baddr,
                                ip_address=row.ip_address)

    def create_switch(self, switch):
        """
        Insert switch record into database

        :param switch:
                {
                    id: '5af62b10-e589-430c-9731-426a24f54df9',
                    name: 'test_switch',
                    fqdn: 'http://xyz.com',
                    type: 0,
                    baddr: 1,
                    ip_address: '1.1.1.1'
                }

        :return:
                Switch data if the insertion is successful
                revoke transaction and raise exception
        """
        session = get_session()
        with session.begin():
            sw_row = Switches(id=switch.id)
            sw_row.update(switch.as_dict())
            session.add(sw_row)
            session.flush()

        return self._row_to_switch(sw_row)

    def update_switch(self, switch):
        """Update an Switch.

        :param switch: the switch to update
        """
        session = get_session()
        with session.begin():
            sw_row = session.merge(Switches(id=switch.id))
            sw_row.update(switch.as_dict())
            session.flush()

        return self._row_to_switch(sw_row)

    def get_switches(self, switch_id=None, name=None, pagination=None):
        """Yields a lists of ports that match filters
        :param name: Optional name to return one switch.
        :param switch_id: Optional switch_id to return one switch details.
        :param pagination: Optional pagination query.
        """

        if pagination:
            raise NotImplementedError(_('Pagination not implemented'))

        session = get_session()
        query = session.query(Switches)
        if name is not None:
            query = query.filter(Switches.name == name)
        if switch_id is not None:
            query = query.filter(Switches.id == switch_id)

        return [self._row_to_switch(x) for x in query.all()]

    @staticmethod
    def delete_switch(switch_id):
        """Delete a Switch

        :param switch_id: ID of the Switch to delete
        """
        session = get_session()
        with session.begin():
            session.query(Switches).filter(Switches.id == switch_id).delete()
            session.flush()

    @staticmethod
    def _row_to_datapath(row):
        return api_model.Datapath(id=row.id,
                                  name=row.name,
                                  subject=row.subject,
                                  switch=row.switch,
                                  domain=row.domain)

    def create_datapath(self, datapath):
        """
        Insert datapath record into database

        :param datapath:
                {
                    id: '5af62b10e589430c',
                    subject: 'test_subject',
                    switch: '5af62b10-e589-430c-9731-426a24f54df9',
                    domain: '5af62b10-e589-430c-9731-426a24f54df9'
                }

        :return:
                Datapath data if the insertion is successful
                revoke transaction and raise exception
        """
        session = get_session()
        with session.begin():
            dp_row = Datapaths(id=datapath.id)
            dp_row.update(datapath.as_dict())
            session.add(dp_row)
            session.flush()

        dp = self._row_to_datapath(dp_row)
        dp.switchname = session.query(Switches.name).filter(Switches.id == dp.switch).all()[0][0]
        dp.domainname = session.query(Domains.name).filter(Domains.id == dp.domain).all()[0][0]
        return dp

    def update_datapath(self, datapath):
        """Update an Datapath.

        :param datapath: the datapath to update
        """
        session = get_session()
        with session.begin():
            dp_row = session.merge(Datapaths(id=datapath.id))
            dp_row.update(datapath.as_dict())
            session.flush()

        dp = self._row_to_datapath(dp_row)
        dp.switchname = session.query(Switches.name).filter(Switches.id == dp.switch).all()[0][0]
        dp.domainname = session.query(Domains.name).filter(Domains.id == dp.domain).all()[0][0]
        return dp

    def get_datapaths(self, datapath_id=None, datapath_name=None, switch=None, pagination=None):
        """Yields a lists of ports that match filters

        :param datapath_id: Optional datapath_id to return one datapath details.
        :param datapath_name: Optional datapath_name to filter
        :param switch: Optional switch id to filter
        :param pagination: Optional pagination query.
        """

        if pagination:
            raise NotImplementedError(_('Pagination not implemented'))

        session = get_session()
        query = session.query(Datapaths)
        if datapath_id is not None:
            query = query.filter(Datapaths.id == datapath_id)

        if datapath_name is not None:
            query = query.filter(Datapaths.name == datapath_name)

        if switch is not None:
            query = query.filter(Datapaths.switch == switch)

        dps = [self._row_to_datapath(x) for x in query.all()]
        for dp in dps:
            dp.switchname = session.query(Switches.name).filter(Switches.id == dp.switch).all()[0][0]
            dp.domainname = session.query(Domains.name).filter(Domains.id == dp.domain).all()[0][0]

        return dps

    @staticmethod
    def delete_datapath(datapath_id):
        """Delete a Datapath

        :param datapath_id: ID of the Datapath to delete
        """
        session = get_session()
        with session.begin():
            session.query(Datapaths).filter(Datapaths.id == datapath_id).delete()
            session.flush()


    @staticmethod
    def _row_to_nwport(row):
        return api_model.NWPort(id=row.id,
                                name=row.name,
                                network_type=row.network_type,
                                data_ip=row.data_ip,
                                bridge=row.bridge,
                                vxlan_vni=row.vxlan_vni,
                                vxlan_port=row.vxlan_port,
                                ip_address=row.ip_address,
                                flow_type=row.flow_type,
                                ovs_port=row.ovs_port,
                                local_data_ip=row.local_data_ip,
                                host=row.host)

    def create_nwport(self, nwport):
        """
        Insert nwport record into database

        :param nwport:
                {
                    id: '',
                    name: '',
                    network_type: '',
                    data_ip: '',
                    bridge: '',
                    ip_address: '',
                    vxlan_vni: '',
                    vxlan_port: '',
                    flow_type: '',
                    ovs_port: '',
                    local_data_ip: ''
                }

        :return:
                Port data if the insertion is successful
                revoke transaction and raise exception
        """
        session = get_session()
        with session.begin():
            nwport_row = NWPorts(id=nwport.id)
            nwport_row.update(nwport.as_dict())
            session.add(nwport_row)
            session.flush()

        nwport_out = self._row_to_nwport(nwport_row)
        return nwport_out

    def update_nwport(self, nwport):
        """Update an Port.

        :param nwport: the nwport to update
        """
        session = get_session()
        with session.begin():
            nwport_row = session.merge(NWPorts(id=nwport.id))
            nwport_row.update(nwport.as_dict())
            session.flush()

        nwport_out = self._row_to_nwport(nwport_row)

        return nwport_out

    def get_nwports(self, nwport_id=None, name=None, pagination=None):
        """Yields a lists of nwports that match filters
        :param name: Optional name to return one virtual machine.
        :param nwport_id: Optional nwport_id to return one nwport details.
        :param pagination: Optional pagination query.
        """

        if pagination:
            raise NotImplementedError(_('Pagination not implemented'))

        session = get_session()
        query = session.query(NWPorts)
        if name is not None:
            query = query.filter(NWPorts.name == name)
        if nwport_id is not None:
            query = query.filter(NWPorts.id == nwport_id)

        nwports = [self._row_to_nwport(x) for x in query.all()]
        return nwports

    @staticmethod
    def delete_nwport(nwport_id):
        """Delete a Port

        :param nwport_id: ID of the Virtual Port to delete
        """
        session = get_session()
        with session.begin():
            session.query(NWPorts).filter(NWPorts.id == nwport_id).delete()
            session.flush()
