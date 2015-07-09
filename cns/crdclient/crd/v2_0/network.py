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


class ListNetwork(ListCommand):
    """List Networks that belong to a given tenant."""

    resource = 'network'
    log = logging.getLogger(__name__ + '.ListNetwork')
    list_columns = ['network_id', 'name','tenant_id','status']
    pagination_support = True
    sorting_support = True

class DeleteNetwork(DeleteCommand):
    """Delete Network information."""

    log = logging.getLogger(__name__ + '.DeleteNetwork')
    resource = 'network'

class UpdateNetwork(UpdateCommand):
    """Update Network information."""

    log = logging.getLogger(__name__ + '.UpdateNetwork')
    resource = 'network'

class ShowNetwork(ShowCommand):
    """Show information of a given OF Network."""

    resource = 'network'
    log = logging.getLogger(__name__ + '.ShowNetwork')


class CreateNetwork(CreateCommand):
    """Create a Network for a given tenant."""

    resource = 'network'
    log = logging.getLogger(__name__ + '.CreateNetwork')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--admin-state-down',
            default=True, action='store_false',
            help='Set Admin State Up to false')
        parser.add_argument(
            '--admin_state_down',
            action='store_false',
            help=argparse.SUPPRESS)
        parser.add_argument(
            '--router_external_up',
            default=False, action='store_true',
            help='Set Router Externa State to True')
        
        
        parser.add_argument(
            '--network_id',
            help='')
        parser.add_argument(
            '--network_type',
            help='Provider Network Type Eg:vlan/gre/vxlan')
        parser.add_argument(
            '--segmentation_id',
            help='Provider Segmentation Id')
        parser.add_argument(
            '--physical_network',
            help='Provider Physical Network')
        parser.add_argument(
            '--status',
            help='Eg:Active/Delete')
        parser.add_argument(
            'name', metavar='NAME',
            help='Name of Network to create')

    def args2body(self, parsed_args):
        print str(parsed_args)
        body = {'network':
                {
                    'name': parsed_args.name,
                    'network_id': parsed_args.network_id,
                    'network_type':parsed_args.network_type,
                    'segmentation_id':parsed_args.segmentation_id,
                    'physical_network':parsed_args.physical_network,
                    'status':parsed_args.status,
                    'router_external': parsed_args.router_external_up,
                    'admin_state_up': parsed_args.admin_state_down
                }
            }
        if parsed_args.tenant_id:
            body['network'].update({'tenant_id' : parsed_args.tenant_id})
        
        return body
