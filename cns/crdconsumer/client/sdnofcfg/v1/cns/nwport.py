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

    resource = 'nwport'
    log = logging.getLogger(__name__ + '.ListPort')
    list_columns = ['id', 'name', 'bridge', 'ip_address', 'data_ip', 'local_data_ip', 'flow_type']
    pagination_support = True
    sorting_support = True

class DeletePort(DeleteCommand):
    """Delete Port information."""

    log = logging.getLogger(__name__ + '.DeletePort')
    resource = 'nwport'

class UpdatePort(UpdateCommand):
    """Update Port information."""

    log = logging.getLogger(__name__ + '.UpdatePort')
    resource = 'nwport'

class ShowPort(ShowCommand):
    """Show information of a given OF Port."""

    resource = 'nwport'
    log = logging.getLogger(__name__ + '.ShowPort')


class CreatePort(CreateCommand):
    """Create a Port for a given tenant."""

    resource = 'nwport'
    log = logging.getLogger(__name__ + '.CreatePort')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--bridge',
            help='Bridge Name')
        parser.add_argument(
            '--vxlan_vni',
            help='Neutron Port Id')
        parser.add_argument(
            '--network_type',
            help='Network Type')
        parser.add_argument(
            '--vxlan_port',
            help='VXLAN UDP Port')
        #parser.add_argument(
        #    '--vlan_id',
        #    help='VLAN Id')
        parser.add_argument(
            '--ip_address',
            help='Ip address')
        parser.add_argument(
            '--flow_type',
            help='Flow Type')
        parser.add_argument(
            '--ovs_port',
            help='OVS Port')
        parser.add_argument(
            '--data_ip',
            help='Data Ip address')
        parser.add_argument(
            '--local_data_ip',
            help='Local Data IP address')
        parser.add_argument(
            '--host',
            help='Compute Node Name')
        parser.add_argument(
            'name', metavar='NAME',
            help='Name of Port to create')

    def args2body(self, parsed_args):
        body = {'nwport':
                {
                    'name': parsed_args.name,
                    'network_type': parsed_args.network_type,
                    'data_ip':parsed_args.data_ip,
                    'bridge':parsed_args.bridge,
                    'vxlan_vni':int(parsed_args.vxlan_vni),
                    'vxlan_port':int(parsed_args.vxlan_port),
                    'ip_address': parsed_args.ip_address,
                    #'vlan_id': int(parsed_args.vlan_id),
                    'flow_type': parsed_args.flow_type,
                    'ovs_port': int(parsed_args.ovs_port),
                    'local_data_ip': parsed_args.local_data_ip,
                    'host': parsed_args.host
                }
            }
        
        return body
