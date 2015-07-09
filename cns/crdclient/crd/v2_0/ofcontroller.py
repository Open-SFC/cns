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


class ListOpenflowController(ListCommand):
    """List Openflow Controllers that belong to a given Cluster"""

    resource = 'ofcontroller'
    log = logging.getLogger(__name__ + '.ListOpenflowController')
    list_columns = ['cluster_id','id', 'name','ip_address','port','status']
    pagination_support = True
    sorting_support = True
    

class DeleteOpenflowController(DeleteCommand):
    """Delete Openflow Controller"""

    log = logging.getLogger(__name__ + '.DeleteOpenflowController')
    resource = 'ofcontroller'
    allow_names = False
    def add_known_arguments(self, parser):
        parser.add_argument(
            '--cluster_id',
            help='Openflow Cluster UUID')
    

class UpdateOpenflowController(UpdateCommand):
    """Update Openflow Controller"""

    log = logging.getLogger(__name__ + '.UpdateOpenflowController')
    resource = 'ofcontroller'
    allow_names = False
    
    

class ShowOpenflowController(ShowCommand):
    """Show information of a given Openflow Controller"""

    resource = 'ofcontroller'
    allow_names = False
    log = logging.getLogger(__name__ + '.ShowOpenflowController')
    def add_known_arguments(self, parser):
        parser.add_argument(
            '--cluster_id',
            required= True,
            help='Openflow Cluster UUID')



class CreateOpenflowController(CreateCommand):
    """Create a Openflow Controller"""

    resource = 'ofcontroller'
    log = logging.getLogger(__name__ + '.CreateOpenflowController')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--cluster_id',
            required= True,
            help='Openflow Cluster UUID')
        parser.add_argument(
            '--ip_address',
            required=True,
            help='IP address of the Openflow Controller')
        parser.add_argument(
            '--port',
            required=True,
            help='Port of the Openflow Controller')
        parser.add_argument(
            '--cell',
            help='Nova compute Cell name or Id')
        parser.add_argument(
            '--name',
            required= True,
            help='Name of OpenflowController to create')

    def args2body(self, parsed_args):
        print str(parsed_args)
        body = {'ofcontroller':
                {
                    'cluster_id': parsed_args.cluster_id,
                    'name': parsed_args.name,
                    'ip_address':parsed_args.ip_address,
                    'port':parsed_args.port,
                    'cell':parsed_args.cell
                }
            }
        return body
