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

from nscs.crdclient.common import utils

class CNSCommands():
    """"""
    
    COMMANDS = {
        # Cluster Management 
        'list-clusters': utils.import_class(
            'cns.crdclient.crd.v2_0.ofcluster.ListOpenflowCluster'),
        'create-cluster' : utils.import_class(
            'cns.crdclient.crd.v2_0.ofcluster.CreateOpenflowCluster'),
        'update-cluster' : utils.import_class(
            'cns.crdclient.crd.v2_0.ofcluster.UpdateOpenflowCluster'),
        'delete-cluster' : utils.import_class(
            'cns.crdclient.crd.v2_0.ofcluster.DeleteOpenflowCluster'),
        'show-cluster' : utils.import_class(
            'cns.crdclient.crd.v2_0.ofcluster.ShowOpenflowCluster'),
        
        # Controller Management 
        'list-controllers': utils.import_class(
            'cns.crdclient.crd.v2_0.ofcontroller.ListOpenflowController'),
        'create-controller' : utils.import_class(
            'cns.crdclient.crd.v2_0.ofcontroller.CreateOpenflowController'),
        'update-controller' : utils.import_class(
            'cns.crdclient.crd.v2_0.ofcontroller.UpdateOpenflowController'),
        'delete-controller' : utils.import_class(
            'cns.crdclient.crd.v2_0.ofcontroller.DeleteOpenflowController'),
        'show-controller' : utils.import_class(
            'cns.crdclient.crd.v2_0.ofcontroller.ShowOpenflowController'),
        # Switch Management 
        'list-switchs': utils.import_class(
            'cns.crdclient.crd.v2_0.ofswitch.ListOpenflowSwitch'),
        'create-switch' : utils.import_class(
            'cns.crdclient.crd.v2_0.ofswitch.CreateOpenflowSwitch'),
        'update-switch' : utils.import_class(
            'cns.crdclient.crd.v2_0.ofswitch.UpdateOpenflowSwitch'),
        'delete-switch' : utils.import_class(
            'cns.crdclient.crd.v2_0.ofswitch.DeleteOpenflowSwitch'),
        'show-switch' : utils.import_class(
            'cns.crdclient.crd.v2_0.ofswitch.ShowOpenflowSwitch'),
        
        'list-network': utils.import_class(
            'cns.crdclient.crd.v2_0.network.ListNetwork'),
        'create-network' : utils.import_class(
            'cns.crdclient.crd.v2_0.network.CreateNetwork'),
        'update-network' : utils.import_class(
            'cns.crdclient.crd.v2_0.network.UpdateNetwork'),
        'delete-network' : utils.import_class(
            'cns.crdclient.crd.v2_0.network.DeleteNetwork'),
        'show-network' : utils.import_class(
            'cns.crdclient.crd.v2_0.network.ShowNetwork'),
    
        'list-subnet': utils.import_class(
            'cns.crdclient.crd.v2_0.subnet.ListSubnet'),
        'create-subnet' : utils.import_class(
            'cns.crdclient.crd.v2_0.subnet.CreateSubnet'),
        'update-subnet' : utils.import_class(
            'cns.crdclient.crd.v2_0.subnet.UpdateSubnet'),
        'delete-subnet' : utils.import_class(
            'cns.crdclient.crd.v2_0.subnet.DeleteSubnet'),
        'show-subnet' : utils.import_class(
            'cns.crdclient.crd.v2_0.subnet.ShowSubnet'),
        
        'list-port': utils.import_class(
            'cns.crdclient.crd.v2_0.port.ListPort'),
        'create-port' : utils.import_class(
            'cns.crdclient.crd.v2_0.port.CreatePort'),
        'update-port' : utils.import_class(
            'cns.crdclient.crd.v2_0.port.UpdatePort'),
        'delete-port' : utils.import_class(
            'cns.crdclient.crd.v2_0.port.DeletePort'),
        'show-port' : utils.import_class(
            'cns.crdclient.crd.v2_0.port.ShowPort'),
    
        'list-compute': utils.import_class(
            'cns.crdclient.crd.v2_0.compute.ListCompute'),
        'create-compute' : utils.import_class(
            'cns.crdclient.crd.v2_0.compute.CreateCompute'),
        'update-compute' : utils.import_class(
            'cns.crdclient.crd.v2_0.compute.UpdateCompute'),
        'delete-compute' : utils.import_class(
            'cns.crdclient.crd.v2_0.compute.DeleteCompute'),
        'show-compute' : utils.import_class(
            'cns.crdclient.crd.v2_0.compute.ShowCompute'),
    
    
        'list-instance': utils.import_class(
            'cns.crdclient.crd.v2_0.instance.ListInstance'),
        'create-instance' : utils.import_class(
            'cns.crdclient.crd.v2_0.instance.CreateInstance'),
        'update-instance' : utils.import_class(
            'cns.crdclient.crd.v2_0.instance.UpdateInstance'),
        'delete-instance' : utils.import_class(
            'cns.crdclient.crd.v2_0.instance.DeleteInstance'),
        'show-instance' : utils.import_class(
            'cns.crdclient.crd.v2_0.instance.ShowInstance'),
    }