# Copyright 2013 Freescale Semiconductor, Inc.
# All Rights Reserved
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
#
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import logging
from nscs.crdclient.v2_0 import client as crd_client

_logger = logging.getLogger(__name__)

class Client(object):
    """
    Firewall related Client Functions in CRD
    """
    ##Firewall URLs
    ofclusters_path = "/ofclusters"
    ofcluster_path =  "/ofclusters/%s"
    ofcontrollers_path = "/ofclusters/%s/ofcontrollers"
    ofcontroller_path =  "/ofclusters/%s/ofcontrollers/%s"
    logicalswitchs_path = "/ofclusters/%s/ofcontrollers/%s/logicalswitchs"
    logicalswitch_path =  "/ofclusters/%s/ofcontrollers/%s/logicalswitchs/%s"
    
    networks_path = "/networks"
    network_path = "/networks/%s"
    subnets_path = "/subnets"
    subnet_path = "/subnets/%s"
    ports_path = "/ports"
    port_path = "/ports/%s"
    computes_path = "/computes"
    compute_path = "/computes/%s"
    instances_path = "/instances"
    instance_path = "/instances/%s"

    
    ################################################################
    ##              Openflow Cluster Management                   ##
    ################################################################
    @crd_client.APIParamsCall
    def create_ofcluster(self, body=None):
        """
        create openflow Ccluster record
        """
        print body
        return self.crdclient.post(self.ofclusters_path,body=body)

    @crd_client.APIParamsCall
    def list_ofclusters(self, retrieve_all=True, **_params):
        """
        Fetches a list of all Openflow clusters
        """
        # Pass filters in "params" argument to do_request
        return self.crdclient.get(self.ofclusters_path,params = _params)

    @crd_client.APIParamsCall
    def update_ofcluster(self, cluster, body=None):
        """
        Updates Openflow Controller record
        """
        print cluster, body
        return self.crdclient.put(self.ofcluster_path % (cluster), body=body)

    @crd_client.APIParamsCall
    def show_ofcluster(self, cluster, body=None):
        """
        Display a Openflow cluster record
        """
        return self.crdclient.get(self.ofcluster_path % (cluster), body=body)

    @crd_client.APIParamsCall
    def delete_ofcluster(self, cluster, body=None):
        """
        Delete Openflow cluster
        """
        return self.crdclient.delete(self.ofcluster_path % (cluster), body=body)

    ################################################################
    ##              Openflow Controller Management                ##
    ################################################################

    @crd_client.APIParamsCall
    def create_ofcontroller(self,body=None):
        """
        create openflow Controller record 
        """
        cluster_id = body['ofcontroller']['cluster_id']
        return self.crdclient.post(self.ofcontrollers_path % (cluster_id),body=body)
       
    @crd_client.APIParamsCall
    def list_ofcontrollers(self,retrieve_all=True, **_params):
        """
        Fetches a list of all Openflow Controllers
        """
        cluster_id = _params['id']
        return self.crdclient.get(self.ofcontrollers_path % (cluster_id), params = _params)
        
    @crd_client.APIParamsCall
    def update_ofcontroller(self,id,body=None):
        """
        Updates Openflow Controller record
        """
        cluster_id = body['ofcontroller']['cluster_id']
        id = body['ofcontroller']['id']
        body['ofcontroller'].pop('id')
        body['ofcontroller'].pop('cluster_id')
        return self.crdclient.put(self.ofcontroller_path % (cluster_id,id), body=body)

    @crd_client.APIParamsCall
    def show_ofcontroller(self,id,body=None):
        """
        Display a Openflow Controller record
        """
        cluster_id = body['cluster_id']
        return self.crdclient.get(self.ofcontroller_path % (cluster_id,id), body=body)

    @crd_client.APIParamsCall
    def delete_ofcontroller(self,id, body=None):
        """
        Delete Openflow Controller
        """
        filters = body['body']
        cluster_id = filters.get('cluster_id')
        id = filters.get('id')
        body = None
        return self.crdclient.delete(self.ofcontroller_path % (cluster_id,id), body=body)

    
    ################################################################
    ##              Openflow Switch Management                    ##
    ################################################################

    @crd_client.APIParamsCall
    def create_logicalswitch(self,body=None):
        """
        create Logical Switch record
        """
        print "create_logicalswitch => ",body
        cluster_id = body['logicalswitch']['cluster_id']
        controller_id = body['logicalswitch']['controller_id']
        return self.crdclient.post(self.logicalswitchs_path % (cluster_id, controller_id),body=body)

    @crd_client.APIParamsCall
    def list_logicalswitchs(self, cluster_id, controller_id, retrieve_all=True, **_params):
        """
        Fetches a list of all Logical Switches
        """
        return self.crdclient.get(self.logicalswitchs_path % (cluster_id, controller_id),params = _params)

    @crd_client.APIParamsCall
    def show_logicalswitch(self,id,body=None):
        """
        Display a logicalswitch record
        """
        cluster_id = body['cluster_id']
        controller_id = body['controller_id']
        return self.crdclient.get(self.logicalswitch_path % (cluster_id, controller_id,id), body=body)

    @crd_client.APIParamsCall
    def delete_logicalswitch(self, id, body=None):
        """
        Delete logical switch records
        """
        print "============>", body
        filters = body['body']
        cluster_id = filters.get('cluster_id')
        controller_id = filters.get('controller_id')
        id = filters.get('id')
        body = None
        return self.crdclient.delete(self.logicalswitch_path % (cluster_id, controller_id,id), body=body)
    
    
    
    
    
    ##################################Network Extension Start####################################
    @crd_client.APIParamsCall
    def create_network(self, body=None):
        """
        create Crd Network
        """
        return self.crdclient.post(self.networks_path,body=body)
        
    @crd_client.APIParamsCall
    def update_network(self, network, body=None):
        """
        Updates a network
        """
        return self.crdclient.put(self.network_path % (network), body=body)
        
    @crd_client.APIParamsCall
    def list_networks(self, **_params):
        """
        Fetches a list of all networks for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.crdclient.get(self.networks_path, params=_params)
        
    @crd_client.APIParamsCall
    def delete_network(self, network):
        """
        Deletes the specified network
        """
        return self.crdclient.delete(self.network_path % (network))
    
    @crd_client.APIParamsCall
    def show_network(self, network, **_params):
        """
        Fetches information of a certain network
        """
        return self.crdclient.get(self.network_path % (network), params=_params)
        
    
    
    ################################## Network Extension End####################################
    
    
    ##################################Subnet Extension Start####################################
    @crd_client.APIParamsCall
    def create_subnet(self, body=None):
        """
        create Crd Network
        """
        return self.crdclient.post(self.subnets_path,body=body)
        
    @crd_client.APIParamsCall
    def update_subnet(self, subnet, body=None):
        """
        Updates a subnet
        """
        return self.crdclient.put(self.subnet_path % (subnet), body=body)
        
    @crd_client.APIParamsCall
    def list_subnets(self, **_params):
        """
        Fetches a list of all subnets for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.crdclient.get(self.subnets_path, params=_params)
        
    @crd_client.APIParamsCall
    def delete_subnet(self, subnet):
        """
        Deletes the specified subnet
        """
        return self.crdclient.delete(self.subnet_path % (subnet))
    
    @crd_client.APIParamsCall
    def show_subnet(self, subnet, **_params):
        """
        Fetches information of a certain subnet
        """
        return self.crdclient.get(self.subnet_path % (subnet), params=_params)
        
    
    
    ################################## Subnet Extension End####################################
    
    ################################## Port Extension Start####################################
    @crd_client.APIParamsCall
    def create_port(self, body=None):
        """
        create Crd Network
        """
        return self.crdclient.post(self.ports_path,body=body)
        
    @crd_client.APIParamsCall
    def update_port(self, port, body=None):
        """
        Updates a port
        """
        return self.crdclient.put(self.port_path % (port), body=body)
        
    @crd_client.APIParamsCall
    def list_ports(self, **_params):
        """
        Fetches a list of all ports for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.crdclient.get(self.ports_path, params=_params)
        
    @crd_client.APIParamsCall
    def delete_port(self, port):
        """
        Deletes the specified port
        """
        return self.crdclient.delete(self.port_path % (port))
    
    @crd_client.APIParamsCall
    def show_port(self, port, **_params):
        """
        Fetches information of a certain port
        """
        return self.crdclient.get(self.port_path % (port), params=_params)
        
    
    
    ################################## Port Extension End####################################
    
    ################################## Compute Extension Start####################################
    @crd_client.APIParamsCall
    def create_compute(self, body=None):
        """
        create Crd Network
        """
        return self.crdclient.post(self.computes_path,body=body)
        
    @crd_client.APIParamsCall
    def update_compute(self, compute, body=None):
        """
        Updates a compute
        """
        return self.crdclient.put(self.compute_path % (compute), body=body)
        
    @crd_client.APIParamsCall
    def list_computes(self, **_params):
        """
        Fetches a list of all computes for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.crdclient.get(self.computes_path, params=_params)
        
    @crd_client.APIParamsCall
    def delete_compute(self, compute):
        """
        Deletes the specified compute
        """
        return self.crdclient.delete(self.compute_path % (compute))
    
    @crd_client.APIParamsCall
    def show_compute(self, compute, **_params):
        """
        Fetches information of a certain compute
        """
        return self.crdclient.get(self.compute_path % (compute), params=_params)
        
    
    
    ################################## Compute Extension End####################################
    
    
    ################################## Instance Extension Start####################################
    @crd_client.APIParamsCall
    def create_instance(self, body=None):
        """
        create Crd Network
        """
        return self.crdclient.post(self.instances_path,body=body)
        
    @crd_client.APIParamsCall
    def update_instance(self, instance, body=None):
        """
        Updates a instance
        """
        return self.crdclient.put(self.instance_path % (instance), body=body)
        
    @crd_client.APIParamsCall
    def list_instances(self, **_params):
        """
        Fetches a list of all instances for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.crdclient.get(self.instances_path, params=_params)
        
    @crd_client.APIParamsCall
    def delete_instance(self, instance):
        """
        Deletes the specified instance
        """
        return self.crdclient.delete(self.instance_path % (instance))
    
    @crd_client.APIParamsCall
    def show_instance(self, instance, **_params):
        """
        Fetches information of a certain instance
        """
        return self.crdclient.get(self.instance_path % (instance), params=_params)
        
    
    
    ################################## Instance Extension End####################################
        
    def __init__(self, **kwargs):
        self.crdclient = crd_client.Client(**kwargs)
        #self.crdclient.EXTED_PLURALS.update(self.FW_EXTED_PLURALS)
        self.format = 'json'
    
