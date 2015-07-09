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

from cns.crdserver.db import nova as nova_db
from cns.crdserver.extensions.nova import NovaBase
from nscs.crdserver.db import api as db_api
from cns.crdserver.listener.nova import NovaListener
from cns.crdserver.plugins import delta
from cns.crdserver.plugins.common.openssl import CertificateAuthority
from cns.crdserver.dispatcher.ofcontroller.nova import NovaDispatcher
from oslo.config import cfg

from sqlalchemy.orm import exc
import netifaces
import re
import random
import string

LOG = logging.getLogger(__name__)

crd_ofcontroller = [
    cfg.StrOpt('cluster', default="DefaultCluster"),
    cfg.StrOpt('controller', default="DefaultController"),
    cfg.StrOpt('ovs_port', default="8090"),
]

cfg.CONF.register_opts(crd_ofcontroller, "OFCONTROLLER")


class NovaPlugin(NovaListener,
                 NovaBase,
                 NovaDispatcher):
    """
    Implementation of the Crd Core Plugin.
    DB related work is implemented in class NovaPluginDb
    """
    supported_extension_aliases = ["nova"]
    
    def __init__(self):
        self.novadb = nova_db.NovaDb()
        self.cnsdelta = delta.CnsDelta()
        self.ca = CertificateAuthority()
        db_api.register_models()
        super(NovaPlugin, self).__init__()
    
    ################ Compute API Start ############################
    def create_compute(self, context, compute):
        v = self.novadb.create_compute(context, compute)
        data = v
        v.update({'operation' : 'create'})
        delta={}
        delta.update({'compute_delta':v})
        datapathdelta = self.cnsdelta.create_compute_delta(context,delta)
        fanoutmsg = {}
        fanoutmsg.update({'method':'create_datapath','payload':datapathdelta})
        delta={}
        version = datapathdelta['version_id']
        delta[version] = fanoutmsg
        self.send_fanout(context,'call_consumer',delta)
        return data

    def update_compute(self, context, compute_id, compute):
        v = self.novadb.update_compute(context, compute_id, compute)
        
        return v

    def delete_compute(self, context, compute_id):
        v = self.get_compute(context, compute_id)
        self.novadb.delete_compute(context, compute_id)

    def get_compute(self, context, compute_id, fields=None):
        #LOG.debug(_('Get compute %s'), compute_id)
        return self.novadb.get_compute(context, compute_id, fields)
        
    def get_computes(self, context, filters=None, fields=None):
        #LOG.debug(_('Get computes'))
        compute_nodes = self.novadb.get_computes(context, filters, fields)
        return compute_nodes
    ################ Compute API End ############################
        
    ################ Instance API Start ############################
    def create_instance(self, context, instance):
        v = self.novadb.create_instance(context, instance)
        data = v
               
        
        v.update({'operation' : 'create'})
        delta={}
        delta.update({'instance_delta':v})
        instancedelta = self.cnsdelta.create_instance_delta(context,delta)
        fanoutmsg = {}
        fanoutmsg.update({'method':'create_instance','payload':instancedelta})
        delta={}
        version = instancedelta['version_id']
        delta[version] = fanoutmsg
        self.send_fanout(context,'call_consumer',delta)
        
        return data

    def update_instance(self, context, instance_id, instance):
        v = self.novadb.update_instance(context, instance_id, instance)
        data = v
        v.update({'operation' : 'update'})
        delta={}
        delta.update({'instance_delta':v})
        instancedelta = self.cnsdelta.create_instance_delta(context,delta)
        fanoutmsg = {}
        fanoutmsg.update({'method':'update_instance','payload':instancedelta})
        delta={}
        version = instancedelta['version_id']
        delta[version] = fanoutmsg
        self.send_fanout(context,'call_consumer',delta)
        return data

    def delete_instance(self, context, instance_id):
        v = self.get_instance(context, instance_id)
        self.novadb.delete_instance(context, instance_id)
        v.update({'operation' : 'delete'})
        delta={}
        delta.update({'instance_delta':v})
        instancedelta = self.cnsdelta.create_instance_delta(context,delta)
        fanoutmsg = {}
        fanoutmsg.update({'method':'delete_instance','payload':instancedelta})
        delta={}
        version = instancedelta['version_id']
        delta[version] = fanoutmsg
        self.send_fanout(context,'call_consumer',delta)

    def get_instance(self, context, instance_id, fields=None):
        #LOG.debug(_('Get instance %s'), instance_id)
        return self.novadb.get_instance(context, instance_id, fields)

    def get_instances(self, context, filters=None, fields=None):
        #LOG.debug(_('Get instances'))
        return self.novadb.get_instances(context, filters, fields)
        
    ################ Instance API End ############################
    
    
    
    def cns_init_consumer(self, context, **kwargs):
        """
        This function is called when ever any consumer is started
        """
        LOG.debug(_("In Init Consumer for CNS.......KWArgs = %s"),str(kwargs))
        payload = kwargs['consumer']
        payload = payload['payload']
        return self.create_ofcontroller(payload)

    def update_consumer(self, context, **kwargs):
        """
        This function is called when any consumer sends keep-alive message.
        """
        LOG.debug(_("In Update Consumer.......KWArgs = %s"),str(kwargs))
        pass

    def create_ofcontroller(self, payload):
        LOG.debug(_("create_ofcontroller = %s"),str(payload))
        body = {
            'ofcontroller':
                {
                        #'name': payload['hostname'],
                        ###### Expecting only 1 controller for now
                        'name': 'DefaultController',
                        'ip_address': payload['ip_address'],
                        'port': payload['ofc_port'],
                        'cell': payload['cell']
                    }
            }
        cluster_id = payload['cluster_id']
        get_cluster = None
        try:
            get_cluster = self.get_ofcluster(self.context,cluster_id)
        except exc.NoResultFound:
            LOG.error(_("No Cluster exist with = %s"),str(cluster_id))
            
        if get_cluster:
            cluster_id = cluster_id
        else:
            cluster = cfg.CONF.OFCONTROLLER.cluster
            filters = {}
            filters['name']= [cluster]
            clusters = self.get_ofclusters(self.context, filters=filters)
            cluster_id = clusters[0]['id']
            controller = self.create_ofcluster_ofcontroller(self.context, body, cluster_id)
        return self.cnsdelta.cns_init(self.context, payload['version'],payload['hostname'])
    #########################################################################
    ##                                                                     ##
    ##             Openflow Cluster Management (Start)                     ##
    ##                                                                     ## 
    #########################################################################

    def _get_file_contents(self,file_path):
        """ Helper function to get the contents of files. """
        with open(file_path,"r") as line:
            content = line.read()
        #LOG.debug(_("Reading File (%s)"), file_path)    
        return content
            
    def create_ofcluster(self,context,ofcluster):
        #LOG.debug(_("In create_ofcluster.....%s"),str(ofcluster))
        # Get the contents of CA Certficaite
        ca_cert_pem = self._get_file_contents(str(ofcluster['ofcluster'].get('ca_cert_path')))
        # Get the contents of Cluster Private Key
        private_key_pem = self._get_file_contents(str(ofcluster['ofcluster'].get('private_key_path')))
        ofcluster['ofcluster']['ca_cert_path'] = ca_cert_pem
        ofcluster['ofcluster']['private_key_path'] = private_key_pem
        cluster_dict = self.novadb.create_ofcluster(context,
                                       ofcluster['ofcluster'])
        #LOG.debug(_("Openflow Cluster CREATE Success. :: %s"),str(cluster_dict))
        return cluster_dict

    def get_ofclusters(self, context, filters=None, fields=None,
                       sorts=None, limit=None, marker=None, page_reverse=False):
        session = context.session
        with session.begin(subtransactions=True):
            list_dict = self.novadb.get_ofclusters(context, filters, None)
        return list_dict

    def update_ofcluster(self, context, id, **params):
        #LOG.debug(_("Update to ofcluster {%s} => %s"), str(id), str(params))
        session = context.session
        with session.begin(subtransactions=True):
            cluster_dict = self.novadb.update_ofcluster(context, id, **params)
        return cluster_dict

    def delete_ofcluster(self, context, id):
        #LOG.debug(_("Delete openflow cluster {%s}"), str(id))
        session = context.session
        with session.begin(subtransactions=True):
            cluster_dict = self.novadb.delete_ofcluster(context, id)
        return cluster_dict    

    def get_ofcluster(self, context, id, fields=None):
        session = context.session
        with session.begin(subtransactions=True):
            ofcluster = self.novadb.get_ofcluster(context, id, None)
        return ofcluster
    #########################################################################
    ##             Openflow Cluster Management (End)                       ##
    #########################################################################
    #########################################################################
    ##                                                                     ##
    ##             Openflow Controller Management (Start)                  ##
    ##                                                                     ## 
    #########################################################################

    def create_ofcluster_ofcontroller(self, context, ofcontroller, ofcluster_id):
        #LOG.debug(_("In create OF Controller {cluster ID = %s}.....%s"), ofcluster_id,str(ofcontroller))
        controller_dict = self.novadb.create_ofcluster_ofcontroller(context,
                                                                   ofcontroller['ofcontroller'], ofcluster_id)
        #LOG.debug(_("Openflow Controller CREATE Success...{Cluster ID = %s} :: %s"), ofcluster_id, str(controller_dict))
        return controller_dict

    def get_ofcluster_ofcontrollers(self, context, ofcluster_id,
                                    filters=None, fields=None,
                                    sorts=None, limit=None,
                                    marker=None, page_reverse=False):
        #LOG.debug(_("Get OF Controller {cluster ID = %s}"),ofcluster_id)
        # remove the Controller name/id based collections.
        # we need Cluster ID based Controller Collection
        #filters.pop('id',None)
        session = context.session
        with session.begin(subtransactions=True):
            list_dict = self.novadb.get_ofcluster_ofcontrollers(context, ofcluster_id,
                                                               filters, None)
        return list_dict

    def update_ofcluster_ofcontroller(self, context, id, ofcluster_id, **params):
        #(TODO) Need to update all switches with changes to Controller IPaddress and Port details
        #LOG.debug(_("Update to ofcontroller {%s} {cluster ID = %s} => %s"),str(id),ofcluster_id, str(params))
        session = context.session
        with session.begin(subtransactions=True):
            controller_dict = self.novadb.\
                                update_ofcluster_ofcontroller(context, id,
                                                              ofcluster_id,
                                                              **params)
        return controller_dict

    def delete_ofcluster_ofcontroller(self,context,id,ofcluster_id):
        #LOG.debug(_("Delete openflow controller {%s} {cluster id = %s}"), str(id), ofcluster_id)
        session = context.session
        with session.begin(subtransactions=True):
            controller_dict = self.novadb.\
                                    delete_ofcluster_ofcontroller(context,id,
                                                                  ofcluster_id)
        return controller_dict    

    def get_ofcluster_ofcontroller(self, context, id, ofcluster_id,
                                    filters=None, fields=None):
        filters = {}
	filters['cluster_id'] = ofcluster_id
	filters['id'] = [id]
        session = context.session
        with session.begin(subtransactions=True):
            ofcontroller = self.novadb.\
                                 get_ofcluster_ofcontroller(context, id,
                                                            ofcluster_id,
							    filters=filters)
        return ofcontroller
    
    #########################################################################
    ##             Openflow Controller Management (End)                    ##
    #########################################################################

    #########################################################################
    ##                                                                     ##
    ##             Openflow Logical Switch Management (Start)              ##
    ##                                                                     ## 
    #########################################################################
    
    def _get_cluster_cacert(self,context,cluster_id):
        """ Get Cluster CA Certificate and Private Key """
        cluster_ca = self.novadb.get_ofcluster(context,cluster_id)
        return cluster_ca['ca_cert_pem'], cluster_ca['private_key_pem']
    
    def certify_logicalswitch(self, context, switch_dict, cluster_id):
        """  Generate keypair and certify the Logical Switch  """
        
        # Datapath ID of the logical Switch
        datapath_id = switch_dict['logicalswitch'].get("datapath_id")
        
        # Get the Cluster CA Cert and Private Key
        ca_cert_pem, private_key_pem = self._get_cluster_cacert(context, cluster_id)
        
        # write the files to temporary location
        cacert_path,ca_pvt_path = self.ca.create_ca_directory(cluster_id,
                                                              ca_cert_pem,private_key_pem)
        
        # generate keypair and csr for the DPID of switch
        switch_key, switch_csr = self.ca.generate_keypair_csr(cluster_id,datapath_id )
        #LOG.debug(_("Switch Private_key => %s"), self._get_file_contents(switch_key))
        #LOG.debug(_("Switch CSR => %s"), self._get_file_contents(switch_csr))
        # Certify CSR with Cluster CA
        switch_cert = self.ca.certify_csr(cluster_id,datapath_id,cacert_path,ca_pvt_path)

        # update the Switch dict with Cert, key data.
        switch_dict['logicalswitch']['private_key_pem'] = self._get_file_contents(switch_key)
        switch_dict['logicalswitch']['certificate_pem'] = self._get_file_contents(switch_cert)
        
        # prepare the file paths dict for use with ovs-vsctl
        cert_dict = {'cacert_path': cacert_path,
                     'switch_key' : switch_key,
                     'switch_cert': switch_cert}

        return switch_dict, cert_dict
    
    def _configure_switch_controller(self,controller):
        """ Configure OVS Logical Switch 
        (note) Assumed that,switch_dict contains data regarding
        ipaddr or hostname of the compute node and port where it is running
        
        cmd: ovs-vsctl --db=tcp:10.232.91.84:8090 set-controller br-int ssl:10.10.10.200:8520
        """
        connection = "ovs-vsctl --db=tcp:"+controller['switch_addr']+":"+controller['switch_port']
	
	# Set openflow switch to operating secure mode
	#set-fail-mode br-int secure
        config_controller_secure = connection + " set-fail-mode "+ controller['switch_name'] +" secure"
	
        #LOG.debug(_("Set openflow switch to operating secure mode ... [%s]"), config_controller_secure)
        output = self.ca.execute_command(config_controller_secure)
	
        # configure controller ip and port
        config_controller = connection + " set-controller "+ controller['switch_name'] +"  tcp:"+ \
                            controller['ip_address']+":"+controller['port']
        #LOG.debug(_("Adding Controller Configuration to logical swith... [%s]"), config_controller)
        #(note) commented for init testing
        output = self.ca.execute_command(config_controller)
        #LOG.debug(_("cmd[%s] => %s"),config_controller, output)
        config_controller = connection + " set bridge " + controller['switch_name'] + \
                            " protocols=OpenFlow10,OpenFlow12,OpenFlow13"
        #LOG.debug(_("Adding Controller Configuration to logical swith... [%s]"), config_controller)
        output = self.ca.execute_command(config_controller)
        #LOG.debug(_("cmd[%s] => %s"),config_controller, output)
        
    def _configure_switch_certificates(self,controller,cert_dict):
        """ Configure OVS Logical Switch with certificates
        (note) Assumed that,controller contains data regarding
        ipaddr or hostname of the compute node and port where it is running
        and cert_dict contains the path to the pki files
        
        cmd: ovs-vsctl --db=tcp:10.10.10.200:8056set-ssl \
                       --private-key=switch.key \
                       --certificate=switch.crt  \
                       --ca-cert=ca_cert.pem
        """
        connection = "ovs-vsctl --db=tcp:"+controller['switch_addr']+":"+controller['switch_port']
        # configure controller ip and port
        config_controller = connection + " set-ssl " + "  --private-key=" + cert_dict['switch_key'] + \
                            "  --certificate=" + cert_dict['switch_cert'] + \
                            "  --ca-cert=" + cert_dict['cacert_path']
        #LOG.debug(_("Adding Certificates to logical swith... [%s]"), config_controller)
        #(note) commented for init testing
        output = self.ca.execute_command(config_controller)
        #LOG.debug(_("cmd[%s] => %s"),config_controller, output)

    def _create_inter_bridge(self, switch_data):
        """ Create Integration bridge in the new Compute Node
        note: need to check the existance of Integration bridge.
        Example:
        Create bridge : ovs-vsctl add-br <br-name>
        Get DPID : ovs-vsctl get bridge <br-name> datapath_id
        """
        ipaddress = switch_data['logicalswitch']['ip_address']
        port = switch_data['logicalswitch']['port']
        br_name = switch_data['logicalswitch']['name']
        # check the existence of integration bridge
        #LOG.debug(_("Checking for Integration Bridge %s in compute Node %s"), br_name, ipaddress)
        vsctl_cmd = "ovs-vsctl --db=tcp:%s:%s list-br" % \
                    (ipaddress, port)
        br_list = ''
        try:
            br_list = self.ca.execute_command(vsctl_cmd)
        except Exception:
            LOG.error(_("Command Execution Failed => %s"), vsctl_cmd)

        LOG.debug(_("Existing Integration bridges => %s"), br_list)
        match_br = re.search(br_name, br_list)

        if match_br is None:
            vsctl_cmd = "ovs-vsctl --db=tcp:%s:%s add-br %s" % \
                        (ipaddress, port, br_name)
            self.ca.execute_command(vsctl_cmd)
        else:
            #LOG.debug(_("Found %s. Fetching Datapath ID..."), br_name)
            pass

        ### Fetch and return the datapath ID of the Inter-br  ####
        fetch_dpid = "ovs-vsctl --db=tcp:%s:%s get bridge %s datapath_id" % \
                     (ipaddress, port, br_name)
        datapath_id = self.ca.execute_command(fetch_dpid)
        if datapath_id:
            return datapath_id.rstrip("\n\r")

    def create_ofcluster_ofcontroller_logicalswitch(self, context, logicalswitch,
                                                    ofcluster_id, ofcontroller_id):
        # Create the integration brdige if not exists
        br_name = logicalswitch['logicalswitch']['name']
        datapath_id = self._create_inter_bridge(logicalswitch)
        
        logicalswitch['logicalswitch']['datapath_id'] = str(datapath_id).strip('"')

        #LOG.debug(_("In create OF Logical Switch {cluster ID = %s, Controller ID = %s}.....%s")
        # , ofcluster_id, ofcontroller_id,str(logicalswitch))
        switch_data, cert_dict = self.certify_logicalswitch(context, logicalswitch, ofcluster_id)
        switch_rec = self.novadb.create_ofcluster_ofcontroller_logicalswitch(context,
                                                                            switch_data['logicalswitch'],
                                                                            ofcluster_id, ofcontroller_id)
        if switch_rec:
            LOG.debug(_("Openflow Controller CREATE Success...{Cluster ID = %s, Controller Id = %s} :: %s"),
                      ofcluster_id, ofcontroller_id, str(switch_rec))
            #### get the controller data based on the cluster ID, to which this
            #### logical switch is assigned
            controller_dict = self.get_ofcluster_ofcontroller(context, ofcontroller_id, ofcluster_id)
            LOG.debug(_("Controller Data => %s"), str(controller_dict))
            #### add the switch ip and port details to the controller dictionary.
            controller_dict['switch_addr'] = switch_rec['ip_address']
            controller_dict['switch_port'] = switch_rec['port']
            controller_dict['switch_name'] = switch_rec['name']

            #### Configure the Logical switch with Openflow Controller IP addr and port
            self._configure_switch_controller(controller_dict)
            #### Configure Certificate and keys to the Logical switch
            self._configure_switch_certificates(controller_dict, cert_dict)
            #LOG.debug(_("Logical switch configuration completed."))
            
        return switch_rec

    def get_ofcluster_ofcontroller_logicalswitchs(self, context, ofcluster_id, ofcontroller_id,
                                                  filters=None, fields=None,
                                                  sorts=None, limit=None,
                                                  marker=None, page_reverse=False):
        #LOG.debug(_("Get OF Controller {cluster ID = %s}"),ofcluster_id)
        session = context.session
        with session.begin(subtransactions=True):
            list_dict = self.novadb.get_ofcluster_ofcontroller_logicalswitchs(context, ofcluster_id,
                                                                             ofcontroller_id, filters, None)
        return list_dict

    def update_ofcluster_ofcontroller_logicalswitch(self, context, id, ofcluster_id,
                                                    ofcontroller_id, **params):
        #LOG.debug(_("Update to Logical Switch {%s}" \ "{ofcontroller = %s, cluster ID = %s} => %s"),
        # str(id),ofcontroller_id,ofcluster_id, str(params))
        session = context.session
        with session.begin(subtransactions=True):
            switch_dict = self.novadb. \
                update_ofcluster_ofcontroller_logicalswitch(context, id,
                                                            ofcluster_id,
                                                            ofcontroller_id,
                                                            **params)
        return switch_dict

    def delete_ofcluster_ofcontroller_logicalswitch(self, context, id,
                                                    ofcluster_id, ofcontroller_id):
        #LOG.debug(_("Delete openflow Logical switch {%s} {cluster id = %s, Controller = %s}"),
        # str(id), ofcluster_id, ofcontroller_id)
        # Get the Switch IP and Port, name
        switch_data = self.get_ofcluster_ofcontroller_logicalswitch(context, id,
                                                                    ofcluster_id, ofcontroller_id)
        #LOG.debug(_("Deleting Integration bridge" \"(%s) in Compute Node %s"),str(switch_data['name']),
        # str(switch_data['ip_address']))
        vsctl_cmd = "ovs-vsctl --db=tcp:%s:%s del-br %s" % \
                    (str(switch_data['ip_address']), str(switch_data['port']), str(switch_data['name']))
        #LOG.debug(_("Executing command [%s]"), vsctl_cmd)
        self.ca.execute_command(vsctl_cmd)
        session = context.session
        with session.begin(subtransactions=True):
            switch_dict = self.novadb. \
                delete_ofcluster_ofcontroller_logicalswitch(context, id,
                                                            ofcluster_id,
                                                            ofcontroller_id)
        return switch_data

    def get_ofcluster_ofcontroller_logicalswitch(self, context, id,
                                                 ofcluster_id, ofcontroller_id,
                                                 filters=None, fields=None):
        filters = {}
        filters['cluster_id'] = ofcluster_id
        filters['controller_id'] = ofcontroller_id
        filters['id'] = [id]
        session = context.session
        with session.begin(subtransactions=True):
            ofswitch = self.novadb. \
                get_ofcluster_ofcontroller_logicalswitch(context, id,
                                                         ofcluster_id,
                                                         ofcontroller_id,
                                                         filters=filters)
        return ofswitch

    #########################################################################
    ##             Openflow Logical switch Management (End)                ##
    #########################################################################
    ################ Nwport API Start ############################
    def create_network_port(self, context,integration_bridge):
        """
        Update the OVS DB with the DATA IP of the compute nodes
        Sample commands:
        
        For VXLAN , flow-type is 'ip'
        ovs_vsctl  --db=tcp:10.232.91.84:8090 --may-exist  \
                        add-port br-int  vxlan-10.10.10.20 -- set \
                        Interface vxlan-10.10.10.20  type=vxlan  \
                        options:remote_ip=10.10.10.20
        For VXLAN, flow-type is 'flow'
        ovs-vsctl --db=tcp:10.232.91.84:8090 --may-exist \
                       add-port br-int vxlan-flow-port -- set \
                       Interface vxlan-flow-port   type=vxlan \
                       options:remote_ip=flow options:key=flow
        """
        utils = CertificateAuthority()
        
        # get the list of compute nodes
        LOG.debug(_("Create Network port..."))
        compute_nodes = self.get_computes(context)
        LOG.debug(_("compute nodes found => %s"), compute_nodes)
        
        #get the config params from crd.conf
        br_int = integration_bridge
        network_type = cfg.CONF.OVS.network_type
        flow_type = ''
        vxlan_udp_port = cfg.CONF.OVS.vxlan_udp_port
        
        #local_data_ip_interface = cfg.CONF.INTERFACES.data
        #local_data_ip = netifaces.ifaddresses(local_data_ip_interface)[2][0]['addr']
        local_data_ip = cfg.CONF.NETWORKNODE.data_ip
        
        if compute_nodes:
            for node in compute_nodes:
                lst = [random.choice(string.ascii_letters + string.digits) for n in xrange(15)]
                nwname = "".join(lst)
                            
                # Processing for VXLAN network type
                if network_type == 'vxlan':
                    lnwportdata = {'nwport':
                                {
                                    'name': nwname,
                                    'network_type': network_type,
                                    'ip_address': node['ip_address'],
                                    'data_ip': local_data_ip,
                                    'bridge': br_int,
                                    'vxlan_vni': 0,
                                    'vxlan_udpport': vxlan_udp_port,
                                    'vlan_id': '',
                                    'flow_type': flow_type,
                                    'ovs_port': node['ovs_port'],
                                    'local_data_ip': node['data_ip'],
                                    'host': node['hostname'],
                                }
                            }
                    computenode = self.create_nwport(context, lnwportdata)
                    
                    lst = [random.choice(string.ascii_letters + string.digits) for n in xrange(15)]
                    nwname = "".join(lst)
                    uniportdata = {'nwport':
                                {
                                    'name': nwname,
                                    'network_type': network_type,
                                    'ip_address': node['ip_address'],
                                    'data_ip': '0',
                                    'bridge': br_int,
                                    'vxlan_vni': 0,
                                    'vxlan_udpport': vxlan_udp_port,
                                    'vlan_id': '',
                                    'flow_type': flow_type,
                                    'ovs_port': node['ovs_port'],
                                    'local_data_ip': node['data_ip'],
                                    'host': node['hostname'],
                                }
                            }
                    computenode = self.create_nwport(context, uniportdata)
                    
                    for data in compute_nodes:
                        lst = [random.choice(string.ascii_letters + string.digits) for n in xrange(15)]
                        nwname = "".join(lst)
                        nwportdata = {'nwport':
                                {
                                    'name': nwname,
                                    'network_type': network_type,
                                    'ip_address': node['ip_address'],
                                    'data_ip': data['data_ip'],
                                    'bridge': br_int,
                                    'vxlan_vni': 0,
                                    'vxlan_udpport': vxlan_udp_port,
                                    'vlan_id': '',
                                    'flow_type': flow_type,
                                    'ovs_port': node['ovs_port'],
                                    'local_data_ip': node['data_ip'],
                                    'host': node['hostname'],
                                }
                            }
                        
                        if data['data_ip'] != node['data_ip']:
                            computenode = self.create_nwport(context,nwportdata)

    def create_nwport(self, context, nwport):
        utils = CertificateAuthority()
        
        network_type = nwport['nwport']['network_type']
        name = nwport['nwport']['name']
        integration_bridge = nwport['nwport']['bridge']
        ovs_port = nwport['nwport']['ovs_port']
        ip_address = nwport['nwport']['ip_address']
        data_ip = nwport['nwport']['data_ip']
        vxlan_udp_port = nwport['nwport']['vxlan_udpport']

        filters={}
        filters['ip_address'] = [ip_address]
        filters['data_ip'] = [data_ip]
        nwports = self.get_nwports(context,filters=filters)
        co_nwports = len(nwports)
        #LOG.debug(_("Count of flows [%s]"), co_nwports)
        if co_nwports == 0:
            if data_ip != '0':
                vsctl_cmd = "ovs-vsctl --db=tcp:"+ip_address+":"+ovs_port+" --may-exist add-port "+integration_bridge+" "+name+" -- set Interface "+name+" type="+network_type+" options:key=flow options:remote_ip="+data_ip+" options:dst_port="+vxlan_udp_port
                #LOG.debug(_("Executing command [%s]"), vsctl_cmd)
                utils.execute_command(vsctl_cmd)
            elif data_ip == '0':
                vsctl_cmd = "ovs-vsctl --db=tcp:"+ip_address+":"+ovs_port+" --may-exist add-port "+integration_bridge+" "+name+" -- set Interface "+name+" type="+network_type+" options:remote_ip=flow options:key=flow options:dst_port="+vxlan_udp_port
                #LOG.debug(_("Executing command [%s]"), vsctl_cmd)
                utils.execute_command(vsctl_cmd)
            v = self.novadb.create_nwport(context, nwport)
            data = v
            
            v.update({'operation' : 'create'})
            delta={}
            delta.update({'nwport_delta':v})
            portdelta = self.cnsdelta.create_nwport_delta(context,delta)
            fanoutmsg = {}
            fanoutmsg.update({'method':'create_nwport','payload':portdelta})
            delta={}
            version = portdelta['version_id']
            delta[version] = fanoutmsg
            self.send_fanout(context,'call_consumer',delta)
            
            return data

    def update_nwport(self, context, nwport_id, nwport):
        v = self.novadb.update_nwport(context, nwport_id, nwport)
        return v

    def delete_nwport(self, context, nwport_id):
        self.novadb.delete_nwport(context, nwport_id)

    def get_nwport(self, context, nwport_id, fields=None):
        #LOG.debug(_('Get nwport %s'), nwport_id)
        return self.novadb.get_nwport(context, nwport_id, fields)

    def get_nwports(self, context, filters=None, fields=None):
        #LOG.debug(_('Get nwports'))
        return self.novadb.get_nwports(context, filters, fields)
        
    ################ Nwport API End ############################
