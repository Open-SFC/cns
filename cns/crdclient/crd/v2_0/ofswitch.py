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


class ListOpenflowSwitch(ListCommand):
    """List Openflow Switchs that belong to a given Cluster and Controller."""

    resource = 'logicalswitch'
    log = logging.getLogger(__name__ + '.ListOpenflowSwitch')
    list_columns = ['id', 'datapath_id','ip_address','port']
    pagination_support = True
    sorting_support = True

class DeleteOpenflowSwitch(DeleteCommand):
    """Delete Openflow Switch"""

    log = logging.getLogger(__name__ + '.DeleteOpenflowSwitch')
    resource = 'logicalswitch'
    allow_names = False
    def add_known_arguments(self, parser):
        parser.add_argument(
            '--cluster_id',
            help='Openflow Cluster UUID')
        parser.add_argument(
            '--controller_id',
            help='Openflow Controller UUID')

class UpdateOpenflowSwitch(UpdateCommand):
    """Update Openflow Switch"""

    log = logging.getLogger(__name__ + '.UpdateOpenflowSwitch')
    resource = 'logicalswitch'
    allow_names = False    

class ShowOpenflowSwitch(ShowCommand):
    """Show information of a given Openflow Switch."""

    resource = 'logicalswitch'
    log = logging.getLogger(__name__ + '.ShowOpenflowSwitch')
    allow_names = False
    def add_known_arguments(self, parser):
        parser.add_argument(
            '--cluster_id',
            help='Openflow Cluster UUID')
        parser.add_argument(
            '--controller_id',
            help='Openflow Controller UUID')


class CreateOpenflowSwitch(CreateCommand):
    """Create a Openflow Switch """

    resource = 'logicalswitch'
    log = logging.getLogger(__name__ + '.CreateOpenflowSwitch')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--name',
            required= True,            
            help='Name of the Switch, [eg: br-int]')
        parser.add_argument(
            '--ip_address',
            required= True,
            help='IP address of the OpenvSwitch Server')
        parser.add_argument(
            '--port',
            required= True,            
            help='Port of OpenvSwitch Server')
        parser.add_argument(
            '--cluster_id',
            required= True,            
            help='Cluster UUID')
        parser.add_argument(
            '--controller_id',
            required= True,            
            help='Controller UUID')

    def args2body(self, parsed_args):
        print "parsed arguments => ", str(parsed_args)
        body = {'logicalswitch':
                {
                    'name': parsed_args.name,
                    'ip_address': parsed_args.ip_address,
                    'port':parsed_args.port,
                    'cluster_id':parsed_args.cluster_id,
                    'controller_id':parsed_args.controller_id
                }
            }
        return body
