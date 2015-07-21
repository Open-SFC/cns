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

import logging
from nscs.crd_consumer.client import ocas_client

_logger = logging.getLogger(__name__)

class Client(object):
    """
    CNS related OCAS Client Functions in CRD Consumer 
    """
    
    def __init__(self, **kwargs):
        self.ocasclient = ocas_client.Client(**kwargs)
        #self.crdclient.EXTED_PLURALS.update(self.FW_EXTED_PLURALS)
        self.format = 'json'
        url = self.ocasclient.url
        dps = 'datapaths'
        networks = 'virtualnetworks'
        subnets = 'subnets'
        ports = 'ports'
        instances = 'virtualmachines'
        switches = 'switches'
        doms = 'domains'
        nw_ports = 'nwports'
        
        #Datapath URL
        self.datapaths = "%s/cns/%s" % (url, dps)
        self.datapath = "%s/cns/%s" % (url, dps) + "/%s"
        self.switchs = "%s/cns/%s" % (url, switches)
        self.switch = "%s/cns/%s" % (url, switches) + "/%s"
        self.domains = "%s/cns/%s" % (url, doms)
        self.domain = "%s/cns/%s" % (url, doms) + "/%s"
        
        #Virtual Networks URLs
        self.virtual_networks_path = "%s/cns/%s" % (url, networks)
        self.delete_virtual_network_path = "%s/cns/%s" % (url, networks) + "/%s"
        self.update_virtual_network_path = "%s/cns/%s" % (url, networks) + "/%s/attributes"
        
        #Subnets URLs
        self.subnets_path = "%s/cns/%s" % (url, networks) + "/%s" + "/%s" % (subnets)
        self.subnet_path = "%s/cns/%s" % (url, networks) + "/%s" + "/%s" % (subnets) + "/%s"
        
        #Ports URLs
        self.ports_path = "%s/cns/%s" % (url, ports)
        self.port_path = "%s/cns/%s" % (url, ports) + "/%s"
        
        #Instances URLs
        self.instances_path = "%s/cns/%s" % (url, instances)
        self.instance_path = "%s/cns/%s" % (url, instances) + "/%s"
        
        #Network Side Ports URLs
        self.nwports_path = "%s/cns/%s" % (url, nw_ports)
        self.nwport_path = "%s/cns/%s" % (url, nw_ports) + "/%s"
    
    def create_datapath(self, body=None):
        """
        Creates a new datapath
        """
        return self.ocasclient.post(self.datapaths, body=body)
        
    def show_datapath(self, dp, **_params):
        """
        Fetches information of a Datapath
        """
        return self.ocasclient.get(self.datapath % (dp), params=_params)
        
    def list_datapaths(self, **_params):
        """
        Fetches a list of all Datapaths
        """
        return self.ocasclient.list('datapaths', self.datapaths, True, **_params)
        
    def delete_datapath(self, dp):
        """
        Deletes the specified Datapath
        """
        return self.ocasclient.delete(self.datapath % (dp))
        
    def update_datapath(self, dp, body=None):
        """
        Updates the specified Datapath
        """
        return self.ocasclient.put(self.datapath % (dp), body=body)
        
    def create_domain(self, body=None):
        """
        Creates a new domain
        """
        return self.ocasclient.post(self.domains, body=body)
        
    def show_domain(self, domain, **_params):
        """
        Fetches information of a Domain
        """
        return self.ocasclient.get(self.domain % (domain), params=_params)
        
    def list_domains(self, **_params):
        """
        Fetches a list of all Domains
        """
        return self.ocasclient.list('domains', self.domains, True, **_params)
        
    def delete_domain(self, domain):
        """
        Deletes the specified Domain
        """
        return self.ocasclient.delete(self.domain % (domain))
        
    def create_switch(self, body=None):
        """
        Creates a new switch
        """
        return self.ocasclient.post(self.switchs, body=body)
        
    def list_switchs(self, **_params):
        """
        Fetches a list of all switches
        """
        switches = self.ocasclient.list('switches', self.switchs, True, **_params)['switches']
        return {'switchs':switches}
        
    def show_switch(self, switch, **_params):
        """
        Fetches information of a Switch
        """
        return self.ocasclient.get(self.switch % (switch), params=_params)
        
    def delete_switch(self, switch):
        """
        Deletes the specified switch
        """
        return self.ocasclient.delete(self.switch % (switch))
        
    def create_virtualnetwork(self, body=None):
        """
        Creates a new network
        """
        return self.ocasclient.post(self.virtual_networks_path, body=body)
        
    def delete_virtualnetwork(self, network):
        """
        Deletes the specified Virtual Network
        """
        return self.ocasclient.delete(self.delete_virtual_network_path % (network))
        
    def update_virtualnetwork(self, network, body=None):
        """
        Updates the specified Virtual Network
        """
        return self.ocasclient.put(self.delete_virtual_network_path % (network), body=body)
        
    def list_virtualnetworks(self, **_params):
        """
        Fetches a list of all networks
        """
        return self.ocasclient.list('virtualnetworks', self.virtual_networks_path, True, **_params)
        
    def show_virtualnetwork(self, network, **_params):
        """
        Fetches information of a Virtual network
        """
        return self.ocasclient.get(self.delete_virtual_network_path % (network), params=_params)
    
    def create_subnet(self, network, body=None):
        """
        Creates a new Subnet
        """
        ###Constructin Allocation Pools dictionary
        allocation_pools = []
        pools_str = body['subnet']['pools']
        if pools_str is not None:
            pools = pools_str.split(',')
            for pool in pools:
                if pool:
                    pstr = str(pool)
                    pdetails = pstr.split('-')
                    pool_details = {'start': pdetails[0], 'end': pdetails[1]}
                    allocation_pools.append(pool_details)
        body['subnet']['pools'] = allocation_pools
        
        ###Constructin DNS Servers dictionary
        dns_servers = []
        dns_str = body['subnet']['dns_servers']
        if dns_str and dns_str != 'None':
            dns_servers = dns_str.split(',')
        body['subnet']['dns_servers'] = dns_servers
        return self.ocasclient.post(self.subnets_path % (network), body=body)
        
    def delete_subnet(self, network, subnet):
        """
        Deletes the specified Subnet
        """
        return self.ocasclient.delete(self.subnet_path % (network, subnet))
        
    def update_subnet(self, network, subnet, body=None):
        """
        Updates the specified Subnet
        """
        if 'name' in body['subnet']:
            subnetname = str(body['subnet']['name'])
            subnetname = subnetname + "_" + subnet
            body['subnet']['name'] = subnetname
                
        if 'pools' in body['subnet']:
            allocation_pools = []
            pools_str = body['subnet']['pools']
            if pools_str is not None:
                pools = pools_str.split(',')
                for pool in pools:
                    pstr = str(pool)
                    pdetails = pstr.split('-')
                    pool_details = {'start': pdetails[0], 'end': pdetails[1]}
                    allocation_pools.append(pool_details)
            body['subnet']['pools'] = allocation_pools
            
        if 'dns_servers' in body['subnet']:
            dns_servers = []
            dns_str = body['subnet']['dns_servers']
            if dns_str is not None:
                dns_servers = dns_str.split(',')
            body['subnet']['dns_servers'] = dns_servers
        return self.ocasclient.put(self.subnet_path % (network, subnet), body=body)
        
    def list_subnets(self, network, **_params):
        """
        Fetches a list of all subnets of a network
        """
        return self.ocasclient.get(self.subnets_path % (network), params=_params)
        
    def show_subnet(self, network, subnet, **_params):
        """
        Fetches information of a Subnet
        """
        return self.ocasclient.get(self.subnet_path % (network, subnet), params=_params)
        
    def create_port(self, body=None):
        """
        Creates a new Port
        """
        return self.ocasclient.post(self.ports_path, body=body)
        
    def delete_port(self, port):
        """
        Deletes the specified Port
        """
        return self.ocasclient.delete(self.port_path % (port))
        
    def update_port(self, port, body=None):
        """
        Updates the specified Port
        """
        return self.ocasclient.put(self.port_path % (port), body=body)
        
    def list_ports(self, **_params):
        """
        Fetches a list of all ports
        """
        return self.ocasclient.get(self.ports_path, params=_params)
        
    def show_port(self, port, **_params):
        """
        Fetches information of a Port
        """
        return self.ocasclient.get(self.port_path % (port), params=_params)
        
    def create_virtualmachine(self, body=None):
        """
        Creates a new instance
        """
        return self.ocasclient.post(self.instances_path, body=body)
        
    def delete_virtualmachine(self, instance):
        """
        Deletes the specified instance
        """
        return self.ocasclient.delete(self.instance_path % (instance))
        
    def update_virtualmachine(self, instance, body=None):
        """
        Updates the specified instance
        """
        return self.ocasclient.put(self.instance_path % (instance), body=body)
        
    def list_virtualmachines(self, **_params):
        """
        Fetches a list of all instances
        """
        return self.ocasclient.get(self.instances_path, params=_params)
        
    def show_virtualmachine(self, instance, **_params):
        """
        Fetches information of a Instance
        """
        return self.ocasclient.get(self.instance_path % (instance), params=_params)
        
    def create_nwport(self, body=None):
        """
        Creates a new network
        """
        return self.ocasclient.post(self.nwports_path, body=body)
        
    def delete_nwport(self, network):
        """
        Deletes the specified Virtual Network
        """
        return self.ocasclient.delete(self.nwport_path % (network))
        
    def update_nwport(self, network, body=None):
        """
        Updates the specified Virtual Network
        """
        return self.ocasclient.put(self.nwport_path % (network), body=body)
        
    def list_nwports(self, **_params):
        """
        Fetches a list of all nw ports
        """
        return self.ocasclient.get(self.nwports_path, params=_params)
        
    def show_nwport(self, network, **_params):
        """
        Fetches information of a Virtual network
        """
        return self.ocasclient.get(self.nwport_path % (network), params=_params)
    
