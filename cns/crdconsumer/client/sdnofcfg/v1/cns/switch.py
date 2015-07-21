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

from datetime import datetime


class ListSwitch(ListCommand):
    """List Switchs that belong to a given tenant."""

    resource = 'switch'
    log = logging.getLogger(__name__ + '.ListSwitch')
    list_columns = ['id', 'name', 'fqdn']
    pagination_support = True
    sorting_support = True

class DeleteSwitch(DeleteCommand):
    """Delete Switch information."""

    log = logging.getLogger(__name__ + '.DeleteSwitch')
    resource = 'switch'

class UpdateSwitch(UpdateCommand):
    """Update Switch information."""

    log = logging.getLogger(__name__ + '.UpdateSwitch')
    resource = 'switch'

class ShowSwitch(ShowCommand):
    """Show information of a given OF Switch."""

    resource = 'switch'
    log = logging.getLogger(__name__ + '.ShowSwitch')


class CreateSwitch(CreateCommand):
    """Create a Switch for a given tenant."""

    resource = 'switch'
    log = logging.getLogger(__name__ + '.CreateSwitch')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--fqdn',
            help='')
        parser.add_argument(
            '--type',
            help='True/False')
        parser.add_argument(
            '--baddr',
            help='True/False')
        parser.add_argument(
            '--ip_address',
            help='IP Address')
        parser.add_argument(
            'name', metavar='NAME',
            help='Name of Switch to create')

    def args2body(self, parsed_args):
        if parsed_args.type.lower() == 'true':
            type = True
        else:
            type = False
            
        if parsed_args.baddr.lower() == 'true':
            baddr = True
        else:
            baddr = False
            
        body = {'switch':
                {
                    'name': parsed_args.name,
                    'fqdn': parsed_args.fqdn,
                    'ip_address': parsed_args.ip_address,
                    'type': type,
                    'baddr': baddr
                }
            }
        
        return body
