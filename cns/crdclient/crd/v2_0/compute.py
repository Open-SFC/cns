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


class ListCompute(ListCommand):
    """List Computes that belong to a given tenant."""

    resource = 'compute'
    log = logging.getLogger(__name__ + '.ListCompute')
    list_columns = ['compute_id', 'hostname','ip_address','status']
    pagination_support = True
    sorting_support = True

class DeleteCompute(DeleteCommand):
    """Delete Compute information."""

    log = logging.getLogger(__name__ + '.DeleteCompute')
    resource = 'compute'

class UpdateCompute(UpdateCommand):
    """Update Compute information."""

    log = logging.getLogger(__name__ + '.UpdateCompute')
    resource = 'compute'

class ShowCompute(ShowCommand):
    """Show information of a given OF Compute."""

    resource = 'compute'
    log = logging.getLogger(__name__ + '.ShowCompute')


class CreateCompute(CreateCommand):
    """Create a Compute for a given tenant."""

    resource = 'compute'
    log = logging.getLogger(__name__ + '.CreateCompute')

    def add_known_arguments(self, parser):
               
        
        parser.add_argument(
            '--compute_id',
            help='')
        parser.add_argument(
            '--ip_address',
            help='COmpute Node Ip address')
        parser.add_argument(
            '--ovs_port',
            help='openvswitch port')
        parser.add_argument(
            '--datapath_id',
            help='Bridge Datapath Id')
        parser.add_argument(
            '--switch',
            help='')
        parser.add_argument(
            '--domain',
            help='')
        parser.add_argument(
            '--subject_name',
            help='')
        parser.add_argument(
            '--status',
            help='Node status')
        parser.add_argument(
            'hostname', metavar='HOSTNAME',
            help='Name of Compute to create')

    def args2body(self, parsed_args):
        print str(parsed_args)
        body = {'compute':
                {
                    'hostname': parsed_args.hostname,
                    'compute_id': parsed_args.compute_id,
                    'ip_address':parsed_args.ip_address,
                    'ovs_port':parsed_args.ovs_port,
                    'datapath_id':parsed_args.datapath_id,
                    'switch':parsed_args.switch,
                    'domain': parsed_args.domain,
                    'subject_name': parsed_args.subject_name,
                    'status': parsed_args.status
                    
                }
            }
        
        
        return body
