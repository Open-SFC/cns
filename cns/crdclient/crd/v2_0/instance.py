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


class ListInstance(ListCommand):
    """List Instances that belong to a given tenant."""

    resource = 'instance'
    log = logging.getLogger(__name__ + '.ListInstance')
    list_columns = ['instance_id', 'display_name','host','state']
    pagination_support = True
    sorting_support = True

class DeleteInstance(DeleteCommand):
    """Delete Instance information."""

    log = logging.getLogger(__name__ + '.DeleteInstance')
    resource = 'instance'

class UpdateInstance(UpdateCommand):
    """Update Instance information."""

    log = logging.getLogger(__name__ + '.UpdateInstance')
    resource = 'instance'

class ShowInstance(ShowCommand):
    """Show information of a given OF Instance."""

    resource = 'instance'
    log = logging.getLogger(__name__ + '.ShowInstance')


class CreateInstance(CreateCommand):
    """Create a Instance for a given tenant."""

    resource = 'instance'
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
            'display_name', metavar='NAME',
            help='Name of Instance to create')

    def args2body(self, parsed_args):
        print str(parsed_args)
        body = {'instance':
                {
                    'display_name': parsed_args.display_name,
                    'instance_id': parsed_args.instance_id,
                    'user_id':parsed_args.user_id,
                    'state_description':parsed_args.state_description,
                    'state':parsed_args.state,
                    'host':parsed_args.host,
                    'reservation_id': parsed_args.reservation_id
                }
            }
        if parsed_args.tenant_id:
            body['instance'].update({'tenant_id' : parsed_args.tenant_id})
        
        return body
