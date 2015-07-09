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


class ListDatapath(ListCommand):
    """List Datapaths that belong to a given tenant."""

    resource = 'datapath'
    log = logging.getLogger(__name__ + '.ListDatapath')
    list_columns = ['id', 'name','subject']
    pagination_support = True
    sorting_support = True

class DeleteDatapath(DeleteCommand):
    """Delete Datapath information."""

    log = logging.getLogger(__name__ + '.DeleteDatapath')
    resource = 'datapath'

class UpdateDatapath(UpdateCommand):
    """Update Datapath information."""

    log = logging.getLogger(__name__ + '.UpdateDatapath')
    resource = 'datapath'

class ShowDatapath(ShowCommand):
    """Show information of a given OF Datapath."""

    resource = 'datapath'
    log = logging.getLogger(__name__ + '.ShowDatapath')


class CreateDatapath(CreateCommand):
    """Create a Datapath for a given tenant."""

    resource = 'datapath'
    log = logging.getLogger(__name__ + '.CreateDatapath')

    def add_known_arguments(self, parser):
        parser.add_argument(
                '--name',
                help='Datapath Name')
        parser.add_argument(
            '--subject',
            help='')
        parser.add_argument(
            '--switch',
            help='Switch UUID')
        parser.add_argument(
            '--domain',
            help='D')
        parser.add_argument(
            'id', metavar='NAME',
            help='Datapath to create')

    def args2body(self, parsed_args):
        body = {'datapath':
                {
                    'subject': parsed_args.subject,
                    'switch': parsed_args.switch,
                    'domain': parsed_args.domain,
                    'id': parsed_args.id,
                    'name': parsed_args.name,
                }
            }
        
        return body
