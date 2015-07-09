# Copyright 2012 OpenStack LLC.
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

import argparse
import logging

from nscs.crdclient.common import utils
from nscs.crdclient.crd.v2_0 import CreateCommand
from nscs.crdclient.crd.v2_0 import DeleteCommand
from nscs.crdclient.crd.v2_0 import ListCommand
from nscs.crdclient.crd.v2_0 import ShowCommand
from nscs.crdclient.crd.v2_0 import UpdateCommand


class ListSubnet(ListCommand):
    """List Subnets that belong to a given tenant."""

    resource = 'subnet'
    log = logging.getLogger(__name__ + '.ListSubnet')
    list_columns = ['subnet_id', 'name', 'network_id','tenant_id','cidr']
    pagination_support = True
    sorting_support = True

class DeleteSubnet(DeleteCommand):
    """Delete Subnet information."""

    log = logging.getLogger(__name__ + '.DeleteSubnet')
    resource = 'subnet'

class UpdateSubnet(UpdateCommand):
    """Update Subnet information."""

    log = logging.getLogger(__name__ + '.UpdateSubnet')
    resource = 'subnet'

class ShowSubnet(ShowCommand):
    """Show information of a given OF Subnet."""
    
    resource = 'subnet'
    log = logging.getLogger(__name__ + '.ShowSubnet')


class CreateSubnet(CreateCommand):
    """Create a Subnet for a given tenant."""

    resource = 'subnet'
    log = logging.getLogger(__name__ + '.CreateSubnet')

    def add_known_arguments(self, parser):
        
        
        
        parser.add_argument(
            '--subnet_id',
            help='Neutron Subnet Id')
        parser.add_argument(
            '--network_id',
            help='Network Id')
        parser.add_argument(
            '--ip_version',
            help='4/6')
        parser.add_argument(
            '--cidr',
            help='Classless Inter-Domain Routing')
        parser.add_argument(
            '--gateway_ip',
            help='Gateway ip')
        parser.add_argument(
            '--dns_nameservers',
            help='Dns Name Server')
        parser.add_argument(
            '--allocation_pools',
            help='Start and End Ip')
        parser.add_argument(
            '--host_routes',
            help='')
        parser.add_argument(
            'name', metavar='NAME',
            help='Name of Subnet to create')

    def args2body(self, parsed_args):
        print str(parsed_args)
        body = {'subnet':
                {
                    'name': parsed_args.name,
                    'subnet_id': parsed_args.subnet_id,
                    'network_id':parsed_args.network_id,
                    'ip_version':parsed_args.ip_version,
                    'cidr':parsed_args.cidr,
                    'gateway_ip':parsed_args.gateway_ip,
                    'dns_nameservers': parsed_args.dns_nameservers,
                    'allocation_pools': parsed_args.allocation_pools,
                    'host_routes': parsed_args.host_routes
                }
            }
        if parsed_args.tenant_id:
            body['subnet'].update({'tenant_id' : parsed_args.tenant_id})
        
        return body
