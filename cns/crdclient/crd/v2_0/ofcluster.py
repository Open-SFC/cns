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


class ListOpenflowCluster(ListCommand):
    """List Openflow Clusters"""

    resource = 'ofcluster'
    log = logging.getLogger(__name__ + '.ListOpenflowCluster')
    list_columns = ['id', 'name','created_at']
    pagination_support = True
    sorting_support = True

class DeleteOpenflowCluster(DeleteCommand):
    """Delete Openflow cluster """

    log = logging.getLogger(__name__ + '.DeleteOpenflowCluster')
    resource = 'ofcluster'

class UpdateOpenflowCluster(UpdateCommand):
    """Update Openflow Cluster"""

    log = logging.getLogger(__name__ + '.UpdateOpenflowCluster')
    resource = 'ofcluster'

class ShowOpenflowCluster(ShowCommand):
    """Show information of a given Openflow Cluster."""

    resource = 'ofcluster'
    log = logging.getLogger(__name__ + '.ShowOpenflowCluster')


class CreateOpenflowCluster(CreateCommand):
    """Create a Openflow Cluster"""

    resource = 'ofcluster'
    log = logging.getLogger(__name__ + '.CreateOpenflowCluster')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--ca_cert_path',
            help='CA Certificate path of Openflow Cluster')
        parser.add_argument(
            '--private_key_path',
            help='Private key path of Openflow Cluster')
        parser.add_argument(
            '--root_cert_path',
            help='ROOT Certificate of Openflow Cluster')
        parser.add_argument(
            '--inter_cert_path',
            help='Intermediate CA Certificate path of Openflow Cluster')
        parser.add_argument(
            'name', metavar='NAME',
            help='Name of OpenflowCluster to create')

    def args2body(self, parsed_args):
        print str(parsed_args)
        body = {'ofcluster':
                {
                    'name': parsed_args.name,
                    'ca_cert_path':parsed_args.ca_cert_path,
                    'private_key_path':parsed_args.private_key_path,
                    'root_cert_path':parsed_args.root_cert_path,
                    'inter_cert_path': parsed_args.inter_cert_path,
                }
            }
        return body
