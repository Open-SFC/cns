import wsme
from pecan import request, response
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan
from oslo.config import cfg

from nscs.nscsas.api.resources.base import BaseController, _Base, IP, \
    BoundedStr, EntityNotFound
from nscs.nscsas.api import utils, constants
from oslo_log import log as logging
from oslo_log._i18n import _
from . import model as api_models
from . import db as cns_db

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


class Switch(_Base):
    """
    Representation of Switch Structure
    """
    id = BoundedStr(minlen=36, maxlen=36)
    "The UUID of the switch"

    name = BoundedStr(maxlen=16)
    "The name for the switch"

    fqdn = BoundedStr(maxlen=96)
    "Switch FQDN"

    type = bool
    "Switch Type"

    baddr = bool
    "Binary IP Address"

    ip_address = IP('switch')
    "Switch IP Address"


class SwitchesResp(_Base):
    """
    Representation of Switches list Response
    """
    switches = [Switch]


class SwitchResp(_Base):
    """
    Representation of Switch Response
    """
    switch = Switch


class SwitchController(BaseController):
    ATTRIBUTES = {
        'name': ['name', {'type': 'string', 'key': True, 'mandatory': True}],
        'fqdn': ['fqdn', {'type': 'string', 'mandatory': False}],
        'baddr': ['baddr', {'type': 'boolean', 'mandatory': False}],
        'baddrip': ['ip_address', {'type': 'ipaddr', 'mandatory': False}],
        'type': ['type', {'type': 'boolean', 'mandatory': False}],
    }
    dmpath = 'onswitch'

    def __init__(self):
        self.conn = cns_db.CNSDBMixin()

    @wsme_pecan.wsexpose(SwitchResp, Switch)
    def post(self, switch):
        """
        This function implements create record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the POST request body and adds the record to DB and UCM if all the
        UCM_ATTRIBUTES are present.

        :return: Dictionary of the added record.
        """
        change = switch.as_dict(api_models.Switch)

        switches = list(self.conn.get_switches(name=switch.name))

        if len(switches) > 0:
            error = _("Switch with the given name exists")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        try:
            switch_in = api_models.Switch(**change)
        except Exception:
            LOG.exception("Error while posting Switch: %s" % change)
            error = _("Switch incorrect")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        switch_out = self.conn.create_switch(switch_in)

        #UCM Support Start
        if cfg.CONF.api.ucm_support:
            body = switch_out.as_dict()
            ucm_record = utils.generate_ucm_data(self, body, [])
            if UCM_LOADED:
                try:
                    ret_val = _ucm.add_record(ucm_record)
                    if ret_val != 0:
                        error = _("Unable to add Switch record to UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))
                except UCMException, msg:
                    LOG.info(_("UCM Exception raised. %s\n"), msg)
                    error = _("Unable to add Switch record to UCM")
                    response.translatable_error = error
                    raise wsme.exc.ClientSideError(unicode(error))
        #UCM Support End

        return SwitchResp(**({'switch': Switch.from_db_model(switch_out)}))

    @wsme_pecan.wsexpose(SwitchResp, wtypes.text, Switch)
    def put(self, switch_id, switch):
        """
        This function implements update record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the PUT request body and adds the record to UCM if all the
        UCM_ATTRIBUTES are present.

        :return: Dictionary of the updated record.
        """

        switch.id = switch_id
        switches = list(self.conn.get_switchs(switch_id=switch.id))

        if len(switches) < 1:
            raise EntityNotFound(_('Switch'), switch_id)

        old_switch = Switch.from_db_model(switches[0]).as_dict(api_models.Switch)
        updated_switch = switch.as_dict(api_models.Switch)
        old_switch.update(updated_switch)
        try:
            sw_in = api_models.Switch(**old_switch)
        except Exception:
            LOG.exception("Error while putting switch: %s" % old_switch)
            error = _("Switch incorrect")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        switch_out = self.conn.update_virtualmachine(sw_in)

        #UCM Support Start
        if cfg.CONF.api.ucm_support:
            body = switch_out.as_dict()
            ucm_record = utils.generate_ucm_data(self, body, [])
            if UCM_LOADED:
                try:
                    req = {'name': {'type': constants.DATA_TYPES['string'], 'value': str(switch.name)},
                           'dmpath': constants.PATH_PREFIX + '.' + self.dmpath}
                    try:
                        rec = _ucm.get_exact_record(req)
                        if not rec:
                            error = _("Unable to find Switch record in UCM")
                            response.translatable_error = error
                            raise wsme.exc.ClientSideError(unicode(error))
                    except UCMException, msg:
                        LOG.info(_("UCM Exception raised. %s\n"), msg)
                        error = _("Unable to find Switch record in UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))

                    ret_val = _ucm.update_record(ucm_record)
                    if ret_val != 0:
                        error = _("Unable to add Switch record to UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))
                except UCMException, msg:
                    LOG.info(_("UCM Exception raised. %s\n"), msg)
                    error = _("Unable to Update Switch record to UCM")
                    response.translatable_error = error
                    raise wsme.exc.ClientSideError(unicode(error))
        #UCM Support End

        return SwitchResp(**({'switch': Switch.from_db_model(switch_out)}))

    @wsme_pecan.wsexpose(SwitchesResp, [Switch])
    def get_all(self):
        """Return all Switches, based on the query provided.

        :param q: Filter rules for the Switches to be returned.
        """
        #TODO: Need to handle Query filters
        return SwitchesResp(**({'switches': [Switch.from_db_model(m)
                                             for m in self.conn.get_switches()]}))

    @wsme_pecan.wsexpose(SwitchResp, wtypes.text)
    def get_one(self, switch_id):
        """Return this Switch."""

        switches = list(self.conn.get_switches(switch_id=switch_id))

        if len(switches) < 1:
            switches = list(self.conn.get_switches(name=switch_id))
            if len(switches) < 1:
                raise EntityNotFound(_('Switch'), switch_id)

        return SwitchResp(**({'switch': Switch.from_db_model(switches[0])}))

    @wsme_pecan.wsexpose(None, wtypes.text, status_code=204)
    def delete(self, switch_id):
        """Delete this Switch."""
        # ensure switch exists before deleting

        switches = list(self.conn.get_switches(switch_id=switch_id))

        if len(switches) < 1:
            raise EntityNotFound(_('Switch'), switch_id)

        switch = switches[0]
        #UCM Configuration Start
        record = {'name': {'type': constants.DATA_TYPES['string'], 'value': str(switch.name)},
                  'dmpath': constants.PATH_PREFIX + '.' + self.dmpath}
        try:
            ret_val = _ucm.delete_record(record)
            LOG.debug(_("return value = %s"), str(ret_val))
            if ret_val != 0:
                error = _("Unable to delete Switch record from UCM")
                response.translatable_error = error
                raise wsme.exc.ClientSideError(unicode(error))
        except UCMException, msg:
            LOG.info(_("UCM Exception raised. %s"), msg)
            error = _("Unable to delete Switch record from UCM")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))
        #UCM Configuration End

        self.conn.delete_switch(switch_id)
