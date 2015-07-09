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


class ListPort(ListCommand):
    """List Ports that belong to a given tenant."""

    resource = 'port'
    log = logging.getLogger(__name__ + '.ListPort')
    list_columns = ['id', 'name', 'mac_address']
    pagination_support = True
    sorting_support = True

class DeletePort(DeleteCommand):
    """Delete Port information."""

    log = logging.getLogger(__name__ + '.DeletePort')
    resource = 'port'

class UpdatePort(UpdateCommand):
    """Update Port information."""

    log = logging.getLogger(__name__ + '.UpdatePort')
    resource = 'port'

class ShowPort(ShowCommand):
    """Show information of a given OF Port."""

    resource = 'port'
    log = logging.getLogger(__name__ + '.ShowPort')


class CreatePort(CreateCommand):
    """Create a Port for a given tenant."""

    resource = 'port'
    log = logging.getLogger(__name__ + '.CreatePort')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--state',
            help='Eg:up/down')
        parser.add_argument(
            '--port_id',
            help='Neutron Port Id')
        parser.add_argument(
            '--subnet_id',
            help='')
        parser.add_argument(
            '--network_id',
            help='')
        parser.add_argument(
            '--mac_address',
            help='Port Mac Address')
        parser.add_argument(
            '--device_id',
            help='Instance Id')
        parser.add_argument(
            '--ip_address',
            help='Instance ip address')
        parser.add_argument(
            '--status',
            help='Eg:active/inactive')
        parser.add_argument(
            '--device_owner',
            help='Device Owner')
        parser.add_argument(
            '--bridge',
            help='Bridge Name')
        parser.add_argument(
            'name', metavar='NAME',
            help='Name of Port to create')

    def args2body(self, parsed_args):
        print str(parsed_args)
        if parsed_args.state.lower() == 'true':
            state = True
        else:
            state = False
        body = {'port':
                {
                    'name': parsed_args.name,
                    'id': parsed_args.port_id,
                    'subnet_id':parsed_args.subnet_id,
                    'nw_id':parsed_args.network_id,
                    'mac_address':parsed_args.mac_address,
                    'device_id':parsed_args.device_id,
                    'ip_address': parsed_args.ip_address,
                    'status': parsed_args.status,
                    'state': state,
                    'bridge': parsed_args.bridge,
                    'device_owner': parsed_args.device_owner
                }
            }
        if parsed_args.tenant_id:
            body['port'].update({'tenant' : parsed_args.tenant_id})
        
        return body
