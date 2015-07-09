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


"""
Views for managing Openflow Clusters.
"""
import logging
from django.core.urlresolvers import reverse_lazy, reverse
from django.utils.translation import ugettext_lazy as _

from openstack_dashboard import api
from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon import workflows
from .forms import CreateCluster, UpdateCluster, CreateController, CreateSwitch
from .tables import ClustersTable, OpenflowControllersTable, OpenflowSwitchTable

LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = ClustersTable
    template_name = 'admin/ofclusters/index.html'

    def get_data(self):
        try:
            clusters = api.ofcontroller.of_cluster_list(self.request)

        except:
            clusters = []
            msg = _('Openflow Cluster list can not be retrieved.')
            exceptions.handle(self.request, msg)
        for n in clusters:
            n.set_id_as_name_if_empty()
        return clusters
    
class CreateClusterView(forms.ModalFormView):
    form_class = CreateCluster
    template_name = 'admin/ofclusters/create.html'
    success_url = reverse_lazy('horizon:admin:ofclusters:index')
    
class UpdateClusterView(forms.ModalFormView):
    form_class = UpdateCluster
    template_name = 'admin/ofclusters/update.html'
    success_url = reverse_lazy("horizon:admin:ofclusters:index")

    def get_context_data(self, **kwargs):
        context = super(UpdateClusterView, self).get_context_data(**kwargs)
        cluster = self._get_object()
        context["cluster_id"] = self.kwargs['cluster_id']
        context["name"] = cluster['name']
        return context

    def _get_object(self, *args, **kwargs):
        if not hasattr(self, "_object"):
            cluster_id = self.kwargs['cluster_id']
            try:
                self._object = api.ofcontroller.of_cluster_get(self.request,
                                                       cluster_id)
            except:
                redirect = self.success_url
                msg = _('Unable to retrieve cluster details.')
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object
    
    def get_initial(self):
        cluster = self._get_object()
        return {'cluster_id': cluster['id'],
                'name': cluster['name']}
        
class DetailClusterView(tables.DataTableView):
    table_class = OpenflowControllersTable
    template_name = 'admin/ofclusters/detail.html'
    failure_url = reverse_lazy('horizon:admin:ofclusters:index')
    
    def get_data(self):
        try:
            cluster = self._get_data()
            ofcontrollers = api.ofcontroller.of_controller_list(self.request,
                                                    id=cluster.id)
        except:
            ofcontrollers = []
            msg = _('Openflow Controller list can not be retrieved.')
            exceptions.handle(self.request, msg)
        for s in ofcontrollers:
            s.set_id_as_name_if_empty()
        return ofcontrollers

    def _get_data(self):
        if not hasattr(self, "_cluster"):
            try:
                cluster_id = self.kwargs['cluster_id']
                cluster = api.ofcontroller.of_cluster_get(self.request, cluster_id)
                cluster.set_id_as_name_if_empty(length=0)
            except:
                msg = _('Unable to retrieve details for cluster "%s".') \
                      % (cluster_id)
                exceptions.handle(self.request, msg, redirect=self.failure_url)
            self._cluster = cluster
        return self._cluster

    def get_context_data(self, **kwargs):
        context = super(DetailClusterView, self).get_context_data(**kwargs)
        context["cluster"] = self._get_data()
        return context
    
class DetailSwitchView(tables.DataTableView):
    table_class = OpenflowSwitchTable
    template_name = 'admin/ofclusters/switch.html'
    failure_url = reverse_lazy('horizon:admin:ofclusters:switches')
    
    def get_data(self):
        try:
            cluster = self._get_cluster_data()
            controller = self._get_controller_data()
            logical_switches = api.ofcontroller.of_switches_list(self.request,
                                                    cluster.id,
                                                    controller.id)
        except:
            logical_switches = []
            msg = _('Openflow Logical Switches list can not be retrieved.')
            exceptions.handle(self.request, msg)
        for s in logical_switches:
            s.set_id_as_name_if_empty()
        return logical_switches

    def _get_cluster_data(self):
        if not hasattr(self, "_cluster"):
            try:
                cluster_id = self.kwargs['cluster_id']
                cluster = api.ofcontroller.of_cluster_get(self.request, cluster_id)
                cluster.set_id_as_name_if_empty(length=0)
            except:
                msg = _('Unable to retrieve details for cluster "%s".') \
                      % (cluster_id)
                exceptions.handle(self.request, msg, redirect=self.failure_url)
            self._cluster = cluster
        return self._cluster
    
    def _get_controller_data(self):
        if not hasattr(self, "_controller"):
            try:
                cluster_id = self.kwargs['cluster_id']
                controller_id = self.kwargs['controller_id']
                controller = api.ofcontroller.of_controller_get(self.request, controller_id, cluster_id)
                controller.set_id_as_name_if_empty(length=0)
            except:
                msg = _('Unable to retrieve details for Openflow Controller "%s".') \
                      % (controller_id)
                exceptions.handle(self.request, msg, redirect=self.failure_url)
            self._controller = controller
        return self._controller

    def get_context_data(self, **kwargs):
        context = super(DetailSwitchView, self).get_context_data(**kwargs)
        context["cluster"] = self._get_cluster_data()
        context["controller"] = self._get_controller_data()
        return context
    
class CreateControllerView(forms.ModalFormView):
    form_class = CreateController
    template_name = 'admin/ofclusters/createofc.html'
    success_url = 'horizon:admin:ofclusters:detail'
    
    def get_success_url(self):
        return reverse(self.success_url,
                       args=(self.kwargs['cluster_id'],))
    
    def get_object(self):
        if not hasattr(self, "_object"):
            try:
                cluster_id = self.kwargs["cluster_id"]
                self._object = api.ofcontroller.of_cluster_get(self.request,
                                                       cluster_id)
            except:
                redirect = reverse('horizon:project:ofclusters:index')
                msg = _("Unable to retrieve Cluster Details.")
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(CreateControllerView, self).get_context_data(**kwargs)
        context['cluster'] = self.get_object()
        return context

    def get_initial(self):
        cluster = self.get_object()
        return {"cluster_id": self.kwargs['cluster_id'],}

class CreateSwitchView(forms.ModalFormView):
    form_class = CreateSwitch
    template_name = 'admin/ofclusters/createswitch.html'
    success_url = 'horizon:admin:ofclusters:switches'
    
    def get_success_url(self):
        return reverse(self.success_url,
                       args=(self.kwargs['cluster_id'], self.kwargs['controller_id']))
    
    def get_cluster_object(self):
        if not hasattr(self, "_object"):
            try:
                cluster_id = self.kwargs["cluster_id"]
                self._object = api.ofcontroller.of_cluster_get(self.request,
                                                       cluster_id)
            except:
                redirect = reverse('horizon:project:ofclusters:index')
                msg = _("Unable to retrieve Cluster Details.")
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object
    
    def get_controller_object(self):
        if not hasattr(self, "_cobject"):
            try:
                cluster_id = self.kwargs["cluster_id"]
                controller_id = self.kwargs["controller_id"]
                self._cobject = api.ofcontroller.of_controller_get(self.request,
                                                       controller_id, cluster_id)
            except:
                redirect = reverse('horizon:admin:ofclusters:detail', args=[self.kwargs["cluster_id"]])
                msg = _("Unable to retrieve OF Controller Details.")
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._cobject
    
    def get_context_data(self, **kwargs):
        context = super(CreateSwitchView, self).get_context_data(**kwargs)
        context['cluster'] = self.get_cluster_object()
        context['controller'] = self.get_controller_object()
        return context
    
    def get_initial(self):
        cluster = self.get_cluster_object()
        controller = self.get_controller_object()
        return {"cluster_id": self.kwargs['cluster_id'],
                "controller_id": self.kwargs['controller_id'],}
    