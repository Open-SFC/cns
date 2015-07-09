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
import time

from nscs.ocas_utils.openstack.common.gettextutils import _
from nscs.ocas_utils.openstack.common import log as logging
#from nscs.crd_consumer.client.common import rm_exceptions as exceptions
from cns.crdconsumer import exceptions
from cns.crdconsumer.client import ocas_client
from nscs.ocas_utils.openstack.common import context
from nscs.ocas_utils.openstack.common.rpc import proxy

LOG = logging.getLogger(__name__)

class CNSConsumerPlugin(proxy.RpcProxy):
    """
    Implementation of the Crd Consumer Core Network Service Plugin.
    """
    RPC_API_VERSION = '1.0'
    
    def __init__(self):
        super(CNSConsumerPlugin,self).__init__(topic="crd-service-queue",default_version=self.RPC_API_VERSION)
        self.uc = ocasclient()
        self.listener_topic = 'crd-listener'
        # RPC network init
        self.consumer_context = context.RequestContext('crd', 'crd',
                                                       is_admin=False)
        
    def get_plugin_type(self):
        return "CNS"
    
    def init_consumer(self, consumer=None):
        delta_msg = {}
        delta_msg = self.call(self.consumer_context,self.make_msg('cns_init_consumer',consumer=consumer),self.listener_topic)
        return delta_msg
        
    
    def build_ucm_wsgi_msg(self, payload, message_type=None):
        msg = {}
        if message_type == 'create_network':
            nwname = payload.get('network_id')[:16]
            nwname = payload.get('name') + "_" + nwname
            nwdesc = ''
            tenant = payload.get('tenant_id')
            type = payload.get('network_type')
            segmentation_id = payload.get('segmentation_id')
            vxlan_service_port = int(payload.get('vxlan_service_port', 4789))
            external = payload.get('router_external')
            status = payload.get('status')
            state = payload.get('admin_state_up')
            if external == 1:
                external = True
            else:
                external = False
            msg = {"virtualnetwork":{"name": nwname,
                                     "id": payload.get('network_id'),
                                     "tenant": tenant,
                                     "type": type,
                                     "segmentation_id": segmentation_id,
                                     "external": external,
                                     "state": state,
                                     "status": status.lower(),
                                     "vxlan_service_port": vxlan_service_port,
                                    }
                }
        elif message_type == 'update_network':
            nwname = payload.get('network_id')[:16]
            nwname = payload.get('name') + "_" + nwname
            msg = {"virtualnetwork":{
                    "name": nwname
                    }
                }
        elif message_type == 'create_subnet':
            subnetname = payload.get('subnet_id')[:16]
            subnetname = payload.get('name') + "_" + subnetname
            ip_version = payload.get('ip_version')
            gateway_ip = payload.get('gateway_ip')
            cidr = payload.get('cidr')
            allocation_pools = str(payload.get('allocation_pools')).split(',')
            pool_details = str(allocation_pools[0]).split('-')
            
            enable_dhcp = True
            
            ###Constructin Allocation Pools dictionary
            allocation_pools = []
            pools_str = str(payload.get('allocation_pools'))
            dns_servers = []
            dns_str = str(payload.get('dns_servers'))
            
            msg = {"subnet":{
                    'name': subnetname,
                    'id': payload.get('subnet_id'),
                    'dhcp': enable_dhcp,
                    'ip_version': ip_version,
                    'gateway_ip': gateway_ip,
                    'cidr': cidr,
                    'pools': pools_str,
                    'dns_servers': dns_str,
                    'nw_id': payload.get('network_id'),
                    'host_routes': payload.get('host_routes')
                    }
                }
        elif message_type == 'update_subnet':
            subnetname = payload.get('subnet_id')[:16]
            subnetname = payload.get('name') + "_" + subnetname
            gateway_ip = payload.get('gateway_ip')
            
            enable_dhcp = True
            ###Constructin DNS Servers dictionary
            dns_servers = []
            dns_str = str(payload.get('dns_servers'))
            if dns_str:
                dns_servers = dns_str.split(',')
            ###
            
            msg = {"subnet":{
                    'name': subnetname,
                    'dhcp': enable_dhcp,
                    'gateway_ip': gateway_ip,
                    'dns_servers': dns_servers
                    }
                }
        elif message_type == 'create_port' or message_type == 'update_port':
            portname = payload.get('port_id')[:11]
            portname = "tap" + portname
            tenant = payload.get('tenant_id')
            mac_address = payload.get('mac_address')
            ip = payload.get('ip_address')
            subnetname = payload.get('subnet_id')[:16]
            nwname = payload.get('network_id')[:16]
            status = payload.get('status')
            state = payload.get('admin_state_up')
            msg = {"port":{"name":portname,
                           "id":payload.get('port_id'),
                           "tenant":tenant,
                           "mac_address":mac_address,
                           "ip_address":ip,
                           "subnet_id":payload.get('subnet_id'),
                           "nw_id":payload.get('network_id'),
                           "device_id":payload.get('device_id'),
                           "device_owner":payload.get('device_owner'),
                           "status":payload.get('status'),
                           "state":payload.get('admin_state_up'),
                           "bridge": 'br-int',
                        }
                }
            
        elif message_type == 'create_instance' or message_type == 'update_instance':
            vmname = payload.get('instance_id')[:16]
            vmname = payload.get('display_name') + "_" + vmname
            tenant = payload.get('tenant_id')
            host = 'os_' + payload.get('host')
            host = host[:16]
            type = payload.get('type')
            msg = {"virtualmachine":{"name":vmname,
                                     "id":payload.get('instance_id'),
                                     "tenant":tenant,
                                     "host":host,
                                     "user_id":payload.get('user_id'),
                                     "state_description":payload.get('state_description'),
                                     "state":payload.get('state'),
                                     "created_at":payload.get('created_at'),
                                     "reservation_id":payload.get('reservation_id'),
                                     "type":type,
                                    }
                }
        elif message_type == 'create_datapath':
            #{"datapath":{"datapathid":"132345","switch":"SWITCH-1","domain":"L3_FWD_DOMAIN","subjectname":"test-curl"}}
            datapath_id = payload.get('datapath_id')
            datapath_name = payload.get('datapath_name')
            switch = 'os_' + payload.get('switch')
            domain = 'TSC_' + payload.get('domain')
            subject_name = payload.get('subject_name')
            
            ###Insert Switch Details
            switch = switch
            fqdn = 'testfqdn'
            ip_address = payload.get('ip_address')
            data_ip = payload.get('data_ip')
            type = False
            baddr = False
            switch_details = self.create_switch(self.consumer_context, payload={'switch':{'name': switch[:16], 'ip_address': data_ip, 'fqdn': fqdn, 'type': type, 'baddr': baddr}})
            #LOG.info(_("Switch Details: %s"), str(switch_details))
            
            ###Insert Domain Details
            domain = domain
            domain_details = self.create_domain(self.consumer_context, payload={'domain':{'name': domain, 'subject': 'openstack'}})
            #LOG.info(_("Domain Details: %s"), str(domain_details))
            
            msg = {"datapath":{"id":datapath_id,
                        "name": datapath_name,
                        "switch":switch_details['switch']['id'],
                        "domain":domain_details['domain']['id'],
                        "subject":subject_name,
                    }
                }
        elif message_type == 'create_nwport':
            portname = payload.get('name')
            tenant = payload.get('tenant_id')
            vxlan_port = int(payload.get('vxlan_udpport'))
            ip = payload.get('ip_address')
            data_ip = payload.get('data_ip')
            vxlan_vni = int(payload.get('vxlan_vni'))
            network_type = payload.get('network_type')
            ovs_port = int(payload.get('ovs_port'))
            bridge = payload.get('bridge')
            flow_type = payload.get('flow_type')
            #vlan_id = int(payload.get('vlan_id'))
            local_data_ip = payload.get('local_data_ip')
            host = 'os_' + payload.get('host')
            host = host[:16]
            msg = {"nwport":{"name":portname,
                           "vxlan_port":vxlan_port,
                           "ip_address":ip,
                           "data_ip":data_ip,
                           "vxlan_vni":vxlan_vni,
                           "network_type":network_type,
                           "ovs_port":ovs_port,
                           "bridge":bridge,
                           "flow_type":flow_type,
                           #"vlan_id":payload.get('vlan_id'),
                           "local_data_ip":local_data_ip,
                           "host":host,
                        }
                }
        
        return msg
    
    
    def create_datapath(self, context, **kwargs):
        payload = kwargs['payload']
        body = self.build_ucm_wsgi_msg(payload, 'create_datapath')
        #LOG.info(_("Create Datapath - %s"), str(body))
        self.uc.create_datapath(body=body)
        
    def create_domain(self, context, **kwargs):
        payload = kwargs['payload']
        try:
            domain_details = self.get_domain(payload['domain'].get('name'))
        except :
            #LOG.info(_("Create Domain - %s"), str(payload))
            domain_details = self.uc.create_domain(body=payload)
            
        return domain_details
        
    def create_switch(self, context, **kwargs):
        payload = kwargs['payload']
        try:
            switch_details = self.get_switch(payload['switch'].get('name'))
        except :
            #LOG.info(_("Create Switch - %s"), str(payload))
            switch_details = self.uc.create_switch(body=payload)
            
        return switch_details
        
    def get_switch(self, switch, **params):
        #LOG.info(_("Show Switch Details for - %s"), str(switch))
        return self.uc.show_switch(switch, **params)
        
    def get_domain(self, domain, **params):
        #LOG.info(_("Show Domain Details for - %s"), str(domain))
        return self.uc.show_domain(domain, **params)
    
    def create_virtual_network(self, context, **kwargs):
        #LOG.info(_("Create Network Body - %s"), str(kwargs))
        payload = kwargs['payload']
        body = self.build_ucm_wsgi_msg(payload, 'create_network')
        #LOG.info(_("Create Network Body - %s"), str(body))
        self.uc.create_virtualnetwork(body=body)
        
    def delete_virtual_network(self, context, **kwargs):
        payload = kwargs['payload']
        nwname = payload.get('network_id')
        #LOG.info(_("Delete Network Name- %s"), str(nwname))
        self.uc.delete_virtualnetwork(nwname)
        
    def update_virtual_network(self, context, **kwargs):
        payload = kwargs['payload']
        nwname = payload.get('network_id')
        body = self.build_ucm_wsgi_msg(payload, 'update_network')
        #LOG.info(_("Update Network Name- %s and body=%s"), str(nwname), str(body))
        self.uc.update_virtualnetwork(nwname, body=body)
        
    def get_virtual_networks(self, **params):
        #LOG.info(_("List Virtual Networks"))
        self.uc.list_virtual_networks(**params)
        
    def get_virtual_network(self, payload, **params):
        nwname = payload.get('network_id')
        #LOG.info(_("Show Virtual Network Details for - %s"), str(nwname))
        self.uc.show_virtualnetwork(nwname, **params)
        
    def create_subnet(self, context, **kwargs):
        payload = kwargs['payload']
        nwname = payload.get('network_id')
        body = self.build_ucm_wsgi_msg(payload, 'create_subnet')
        #LOG.info(_("Create Subnet - %s"), str(body))
        self.uc.create_subnet(nwname, body=body)
        
    def delete_subnet(self, context, **kwargs):
        payload = kwargs['payload']
        nwname = payload.get('network_id')
        subnetname = payload.get('subnet_id')
        #LOG.info(_("Delete Subnet Name - %s"), str(subnetname))
        self.uc.delete_subnet(nwname, subnetname)
    
    def update_subnet(self, context, **kwargs):
        payload = kwargs['payload']
        nwname = payload.get('network_id')
        subnetname = payload.get('subnet_id')
        body = self.build_ucm_wsgi_msg(payload, 'update_subnet')
        #LOG.info(_("Update Subnet Name- %s and network=%s and body=%s"), str(subnetname), str(nwname), str(body))
        self.uc.update_subnet(nwname, subnetname, body=body)
        
    def get_subnets(self, payload, **params):
        nwname = payload.get('network_id')
        #LOG.info(_("List Subnets of Network Name- %s"), str(nwname))
        self.uc.list_subnets(nwname, **params)
        
    def get_subnet(self, payload, **params):
        nwname = payload.get('network_id')
        subnetname = payload.get('subnet_id')
        #LOG.info(_("Show Subnet Details for Network - %s, Subnet - %s"), str(nwname), str(subnetname))
        self.uc.show_subnet(nwname, subnetname, **params)
        
    def create_port(self, context, **kwargs):
        payload = kwargs['payload']
        body = self.build_ucm_wsgi_msg(payload, 'create_port')
        #LOG.info(_("Create Port Body - %s"), str(body))
        retry = 5
        while retry:
            try:
                self.uc.create_port(body=body)
                break
            except Exception:
                retry -= 1
                time.sleep(2)
        
    def delete_port(self, context, **kwargs):
        payload = kwargs['payload']
        portname = payload.get('port_id')
        #LOG.info(_("Delete Port Name- %s"), str(portname))
        self.uc.delete_port(portname)
        
    def update_port(self, context, **kwargs):
        payload = kwargs['payload']
        portname = payload.get('port_id')
        body = self.build_ucm_wsgi_msg(payload, 'update_port')
        #LOG.info(_("Update Port Name- %s and body=%s"), str(portname), str(body))
        self.uc.update_port(portname, body=body)
        
    def get_ports(self, **params):
        #LOG.info(_("List Ports"))
        self.uc.list_ports(**params)
        
    def get_port(self, payload, **params):
        portname = payload.get('port_id')
        #LOG.info(_("Show Port Details for - %s"), str(portname))
        self.uc.show_port(portname, **params)
        
    def create_instance(self, context, **kwargs):
        payload = kwargs['payload']
        body = self.build_ucm_wsgi_msg(payload, 'create_instance')
        #LOG.info(_("Create Instance Body - %s"), str(body))
        self.uc.create_virtualmachine(body=body)
        
    def delete_instance(self, context, **kwargs):
        payload = kwargs['payload']
        vmname = payload.get('instance_id')
        #LOG.info(_("Delete Instance Name- %s"), str(vmname))
        self.uc.delete_virtualmachine(vmname)
        
    def update_instance(self, context, **kwargs):
        payload = kwargs['payload']
        vmname = payload.get('instance_id')
        body = self.build_ucm_wsgi_msg(payload, 'update_instance')
        #LOG.info(_("Update Instance Name- %s and body=%s"), str(vmname), str(body))
        self.uc.update_virtualmachine(vmname, body=body)
        
    def get_instances(self, **params):
        #LOG.info(_("List Instances"))
        self.uc.list_virtualmachines(**params)
        
    def get_instance(self, payload, **params):
        vmname = payload.get('instance_id')
        #LOG.info(_("Show Instance Details for - %s"), str(vmname))
        self.uc.show_virtualmachine(vmname, **params)
        
    def create_nwport(self, context, **kwargs):
        #LOG.info(_("Create Networkside Ports - %s"), str(kwargs))
        payload = kwargs['payload']
        body = self.build_ucm_wsgi_msg(payload, 'create_nwport')
        #LOG.info(_("Create Network side Ports Body - %s"), str(body))
        self.uc.create_nwport(body=body)
        
def ocasclient():
    c = ocas_client.Client()
    return c
