# Copyright 2013 Freescale Semiconductor, Inc.
# All rights reserved.
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

from nscs.crd_consumer.client.common import utils

class CNSCommands():
    """"""
    
    COMMANDS = {
        ###Networks
        'list-networks': utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.network.ListNetwork'),
        'create-network' : utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.network.CreateNetwork'),
        'delete-network' : utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.network.DeleteNetwork'),
        'show-network' : utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.network.ShowNetwork'),
        'update-network' : utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.network.UpdateNetwork'),
    
        ###Subnets
        'list-subnets': utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.subnet.ListSubnet'),
        'create-subnet' : utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.subnet.CreateSubnet'),
        'update-subnet' : utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.subnet.UpdateSubnet'),
        'delete-subnet' : utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.subnet.DeleteSubnet'),
        'show-subnet' : utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.subnet.ShowSubnet'),
    
        ###Ports
        'list-ports': utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.port.ListPort'),
        'create-port' : utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.port.CreatePort'),
        'update-port' : utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.port.UpdatePort'),
        'delete-port' : utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.port.DeletePort'),
        'show-port' : utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.port.ShowPort'),
        
        ###Instances
        'list-instances': utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.instance.ListInstance'),
        'create-instance' : utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.instance.CreateInstance'),
        'update-instance' : utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.instance.UpdateInstance'),
        'delete-instance' : utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.instance.DeleteInstance'),
        'show-instance' : utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.instance.ShowInstance'),
    
        ###Domains
        'list-domains': utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.domain.ListDomain'),
        'create-domain' : utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.domain.CreateDomain'),
        'update-domain' : utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.domain.UpdateDomain'),
        'delete-domain' : utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.domain.DeleteDomain'),
        'show-domain' : utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.domain.ShowDomain'),
    
        ###Switches
        'list-switches': utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.switch.ListSwitch'),
        'create-switch' : utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.switch.CreateSwitch'),
        'update-switch' : utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.switch.UpdateSwitch'),
        'delete-switch' : utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.switch.DeleteSwitch'),
        'show-switch' : utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.switch.ShowSwitch'),
        
        ###Datapaths
        'list-datapaths': utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.datapath.ListDatapath'),
        'create-datapath' : utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.datapath.CreateDatapath'),
        'update-datapath' : utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.datapath.UpdateDatapath'),
        'delete-datapath' : utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.datapath.DeleteDatapath'),
        'show-datapath' : utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.datapath.ShowDatapath'),
    
        ###Network side Ports
        'list-nwports': utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.nwport.ListPort'),
        'create-nwport' : utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.nwport.CreatePort'),
        'update-nwport' : utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.nwport.UpdatePort'),
        'delete-nwport' : utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.nwport.DeletePort'),
        'show-nwport' : utils.import_class(
            'cns.crdconsumer.client.sdnofcfg.v1.cns.nwport.ShowPort'),
    }