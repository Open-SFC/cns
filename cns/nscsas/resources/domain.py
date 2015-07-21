import wsme
from pecan import response
from wsme import types as wtypes
from oslo_config import cfg
from oslo_log import log as logging
from oslo_log._i18n import _

import wsmeext.pecan as wsme_pecan
from nscs.nscsas.api.resources.base import BaseController, _Base,  \
    BoundedStr, EntityNotFound
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


class Domain(_Base):
    """
    Representation of Domain Structure
    """
    id = BoundedStr(minlen=36, maxlen=36)
    "The UUID of the domain"

    name = BoundedStr(maxlen=16)
    "The name for the domain"

    ttp_name = BoundedStr(maxlen=64, minlen=8)
    "The Table Type name for the domain"

    subject = BoundedStr(maxlen=256)
    "The Subject name of this domain"


class DomainsResp(_Base):
    """
    Representation of Domains list Response
    """
    domains = [Domain]


class DomainResp(_Base):
    """
    Representation of Domain Response
    """
    domain = Domain


class DomainController(BaseController):
    ATTRIBUTES = {
        'name': ['name', {'type': 'string', 'key': True, 'mandatory': True}],
        'ttp_name': ['ttp_name', {'type': 'string', 'mandatory': True}],
        'subjectname': ['subject', {'type': 'string', 'mandatory': True}],
    }
    dmpath = 'domain'

    def __init__(self):
        self.conn = cns_db.CNSDBMixin()

    @wsme_pecan.wsexpose(DomainResp, Domain)
    def post(self, domain):
        """
        This function implements create record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the POST request body and adds the record to DB and UCM if all the
        UCM_ATTRIBUTES are present.

        :return: Dictionary of the added record.
        """
        change = domain.as_dict(api_models.Domain)
        change['ttp_name'] = 'DATA_CENTER_VIRTUAL_SWITCH_TTP'

        domains = list(self.conn.get_domains(name=domain.name))

        if len(domains) > 0:
            error = _("Domain with the given name exists")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        try:
            domain_in = api_models.Domain(**change)
        except Exception:
            LOG.exception("Error while posting Domain: %s" % change)
            error = _("Domain incorrect")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        domain_out = self.conn.create_domain(domain_in)

        #UCM Support Start
        #if cfg.CONF.api.ucm_support:
        #    body = domain_out.as_dict()
        #    ucm_record = utils.generate_ucm_data(self, body, [])
        #    if UCM_LOADED:
        #        try:
        #            ret_val = _ucm.add_record(ucm_record)
        #            if ret_val != 0:
        #                error = _("Unable to add Domain record to UCM")
        #                response.translatable_error = error
        #                raise wsme.exc.ClientSideError(unicode(error))
        #        except UCMException, msg:
        #            LOG.info(_("UCM Exception raised. %s\n"), msg)
        #            error = _("Unable to add Domain record to UCM")
        #            response.translatable_error = error
        #            raise wsme.exc.ClientSideError(unicode(error))
        #UCM Support End

        return DomainResp(**({'domain': Domain.from_db_model(domain_out)}))

    @wsme_pecan.wsexpose(DomainResp, wtypes.text, Domain)
    def put(self, domain_id, domain):
        """
        This function implements update record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the PUT request body and adds the record to UCM if all the
        UCM_ATTRIBUTES are present.

        :return: Dictionary of the updated record.
        """

        domain.id = domain_id
        domains = list(self.conn.get_domains(domain_id=domain.id))

        if len(domains) < 1:
            raise EntityNotFound(_('Domain'), domain_id)

        old_domain = Domain.from_db_model(domains[0]).as_dict(api_models.Domain)
        updated_domain = domain.as_dict(api_models.Domain)
        old_domain.update(updated_domain)
        try:
            dom_in = api_models.Domain(**old_domain)
        except Exception:
            LOG.exception("Error while putting domain: %s" % old_domain)
            error = _("Domain incorrect")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        dom = self.conn.update_virtualmachine(dom_in)

        #UCM Support Start
        if cfg.CONF.api.ucm_support:
            body = dom.as_dict()
            ucm_record = utils.generate_ucm_data(self, body, [])
            if UCM_LOADED:
                try:
                    req = {'name': {'type': constants.DATA_TYPES['string'], 'value': str(dom.name)},
                           'dmpath': constants.PATH_PREFIX + '.' + self.dmpath}
                    try:
                        rec = _ucm.get_exact_record(req)
                        if not rec:
                            error = _("Unable to find Domain record in UCM")
                            response.translatable_error = error
                            raise wsme.exc.ClientSideError(unicode(error))
                    except UCMException, msg:
                        LOG.info(_("UCM Exception raised. %s\n"), msg)
                        error = _("Unable to find Domain record in UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))

                    ret_val = _ucm.update_record(ucm_record)
                    if ret_val != 0:
                        error = _("Unable to add Domain record to UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))
                except UCMException, msg:
                    LOG.info(_("UCM Exception raised. %s\n"), msg)
                    error = _("Unable to Update Domain record to UCM")
                    response.translatable_error = error
                    raise wsme.exc.ClientSideError(unicode(error))
        #UCM Support End

        return DomainResp(**({'domain': Domain.from_db_model(dom)}))

    @wsme_pecan.wsexpose(DomainsResp, [Domain])
    def get_all(self):
        """Return all Domains, based on the query provided.

        :param q: Filter rules for the domains to be returned.
        """
        #TODO: Need to handle Query filters
        return DomainsResp(**({'domains': [Domain.from_db_model(m)
                                           for m in self.conn.get_domains()]}))

    @wsme_pecan.wsexpose(DomainResp, wtypes.text)
    def get_one(self, domain_id):
        """Return this domain."""

        domains = list(self.conn.get_domains(domain_id=domain_id))

        if len(domains) < 1:
            domains = list(self.conn.get_domains(name=domain_id))
            if len(domains) < 1:
                raise EntityNotFound(_('Domain'), domain_id)

        return DomainResp(**({'domain': Domain.from_db_model(domains[0])}))

    @wsme_pecan.wsexpose(None, wtypes.text, status_code=204)
    def delete(self, domain_id):
        """Delete this domain."""
        # ensure port exists before deleting

        domains = list(self.conn.get_domains(domain_id=domain_id))

        if len(domains) < 1:
            raise EntityNotFound(_('Domain'), domain_id)

        domain = domains[0]
        #UCM Configuration Start
        record = {'name': {'type': constants.DATA_TYPES['string'], 'value': str(domain.name)},
                  'dmpath': constants.PATH_PREFIX + '.' + self.dmpath}
        try:
            ret_val = _ucm.delete_record(record)
            LOG.debug(_("return value = %s"), str(ret_val))
            if ret_val != 0:
                error = _("Unable to delete Domain record from UCM")
                response.translatable_error = error
                raise wsme.exc.ClientSideError(unicode(error))
        except UCMException, msg:
            LOG.info(_("UCM Exception raised. %s"), msg)
            error = _("Unable to delete Domain record from UCM")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))
        #UCM Configuration End

        self.conn.delete_domain(domain_id)
