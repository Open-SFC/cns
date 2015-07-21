import copy

import wsme
from pecan import request, response
from wsme import types as wtypes
from oslo_config import cfg
from oslo_log import log as logging
from oslo_log._i18n import _
from oslo_utils import uuidutils

import wsmeext.pecan as wsme_pecan
from nscs.nscsas.api.resources.base import BaseController, _Base, \
    BoundedStr, EntityNotFound, IP
from . import model as api_models
from . import db as cns_db
from .views import ViewController
from .attributes import AttributeController
from nscs.nscsas.api import utils, constants


LOG = logging.getLogger(__name__)

#UCM Support Start
UCM_LOADED = False
if cfg.CONF.api.ucm_support:
    try:
        import _ucm
        from _ucm import UCMException
        UCM_LOADED = True
    except ImportError:
        LOG.info(_("Unable to Load UCM"))
#UCM Support End


class Port(_Base):
    """
    Representation of Virtual Machine Ports Structure
    """
    id = BoundedStr(minlen=36, maxlen=36)
    "The UUID of the virtual machine"

    name = BoundedStr(maxlen=128)
    "The name for the virtual machine"

    tenant = BoundedStr(minlen=32, maxlen=32)
    "The Tenant UUID to which the Virtual machine belongs"

    state = bool
    "Port state."

    bridge = wtypes.text
    "Bridge name to which this port is attached"

    mac_address = wtypes.text
    "Port Mac Address"

    ip_address = IP('port')
    "Port IP Address"

    status = wtypes.text
    "Port status"

    device_owner = wtypes.text
    "device owner id"

    security_groups = [BoundedStr(minlen=36, maxlen=36)]
    "Security group UUID"

    subnet_id = BoundedStr(minlen=36, maxlen=36)
    "Subnet UUID"

    nw_id = BoundedStr(minlen=36, maxlen=36)
    "Network UUID"

    device_id = BoundedStr(minlen=36, maxlen=255)
    "Virtual Machine UUID"

    type = wtypes.text
    "Port Type"

    datapath = BoundedStr(maxlen=16)
    "The Datapath ID of a logical switch to which this port is connected"


class PortsResp(_Base):
    """
    Representation of Virtual Machine Ports list Response
    """
    ports = [Port]


class PortResp(_Base):
    """
    Representation of Virtual machine Port Response
    """
    port = Port


class PortController(BaseController):
    ATTRIBUTES = {
        'portname':          ['name', {'type': 'string', 'mandatory': True, 'key': True}],
        'porttype':          ['type', {'type': 'string', 'mandatory': True}],
        'vmname':            ['instance', {'type': 'string', 'mandatory': True}],
        'bridgename':        ['bridge', {'type': 'string', 'mandatory': True}],
        'vmportmacaddr':     ['mac_address', {'type': 'string', 'mandatory': True}],
    }
    dmpath = 'crm.virtualnetwork{%s}.computenodes{%s}.vmsideports'
    attributes = AttributeController(dmpath)
    views = ViewController(dmpath)

    def __init__(self):
        self.conn = cns_db.CNSDBMixin()

    @wsme_pecan.wsexpose(PortResp, Port)
    def post(self, port):
        """
        This function implements create record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the POST request body and adds the record to DB and UCM if all the
        UCM_ATTRIBUTES are present.

        :return: Dictionary of the added record.
        """

        change = port.as_dict(api_models.Port)
        change['type'] = 'DHCP_PORT'
        vm = list(self.conn.get_virtualmachines(vm_id=port.device_id))
        if len(vm) > 0:
            vm = vm[0]
            if vm.type == 'VM_TYPE_NETWORK_SERVICE':
                change['type'] = 'VMNS_PORT'
            elif vm.type == 'VM_TYPE_NORMAL_APPLICATION':
                change['type'] = 'VMSIDE_PORT'

        ports = list(self.conn.get_ports(port_id=port.id))

        if len(ports) > 0:
            error = _("Port with the given id exists")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        try:
            port_in = api_models.Port(**change)
        except Exception:
            LOG.exception("Error while posting Port: %s" % change)
            error = _("Port incorrect")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        port_out = self.conn.create_port(port_in)

        # UCM Configuration Start
        if len(port_out.device_id) == 36:
            vn = list(self.conn.get_virtualnetworks(nw_id=port.nw_id))[0]

            if cfg.CONF.api.ucm_support:
                body = port_out.as_dict()
                body['instance'] = vm.name
                ucm_record = utils.generate_ucm_data(self, body, (vn.name, vm.host))
                if UCM_LOADED:
                    try:
                        req = {'computenodename': {'type': constants.DATA_TYPES['string'], 'value': str(vm.host)},
                               'bridgename': {'type': constants.DATA_TYPES['string'], 'value': str(port_out.bridge)},
                               'dmpath': str(constants.PATH_PREFIX + '.' +
                                             'crm.virtualnetwork{' + vn.name + '}.computenodes')}
                        try:
                            comp_req = copy.deepcopy(req)
                            rec = _ucm.get_exact_record(comp_req)
                            if not rec:
                                ret_val = _ucm.add_record(req)
                                if ret_val != 0:
                                    error = _("Unable to add compute nodes record to UCM")
                                    response.translatable_error = error
                                    raise wsme.exc.ClientSideError(unicode(error))
                        except UCMException, msg:
                            LOG.info(_("UCM Exception raised. %s\n"), msg)
                            error = _("Unable to add compute nodes record in UCM")
                            response.translatable_error = error
                            raise wsme.exc.ClientSideError(unicode(error))

                        ret_val = _ucm.add_record(ucm_record)
                        if ret_val != 0:
                            error = _("Unable to add ports record to UCM")
                            response.translatable_error = error
                            raise wsme.exc.ClientSideError(unicode(error))
                    except UCMException, msg:
                        LOG.info(_("UCM Exception raised. %s\n"), msg)
                        error = _("Unable to add ports record to UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))
        # UCM Configuration End

        return PortResp(**({'port': Port.from_db_model(port_out)}))

    @wsme_pecan.wsexpose(PortResp, wtypes.text, Port)
    def put(self, port_id, port):
        """
        This function implements update record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the PUT request body and adds the record to UCM if all the
        UCM_ATTRIBUTES are present.

        :return: Dictionary of the added record.
        """

        port.id = port_id
        ports = list(self.conn.get_ports(port_id=port.id))

        if len(ports) < 1:
            raise EntityNotFound(_('Port'), port_id)

        old_port = Port.from_db_model(ports[0]).as_dict(api_models.Port)
        updated_port = port.as_dict(api_models.Port)
        old_port.update(updated_port)
        try:
            port_in = api_models.Port(**old_port)
        except Exception:
            LOG.exception("Error while putting Port: %s" % old_port)
            error = _("Port incorrect")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        port_out = self.conn.update_port(port_in)
        return PortResp(**({'port': Port.from_db_model(port_out)}))

    @wsme_pecan.wsexpose(PortsResp, [Port])
    def get_all(self):
        """Return all virtual machines, based on the query provided.

        :param q: Filter rules for the virtual ports to be returned.
        """
        #TODO: Need to handle Query filters
        return PortsResp(**({'ports': [Port.from_db_model(m)
                                       for m in self.conn.get_ports()]}))

    @wsme_pecan.wsexpose(PortResp, wtypes.text)
    def get_one(self, port_id):
        """Return this virtual port."""

        ports = list(self.conn.get_ports(port_id=port_id))

        if len(ports) < 1:
            raise EntityNotFound(_('Port'), port_id)

        return PortResp(**({'port': Port.from_db_model(ports[0])}))

    @wsme_pecan.wsexpose(None, wtypes.text, status_code=204)
    def delete(self, port_id):
        """Delete this Port."""
        # ensure port exists before deleting

        ports = list(self.conn.get_ports(port_id=port_id))

        if len(ports) < 1:
            raise EntityNotFound(_('Port'), port_id)

        #UCM Configuration Start
        port = ports[0]
        if len(port.device_id) == 36:
            vm = list(self.conn.get_virtualmachines(vm_id=port.device_id))[0]

            vn = list(self.conn.get_virtualnetworks(nw_id=port.nw_id))[0]

            if cfg.CONF.api.ucm_support:
                body = port.as_dict()
                body['instance'] = vm.name
                ucm_record = utils.generate_ucm_data(self, body, (vn.name, vm.host))
                if UCM_LOADED:
                    try:
                        ret_val = _ucm.delete_record(ucm_record)
                        if ret_val != 0:
                            error = _("Unable to delete port record to UCM")
                            response.translatable_error = error
                            raise wsme.exc.ClientSideError(unicode(error))
                    except UCMException, msg:
                        LOG.info(_("UCM Exception raised. %s\n"), msg)
                        error = _("Unable to delete port record to UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))
        #UCM Configuration End

        self.conn.delete_port(port_id)


class NWPort(_Base):
    """
    Representation of Network Side Ports Structure
    """
    id = BoundedStr(minlen=36, maxlen=36)
    "The UUID of the Network Side Port"

    name = BoundedStr(maxlen=128)
    "The name for the Network Side Port"

    network_type = BoundedStr(maxlen=50)
    "Network Type"

    data_ip = BoundedStr(maxlen=50)
    "Data IP Address."

    bridge = BoundedStr(maxlen=50)
    "Bridge Name"

    vxlan_vni = int
    "Segmentation ID"

    ip_address = BoundedStr(maxlen=50)
    "Port IP Address"

    vxlan_port = int
    "VXLAN Port"

    #vlan_id = int
    #"VLAN ID"

    flow_type = BoundedStr(maxlen=50)
    "Flow Type"

    ovs_port = int
    "OVS Port"

    local_data_ip = BoundedStr(maxlen=50)
    "Local Data IP Address"

    host = BoundedStr(maxlen=255)
    "Compute Node name in which the network side port is created"


class NWPortsResp(_Base):
    """
    Representation of Network Side Ports list Response
    """
    nwports = [NWPort]


class NWPortResp(_Base):
    """
    Representation of Network Side Port Response
    """
    nwport = NWPort


class NWPortController(BaseController):
    ATTRIBUTES = {
        'portname':  ['name', {'type': 'string', 'mandatory': True, 'key': True}],
        'nwtype':  ['network_type', {'type': 'string', 'mandatory': True}],
        'switchname':  ['host', {'type': 'string', 'mandatory': True}],
        'bridgename':  ['bridge', {'type': 'string', 'mandatory': True}],
        'vxlan_vni':  ['vxlan_vni', {'type': 'uint', 'mandatory': True}],
        'vxlan_serviceport':  ['vxlan_port', {'type': 'uint', 'mandatory': True}],
        'remoteip':  ['data_ip', {'type': 'ipaddr', 'mandatory': True}],
    }
    dmpath = 'crm.nwsideports'
    attributes = AttributeController(dmpath)
    views = ViewController(dmpath)

    def __init__(self):
        self.conn = cns_db.CNSDBMixin()

    @wsme_pecan.wsexpose(NWPortResp, NWPort)
    def post(self, nwport):
        """
        This function implements create record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the POST request body and adds the record to DB and UCM if all the
        UCM_ATTRIBUTES are present.

        :return: Dictionary of the added record.
        """

        change = nwport.as_dict(api_models.NWPort)
        change['id'] = uuidutils.generate_uuid()
        
        ports = list(self.conn.get_nwports(nwport_id=change['id']))

        if len(ports) > 0:
            error = _("NWPort with the given id exists")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        try:
            port_in = api_models.NWPort(**change)
        except Exception:
            LOG.exception("Error while posting NWPort: %s" % change)
            error = _("NWPort incorrect")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        port_out = self.conn.create_nwport(port_in)
        # UCM Configuration Start
        if cfg.CONF.api.ucm_support:
            body = port_out.as_dict()
            if body['network_type'] == 'vxlan':
              body['network_type'] = 'VXLAN_TYPE'
            ucm_record = utils.generate_ucm_data(self, body, [])
            if UCM_LOADED:
                try:
                    ret_val = _ucm.add_record(ucm_record)
                    if ret_val != 0:
                        error = _("Unable to add nwside port record to UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))
                except UCMException, msg:
                    LOG.info(_("UCM Exception raised. %s\n"), msg)
                    error = _("Unable to add nwside port record to UCM")
                    response.translatable_error = error
                    raise wsme.exc.ClientSideError(unicode(error))
        # UCM Configuration End

        return NWPortResp(**({'nwport': NWPort.from_db_model(port_out)}))

    @wsme_pecan.wsexpose(NWPortResp, wtypes.text, NWPort)
    def put(self, port_id, nwport):
        """
        This function implements update record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the PUT request body and adds the record to UCM if all the
        UCM_ATTRIBUTES are present.

        :return: Dictionary of the added record.
        """

        nwport.id = port_id
        ports = list(self.conn.get_nwports(nwport_id=nwport.id))

        if len(ports) < 1:
            raise EntityNotFound(_('NWPort'), port_id)

        old_port = NWPort.from_db_model(ports[0]).as_dict(api_models.NWPort)
        updated_port = nwport.as_dict(api_models.NWPort)
        old_port.update(updated_port)
        try:
            port_in = api_models.NWPort(**old_port)
        except Exception:
            LOG.exception("Error while putting NWPort: %s" % old_port)
            error = _("NWPort incorrect")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        port_out = self.conn.update_nwport(port_in)

        #UCM Configuration Start
        if cfg.CONF.api.ucm_support:
            body = port_out.as_dict()
            ucm_record = utils.generate_ucm_data(self, body, [])
            if UCM_LOADED:
                try:
                    req = {'portName': {'type': constants.DATA_TYPES['string'], 'value': str(port_out.name)},
                           'dmpath': constants.PATH_PREFIX + '.' + self.dmpath}
                    try:
                        rec = _ucm.get_exact_record(req)
                        if not rec:
                            error = _("Unable to find nwside port record in UCM")
                            response.translatable_error = error
                            raise wsme.exc.ClientSideError(unicode(error))
                    except UCMException, msg:
                        LOG.info(_("UCM Exception raised. %s\n"), msg)
                        error = _("Unable to find nwside port record in UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))

                    ret_val = _ucm.update_record(ucm_record)
                    if ret_val != 0:
                        error = _("Unable to update nwside port record to UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))
                except UCMException, msg:
                    LOG.info(_("UCM Exception raised. %s\n"), msg)
                    error = _("Unable to Update nwside port record to UCM")
                    response.translatable_error = error
                    raise wsme.exc.ClientSideError(unicode(error))
        #UCM Configuration End

        return NWPortResp(**({'nwport': NWPort.from_db_model(port_out)}))

    @wsme_pecan.wsexpose(NWPortsResp, [NWPort])
    def get_all(self):
        """Return all virtual machines, based on the query provided.

        :param q: Filter rules for the virtual ports to be returned.
        """
        #TODO: Need to handle Query filters
        return NWPortsResp(**({'nwports': [NWPort.from_db_model(m)
                                           for m in self.conn.get_nwports()]}))

    @wsme_pecan.wsexpose(NWPortResp, wtypes.text)
    def get_one(self, port_id):
        """Return this virtual nwport."""

        ports = list(self.conn.get_nwports(nwport_id=port_id))

        if len(ports) < 1:
            raise EntityNotFound(_('Network Side Port'), port_id)

        return NWPortResp(**({'nwport': NWPort.from_db_model(ports[0])}))

    @wsme_pecan.wsexpose(None, wtypes.text, status_code=204)
    def delete(self, port_id):
        """Delete this Port."""
        # ensure nwport exists before deleting

        ports = list(self.conn.get_nwports(nwport_id=port_id))

        if len(ports) < 1:
            raise EntityNotFound(_('Network Side Port'), port_id)

        #UCM Configuration Start
        record = {'portName': {'type': constants.DATA_TYPES['string'], 'value': str(ports[0].name)},
                  'dmpath': constants.PATH_PREFIX + '.' + self.dmpath}
        try:
            ret_val = _ucm.delete_record(record)
            LOG.debug(_("return value = %s"), str(ret_val))
            if ret_val != 0:
                error = _("Unable to delete nwside port record from UCM")
                response.translatable_error = error
                raise wsme.exc.ClientSideError(unicode(error))
        except UCMException, msg:
            LOG.info(_("UCM Exception raised. %s"), msg)
            error = _("Unable to delete nwside port record from UCM")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))
        #UCM Configuration End

        self.conn.delete_nwport(port_id)
