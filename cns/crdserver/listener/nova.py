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
from nscs.crdserver.openstack.common import context
from nscs.crdserver import context as crd_context
from nscs.crdserver.openstack.common import rpc
from nscs.crdserver.openstack.common.rpc import dispatcher
from nscs.crdserver.openstack.common.rpc import proxy
from oslo.config import cfg
from novaclient.v1_1 import client as nova_client
from nscs.crdserver.openstack.common import timeutils
from nscs.crdserver.common import exceptions as crd_exc




import re
import socket
import time
import datetime

LOG = logging.getLogger(__name__)


crd_nova_opts = [
    cfg.StrOpt('admin_user',default="neutron"),
    cfg.StrOpt('admin_password',default="password"),
    cfg.StrOpt('admin_tenant_name',default="service"),
    cfg.StrOpt('auth_url'),
    cfg.StrOpt('endpoint_url'),
]
cfg.CONF.register_opts(crd_nova_opts, "CRDNOVACLIENT")

crd_ofcontroller = [
    cfg.StrOpt('cluster',default="DefaultCluster"),
    cfg.StrOpt('controller',default="DefaultController"),
    cfg.StrOpt('ovs_port',default="8090"),
]
cfg.CONF.register_opts(crd_ofcontroller, "OFCONTROLLER")

crd_ovs = [
    cfg.StrOpt('network_type',default="vxlan"),
    cfg.StrOpt('vxlan_udp_port',default="4789"),
    cfg.StrOpt('flow_type',default="ip"),
    cfg.StrOpt('integration_bridge',default="br-int"),
]
cfg.CONF.register_opts(crd_ovs, "OVS")

crd_interfaces = [
    cfg.StrOpt('host_ip',default="127.0.0.1"),
    cfg.StrOpt('data_ip',default="127.0.0.1"),
    
]
cfg.CONF.register_opts(crd_interfaces, "NETWORKNODE")

class NovaListener(proxy.RpcProxy):
    """
    Keep listening on Nova and CRD-Consumer Notifications
    """
    RPC_API_VERSION = '1.0'
    
    def __init__(self):
	self.context = crd_context.Context('crd', 'crd',
                                                   is_admin=True)
        #super(NovaListener,self).__init__(topic='crd-service-consume',default_version=self.RPC_API_VERSION)
        polling_interval = 2
        reconnect_interval = 2
        self.rpc = True
        
        self.polling_interval = polling_interval
        self.reconnect_interval = reconnect_interval
        if self.rpc:
            self.setup_rpc()
        LOG.info("NOVA RPC Listener initialized successfully, now running...")
        
    
    def setup_rpc(self):
        self.host = self.get_hostname()
        self.listen_topic = "crd-service-consume"
	self.consumer_listener_topic = "crd-listener"

        # CRD RPC Notification
        self.listen_context = context.RequestContext('crd', 'crd',
                                              is_admin=False)
        
        # Handle updates from service
        self.dispatcher = self.create_rpc_dispatcher()
        #self.dispatcher = None
        # Define the listening consumers for the agent
        self.listen_conn = rpc.create_connection(new=True)
        #LOG.debug(_("Creating CONSUMER with topic %s....\n"), self.listen_topic)
        self.listen_conn.join_consumer_pool(self.process_event,self.listen_topic,'notifications.info','nova')
        self.listen_conn.join_consumer_pool(self.process_event,self.listen_topic,'scheduler','nova')
        self.listen_conn.join_consumer_pool(self.process_event,self.listen_topic,'conductor','nova')
        self.listen_conn.join_consumer_pool(self.process_event,self.listen_topic,'crd-service-consume','crd')
        self.listen_conn.consume_in_thread()
	
	self.consumer_conn =  rpc.create_connection(new=True)
	self.consumer_conn.create_consumer(self.consumer_listener_topic, self.dispatcher, fanout=False)
        self.consumer_conn.consume_in_thread()
        
        #self.cast(self.listen_context,self.make_msg('check_compute_status',payload={'Status':'Active'}))
        
        
    def get_hostname(self):
        return "%s" % socket.gethostname()
    
    def create_rpc_dispatcher(self):
        '''Get the rpc dispatcher for this manager.

        If a manager would like to set an rpc API version, or support more than
        one class as the target of rpc messages, override this method.
        '''
        return dispatcher.RpcDispatcher([self])

    def process_event(self,message_data):
        event_type = message_data.get('event_type', None)
        method = message_data.get('method', None)
        if event_type is not None:
            payload = message_data.get('payload', {})
            if event_type == 'compute.instance.update':
                host_node = payload['host']
                if host_node != None:
                    nt = self.novaclient()
                    host_node_details = nt.hypervisors.search(host_node)
                    compute_id = host_node_details[0].id
                    compute = self.get_compute(self.context,compute_id)
                    if compute:
                        self.create_instance_notification(payload)
            elif event_type == 'scheduler.run_instance.scheduled':
                self.create_compute_logicalswitch(payload,'inst')
                pass
        if (method is not None) and (method == 'compute_node_update'):
            payload = message_data.get('args', None)
            if payload is not None:
                node_details = payload.get('node', None)
                if (node_details is not None) and (type(node_details) is dict):
                    self.create_compute_logicalswitch(node_details,'rpc')
                    pass
        
        if (method is not None) and (method == 'check_compute_status'):
            self.check_compute_status()
            
    def novaclient(self):
        return  nova_client.Client(cfg.CONF.CRDNOVACLIENT.admin_user,
                                   cfg.CONF.CRDNOVACLIENT.admin_password,
                                   cfg.CONF.CRDNOVACLIENT.admin_tenant_name,
                                   auth_url=cfg.CONF.CRDNOVACLIENT.auth_url,
                                   service_type="compute")
    
    def check_compute_status(self):
        nt = self.novaclient()
        computes = self.get_computes(self.context)
        if computes:
            for compute in computes:
                host_name = compute['hostname']
                compute_id = compute['compute_id']
                host_node_details = nt.services.list(host_name)
                if host_node_details:
                    state = host_node_details[0].state
                    if state == 'down':
                        body = {'compute': {'status': 'Inactive'}}
                        self.update_compute(self.context,compute_id,body)
                    if state == 'up':
                        body = {'compute': {'status': 'Active'}}
                        self.update_compute(self.context,compute_id,body)
        #time.sleep(5)
        #self.cast(self.listen_context,self.make_msg('check_compute_status',payload={'Status':'Active'}))
        
        
    def create_compute_logicalswitch(self, payload,type):
        if type == 'rpc':
            host_node = payload['hypervisor_hostname']
            compute_id = payload['id']
            compute_ipaddress = payload['host_ip']
            compute_dataip = payload['data_ip']
        if type == 'inst':
            host_node = payload['weighted_host']['host']
            nt = self.novaclient()
            host_node_details = nt.hypervisors.search(host_node)
            #LOG.debug(_("host_node_details %s\n"), str(host_node_details[0]))
            compute_id = host_node_details[0].id
            compute_ipaddress = host_node_details[0].host_ip
            compute_dataip = host_node_details[0].data_ip
        
        cluster = cfg.CONF.OFCONTROLLER.cluster
        controller = cfg.CONF.OFCONTROLLER.controller
        ovs_port = cfg.CONF.OFCONTROLLER.ovs_port
        
        integration_bridge = cfg.CONF.OVS.integration_bridge
        
        
        cluster_filters = {}
        cluster_filters['name']= [cluster]
        clusters = self.get_ofclusters(self.context,filters=cluster_filters)
        if clusters:
            cluster_id = clusters[0]['id']
            
            controller_filters = {}
            controller_filters['name']= [controller]
            controllers = self.get_ofcluster_ofcontrollers(self.context,cluster_id, filters=controller_filters)
            if controllers:
                controller_id = controllers[0]['id']
                try:
                    compute = self.get_compute(self.context,compute_id)
                except crd_exc.ComputeNotFound:
                    logicalswitchdata = {'logicalswitch':
                                    {
                                      'name' : integration_bridge,
                                      'ip_address' : compute_dataip,
                                      'port': ovs_port,
                                    }
                          }
                    logicalswitch = self.create_ofcluster_ofcontroller_logicalswitch(self.context,logicalswitchdata,cluster_id,controller_id)
                    LOG.info(_("Create Integration bridge :: Plugin %s\n"), str(logicalswitch))
                    if logicalswitch:
                        datapath_id = logicalswitch['datapath_id']
                        computedata = {'compute':
                                        {
                                            'compute_id': compute_id,
                                            'hostname': host_node,
                                            'ip_address': compute_ipaddress,
                                            'data_ip': compute_dataip,
                                            'created_at': datetime.datetime.now(),
                                            'ovs_port': ovs_port,
                                            'datapath_id': datapath_id,
                                            'datapath_name': integration_bridge,
                                            'switch': host_node,
                                            'domain': 'DOMAIN',
                                            'subject_name': 'fc_domain@abc.com',
                                            'status': 'Active',
                                        }
                              }
                        computenode = self.create_compute(self.context,computedata)
                        LOG.info(_("Compute Node Details :: Plugin %s\n"), str(computenode))
                        time.sleep(2)
			nwports = self.create_network_port(self.context,integration_bridge)
                
                
    def create_instance_notification(self, payload):
	LOG.debug(_("Instance Payload %s....\n"), str(payload))
        n = payload
        instance_id = n['instance_id']
        state = n['state']
        state_description = n['state_description']
        old_task_state = n['old_task_state']
        instance_id = n['instance_id']
        vm_type = 'VM_TYPE_NORMAL_APPLICATION'
	if 'metadata' in n:
	    if 'vmtype' in n['metadata']:
		vm_type = 'VM_TYPE_NETWORK_SERVICE'
        instancedata = {'instance':
                                {
                                    'tenant_id': n['tenant_id'],
                                    'display_name': n['display_name'],
                                    'instance_id': n['instance_id'],
                                    'user_id': n['user_id'],
                                    'state_description': n['state_description'],
                                    'state': n['state'],
                                    'created_at': datetime.datetime.now(),
                                    'launched_at': n['launched_at'],
                                    'reservation_id': n['reservation_id'],
                                    'host': n['host'],
                                    'type': vm_type,
                                }
                      }
        try:
            instance = self.get_instance(self.context,instance_id)
            if state == 'deleted':
                LOG.info(_("Instance Delete Details :: Plugin %s\n"), str(instancedata))
                instance_uuid = instance['instance_id']
                self.delete_instance(self.context,instance_id)
            else:
                instance = self.update_instance(self.context, instance_id, instancedata)
                LOG.info(_("Instance update Details :: Plugin %s\n"), str(instance))
        except crd_exc.InstanceNotFound:
            LOG.info(_("New instance Creating :: Plugin %s\n"), str(instancedata))
            if state_description == 'spawning' and old_task_state == 'block_device_mapping':
                instance = self.create_instance(self.context,instancedata)
            
