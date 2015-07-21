# Copyright 2013 Freescale Semiconductor, Inc.
# All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from nscs.crdservice.openstack.common import log as logging
from nscs.crdservice.openstack.common import context
from nscs.crdservice import context as crd_context
from nscs.crdservice.openstack.common import rpc
from nscs.crdservice.openstack.common.rpc import dispatcher
from nscs.crdservice.openstack.common.rpc import proxy
from oslo.config import cfg
from novaclient.v1_1 import client as nova_client
from nscs.crdservice.common import exceptions as crd_exc

import socket
import time
import datetime
import json

LOG = logging.getLogger(__name__)

crd_nova_opts = [
    cfg.StrOpt('admin_user', default="neutron"),
    cfg.StrOpt('admin_password', default="password"),
    cfg.StrOpt('admin_tenant_name', default="service"),
    cfg.StrOpt('auth_url'),
    cfg.StrOpt('endpoint_url'),
]
cfg.CONF.register_opts(crd_nova_opts, "CRDNOVACLIENT")

crd_ofcontroller = [
    cfg.StrOpt('enable', default="True"),
    cfg.StrOpt('cluster', default="DefaultCluster"),
    cfg.StrOpt('controller', default="DefaultController"),
    cfg.StrOpt('ovs_port', default="8090"),
    cfg.StrOpt('integration_bridge', default="br-int"),
]
cfg.CONF.register_opts(crd_ofcontroller, "OFCONTROLLER")


crd_interfaces = [
    cfg.StrOpt('host_ip', default="127.0.0.1"),
    cfg.StrOpt('data_ip', default="127.0.0.1"),

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
        #super(NovaListener, self).__init__(topic='crd-service-consume',
        #                                default_version=self.RPC_API_VERSION)
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
        #LOG.debug(_("Creating CONSUMER with topic %s....\n"),
        #  self.listen_topic)
	self.listen_conn.join_consumer_pool(self.process_event,
                                            self.listen_topic,
                                            'notifications.info', 'nova')
        self.listen_conn.join_consumer_pool(self.process_event,
                                            self.listen_topic, 'scheduler',
                                            'nova')
        self.listen_conn.join_consumer_pool(self.process_event,
                                            self.listen_topic, 'conductor',
                                            'nova')
        self.listen_conn.join_consumer_pool(self.process_event,
                                            self.listen_topic,
                                            'crd-service-consume', 'crd')
        self.listen_conn.consume_in_thread()

        self.consumer_conn = rpc.create_connection(new=True)
        self.consumer_conn.create_consumer(self.consumer_listener_topic,
                                           self.dispatcher, fanout=False)
        self.consumer_conn.consume_in_thread()

        # self.cast(self.listen_context,
        #           self.make_msg('check_compute_status',
        #                         payload={'Status': 'Active'}))

    @staticmethod
    def get_hostname():
        return "%s" % socket.gethostname()

    def create_rpc_dispatcher(self):
        """Get the rpc dispatcher for this manager.

        If a manager would like to set an rpc API version, or support more than
        one class as the target of rpc messages, override this method.
        """
        return dispatcher.RpcDispatcher([self])
    
    
    def process_event(self, message_data):
	foramted_txt = json.dumps(message_data, indent=4, separators=(',', ': '))
	#LOG.debug(_("Message Delta %s\n"), str(foramted_txt))
	event_type = message_data.get('event_type', None)
        method = message_data.get('method', None)
        if event_type is not None:
            payload = message_data.get('payload', {})
            if event_type == 'compute.instance.update':
                host_node = payload['host']
                if host_node:
                    nt = self.novaclient()
                    host_node_details = nt.hypervisors.search(host_node)
                    for node in host_node_details:
                        node = node.to_dict()
                        if node['hypervisor_hostname'] == host_node:
                            compute_id = node['id']
                    try:
                        compute = self.get_compute(self.context, compute_id)
                        if compute:
                            self.create_instance_notification(payload)
                    except:
                        LOG.debug(_("Compute Node :%s Not Found"),
                                  str(compute_id))

        if (method is not None) and (method == 'update_node_details'):
            payload = message_data.get('args', None)
            if payload is not None:
                #node_details = payload.get('service', None)
                node_details = payload['payload']
                if (node_details is not None) and (type(node_details) is dict):
                    self.create_compute_logicalswitch(node_details)

        if (method is not None) and (method == 'check_compute_status'):
            self.check_compute_status()
	    
	
	

    @staticmethod
    def novaclient():
        return nova_client.Client(cfg.CONF.CRDNOVACLIENT.admin_user,
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
                        self.update_compute(self.context, compute_id, body)
                    if state == 'up':
                        body = {'compute': {'status': 'Active'}}
                        self.update_compute(self.context, compute_id, body)
                        #time.sleep(5)
                        # self.cast(self.listen_context,
                        #           self.make_msg('check_compute_status',
                        #                        payload={'Status': 'Active'}))

    def create_compute_logicalswitch(self, payload):
        host_node = payload['host']
	#compute_id = payload['id']
	nt = self.novaclient()
	host_node_details = nt.hypervisors.search(host_node)
	for node in host_node_details:
	    node = node.to_dict()
	    if node['hypervisor_hostname'] == host_node:
		compute_id = node['id']
	host_node_details = nt.hypervisors.get(compute_id)
	compute_ipaddress = host_node_details.host_ip
	try:
	    compute_dataip = payload['data_ip']
	except Exception:
	    compute_dataip = host_node_details.host_ip
            
	
        try:
            self.get_compute(self.context, compute_id)
            return
        except crd_exc.ComputeNotFound:
            LOG.debug(_("Compute : %s Not Exist, Adding compute"), str(compute_id))
            pass
	controller_enable = cfg.CONF.OFCONTROLLER.enable
        cluster = cfg.CONF.OFCONTROLLER.cluster
        controller = cfg.CONF.OFCONTROLLER.controller
        ovs_port = cfg.CONF.OFCONTROLLER.ovs_port

        integration_bridge = cfg.CONF.OFCONTROLLER.integration_bridge

        cluster_filters = dict()
        cluster_filters['name'] = [cluster]
        clusters = self.get_ofclusters(self.context, filters=cluster_filters)
        if clusters:
            cluster_id = clusters[0]['id']

            controller_filters = dict()
            controller_filters['name'] = [controller]
            controllers = self.get_ofcluster_ofcontrollers(self.context,
                                                           cluster_id,
                                                           filters=controller_filters)
            if controllers:
                controller_id = controllers[0]['id']
                try:
                    compute = self.get_compute(self.context, compute_id)
                except crd_exc.ComputeNotFound:
                    logicalswitchdata = {
                        'logicalswitch': {
                            'name': integration_bridge,
                            'ip_address': compute_dataip,
                            'port': ovs_port,
                            }
                    }
                    logicalswitch = self.create_ofcluster_ofcontroller_logicalswitch(
                        self.context, logicalswitchdata, cluster_id,
                        controller_id)
                    LOG.info(_("Create Integration bridge :: Plugin %s\n"),
                             str(logicalswitch))
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
			###Sending Notification to neutron-server to add tunnel in NetworkNode
			neutron_topic = 'q-plugin'
			self.listen_conn.join_consumer_pool(None,neutron_topic,neutron_topic,'crd')
			self.cast(self.context, self.make_msg('tunnel_sync',tunnel_ip=compute_dataip,tunnel_type='vxlan',host=host_node),
				  version=self.RPC_API_VERSION,
				  topic=neutron_topic)
			
                        computenode = self.create_compute(self.context,
                                                          computedata)
                        LOG.info(_("Compute Node Details :: Plugin %s\n"),
                                 str(computenode))
	                time.sleep(2)
        	        self.create_network_port(self.context,
                                      integration_bridge)

	elif controller_enable == 'False':
	    datapath_id = None
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
	    try:
		compute = self.get_compute(self.context, compute_id)
	    except crd_exc.ComputeNotFound:
		computenode = self.create_compute(self.context,computedata)
		LOG.info(_("Compute Node Details :: Plugin %s\n"),str(computenode))
		
	else:
	    LOG.warning("Cluster and Controller nor exist...")

		

    def create_instance_notification(self, payload):
        LOG.debug(_("Instance Payload %s....\n"), str(payload))
        n = payload
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
            self.get_instance(self.context, instance_id)
            if state == 'deleted':
                LOG.info(_("Instance Delete Details :: Plugin %s\n"),
                         str(instancedata))
                self.delete_instance(self.context, instance_id)
            else:
                instance = self.update_instance(self.context, instance_id,
                                                instancedata)
                LOG.info(_("Instance update Details :: Plugin %s\n"),
                         str(instance))
        except crd_exc.InstanceNotFound:
            LOG.info(_("New instance Creating :: Plugin %s\n"),
                     str(instancedata))
            if (state_description == 'spawning') and \
                    (old_task_state == 'block_device_mapping'):
                self.create_instance(self.context, instancedata)
