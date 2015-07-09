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

from nscs.crd_consumer.client.common import utils
from nscs.crd_consumer.client.sdnofcfg.v1 import CreateCommand
from nscs.crd_consumer.client.sdnofcfg.v1 import DeleteCommand
from nscs.crd_consumer.client.sdnofcfg.v1 import ListCommand
from nscs.crd_consumer.client.sdnofcfg.v1 import ShowCommand
from nscs.crd_consumer.client.sdnofcfg.v1 import UpdateCommand


class ListNetwork(ListCommand):
    """List Networks that belong to a given tenant."""
    resource = 'virtualnetwork'
    log = logging.getLogger(__name__ + '.ListNetwork')
    list_columns = ['id', 'name', 'status', 'type', 'vxlan_service_port', 'state']
    pagination_support = True
    sorting_support = True
    
class CreateNetwork(CreateCommand):
    """Create a Network for a given tenant."""

    resource = 'virtualnetwork'
    log = logging.getLogger(__name__ + '.CreateNetwork')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--router_external_up',
            default=False, action='store_true',
            help='Set Router Externa State to True')
        parser.add_argument(
            '--network_id',
            help='Network ID')
        parser.add_argument(
            '--network_type',
            help='Provider Network Type Eg:vlan/gre/vxlan')
        parser.add_argument(
            '--segmentation_id',
            help='Provider Segmentation Id')
        parser.add_argument(
            '--service_port',
            help='VXLAN Service Port')
        parser.add_argument(
            '--status',
            help='Eg:active/inactive')
        parser.add_argument(
            '--state',
            help='Eg:up/down')
        parser.add_argument(
            'name', metavar='NAME',
            help='Name of Network to create')
        
    def args2body(self, parsed_args):
        print str(parsed_args)
        if parsed_args.state.lower() == 'true':
            state = True
        else:
            state = False
        body = {'virtualnetwork':
                {
                    'name': parsed_args.name,
                    'id': parsed_args.network_id,
                    'type':parsed_args.network_type,
                    'segmentation_id':parsed_args.segmentation_id,
                    'vxlan_service_port':parsed_args.service_port,
                    'status':parsed_args.status,
                    'external': parsed_args.router_external_up,
                    'state': state
                }
            }
        if parsed_args.tenant_id:
            body['virtualnetwork'].update({'tenant' : parsed_args.tenant_id})

        return body
    
class DeleteNetwork(DeleteCommand):
    """Delete Network information."""

    log = logging.getLogger(__name__ + '.DeleteNetwork')
    resource = 'virtualnetwork'
    
class ShowNetwork(ShowCommand):
    """Show information of a given CRM Network."""

    resource = 'virtualnetwork'
    log = logging.getLogger(__name__ + '.ShowNetwork')
    
class UpdateNetwork(UpdateCommand):
    """Update Network information."""

    log = logging.getLogger(__name__ + '.UpdateNetwork')
    resource = 'virtualnetwork'
