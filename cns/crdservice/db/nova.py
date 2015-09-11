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
    

class cns_compute(model_base.BASEV2, HasId):
    compute_id = sa.Column(sa.Integer, nullable=False)
    hostname = sa.Column(sa.String(255), nullable=False)
    ip_address = sa.Column(sa.String(64))
    data_ip = sa.Column(sa.String(64))
    created_at = sa.Column(sa.DateTime)
    ovs_port = sa.Column(sa.String(64))
    datapath_id = sa.Column(sa.String(255))
    datapath_name = sa.Column(sa.String(255))
    switch = sa.Column(sa.String(255))
    domain = sa.Column(sa.String(255))
    subject_name = sa.Column(sa.String(255))
    status = sa.Column(sa.String(16))
    
    
class cns_instance(model_base.BASEV2, HasId, HasTenant):
    display_name = sa.Column(sa.String(255))
    instance_id = sa.Column(sa.String(36), nullable=False)
    user_id = sa.Column(sa.String(36))
    state_description = sa.Column(sa.String(255))
    state = sa.Column(sa.String(255))
    created_at = sa.Column(sa.DateTime)
    launched_at = sa.Column(sa.String(50))
    host = sa.Column(sa.String(50))
    type = sa.Column(sa.String(50))
    reservation_id = sa.Column(sa.String(50))
    zone = sa.Column(sa.String(255),
                     nullable=True)
    
class OpenflowCluster(model_base.BASEV2):
    """Represents Openflow Cluster in Db mode """
    __tablename__ = 'cns_openflow_cluster'

    id = sa.Column(sa.String(255), nullable=False, primary_key=True)
    name = sa.Column(sa.String(255))
    ca_cert_pem = sa.Column(sa.String(2048))
    private_key_pem = sa.Column(sa.String(2048))
    root_cert_pem = sa.Column(sa.String(2048))
    inter_cert_pem = sa.Column(sa.String(2048))
    created_at = sa.Column(sa.String(255))
    deleted_at = sa.Column(sa.String(255))
    updated_at = sa.Column(sa.String(255))
    

class OpenflowController(model_base.BASEV2):
    """Represents Openflow Controller in Db mode """
    __tablename__ = 'cns_openflow_controller'

    id = sa.Column(sa.String(255), nullable=False, primary_key=True)
    name = sa.Column(sa.String(255))
    ip_address = sa.Column(sa.String(64), unique=True)
    port = sa.Column(sa.String(4))
    cell = sa.Column(sa.String(255))
    cluster_id = sa.Column(sa.String(36), sa.ForeignKey("cns_openflow_cluster.id"),nullable=False)
    status = sa.Column(sa.String(16))
    created_at = sa.Column(sa.String(255))
    deleted_at = sa.Column(sa.String(255))
    updated_at = sa.Column(sa.String(255))


class OpenflowSwitch(model_base.BASEV2):
    """Represents Openflow Cluster in Db mode """
    __tablename__ = 'cns_openflow_logicalswitch'

    id = sa.Column(sa.String(255), nullable=False, primary_key=True)
    datapath_id = sa.Column(sa.String(32))
    name = sa.Column(sa.String(32))
    certificate_pem = sa.Column(sa.String(2048))
    private_key_pem = sa.Column(sa.String(2048))
    ip_address = sa.Column(sa.String(64))
    port = sa.Column(sa.String(4))
    created_at = sa.Column(sa.String(255))
    deleted_at = sa.Column(sa.String(255))
    updated_at = sa.Column(sa.String(255))
    cluster_id = sa.Column(sa.String(255))    
    controller_id = sa.Column(sa.String(255))
    

class cns_nwport(model_base.BASEV2, HasId):
    name = sa.Column(sa.String(255), nullable=False)
    network_type = sa.Column(sa.String(64))
    ip_address = sa.Column(sa.String(64))
    data_ip = sa.Column(sa.String(64))
    bridge = sa.Column(sa.String(64))
    vxlan_vni = sa.Column(sa.String(3))
    vxlan_udpport = sa.Column(sa.String(5))
    vlan_id = sa.Column(sa.String(5))
    flow_type = sa.Column(sa.String(64))
    ovs_port = sa.Column(sa.String(5))
    local_data_ip = sa.Column(sa.String(64))
    host = sa.Column(sa.String(64))
    
    
class NovaDb(db_base_plugin_v2.CrdDbPluginV2):
    
    #################### Compute Start######################################
    def _make_compute_dict(self, compute, fields=None):
        res = {'id': compute['id'],
               'compute_id': compute['compute_id'],
               'hostname': compute['hostname'],
               'ip_address': compute['ip_address'],
               'data_ip': compute['data_ip'],
               'created_at': compute['created_at'],
               'ovs_port': compute['ovs_port'],
               'datapath_id': compute['datapath_id'],
               'datapath_name': compute['datapath_name'],
               'switch': compute['switch'],
               'domain': compute['domain'],
               'subject_name': compute['subject_name'],
               'status': compute['status']}
        return self._fields(res, fields)
        
    def create_compute(self, context, compute):
        n = compute['compute']
        with context.session.begin(subtransactions=True):
            compute = cns_compute(id=n['compute_id'],
                                        compute_id = n['compute_id'],
                                        hostname = n['hostname'],
                                        ip_address = n['ip_address'],
                                        data_ip = n['data_ip'],
                                        created_at = datetime.datetime.now(),
                                        ovs_port = n['ovs_port'],
                                        datapath_id = n['datapath_id'],
                                        datapath_name = n['datapath_name'],
                                        switch = n['switch'],
                                        domain = n['domain'],
                                        subject_name = n['subject_name'],
                                        status = n['status']
                                        )
            context.session.add(compute)
        return self._make_compute_dict(compute)
        
    def get_compute(self, context, id, fields=None):
        compute = self._get_compute(context, id)
        return self._make_compute_dict(compute, fields)
        
    
    def get_computes(self, context, filters=None, fields=None):
        return self._get_collection(context, cns_compute,
                                    self._make_compute_dict,
                                    filters=filters, fields=fields)
        
    def _get_compute(self, context, id):
        try:
            query = context.session.query(cns_compute)
            compute = query.filter(cns_compute.compute_id == id).one()
        except exc.NoResultFound:
            raise q_exc.ComputeNotFound(compute_id=id)
            #return False
        except exc.MultipleResultsFound:
            LOG.error('Multiple Compute match for %s' % id)
            raise q_exc.ComputeNotFound(compute_id=id)
        return compute
    
    def update_compute(self, context, id, compute):
        n = compute['compute']
        with context.session.begin(subtransactions=True):
            compute = self._get_compute(context, id)
            compute.update(n)
        return self._make_compute_dict(compute)
        
    def delete_compute(self, context, id):
        compute = self._get_compute(context, id)
        with context.session.begin(subtransactions=True):
            context.session.delete(compute)
            
    ################## compute End #######################################
    
    
    
    #################### Instance Start######################################
    def _make_instance_dict(self, instance, fields=None):
        res = {'id': instance['id'],
               'tenant_id': instance['tenant_id'],
               'display_name': instance['display_name'],
               'instance_id': instance['instance_id'],
               'user_id': instance['user_id'],
               'state_description': instance['state_description'],
               'state': instance['state'],
               'created_at': instance['created_at'],
               'launched_at': instance['launched_at'],
               'host': instance['host'],
               'type': instance['type'],
               'reservation_id': instance['reservation_id'],
               'zone': instance['zone']}
        return self._fields(res, fields)
        
    def create_instance(self, context, instance):
        n = instance['instance']
        with context.session.begin(subtransactions=True):
            instance = cns_instance(id=n['instance_id'],
                                        tenant_id = n['tenant_id'],
                                        display_name = n['display_name'],
                                        instance_id = n['instance_id'],
                                        user_id = n['user_id'],
                                        state_description = n['state_description'],
                                        state = n['state'],
                                        created_at = n['created_at'],
                                        launched_at = n['launched_at'],
                                        host = n['host'],
                                        type = n['type'],
                                        reservation_id = n['reservation_id'],
                                        zone = n['zone'],
                                        )
            context.session.add(instance)
        return self._make_instance_dict(instance)
        
    def get_instance(self, context, id, fields=None):
        instance = self._get_instance(context, id)
        return self._make_instance_dict(instance, fields)
        
    
    def get_instances(self, context, filters=None, fields=None):
        return self._get_collection(context, cns_instance,
                                    self._make_instance_dict,
                                    filters=filters, fields=fields)
        
    def _get_instance(self, context, id):
        try:
            query = context.session.query(cns_instance)
            instance = query.filter(cns_instance.instance_id == id).one()
        except exc.NoResultFound:
            raise q_exc.InstanceNotFound(instance_id=id)
            #return False
        except exc.MultipleResultsFound:
            LOG.error('Multiple Instance match for %s' % id)
            raise q_exc.InstanceNotFound(instance_id=id)
        return instance
    
    def update_instance(self, context, id, instance):
        n = instance['instance']
        with context.session.begin(subtransactions=True):
            instance = self._get_instance(context, id)
            instance.update(n)
        return self._make_instance_dict(instance)
        
    def delete_instance(self, context, id):
        instance = self._get_instance(context, id)
        with context.session.begin(subtransactions=True):
            context.session.delete(instance)
            
    ################## instance End #######################################            
        
    
    def _check_ofcluster(self, context, params):
        """ check for duplicate record """
        model = OpenflowCluster
        try:
            query = self._model_query(context, model)
            db_record = query.filter(model.name == params['name']). \
                filter(model.ca_cert_pem == params['ca_cert_path']). \
                filter(model.private_key_pem == params['private_key_path']). \
                one()
            return db_record
        except exc.NoResultFound:
            return None

    def create_ofcluster(self, context, params):
        """ Create a New Openflow Cluster record """
        
        # check any other cluster exists with the same name and key-cert
        db_record = self._check_ofcluster( context, params)
        if db_record is None:
            with context.session.begin(subtransactions=True):
                cluster = OpenflowCluster(id=str(uuidutils.generate_uuid()),
                                          name=str(params['name']),
                                          ca_cert_pem=str(params['ca_cert_path']),
                                          private_key_pem=str(params['private_key_path']),
                                          root_cert_pem=str(params['root_cert_path']),
                                          inter_cert_pem=str(params['inter_cert_path']),
                                          created_at=datetime.datetime.now(),
                                          updated_at=None,
                                          deleted_at=None)
                context.session.add(cluster)
            new_cluster = self._make_cluster_dict(cluster)    
            return new_cluster
        else:
            return db_record

    def get_ofclusters(self, context,filters=None, fields=None):
        """ Get the list of all Openflow Clusters """
        collection_list = self._get_collection(context, OpenflowCluster,
                                               self._make_cluster_dict,
                                               filters=filters, fields=fields)
        return collection_list

    def get_ofcluster(self, context, id, filters=None, fields=None):
        """ Get the details of an openflow cluster """
        cluster_data = self._get_by_id(context, OpenflowCluster,id)
        return self._make_cluster_dict(cluster_data)

    def update_ofcluster(self,context, id, **params):
        """ Update Openflow Cluster record """
        update_data = params
        update_data['updated_at'] = datetime.datetime.now()
        db_record = self._get_by_id(context,OpenflowCluster,id)
        db_record.update(update_data)
        return self._make_cluster_dict(db_record)

    def delete_ofcluster(self, context, id):
        """ Delete a Openflow Controller based on UUID """
        db_record = self._get_by_id(context, OpenflowCluster, id)
        controller_records = self.get_ofcluster_ofcontrollers(context, id)
        if [rec['cluster_id'] in [id] for rec in controller_records]:
            msg = _('Openflow Cluster {%s} cannot be deleted.'
                    'One or more Openflow Controller exists for the cluster ') % id
            raise q_exc.InvalidInput(error_message=msg)
        else:
            LOG.debug(_("Deleting Openflow Cluster {%s} => %s "),
                      str(id), str(db_record))
        with context.session.begin(subtransactions=True):
            context.session.delete(db_record)

    def _offields(self, resource, fields):
        if fields:
            return dict((key, item) for key, item in resource.iteritems()
                        if key in fields)
        resource = {'ofcluster': resource}
        return resource

    def _make_cluster_dict(self, params, fields=None, filters=None):
        fields = ['id', 'name', 'created_at', 'updated_at', 'ca_cert_pem', 'private_key_pem', 'root_cert_pem',
                  'inter_cert_pem']
        response = {'id': params.get('id'),
                    'name': params.get('name'),
                    'ca_cert_pem': params.get('ca_cert_pem'),
                    'private_key_pem': params.get('private_key_pem'),
                    'root_cert_pem': params.get('root_cert_pem'),
                    'inter_cert_pem': params.get('inter_cert_pem'),
                    'created_at': params.get('created_at'),
                    'updated_at': params.get('updated_at')}
        return self._offields(response, fields)

    # Openflow Controller Management    

    def _check_ofcluster_ofcontroller(self, context, params, cluster_id):
        """ Check for any duplicate record. """
        model = OpenflowController
        try:
            query = self._model_query(context,model)
            db_record = query.filter(model.ip_address == str(params['ip_address'])). \
                filter(model.cluster_id == cluster_id). \
                filter(model.port == str(params['port'])). \
                one()
            return db_record
        except exc.NoResultFound:
            return None

    def create_ofcluster_ofcontroller(self, context, params, cluster_id):
        """ Creiate a New Openflow Controller record """
        # Check whether a row exists with this data in the table
        try:
            with context.session.begin(subtransactions=True):
                controller = OpenflowController(id=str(uuidutils.generate_uuid()),
                                                name=str(params['name']),
                                                ip_address=str(params['ip_address']),
                                                port=str(params['port']),
                                                cell=str(params['cell']),
                                                cluster_id=str(cluster_id),
                                                created_at=datetime.datetime.now(),
                                                updated_at=None,
                                                status='Active',
                                                deleted_at=None)
                
                context.session.add(controller)
                return self._make_controller_dict(controller)
        except BaseException:
            LOG.error("OF-Controller Already exist")
            return {}

    def get_ofcluster_ofcontrollers(self, context, cluster_id,
                                    filters=None, fields=None):
        """ Get the list of all Openflow Controllers """
        filters={}
        filters['cluster_id'] = [cluster_id]
        collection_list = self._get_collection(context, OpenflowController,
                                               self._make_controller_dict,
                                               filters=filters, fields=fields)
        return collection_list

    def get_ofcluster_ofcontroller(self, context, id, cluster_id,
                                   filters=None, fields=None):
        """ Get the details of an openflow controller """
        #controller_data = self._get_ofcontroller_data(context,id)
        controller_data = self._get_on_Clusterid(context, OpenflowController,
                                                 id, cluster_id)
        return self._make_controller_dict(controller_data)

    def _get_on_Clusterid(self, context, model, id, cluster_id):
        """Get Openflow controller record based on Cluster ID and Controller ID """
        query = self._model_query(context,model)
        db_record = query.filter(model.id == id). \
            filter(model.cluster_id == cluster_id). \
            one()
        return db_record
    
    def update_ofcluster_ofcontroller(self, context, id, cluster_id, **params):
        """ Update Openflow Controller record """
        with context.session.begin(subtransactions=True):
            update_data = params['ofcontroller']['ofcontroller']
            update_data['updated_at'] = datetime.datetime.now()
            db_record = self._get_by_id(context, OpenflowController, id)
            LOG.debug(_("Update OF Controller data => %s"), str(update_data))
            db_record.update(update_data)
            LOG.debug(_("Updated Openflow Controller with UUID %s and Cluster ID %s"), id, cluster_id)
            return self._make_controller_dict(db_record)

    def delete_ofcluster_ofcontroller(self, context, id, cluster_id):
        """ Delete a Openflow Controller based on UUID """
        # (TODO) trinaths: check whether an Logical switches attached to this 
        # controller before destroying the same. 	
        controller_record = self._get_on_Clusterid(context, OpenflowController, id, cluster_id)
        LOG.debug(_("Deleting Openflow Controller {%s} with Cluster ID {%s} => %s "), str(id),
                  str(cluster_id),
                  str(controller_record))
        with context.session.begin(subtransactions=True):
            context.session.delete(controller_record)
    
    def _ofctrfields(self, resource, fields):
        if fields:
            return dict((key, item) for key, item in resource.iteritems()
                         if key in fields)
        resource = {'ofcontroller': resource}
        return resource

    def _make_controller_dict(self, params, fields=None, filters=None):
        fields = ['id', 'name', 'ip_address', 'port',
                  'cell', 'status', 'created_at', 'updated_at',
                  'cluster_id']
        response = {'id': params.get('id'),
                    'name': params.get('name'),
                    'ip_address': params.get('ip_address'),
                    'port': params.get('port'),
                    'cell': params.get('cell'),
                    'status': params.get('status'),
                    'created_at': params.get('created_at'),
                    'updated_at': params.get('updated_at'),
                    'cluster_id': params.get('cluster_id')}
        return self._ofctrfields(response, fields)
    # Openflow Logical Switch Management
    
    def _check_ofcluster_ofcontroller_logicalswitch(self, context, params):
        """ check for duplicate record """
        model = OpenflowSwitch
        try:
            query = self._model_query(context, model)
            db_record = query.filter(model.datapath_id == str(params['datapath_id'])). \
                filter(model.ip_address == str(params['ip_address'])). \
                filter(model.port == str(params['port'])). \
                one()
            return db_record
        except exc.NoResultFound:
            return None

    def create_ofcluster_ofcontroller_logicalswitch(self, context, params,
                                                    cluster_id, controller_id=None):
        """ Create a New Switch record """
        if self._check_ofcluster_ofcontroller_logicalswitch(context, params) is None:
            with context.session.begin(subtransactions=True):
                controller = OpenflowSwitch(id=str(uuidutils.generate_uuid()),
                                            datapath_id=str(params['datapath_id']),
                                            name=str(params['name']),
                                            ip_address=str(params['ip_address']),
                                            port=str(params['port']),
                                            certificate_pem=str(params['certificate_pem']),
                                            private_key_pem=str(params['private_key_pem']),
                                            created_at=datetime.datetime.now(),
                                            updated_at=None,
                                            deleted_at=None,
                                            cluster_id=cluster_id,
                                            controller_id=controller_id)
                context.session.add(controller)
            return self._make_switch_dict(controller)
        else:
            LOG.debug(_("Create Logical Switch failed."
                        "Duplicate record found."))

    def get_ofcluster_ofcontroller_logicalswitchs(self, context, cluster_id,
                                                  controller_id=None, filters=None, fields=None):
        """ Get the list of all Openflow Controllers """
        filters = {}
        filters['cluster_id'] = [cluster_id]
        if controller_id is not None:
            filters['controller_id'] = [controller_id]

        collection_list = self._get_collection(context, OpenflowSwitch,
                                               self._make_switch_dict,
                                               filters=filters, fields=fields)
        return collection_list

    def get_ofcluster_ofcontroller_logicalswitch(self, context, id, cluster_id,
                                        controller_id=None, filters=None, fields=None):
        """ Get the details of an openflow switch """
        switch_data = self._get_on_Clusterid_Controllerid(context, OpenflowSwitch,
                                           id, cluster_id, controller_id)
        return self._make_switch_dict(switch_data)

    def _get_on_Clusterid_Controllerid(self, context, model, id, cluster_id, controller_id=None):
        """Get Openflow Logical Switch record based on ID, Cluster ID and Controller ID """
        query = self._model_query(context, model)
        db_record = query.filter(model.id == id). \
            filter(model.cluster_id == cluster_id). \
            filter(model.controller_id == controller_id). \
            one()
        return db_record

    def update_ofcluster_ofcontroller_logicalswitch(self, context, id,
                                                    cluster_id, controller_id=None, **params):
        """ Update Logical Switch record """

        update_data = params
        update_data['updated_at'] = datetime.datetime.now()
        db_record = self._get_on_Clusterid_Controllerid(context, OpenflowSwitch, id, cluster_id, controller_id)
        db_record.update(update_data)
        LOG.debug(_("Updated Openflow Switch with UUID %s Controller ID {%s} Cluster ID {%s}"),
                  id, controller_id, cluster_id)
        return self._make_switch_dict(db_record)

    def delete_ofcluster_ofcontroller_logicalswitch(self, context, id,
                                                    cluster_id,controller_id=None):
        """ Delete a Openflow Logical Switch based on UUID """
        switch_record = self._get_on_Clusterid_Controllerid(context,OpenflowSwitch,id,cluster_id,controller_id)
        LOG.debug(_("Deleting Openflow Switch {%s} with Cluster ID {%s}, Controller ID {%s} => %s "), str(id),
                                        str(cluster_id),
                                        str(controller_id),
                                        str(switch_record))
        with context.session.begin(subtransactions=True):
            context.session.delete(switch_record)

    def _lsfields(self, resource, fields):
        if fields:
            return dict((key, item) for key, item in resource.iteritems()
                        if key in fields)
        resource = {'logicalswitch': resource}
        return resource

    def _make_switch_dict(self, params, fields=None, filters=None):
        fields = ['id', 'datapath_id', 'name', 'ip_address', 'port',
                  'cluster_id', 'controller_id',
                  'created_at', 'updated_at']
        response = {'id': params.get('id'),
                    'datapath_id': params.get('datapath_id'),
                    'name': params.get('name'),
                    'ip_address': params.get('ip_address'),
                    'port': params.get('port'),
                    'cluster_id': params.get('cluster_id'),
                    'controller_id': params.get('controller_id'),
                    'created_at': params.get('created_at'),
                    'updated_at': params.get('updated_at'),
        }
        return self._lsfields(response, fields)

    #################### Nwport Start######################################
    def _make_nwport_dict(self, nwport, fields=None):
        res = {'id': nwport['id'],
               'name': nwport['name'],
               'network_type': nwport['network_type'],
               'ip_address': nwport['ip_address'],
               'data_ip': nwport['data_ip'],
               'bridge': nwport['bridge'],
               'vxlan_vni': nwport['vxlan_vni'],
               'vxlan_udpport': nwport['vxlan_udpport'],
               'vlan_id': nwport['vlan_id'],
               'flow_type': nwport['flow_type'],
               'ovs_port': nwport['ovs_port'],
               'local_data_ip': nwport['local_data_ip'],
               'host': nwport['host']}
        return self._fields(res, fields)

    def create_nwport(self, context, nwport):
        n = nwport['nwport']
        with context.session.begin(subtransactions=True):
            nwport = cns_nwport(id=str(uuid.uuid4()),
                                name=n['name'],
                                network_type=n['network_type'],
                                ip_address=n['ip_address'],
                                data_ip=n['data_ip'],
                                bridge=n['bridge'],
                                vxlan_vni=n['vxlan_vni'],
                                vxlan_udpport=n['vxlan_udpport'],
                                vlan_id=n['vlan_id'],
                                flow_type=n['flow_type'],
                                ovs_port=n['ovs_port'],
                                local_data_ip=n['local_data_ip'],
                                host=n['host'])
            context.session.add(nwport)
        return self._make_nwport_dict(nwport)
        
    def get_nwport(self, context, id, fields=None):
        nwport = self._get_nwport(context, id)
        return self._make_nwport_dict(nwport, fields)
    
    def get_nwports(self, context, filters=None, fields=None):
        return self._get_collection(context, cns_nwport,
                                    self._make_nwport_dict,
                                    filters=filters, fields=fields)
        
    def _get_nwport(self, context, id):
        try:
            nwport = self._get_by_id(context, ns_nwport, id)
        except exc.NoResultFound:
            raise q_exc.NwportNotFound(nwport_id=id)
            #return False
        except exc.MultipleResultsFound:
            LOG.error('Multiple Nwport match for %s' % id)
            raise q_exc.NwportNotFound(nwport_id=id)
        return nwport
    
    def update_nwport(self, context, id, nwport):
        n = nwport['nwport']
        with context.session.begin(subtransactions=True):
            nwport = self._get_nwport(context, id)
            nwport.update(n)
        return self._make_nwport_dict(nwport)
        
    def delete_nwport(self, context, id):
        nwport = self._get_nwport(context, id)
        with context.session.begin(subtransactions=True):
            context.session.delete(nwport)
            
    ################## compute End #######################################       
    
        
    
