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


import logging

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from openstack_dashboard import api
from horizon import exceptions
from horizon import forms
from horizon import messages

import tempfile
import shutil

FILE_UPLOAD_DIR = '/tmp/'
LOG = logging.getLogger(__name__)

class CreateCluster(forms.SelfHandlingForm):
    name = forms.CharField(label=_("Name"), required=True)
    ca_cert_pem = forms.FileField(label=_("CA Certificate"),
                                 help_text=("CA Certificate."),
                                 required=True)
    private_key_pem = forms.FileField(label=_("Private Key"),
                                 help_text=("Private Key."),
                                 required=True)
    root_cert_pem = forms.FileField(label=_("Root Certificate"),
                                 help_text=("Root Certificate."),
                                 required=True)
    inter_cert_pem = forms.FileField(label=_("Intermediate Certificate"),
                                 help_text=("Intermediate Certificate."),
                                 required=True)
    def handle(self, request, data):
        try:
            ##Upload CA Certificate
            ca_path = self.handle_uploaded_file(self.files['ca_cert_pem'])
            
            ##Upload Private Key
            private_key_path = self.handle_uploaded_file(self.files['private_key_pem'])
            
            ##Upload Root Certificate
            root_cert_path = self.handle_uploaded_file(self.files['root_cert_pem'])
            
            ##Upload Intermediate Certificate
            inter_cert_path = self.handle_uploaded_file(self.files['inter_cert_pem'])

            cluster = api.ofcontroller.of_cluster_create(request,
                                            name=data['name'],
                                            ca_cert_path=ca_path,
                                            private_key_path=private_key_path,
                                            root_cert_path=root_cert_path,
                                            inter_cert_path=inter_cert_path)
            
            messages.success(request,
                             _('Successfully created Cluster: %s')
                               % data['name'])
            return cluster
        except:
            redirect = reverse("horizon:admin:ofclusters:index")
            exceptions.handle(request,
                              _('Unable to create Cluster.'),
                              redirect=redirect)
            
    def handle_uploaded_file(self, source):
        #fd, filepath = tempfile.mkstemp(prefix="", dir=FILE_UPLOAD_DIR)
        filepath = FILE_UPLOAD_DIR + str(source)
        with open(filepath, 'wb') as dest:
            shutil.copyfileobj(source, dest)
        return filepath
    
class UpdateCluster(forms.SelfHandlingForm):
    name = forms.CharField(label=_("Name"))
    cluster_id = forms.CharField(label=_("ID"),
                                 widget=forms.TextInput(
                                     attrs={'readonly': 'readonly'}))
    failure_url = 'horizon:admin:ofclusters:index'

    def handle(self, request, data):
        try:
            cluster = api.ofcontroller.of_cluster_modify(request, data['cluster_id'],
                                                 name=data['name'])
            msg = _('Cluster %s was successfully updated.') % data['name']
            LOG.debug(msg)
            messages.success(request, msg)
            return cluster
        except:
            msg = _('Failed to update cluster %s') % data['name']
            LOG.info(msg)
            redirect = reverse(self.failure_url)
            exceptions.handle(request, msg, redirect=redirect)
            
class CreateController(forms.SelfHandlingForm):
    cluster_id = forms.CharField(label=_("Cluster ID"),
                                 widget=forms.TextInput(
                                     attrs={'readonly': 'readonly'}))
    name = forms.CharField(label=_("Name"), required=True)
    ip_address = forms.CharField(label=_("IP Address"), required=True)
    port = forms.CharField(label=_("Port"), required=True)
    cell = forms.CharField(label=_("Cell"), required=True)
    failure_url = 'horizon:admin:ofclusters:detail'
        
    def handle(self, request, data):
        try:
            controller = api.ofcontroller.of_controller_create(request,
                                            name=data['name'],
                                            cluster_id=data['cluster_id'],
                                            ip_address=data['ip_address'],
                                            port=data['port'],
                                            cell=data['cell'])
            
            messages.success(request,
                             _('Successfully created Controller: %s')
                               % data['name'])
            return controller
        except Exception as e:
            msg = _('Unable to create Controller: %s') % e.message
            LOG.info(msg)
            messages.error(request, msg)
            redirect = reverse(self.failure_url,
                               args=[data['cluster_id']])
            exceptions.handle(request, msg, redirect=redirect)
            return
        
class CreateSwitch(forms.SelfHandlingForm):
    cluster_id = forms.CharField(label=_("Cluster ID"),
                                 widget=forms.TextInput(
                                     attrs={'readonly': 'readonly'}))
    controller_id = forms.CharField(label=_("Controller ID"),
                                 widget=forms.TextInput(
                                     attrs={'readonly': 'readonly'}))
    name = forms.CharField(label=_("Name"), required=True)
    ip_address = forms.CharField(label=_("IP Address"), required=True)
    port = forms.CharField(label=_("Port"), required=True)
    #datapath_id = forms.CharField(label=_("Datapath ID"), required=True)
    failure_url = 'horizon:admin:ofclusters:switches'
        
    def handle(self, request, data):
        try:
            switch = api.ofcontroller.of_switch_create(request,
                                            name=data['name'],
                                            cluster_id=data['cluster_id'],
                                            controller_id=data['controller_id'],
                                            ip_address=data['ip_address'],
                                            port=data['port'])
            
            messages.success(request,
                             _('Successfully created Logical Switch: %s')
                               % data['name'])
            return switch
        except Exception as e:
            msg = _('Unable to create Logical Switch: %s') % e.message
            LOG.info(msg)
            messages.error(request, msg)
            redirect = reverse(self.failure_url,
                               args=[data['cluster_id'], data['controller_id']])
            exceptions.handle(request, msg, redirect=redirect)
            return