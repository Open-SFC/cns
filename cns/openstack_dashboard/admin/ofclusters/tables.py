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

from django import template
from django.core.urlresolvers import reverse
from django.template import defaultfilters as filters
from django.utils.translation import ugettext_lazy as _

from openstack_dashboard import api
from horizon import exceptions
from horizon import tables

LOG = logging.getLogger(__name__)

class CheckClusterEditable(object):
    """Mixin class to determine the specified cluster is editable."""

    def allowed(self, request, datum=None):
        return True

class CreateCluster(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Cluster")
    url = "horizon:admin:ofclusters:create"
    classes = ("ajax-modal", "btn-create")
    
class DeleteCluster(CheckClusterEditable, tables.DeleteAction):
    data_type_singular = _("Cluster")
    data_type_plural = _("Clusters")

    def delete(self, request, cluster_id):
        try:
            api.ofcontroller.of_cluster_delete(request, cluster_id)
            LOG.debug('Deleted cluster %s successfully' % cluster_id)
        except:
            msg = _('Failed to delete cluster %s') % cluster_id
            LOG.info(msg)
            redirect = reverse("horizon:admin:ofclusters:index")
            exceptions.handle(request, msg, redirect=redirect)
            
class EditCluster(CheckClusterEditable, tables.LinkAction):
    name = "update"
    verbose_name = _("Edit Cluster")
    url = "horizon:admin:ofclusters:update"
    classes = ("ajax-modal", "btn-edit")

class CreateController(tables.LinkAction):
    name = "createofc"
    verbose_name = _("Create Controller")
    url = "horizon:admin:ofclusters:createofc"
    classes = ("ajax-modal", "btn-create")
    
    def get_link_url(self, datum=None):
        if datum:
            cluster_id = datum.id    
        else:
            cluster_id = self.table.kwargs['cluster_id']
        return reverse(self.url, args=(cluster_id,))
    
class DeleteController(tables.DeleteAction):
    data_type_singular = _("Controller")
    data_type_plural = _("Controllers")

    def delete(self, request, controller_id):
        try:
            cluster_id = self.table.kwargs['cluster_id']
            api.ofcontroller.of_controller_delete(request, cluster_id, controller_id)
            LOG.debug('Deleted Controller %s successfully' % controller_id)
        except:
            msg = _('Failed to Delete Controller %s') % controller_id
            LOG.info(msg)
            cluster_id = self.table.kwargs['cluster_id']
            redirect = reverse('horizon:admin:ofclusters:detail',
                               args=[cluster_id])
            exceptions.handle(request, msg, redirect=redirect)
            
class CreateOpenflowSwitch(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Switch")
    url = "horizon:admin:ofclusters:createswitch"
    classes = ("ajax-modal", "btn-create")
    
    def get_link_url(self, datum=None):
        cluster_id = self.table.kwargs['cluster_id']
        if datum:
            controller_id = datum.id
        else:
            controller_id = self.table.kwargs['controller_id']
            
        return reverse(self.url, args=(cluster_id, controller_id))
    
class DeleteOpenflowSwitch(tables.DeleteAction):
    data_type_singular = _("Switch")
    data_type_plural = _("Switches")

    def delete(self, request, switch_id):
        try:
            cluster_id = self.table.kwargs['cluster_id']
            controller_id = self.table.kwargs['controller_id']
            api.ofcontroller.of_switch_delete(request, cluster_id, controller_id, switch_id)
            LOG.debug('Deleted Switch %s successfully' % switch_id)
        except:
            msg = _('Failed to Delete Switch %s') % switch_id
            LOG.info(msg)
            cluster_id = self.table.kwargs['cluster_id']
            controller_id = self.table.kwargs['controller_id']
            redirect = reverse('horizon:admin:ofclusters:switches',
                               args=[cluster_id, controller_id])
            exceptions.handle(request, msg, redirect=redirect)
            
class ShowSwitch(tables.LinkAction):
    name = "switches"
    verbose_name = _("Switch Details")
    url = "horizon:admin:ofclusters:switches"
    classes = ("btn-edit", )

    def get_link_url(self, ofcontroller):
        cluster_id = self.table.kwargs['cluster_id']
        return reverse(self.url, args=(cluster_id, ofcontroller.id))
    
class ClustersTable(tables.DataTable):
    name = tables.Column("name",
                         verbose_name=_("Name"),
                         link='horizon:admin:ofclusters:detail')
    created_at = tables.Column("created_at", verbose_name=_("Created At"))
    
    class Meta:
        name = "ofclusters"
        verbose_name = _("Openflow Clusters")
        table_actions = (CreateCluster, DeleteCluster)
        row_actions = (EditCluster, CreateController, DeleteCluster)

class OpenflowControllersTable(tables.DataTable):
    name = tables.Column("name",
                         verbose_name=_("Name"))
    ip_address = tables.Column("ip_address", verbose_name=_("IP Address"))
    port = tables.Column("port", verbose_name=_("Port"))
    cell = tables.Column("cell", verbose_name=_("Cell"))
    created_at = tables.Column("created_at", verbose_name=_("Created At"))
    
    class Meta:
        name = "ofcontrollers"
        verbose_name = _("Openflow Controllers")
        table_actions = (CreateController, DeleteController)
        row_actions = (ShowSwitch, CreateOpenflowSwitch, DeleteController)

class OpenflowSwitchTable(tables.DataTable):
    name = tables.Column("name",
                         verbose_name=_("Name"))
    datapath_id = tables.Column("datapath_id", verbose_name=_("Datapath ID"))
    ip_address = tables.Column("ip_address", verbose_name=_("IP Address"))
    port = tables.Column("port", verbose_name=_("Port"))
    created_at = tables.Column("created_at", verbose_name=_("Created At"))
    
    class Meta:
        name = "ofswitches"
        verbose_name = _("Openflow Logical Switches")
        table_actions = (CreateOpenflowSwitch, DeleteOpenflowSwitch)
        row_actions = (DeleteOpenflowSwitch, )
