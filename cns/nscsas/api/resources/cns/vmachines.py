import datetime

import wsme
from pecan import request, response
from wsme import types as wtypes
from oslo.config import cfg
from nscs.ocas_utils.openstack.common import log as logging
from nscs.ocas_utils.openstack.common.gettextutils import _

import wsmeext.pecan as wsme_pecan
from nscs.nscsas.api.resources.base import BaseController, _Base, BoundedStr, EntityNotFound
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


class VirtualMachine(_Base):
    """
    Representation of Virtual Machine Structure
    """
    id = BoundedStr(minlen=36, maxlen=36)
    "The UUID of the virtual machine"

    name = BoundedStr(maxlen=128)
    "The name for the virtual machine"

    #state = AdvEnum("state", str, "active", "inactive")
    state = BoundedStr(maxlen=255)
    "The virtual machine state."

    state_description = BoundedStr(maxlen=255)
    "Virtual machine state description"

    tenant = BoundedStr(minlen=32, maxlen=32)
    "The Tenant UUID to which the Virtual machine belongs"

    created_at = datetime.datetime
    "Virtual Machine Created time"

    launched_at = datetime.datetime
    "Virtual Machine launched time"

    host = BoundedStr(maxlen=255)
    "Compute Node name in which the virtual machine is brought up"

    user_id = BoundedStr(minlen=32, maxlen=32)
    "virtual machine creator User ID"

    reservation_id = BoundedStr(maxlen=50)
    "Reservation ID of virtual machine"

    type = BoundedStr(maxlen=50)
    "Virtual Machine Type"


class VirtualMachinesResp(_Base):
    """
    Representation of Virtual Machines list Response
    """
    virtualmachines = [VirtualMachine]


class VirtualMachineResp(_Base):
    """
    Representation of Virtual Network Response
    """
    virtualmachine = VirtualMachine


class VMController(BaseController):
    ATTRIBUTES = {
        'name':   ['name', {'type': 'string', 'mandatory': True, 'key': True}],
        'tenant': ['tenant', {'type': 'string', 'mandatory': True}],
        'type': ['type', {'type': 'string', 'mandatory': True}],
        'switch': ['host', {'type': 'string', 'mandatory': True}],
    }
    dmpath = 'crm.virtualmachine'
    attributes = AttributeController(dmpath)
    views = ViewController(dmpath)

    def __init__(self):
        self.conn = cns_db.CNSDBMixin()

    @wsme_pecan.wsexpose(VirtualMachineResp, VirtualMachine)
    def post(self, virtualmachine):
        """
        This function implements create record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the POST request body and adds the record to DB and UCM if all the
        UCM_ATTRIBUTES are present.

        :return: Dictionary of the added record.
        """

        change = virtualmachine.as_dict(api_models.VirtualMachine)

        virtualmachines = list(self.conn.get_virtualmachines(vm_id=virtualmachine.id))

        if len(virtualmachines) > 0:
            error = _("Virtual Machine with the given id exists")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        try:
            vm_in = api_models.VirtualMachine(**change)
        except Exception:
            LOG.exception("Error while posting Virtual Machine: %s" % change)
            error = _("Virtual Machine incorrect")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        vm_out = self.conn.create_virtualmachine(vm_in)

        # UCM Configuration Start
        if cfg.CONF.api.ucm_support:
            body = vm_out.as_dict()
            ucm_record = utils.generate_ucm_data(self, body, [])
            if UCM_LOADED:
                try:
                    ret_val = _ucm.add_record(ucm_record)
                    if ret_val != 0:
                        error = _("Unable to add virtual machine record to UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))
                except UCMException, msg:
                    LOG.info(_("UCM Exception raised. %s\n"), msg)
                    error = _("Unable to add virtual machine record to UCM")
                    response.translatable_error = error
                    raise wsme.exc.ClientSideError(unicode(error))
        # UCM Configuration End

        return VirtualMachineResp(**({'virtualmachine': VirtualMachine.from_db_model(vm_out)}))

    @wsme_pecan.wsexpose(VirtualMachinesResp, [VirtualMachine])
    def get_all(self):
        """Return all virtual machines, based on the query provided.

        :param q: Filter rules for the virtual machines to be returned.
        """
        #TODO: Need to handle Query filters
        return VirtualMachinesResp(**({'virtualmachines': [VirtualMachine.from_db_model(m)
                                                           for m in self.conn.get_virtualmachines()]}))

    @wsme_pecan.wsexpose(VirtualMachineResp, wtypes.text)
    def get_one(self, vm_id):
        """Return this virtual machine."""

        virtualmachines = list(self.conn.get_virtualmachines(vm_id=vm_id))

        if len(virtualmachines) < 1:
            raise EntityNotFound(_('Virtual Machine'), vm_id)

        return VirtualMachineResp(**({'virtualmachine': VirtualMachine.from_db_model(virtualmachines[0])}))

    @wsme_pecan.wsexpose(VirtualMachineResp, wtypes.text, VirtualMachine)
    def put(self, vm_id, virtualmachine):
        """
        This function implements update record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the PUT request body and adds the record to UCM if all the
        UCM_ATTRIBUTES are present.

        :return: Dictionary of the added record.
        """

        virtualmachine.id = vm_id
        virtualmachines = list(self.conn.get_virtualmachines(vm_id=virtualmachine.id))

        if len(virtualmachines) < 1:
            raise EntityNotFound(_('Virtual Machine'), vm_id)

        old_vm = VirtualMachine.from_db_model(virtualmachines[0]).as_dict(api_models.VirtualMachine)
        updated_vm = virtualmachine.as_dict(api_models.VirtualMachine)
        old_vm.update(updated_vm)
        try:
            vm_in = api_models.VirtualMachine(**old_vm)
        except Exception:
            LOG.exception("Error while putting virtual machine: %s" % old_vm)
            error = _("Virtual Machine incorrect")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        vm_out = self.conn.update_virtualmachine(vm_in)

        #UCM Support Start
        if cfg.CONF.api.ucm_support:
            body = vm_out.as_dict()
            ucm_record = utils.generate_ucm_data(self, body, [])
            if UCM_LOADED:
                try:
                    req = {'name': {'type': constants.DATA_TYPES['string'], 'value': str(vm_out.name)},
                           'dmpath': constants.PATH_PREFIX + '.' + self.dmpath}
                    try:
                        rec = _ucm.get_exact_record(req)
                        if not rec:
                            error = _("Unable to find virtual machine record in UCM")
                            response.translatable_error = error
                            raise wsme.exc.ClientSideError(unicode(error))
                    except UCMException, msg:
                        LOG.info(_("UCM Exception raised. %s\n"), msg)
                        error = _("Unable to find virtual machine record in UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))

                    ret_val = _ucm.update_record(ucm_record)
                    if ret_val != 0:
                        error = _("Unable to add virtual machine record to UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))
                except UCMException, msg:
                    LOG.info(_("UCM Exception raised. %s\n"), msg)
                    error = _("Unable to Update virtual machine record to UCM")
                    response.translatable_error = error
                    raise wsme.exc.ClientSideError(unicode(error))
        #UCM Support End

        return VirtualMachineResp(**({'virtualmachine': VirtualMachine.from_db_model(vm_out)}))

    @wsme_pecan.wsexpose(None, wtypes.text, status_code=204)
    def delete(self, vm_id):
        """Delete this Virtual Machine."""
        # ensure virtual machine exists before deleting

        virtualmachines = list(self.conn.get_virtualmachines(vm_id=vm_id))

        if len(virtualmachines) < 1:
            raise EntityNotFound(_('Virtual Machine'), vm_id)

        self.conn.delete_virtualmachine(vm_id)
        vm = virtualmachines[0]

        #UCM Configuration Start
        record = {'name': {'type': constants.DATA_TYPES['string'], 'value': str(vm.name)},
                  'dmpath': constants.PATH_PREFIX + '.' + self.dmpath}
        try:
            ret_val = _ucm.delete_record(record)
            LOG.debug(_("return value = %s"), str(ret_val))
            if ret_val != 0:
                error = _("Unable to delete virtual machine record from UCM")
                response.translatable_error = error
                raise wsme.exc.ClientSideError(unicode(error))
        except UCMException, msg:
            LOG.info(_("UCM Exception raised. %s"), msg)
            error = _("Unable to delete virtual machine record from UCM")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))
        #UCM Configuration End

