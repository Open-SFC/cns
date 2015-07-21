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

from abc import abstractmethod

from nscs.crdservice.api.v2 import attributes as attr
from nscs.crdservice.api.v2 import base
from nscs.crdservice.api import extensions
from nscs.crdservice.common import exceptions as qexception
from nscs.crdservice import manager
from nscs.crdservice.openstack.common import log as logging
from nscs.crdservice.plugins.services.service_base import ServicePluginBase
LOG = logging.getLogger(__name__)

OVS_PLURALS = {
    'networks': 'network',
    'subnets': 'subnet',
    'ports': 'port',
}

NETWORK="NETWORK"

RESOURCE_ATTRIBUTE_MAP = {
    'networks': {
        'id': {'allow_post': False, 'allow_put': False,
               'is_visible': True,  'validate': {'type:regex': attr.UUID_PATTERN},
               'primary_key' : True,
              },
        'name': {'allow_post': True, 'allow_put': True,
                 'is_visible': True, 'default': ''
                },
        'network_id': {'allow_post': True, 'allow_put': True,
                      'is_visible': True
                     },
        'network_type': { 'allow_post': True,'allow_put': True,
                    'is_visible': True,  'default': ''
                },
        'segments': { 'allow_post': True,'allow_put': True,
                    'is_visible': True,  'default': ''
                },
        'physical_network': { 'allow_post': True, 'allow_put': True,
                    'is_visible': True, 'default': ''
                },
        'router_external': { 'allow_post': True, 'allow_put': True,
                    'is_visible': True, 'default': 0
                },
        'vxlan_service_port': { 'allow_post': True, 'allow_put': True,
                    'is_visible': True, 'default': 4789
                },
        'segmentation_id': { 'allow_post': True,'allow_put': True,
                        'is_visible': True,'default': 0
                      },
        'status': { 'allow_post': True,'allow_put': True,
                        'is_visible': True,'default': ''
                      },
        'admin_state_up': { 'allow_post': True,'allow_put': True,
                        'is_visible': True,'default': 0
                      },
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'required_by_policy': True,'validate': {'type:string': None},
                        'is_visible': True
                     },
    },
        
    'subnets': {
        'id': {'allow_post': False, 'allow_put': False,
               'is_visible': True,  'validate': {'type:regex': attr.UUID_PATTERN},
               'primary_key' : True,
              },
        'name': {'allow_post': True, 'allow_put': True,
                 'is_visible': True, 'default': ''
                },
        'subnet_id': { 'allow_post': True,'allow_put': True,
                    'is_visible': True,  'default': ''
                },
        'network_id': {'allow_post': True, 'allow_put': True,
                      'is_visible': True
                     },
        'ip_version': { 'allow_post': True, 'allow_put': True,
                    'is_visible': True, 'default': ''
                },
        'cidr': { 'allow_post': True,'allow_put': True,
                        'is_visible': True,'default': ''
                      },
        'gateway_ip': { 'allow_post': True,'allow_put': True,
                        'is_visible': True,'default': ''
                      },
        'dns_nameservers': { 'allow_post': True,'allow_put': True,
                        'is_visible': True,'default': ''
                      },
        'allocation_pools': { 'allow_post': True,'allow_put': True,
                        'is_visible': True,'default': ''
                      },
        'host_routes': { 'allow_post': True,'allow_put': True,
                        'is_visible': True,'default': ''
                      },
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'required_by_policy': True,'validate': {'type:string': None},
                        'is_visible': True
                     },
    },
    
    'ports': {
        'id': {'allow_post': False, 'allow_put': False,
               'is_visible': True,  'validate': {'type:regex': attr.UUID_PATTERN},
               'primary_key' : True,
              },
        'name': {'allow_post': True, 'allow_put': True,
                 'is_visible': True, 'default': ''
                },
        'network_id': { 'allow_post': True,'allow_put': True,
                    'is_visible': True,  'default': ''
                },
        'subnet_id': { 'allow_post': True,'allow_put': True,
                    'is_visible': True,  'default': ''
                },
        'port_id': { 'allow_post': True, 'allow_put': True,
                    'is_visible': True, 'default': ''
                },
        'mac_address': { 'allow_post': True, 'allow_put': True,
                    'is_visible': True, 'default': ''
                },
        'device_id': { 'allow_post': True,'allow_put': True,
                        'is_visible': True,'default': ''
                      },
        'ip_address': { 'allow_post': True,'allow_put': True,
                        'is_visible': True,'default': ''
                      },
        'device_owner': { 'allow_post': True,'allow_put': True,
                        'is_visible': True,'default': ''
                      },
        'security_groups': { 'allow_post': True,'allow_put': True,
                        'is_visible': True,'default': ''
                      },
        'status': { 'allow_post': True,'allow_put': True,
                        'is_visible': True,'default': ''
                      },
        'admin_state_up': { 'allow_post': True,'allow_put': True,
                        'is_visible': True,'default': 0
                      },
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'required_by_policy': True,'validate': {'type:string': None},
                        'is_visible': True
                     },
    },
}

class Network(object):
    """ CRD extension"""

    @classmethod
    def get_name(cls):
        return "CRD Mgmt"

    @classmethod
    def get_alias(cls):
        return "network"

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
        plugin = manager.CrdManager.get_service_plugins()[NETWORK]
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

class NetworkBase(ServicePluginBase):
        
    """ CRD management """
    def get_plugin_name(self):
        return NETWORK
    def get_plugin_type(self):
        return NETWORK

    def get_plugin_description(self):
        return "Crd  Network Service Plugin"
    
    
    
    
    
