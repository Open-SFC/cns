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


class ListInstance(ListCommand):
    """List Instances that belong to a given tenant."""

    resource = 'virtualmachine'
    log = logging.getLogger(__name__ + '.ListInstance')
    list_columns = ['id', 'name','host']
    pagination_support = True
    sorting_support = True

class DeleteInstance(DeleteCommand):
    """Delete Instance information."""

    log = logging.getLogger(__name__ + '.DeleteInstance')
    resource = 'virtualmachine'

class UpdateInstance(UpdateCommand):
    """Update Instance information."""

    log = logging.getLogger(__name__ + '.UpdateInstance')
    resource = 'virtualmachine'

class ShowInstance(ShowCommand):
    """Show information of a given OF Instance."""

    resource = 'virtualmachine'
    log = logging.getLogger(__name__ + '.ShowInstance')


class CreateInstance(CreateCommand):
    """Create a Instance for a given tenant."""

    resource = 'virtualmachine'
    log = logging.getLogger(__name__ + '.CreateInstance')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--instance_id',
            help='')
        parser.add_argument(
            '--user_id',
            help='')
        parser.add_argument(
            '--state_description',
            help='')
        parser.add_argument(
            '--state',
            help='Instance status')
        parser.add_argument(
            '--host',
            help='Instance Host')
        parser.add_argument(
            '--reservation_id',
            help='')
        parser.add_argument(
            'name', metavar='NAME',
            help='Name of Instance to create')

    def args2body(self, parsed_args):
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        launched_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        body = {'virtualmachine':
                {
                    'name': parsed_args.name,
                    'id': parsed_args.instance_id,
                    'user_id':parsed_args.user_id,
                    'state_description':parsed_args.state_description,
                    'state':parsed_args.state,
                    'host':parsed_args.host,
                    'reservation_id': parsed_args.reservation_id,
                    'created_at': created_at,
                    'launched_at': launched_at,
                    
                }
            }
        if parsed_args.tenant_id:
            body['virtualmachine'].update({'tenant' : parsed_args.tenant_id})
        
        return body
