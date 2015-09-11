# Copyright 2013 Freescale Semiconductor, Inc.
# vim: tabstop=4 shiftwidth=4 softtabstop=4

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
#

import abc
from nscs.crdservice.api.v2 import attributes as attr
from nscs.crdservice.api.v2 import base
from nscs.crdservice.api import extensions
from nscs.crdservice.common import exceptions as qexception
from nscs.crdservice import manager
from nscs.crdservice.openstack.common import log as logging
from nscs.crdservice.plugins.services.service_base import ServicePluginBase
LOG = logging.getLogger(__name__)

OVS_PLURALS = {
    'computes': 'compute',
    'instances': 'instance',
    'ofclusters': 'ofcluster',
    'ofcontrollers': 'ofcontroller',
    'logicalswitchs': 'logicalswitch',
    
}

NOVASERVICE = "NOVA"

RESOURCE_ATTRIBUTE_MAP = {
    'computes': {
        'id': {'allow_post': False, 'allow_put': False,
               'is_visible': True,  'validate': {'type:regex': attr.UUID_PATTERN},
               'primary_key' : True,
              },
        'hostname': {'allow_post': True, 'allow_put': True,
                 'is_visible': True, 'default': ''
                },
        'compute_id': {'allow_post': True, 'allow_put': True,
                      'is_visible': True
                     },
        'ip_address': { 'allow_post': True,'allow_put': True,
                    'is_visible': True,  'default': ''
                },
        'data_ip': { 'allow_post': True,'allow_put': True,
                    'is_visible': True,  'default': ''
                },
        'created_at': { 'allow_post': True, 'allow_put': True,
                    'is_visible': True, 'default': ''
                },
        'ovs_port': { 'allow_post': True, 'allow_put': True,
                    'is_visible': True, 'default': 0
                },
        'datapath_id': { 'allow_post': True,'allow_put': True,
                        'is_visible': True,'default': 0
                      },
        'datapath_name': { 'allow_post': True,'allow_put': True,
                        'is_visible': True,'default': 0
                      },
        'switch': { 'allow_post': True,'allow_put': True,
                        'is_visible': True,'default': ''
                      },
        'domain': { 'allow_post': True,'allow_put': True,
                        'is_visible': True,'default': 0
                      },
        'subject_name': { 'allow_post': True,'allow_put': True,
                        'is_visible': True,'default': 0
                      },
        'status': { 'allow_post': True,'allow_put': True,
                        'is_visible': True,'default': 0
                      },
        'tenant_id': { 'allow_post': True,'allow_put': True,
                        'is_visible': False,'default': 0
                      },
    },
        
    'instances': {
        'id': {'allow_post': False, 'allow_put': False,
               'is_visible': True,  'validate': {'type:regex': attr.UUID_PATTERN},
               'primary_key' : True,
              },
        'display_name': {'allow_post': True, 'allow_put': True,
                 'is_visible': True, 'default': ''
                },
        'instance_id': {'allow_post': True, 'allow_put': True,
                      'is_visible': True
                     },
        'user_id': { 'allow_post': True,'allow_put': True,
                    'is_visible': True,  'default': ''
                },
        'state_description': { 'allow_post': True, 'allow_put': True,
                    'is_visible': True, 'default': ''
                },
        'state': { 'allow_post': True,'allow_put': True,
                        'is_visible': True,'default': ''
                      },
        'created_at': { 'allow_post': True,'allow_put': True,
                        'is_visible': True,'default': ''
                      },
        'launched_at': { 'allow_post': True,'allow_put': True,
                        'is_visible': True,'default': ''
                      },
        'host': { 'allow_post': True,'allow_put': True,
                        'is_visible': True,'default': ''
                      },
        'reservation_id': { 'allow_post': True,'allow_put': True,
                        'is_visible': True,'default': ''
                      },
        'zone': {'allow_post': True, 'allow_put': False,
                 'default': None, 'is_visible': True},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'required_by_policy': True,'validate': {'type:string': None},
                        'is_visible': True
                     },
    },
        
    'ofclusters': {
        'id': {'allow_post': False, 'allow_put': False,
               'is_visible': True, 'validate': {'type:regex': attr.UUID_PATTERN},
               'primary_key': True},
        'name': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'is_visible': True, 'default': ''},
        'ca_cert_path': {'allow_post': True, 'allow_put': True,
                         'is_visible': True, 'default': ''},
        'private_key_path': {'allow_post': True, 'allow_put': True,
                             'is_visible': True, 'default': ''},
        'root_cert_path': {'allow_post': True, 'allow_put': True,
                           'is_visible': True, 'default': ''},
        'inter_cert_path': {'allow_post': True, 'allow_put': True,
                            'is_visible': True, 'default': ''},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'required_by_policy': True, 'validate': {'type:string': None},
                      'is_visible': True},
        'created_at': {'allow_post': False, 'allow_put': False,
                       'required_by_policy': False,
                       'is_visible': True},
        'updated_at': {'allow_post': False, 'allow_put': False,
                       'required_by_policy': False,
                       'is_visible': True},
    },
    'ofcontrollers': {
        'parent': {'collection_name': 'ofclusters',
                   'member_name': 'ofcluster'},
        'parameters': {
            'id': {'allow_post': False, 'allow_put': False,
                   'is_visible': True, 'validate': {'type:uuid': attr.UUID_PATTERN},
                   'primary_key': True,},
            'name': {'allow_post': True, 'allow_put': True,
                     'validate': {'type:string': None},
                     'is_visible': True, 'default': ''},
            'ip_address': {'allow_post': True, 'allow_put': True,
                           'is_visible': True, 'default': ''},
            'port': {'allow_post': True, 'allow_put': True,
                     'is_visible': True, 'default': ''},
            'cell': {'allow_post': True, 'allow_put': True,
                     'is_visible': True, 'default': ''},
            'cluster_id': {'allow_post': True, 'allow_put': True,
                           'is_visible': True, 'default': ''},
            'tenant_id': {'allow_post': True, 'allow_put': False,
                          'required_by_policy': True, 'validate': {'type:string': None},
                          'is_visible': True},
            'created_at': {'allow_post': False, 'allow_put': False,
                           'required_by_policy': False,
                           'is_visible': True},
            'updated_at': {'allow_post': False, 'allow_put': False,
                           'required_by_policy': False,
                           'is_visible': True},
        }
    },
    'logicalswitchs': {
        'parent': {'collection_name': 'ofcontrollers',
                   'member_name': 'ofcontroller'},
        'parameters': {
            'id': {'allow_post': False, 'allow_put': False,
                   'is_visible': True, 'validate': {'type:uuid': attr.UUID_PATTERN},
                   'primary_key': True},
            'datapath_id': {'allow_post': False, 'allow_put': False,
                            'is_visible': True, 'default': ''},
            'name': {'allow_post': True, 'allow_put': True,
                     'is_visible': True, 'default': 'br-int'},
            'ip_address': {'allow_post': True, 'allow_put': True,
                           'is_visible': True, 'default': ''},
            'port': {'allow_post': True, 'allow_put': True,
                     'is_visible': True, 'default': ''},
            'cluster_id': {'allow_post': True, 'allow_put': True,
                           'is_visible': True, 'default': ''},
            'controller_id': {'allow_post': True, 'allow_put': True,
                              'is_visible': True, 'default': ''},
            'tenant_id': {'allow_post': True, 'allow_put': False,
                          'required_by_policy': True, 'validate': {'type:string': None},
                          'is_visible': True},
            'created_at': {'allow_post': False, 'allow_put': False,
                           'required_by_policy': False,
                           'is_visible': True},
            'updated_at': {'allow_post': False, 'allow_put': False,
                           'required_by_policy': False,
                           'is_visible': True},
        }
    },
    
    
}

class Nova(extensions.ExtensionDescriptor):
    """ CRD extension"""

    @classmethod
    def get_name(cls):
        return "CRD Mgmt"

    @classmethod
    def get_alias(cls):
        return "nova"

    @classmethod
    def get_description(cls):
        return "Extension for CRD Management."

    @classmethod
    def get_namespace(cls):
        return "http://docs.openstack.org/ext/openflow-cluster/api/v2.0"

    @classmethod
    def get_updated(cls):
        return "2012-10-05T10:00:00-00:00"
    
    @classmethod
    def get_resources(cls):
        resources = []
        plugin = manager.CrdManager.get_service_plugins()[NOVASERVICE]
        for collection_name in RESOURCE_ATTRIBUTE_MAP:
            resource_name = OVS_PLURALS[collection_name]
            parents = None
            path_prefix=""
            parent = None
            if RESOURCE_ATTRIBUTE_MAP[collection_name].has_key('parameters'):
                params = RESOURCE_ATTRIBUTE_MAP[collection_name].get('parameters')
                parent = RESOURCE_ATTRIBUTE_MAP[collection_name].get('parent')
                parents = []
                path_prefix=[]
                def generate_parent(parent_attr):
                    parents.append(parent_attr)
                    if parent_attr != parent:
                        path_prefix.insert(0,"/%s/{%s_id}" % (parent_attr['collection_name'],parent_attr['member_name']))
                    if RESOURCE_ATTRIBUTE_MAP[parent_attr['collection_name']].has_key('parent'):
                        generate_parent(RESOURCE_ATTRIBUTE_MAP[parent_attr['collection_name']].get('parent'))
                generate_parent(parent)
                path_prefix= ''.join(path_prefix)
            else :
                params = RESOURCE_ATTRIBUTE_MAP[collection_name]

            member_actions = {}
            controller = base.create_resource(collection_name,
                                              resource_name,
                                              plugin, params,
                                              member_actions=member_actions,
                                              parent=parents)

            resource = extensions.ResourceExtension(
                collection_name,
                controller,
                parent=parent,
                path_prefix=path_prefix,
                member_actions=member_actions,
                attr_map=params)
            resources.append(resource)

        return resources

    def get_extended_resources(self, version):
        if version == "2.0":
            return {}
        else:
            return {}


class NovaBase(ServicePluginBase):
    __metaclass__ = abc.ABCMeta    
    """ CRD management """
    def get_plugin_name(self):
        return NOVASERVICE
    def get_plugin_type(self):
        return NOVASERVICE

    def get_plugin_description(self):
        return "Crd  Nova Service Plugin"
    
    
    
    
    
