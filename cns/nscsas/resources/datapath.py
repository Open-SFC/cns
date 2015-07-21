from exceptions import Exception

import wsme
from pecan import response
from wsme import types as wtypes
from oslo_config import cfg
from oslo_log import log as logging
from oslo_log._i18n import _

import wsmeext.pecan as wsme_pecan
from nscs.nscsas.api.resources.base import BaseController, \
        _Base, BoundedStr, EntityNotFound
from . import db as cns_db
from . import model as api_models
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


class Datapath(_Base):
    """
    Representation of Datapath Structure
    """
    id = BoundedStr(maxlen=16)
    "The Datapath ID of a logical switch"

    name = BoundedStr(maxlen=256)
    "Datapath name of logical switch"

    subject = BoundedStr(maxlen=256)
    "The SSL Subject of the logical switch"

    switch = BoundedStr(minlen=36, maxlen=36)
    "Switch UUID"

    switchname = BoundedStr(maxlen=16)
    "Switch Name to which the logical switch belongs"

    domain = BoundedStr(minlen=36, maxlen=36)
    "Domain UUID"

    domainname = BoundedStr(maxlen=16)
    "Domain name to which the logical switch belongs"


class DatapathsResp(_Base):
    """
    Representation of Datapath list Response
    """
    datapaths = [Datapath]


class DatapathResp(_Base):
    """
    Representation of Datapath Response
    """
    datapath = Datapath


#class PortController(BaseController):
#    """
#
#    """
#
#    ATTRIBUTES = {
#        'portname': {'type': 'string', 'key': True, 'mandatory': True},
#        'portid': {'type': 'int', 'mandatory': True},
#    }
#
#    dmpath = 'datapath{%s}.port'
#
#    def __init__(self):
#        self.name = 'port'


class DatapathController(BaseController):
    """
    """

    ATTRIBUTES = {
        'datapathid': ['id', {'type': 'uint64', 'key': True, 'mandatory': True}],
        'onswitch': ['switchname', {'type': 'string', 'mandatory': True}],
        'domain': ['domainname', {'type': 'string', 'mandatory': True}],
        'subjectname': ['subject', {'type': 'string', 'mandatory': True}],
        'datapathname': ['name', {'type': 'string', 'mandatory': True}],
    }
    dmpath = 'datapath'

    def __init__(self):
        self.conn = cns_db.CNSDBMixin()

    @wsme_pecan.wsexpose(DatapathResp, Datapath)
    def post(self, datapath):
        """
        This function implements create record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the POST request body and adds the record to DB and UCM if all the
        UCM_ATTRIBUTES are present.

        :return: Dictionary of the added record.
        """
        change = datapath.as_dict(api_models.Datapath)

        datapaths = list(self.conn.get_datapaths(datapath_id=datapath.id))

        if len(datapaths) > 0:
            error = _("Datapath with the given name exists")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        try:
            datapath_in = api_models.Datapath(**change)
        except Exception:
            LOG.exception("Error while posting Datapath: %s" % change)
            error = _("Datapath incorrect")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        datapath_out = self.conn.create_datapath(datapath_in)

        # UCM Configuration Start
        if cfg.CONF.api.ucm_support:
            body = datapath_out.as_dict()
            ucm_record = utils.generate_ucm_data(self, body, [])
            if UCM_LOADED:
                try:
                    ret_val = _ucm.add_record(ucm_record)
                    if ret_val != 0:
                        error = _("Unable to add datapath record to UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))
                except UCMException, msg:
                    LOG.info(_("UCM Exception raised. %s\n"), msg)
                    error = _("Unable to add datapath record to UCM")
                    response.translatable_error = error
                    raise wsme.exc.ClientSideError(unicode(error))
        # UCM Configuration End

        datapath_out.domainname = wsme.Unset
        datapath_out.switchname = wsme.Unset
        return DatapathResp(**({'datapath': Datapath.from_db_model(datapath_out)}))

    @wsme_pecan.wsexpose(DatapathResp, wtypes.text, Datapath)
    def put(self, datapath_id, datapath):
        """
        This function implements update record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the PUT request body and adds the record to UCM if all the
        UCM_ATTRIBUTES are present.

        :return: Dictionary of the updated record.
        """

        datapath.id = datapath_id
        datapaths = list(self.conn.get_datapaths(datapath_id=datapath.id))

        if len(datapaths) < 1:
            raise EntityNotFound(_('Datapath'), datapath_id)

        old_datapath = Datapath.from_db_model(datapaths[0]).as_dict(api_models.Datapath)
        updated_datapath = datapath.as_dict(api_models.Datapath)
        old_datapath.update(updated_datapath)
        try:
            datapath_in = api_models.Datapath(**old_datapath)
        except Exception:
            LOG.exception("Error while putting datapath: %s" % old_datapath)
            error = _("Datapath incorrect")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        datapath_out = self.conn.update_datapath(datapath_in)

        #UCM Configuration Start
        if cfg.CONF.api.ucm_support:
            body = datapath_out.as_dict()
            ucm_record = utils.generate_ucm_data(self, body, [])
            if UCM_LOADED:
                try:
                    req = {'name': {'type': constants.DATA_TYPES['uint64'], 'value': str(datapath_out.id)},
                           'dmpath': constants.PATH_PREFIX + '.' + self.dmpath}
                    try:
                        rec = _ucm.get_exact_record(req)
                        if not rec:
                            error = _("Unable to find datapath record in UCM")
                            response.translatable_error = error
                            raise wsme.exc.ClientSideError(unicode(error))
                    except UCMException, msg:
                        LOG.info(_("UCM Exception raised. %s\n"), msg)
                        error = _("Unable to find datapath record in UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))

                    ret_val = _ucm.update_record(ucm_record)
                    if ret_val != 0:
                        error = _("Unable to update datapath record to UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))
                except UCMException, msg:
                    LOG.info(_("UCM Exception raised. %s\n"), msg)
                    error = _("Unable to Update datapath record to UCM")
                    response.translatable_error = error
                    raise wsme.exc.ClientSideError(unicode(error))
        #UCM Configuration End

        return DatapathResp(**({'datapath': Datapath.from_db_model(datapath_out)}))

    @wsme_pecan.wsexpose(DatapathsResp, [Datapath])
    def get_all(self):
        """Return all Datapaths, based on the query provided.

        :param q: Filter rules for the datapaths to be returned.
        """
        #TODO: Need to handle Query filters
        return DatapathsResp(**({'datapaths': [Datapath.from_db_model(m)
                                               for m in self.conn.get_datapaths()]}))

    @wsme_pecan.wsexpose(DatapathResp, wtypes.text)
    def get_one(self, datapath_id):
        """Return this datapath."""

        datapaths = list(self.conn.get_datapaths(datapath_id=datapath_id))

        if len(datapaths) < 1:
            raise EntityNotFound(_('Datapath'), datapath_id)

        return DatapathResp(**({'datapath': Datapath.from_db_model(datapaths[0])}))

    @wsme_pecan.wsexpose(None, wtypes.text, status_code=204)
    def delete(self, datapath_id):
        """Delete this datapath."""
        # ensure datapath exists before deleting

        datapaths = list(self.conn.get_datapaths(datapath_id=datapath_id))

        if len(datapaths) < 1:
            raise EntityNotFound(_('Datapath'), datapath_id)

        #UCM Configuration Start
        record = {'datapathid': {'type': constants.DATA_TYPES['uint64'], 'value': str(datapath_id)},
                  'dmpath': constants.PATH_PREFIX + '.' + self.dmpath}
        try:
            ret_val = _ucm.delete_record(record)
            LOG.debug(_("return value = %s"), str(ret_val))
            if ret_val != 0:
                error = _("Unable to delete datapath record from UCM")
                response.translatable_error = error
                raise wsme.exc.ClientSideError(unicode(error))
        except UCMException, msg:
            LOG.info(_("UCM Exception raised. %s"), msg)
            error = _("Unable to delete datapath record from UCM")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))
        #UCM Configuration End
        self.conn.delete_datapath(datapath_id)
