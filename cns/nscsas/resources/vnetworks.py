import uuid
import wsme
from pecan import request, response
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan
from oslo_config import cfg

from nscs.nscsas.api.resources.base import BaseController, _Base, AdvEnum, \
    BoundedStr, BoundedInt, EntityNotFound, CIDR, IP, validate_ip
from oslo_log import log as logging
from oslo_log._i18n import _
from . import model as api_models
from . import db as cns_db
from .views import ViewController
from .attributes import AttributeController
from nscs.nscsas.api import utils, constants
from nscs.nscsas.utils import decode_cidr

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


class Pool(_Base):
    """
    Allocation Pool Data Type
    """
    id = BoundedStr(minlen=36, maxlen=36)
    "UUID for pool"

    start = IP('start', mandatory=True)
    "Start IP Address"

    end = IP('end', mandatory=True)
    "End IP Address"

    subnet_id = BoundedStr(minlen=36, maxlen=36)
    "Subnet UUID"


class Subnet(_Base):
    """
    Representation of Subnet Structure
    """
    id = BoundedStr(minlen=36, maxlen=36)
    "The UUID of the subnet"

    name = BoundedStr(minlen=16, maxlen=128)
    "The name for the subnet"

    nw_id = BoundedStr(minlen=36, maxlen=36)
    "The UUID of the Virtual Network"

    vnname = BoundedStr(minlen=16, maxlen=128)
    "Virtual Network Name"

    dhcp = bool
    "Enable DHCP for this subnet."

    ip_version = AdvEnum("ip_version", str, '4', '6')
    "The IP version of the subnet. Allowed values are 4 / 6."

    cidr = CIDR('cidr')
    "Subnet CIDR address"

    gateway_ip = IP('gw_ip')
    "Gateway IP Address"

    pools = [Pool]
    "IP Address Pools"

    dns_servers = [wtypes.text]
    "DNS Servers"

    host_routes = BoundedStr(maxlen=255)
    "Host Routes"


class SubnetsResp(_Base):
    """
    Representation of Virtual Networks list Response
    """
    subnets = [Subnet]


class SubnetResp(_Base):
    """
    Representation of Virtual Network Response
    """
    subnet = Subnet


class SubnetController(BaseController):

    ATTRIBUTES = {
        'name':               ['name', {'type': 'string', 'mandatory': True, 'key': True}],
        'vnname':             ['vnname', {'type': 'string', 'mandatory': True}],
        'cidrip':             ['cidr', {'type': 'ipaddr', 'mandatory': True}],
        'cidrmask':           ['cidr', {'type': 'ipaddr', 'mandatory': True}],
        'ip_version':         ['ip_version', {'type': 'uint', 'mandatory': True, 'default': '4'}],
        'pool_start_addr':    ['pools', {'type': 'ipaddr', 'mandatory': False}],
        'pool_end_addr':      ['pools', {'type': 'ipaddr', 'mandatory': False}],
        'gateway':            ['gateway_ip', {'type': 'ipaddr', 'mandatory': False}],
        'enabledhcp':         ['dhcp', {'type': 'boolean', 'mandatory': False, 'default': 'true'}]
    }
    dmpath = 'crm.subnet'
    attributes = AttributeController(dmpath)
    views = ViewController(dmpath)

    def __init__(self):
        self.conn = cns_db.CNSDBMixin()

    @staticmethod
    def pools_from_db_model(pool_list, final=False):
        pools = []
        for pool in pool_list:
            p = Pool.from_db_model(pool)
            if final:
                del p.subnet_id
                del p.id
            pools.append(p)
        return pools

    @wsme_pecan.wsexpose(SubnetResp, wtypes.text, Subnet)
    def post(self, nw_id, subnet):
        """
        This function implements create record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the POST request body and adds the record to UCM if all the
        UCM_ATTRIBUTES are present.

        :return: Dictionary of the added record.
        """
        sn = subnet.as_dict(api_models.Subnet)
        for ip in sn['dns_servers']:
            validate_ip(ip)
        subnets = list(self.conn.get_subnets(sub_id=subnet.id))

        if len(subnets) > 0:
            error = _("Subnet with the given id exists")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        virtualnetworks = list(self.conn.get_virtualnetworks(nw_id=nw_id))

        if len(virtualnetworks) < 1:
            raise EntityNotFound(_('Virtual Network'), nw_id)

        sn['nw_id'] = nw_id

        # Expand Pools and update the details with IDs
        pools = []
        for pool in sn['pools']:
            pool.id = str(uuid.uuid4())
            pool.subnet_id = sn['id']
            pools.append(api_models.Pool(**pool.as_dict(api_models.Pool)))
        sn['pools'] = pools

        try:
            sub_in = api_models.Subnet(**sn)
        except Exception:
            LOG.exception("Error while posting Subnet: %s" % sn)
            error = _("Virtual Network incorrect")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        sub = self.conn.create_subnet(sub_in)
        sub.pools = self.pools_from_db_model(sub.pools, final=True)
        sub.vnname = VirtualNetwork.from_db_model(virtualnetworks[0]).name

        #UCM Configuration Start
        if cfg.CONF.api.ucm_support:
            body = sub.as_dict()
            pools = []
            for pool in body['pools']:
                pools.append(pool.as_dict(api_models.Pool))
            body['pools'] = pools
            ucm_record = utils.generate_ucm_data(self, body, [])
            ucm_record['cidrip']['value'], ucm_record['cidrmask']['value'] = decode_cidr(body['cidr'])

            if len(body['pools']):
                ucm_record['pool_start_addr']['value'] = body['pools'][0]['start']
                ucm_record['pool_end_addr']['value'] = body['pools'][0]['end']
            if len(body['dns_servers']):
                for i in range(0, len(sub.dns_servers)):
                    ucm_record['dns_server'+str(i + 1)] = {'type': constants.DATA_TYPES['ipaddr'],
                                                           'value': sub.dns_servers[i]}

            if UCM_LOADED:
                try:
                    ret_val = _ucm.add_record(ucm_record)
                    if ret_val != 0:
                        error = _("Unable to add Subnet record to UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))
                except UCMException, msg:
                    LOG.info(_("UCM Exception raised. %s\n"), msg)
                    error = _("Unable to add Subnet record to UCM")
                    response.translatable_error = error
                    raise wsme.exc.ClientSideError(unicode(error))
        #UCM Configuration End

        return SubnetResp(**({'subnet': Subnet.from_db_model(sub)}))

    @wsme_pecan.wsexpose(SubnetsResp, wtypes.text, [Subnet])
    def get_all(self, nw_id):
        """Return all virtual networks, based on the query provided.
        """
        #TODO: Need to handle Query filters
        subnets = self.conn.get_subnets(nw_id=nw_id)
        for sub in subnets:
            sub.pools = self.pools_from_db_model(sub.pools, final=True)
        return SubnetsResp(**({'subnets': [Subnet.from_db_model(sub)
                                           for sub in subnets]}))

    @wsme_pecan.wsexpose(SubnetResp, wtypes.text, wtypes.text)
    def get_one(self, nw_id, sub_id):
        """Return this virtual network."""

        subnets = list(self.conn.get_subnets(nw_id=nw_id, sub_id=sub_id))

        if len(subnets) < 1:
            raise EntityNotFound(_('Subnet'), sub_id)
        for sub in subnets:
            sub.pools = self.pools_from_db_model(sub.pools, final=True)

        return SubnetResp(**({'subnet': Subnet.from_db_model(subnets[0])}))

    @wsme_pecan.wsexpose(SubnetResp, wtypes.text, wtypes.text, Subnet)
    def put(self, nw_id, sub_id, subnet):
        """
        This function implements update record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the PUT request body and adds the record to UCM if all the
        UCM_ATTRIBUTES are present.

        :return: Dictionary of the added record.
        """

        virtualnetworks = list(self.conn.get_virtualnetworks(nw_id=nw_id))

        if len(virtualnetworks) < 1:
            raise EntityNotFound(_('Virtual Network'), nw_id)

        sn = subnet.as_dict(api_models.Subnet)
        if 'dns_servers' in sn:
            for ip in sn['dns_servers']:
                try:
                    validate_ip(ip)
                except Exception:
                    LOG.exception("Error while putting subnet: %s" % str(sn))
                    error = _("Subnet incorrect. Invalid DNS Server IP")
                    response.translatable_error = error
                    raise wsme.exc.ClientSideError(unicode(error))

        subnets = list(self.conn.get_subnets(sub_id=sub_id, nw_id=nw_id))

        if len(subnets) < 1:
            raise EntityNotFound(_('Subnet'), sub_id)

        subnets[0].pools = self.pools_from_db_model(subnets[0].pools)
        old_subnet = Subnet.from_db_model(subnets[0]).as_dict(api_models.Subnet)

        old_subnet.update(sn)

        try:
            sub_in = api_models.Subnet(**old_subnet)
        except Exception:
            LOG.exception("Error while putting subnet: %s" % old_subnet)
            error = _("Subnet incorrect")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        sub = self.conn.update_subnet(sub_in)
        sub.pools = self.pools_from_db_model(sub.pools, final=True)
        #UCM Configuration Start
        if cfg.CONF.api.ucm_support:
            body = sub.as_dict()
            pools = []
            for pool in body['pools']:
                pools.append(pool.as_dict(api_models.Pool))
            body['pools'] = pools
            ucm_record = utils.generate_ucm_data(self, body, [])

            del ucm_record['pool_start_addr']
            del ucm_record['pool_end_addr']
            if len(body['dns_servers']):
                for i in range(0, len(sub.dns_servers)):
                    ucm_record['dns_server'+str(i + 1)] = {'type': constants.DATA_TYPES['ipaddr'],
                                                           'value': sub.dns_servers[i]}
            else:
                for i in range(0, 4):
                    ucm_record['dns_server'+str(i + 1)] = {'type': constants.DATA_TYPES['ipaddr'],
                                                           'value': '0.0.0.0'}

            if UCM_LOADED:
                try:
                    req = {'name': {'type': constants.DATA_TYPES['string'], 'value': str(sub.name)},
                           'dmpath': constants.PATH_PREFIX + '.' + self.dmpath}
                    try:
                        rec = _ucm.get_exact_record(req)
                        if not rec:
                            error = _("Unable to find Subnet record in UCM")
                            response.translatable_error = error
                            raise wsme.exc.ClientSideError(unicode(error))
                    except UCMException, msg:
                        LOG.info(_("UCM Exception raised. %s\n"), msg)
                        error = _("Unable to find Subnet record in UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))

                    ret_val = _ucm.update_record(ucm_record)
                    if ret_val != 0:
                        error = _("Unable to add Subnet record to UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))
                except UCMException, msg:
                    LOG.info(_("UCM Exception raised. %s\n"), msg)
                    error = _("Unable to Update Subnet record to UCM")
                    response.translatable_error = error
                    raise wsme.exc.ClientSideError(unicode(error))
        #UCM Configuration End

        return SubnetResp(**({'subnet': Subnet.from_db_model(sub)}))

    @wsme_pecan.wsexpose(None, wtypes.text, wtypes.text, status_code=204)
    def delete(self, nw_id, sub_id):
        """Delete this Subnet."""
        # ensure subnet exists before deleting

        subnets = list(self.conn.get_subnets(nw_id=nw_id, sub_id=sub_id))

        if len(subnets) < 1:
            raise EntityNotFound(_('Subnet'), sub_id)

        #UCM Configuration Start
        record = {'name': {'type': constants.DATA_TYPES['string'], 'value': str(subnets[0].name)},
                  'dmpath': constants.PATH_PREFIX + '.' + self.dmpath}
        try:
            ret_val = _ucm.delete_record(record)
            LOG.debug(_("return value = %s"), str(ret_val))
            if ret_val != 0:
                error = _("Unable to delete Subnet record from UCM")
                response.translatable_error = error
                raise wsme.exc.ClientSideError(unicode(error))
        except UCMException, msg:
            LOG.info(_("UCM Exception raised. %s"), msg)
            error = _("Unable to delete Subnet record from UCM")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))
        #UCM Configuration End

        self.conn.delete_subnet(sub_id)


class VirtualNetwork(_Base):
    """
    Representation of Virtual Network Structure
    """
    id = BoundedStr(minlen=36, maxlen=36)
    "The UUID of the virtual network"

    name = wsme.wsattr(BoundedStr(minlen=16, maxlen=128), mandatory=True)
    "The name for the virtual network"

    status = AdvEnum("status", str, "active", "inactive")
    "The virtual network status. Values allowed are active/inactive"

    state = bool
    "The virtual network admin state. Values allowed are up/down"

    tenant = BoundedStr(minlen=32, maxlen=32)
    "The Tenant UUID to which the Virtual Network belongs"

    type = AdvEnum("nw_type", str, "vlan", "vxlan")
    "Virtual Network Type"

    segmentation_id = int
    "Segmentation ID to use for a specific virtual network. (VLAN ID if VLAN) or (VNI if VXLAN)"

    vxlan_service_port = BoundedInt(min=1, max=65535)
    "VXLAN Service Port."

    external = bool
    "The virtual network is external?"


class VirtualNetworksResp(_Base):
    """
    Representation of Virtual Networks list Response
    """
    virtualnetworks = [VirtualNetwork]


class VirtualNetworkResp(_Base):
    """
    Representation of Virtual Network Response
    """
    virtualnetwork = VirtualNetwork


class VNController(BaseController):
    ATTRIBUTES = {
        'name':               ['name', {'type': 'string', 'mandatory': True, 'key': True}],
        'tenant':             ['tenant', {'type': 'string', 'mandatory': True}],
        'type':               ['type', {'type': 'string', 'mandatory': True}],
        'segmentation_id':    ['segmentation_id', {'type': 'uint', 'mandatory': True}],
        'vxlan_service_port': ['vxlan_service_port', {'type': 'uint', 'mandatory': False, 'default': '4789'}],
        'status':             ['status', {'type': 'boolean', 'mandatory': False, 'default': True}],
        'state':              ['state', {'type': 'boolean', 'mandatory': False, 'default': True}],
        'external':           ['external', {'type': 'boolean', 'mandatory': False, 'default': False}],
    }
    dmpath = 'crm.virtualnetwork'
    attributes = AttributeController(dmpath)
    subnets = SubnetController()
    views = ViewController(dmpath)

    def __init__(self):
        self.conn = cns_db.CNSDBMixin()

    @wsme_pecan.wsexpose(VirtualNetworkResp, VirtualNetwork)
    def post(self, virtualnetwork):
        """
        This function implements create record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the POST request body and adds the record to DB and UCM if all the
        UCM_ATTRIBUTES are present.

        :return: Dictionary of the added record.
        """

        change = virtualnetwork.as_dict(api_models.VirtualNetwork)

        virtualnetworks = list(self.conn.get_virtualnetworks(nw_id=virtualnetwork.id))

        if len(virtualnetworks) > 0:
            error = _("Virtual Network with the given id exists")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        try:
            vn_in = api_models.VirtualNetwork(**change)
        except Exception:
            LOG.exception("Error while posting Virtual Network: %s" % change)
            error = _("Virtual Network incorrect")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        vn_out = self.conn.create_virtualnetwork(vn_in)
        
        # UCM Configuration Start
        if cfg.CONF.api.ucm_support:
            body = vn_out.as_dict()
            if body['type'] == 'vxlan':
                body['type'] = 'VXLAN_TYPE'
            ucm_record = utils.generate_ucm_data(self, body, [])
            if UCM_LOADED:
                try:
                    ret_val = _ucm.add_record(ucm_record)
                    if ret_val != 0:
                        error = _("Unable to add Virtual Network record to UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))
                    else:
                        LOG.debug(_("Virtual Network Added to UCM"))
                except UCMException, msg:
                    LOG.info(_("UCM Exception raised. %s\n"), msg)
                    error = _("Unable to add Virtual Network record to UCM")
                    response.translatable_error = error
                    raise wsme.exc.ClientSideError(unicode(error))
        # UCM Configuration End
        
        return VirtualNetworkResp(**({'virtualnetwork': VirtualNetwork.from_db_model(vn_out)}))

    @wsme_pecan.wsexpose(VirtualNetworksResp, [VirtualNetwork])
    def get_all(self):
        """Return all virtual networks, based on the query provided.

        :param q: Filter rules for the virtual networks to be returned.
        """
        #TODO: Need to handle Query filters
        return VirtualNetworksResp(**({'virtualnetworks': [VirtualNetwork.from_db_model(m)
                                                           for m in self.conn.get_virtualnetworks()]}))

    @wsme_pecan.wsexpose(VirtualNetworkResp, wtypes.text)
    def get_one(self, nw_id):
        """Return this virtual network."""

        virtualnetworks = list(self.conn.get_virtualnetworks(nw_id=nw_id))

        if len(virtualnetworks) < 1:
            raise EntityNotFound(_('Virtual Network'), nw_id)

        return VirtualNetworkResp(**({'virtualnetwork': VirtualNetwork.from_db_model(virtualnetworks[0])}))

    @wsme_pecan.wsexpose(VirtualNetworkResp, wtypes.text, VirtualNetwork)
    def put(self, nw_id, virtualnetwork):
        """
        This function implements update record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the PUT request body and adds the record to UCM if all the
        UCM_ATTRIBUTES are present.

        :return: Dictionary of the added record.
        """

        virtualnetwork.id = nw_id
        virtualnetworks = list(self.conn.get_virtualnetworks(nw_id=virtualnetwork.id))

        if len(virtualnetworks) < 1:
            raise EntityNotFound(_('Virtual Network'), nw_id)

        old_vn = VirtualNetwork.from_db_model(virtualnetworks[0]).as_dict(api_models.VirtualNetwork)
        updated_vn = virtualnetwork.as_dict(api_models.VirtualNetwork)
        old_vn.update(updated_vn)
        try:
            vn_in = api_models.VirtualNetwork(**old_vn)
        except Exception:
            LOG.exception("Error while putting virtual network: %s" % old_vn)
            error = _("Virtual Network incorrect")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        vn_out = self.conn.update_virtualnetwork(vn_in)
        
        #UCM Configuration Start
        if cfg.CONF.api.ucm_support:
            body = vn_out.as_dict()
            ucm_record = utils.generate_ucm_data(self, body, [])
            if UCM_LOADED:
                try:
                    req = {'name': {'type': constants.DATA_TYPES['string'], 'value': str(vn_out.name)},
                           'dmpath': constants.PATH_PREFIX + '.' + self.dmpath}
                    try:
                        rec = _ucm.get_exact_record(req)
                        if not rec:
                            error = _("Unable to find Virtual Network record in UCM")
                            response.translatable_error = error
                            raise wsme.exc.ClientSideError(unicode(error))
                    except UCMException, msg:
                        LOG.info(_("UCM Exception raised. %s\n"), msg)
                        error = _("Unable to find Virtual Network record in UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))

                    ret_val = _ucm.update_record(ucm_record)
                    if ret_val != 0:
                        error = _("Unable to add Virtual Network record to UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))
                except UCMException, msg:
                    LOG.info(_("UCM Exception raised. %s\n"), msg)
                    error = _("Unable to Update Virtual Network record to UCM")
                    response.translatable_error = error
                    raise wsme.exc.ClientSideError(unicode(error))
        #UCM Configuration End
        
        return VirtualNetworkResp(**({'virtualnetwork': VirtualNetwork.from_db_model(vn_out)}))

    @wsme_pecan.wsexpose(None, wtypes.text, status_code=204)
    def delete(self, nw_id):
        """Delete this Virtual Network."""
        # ensure virtual network exists before deleting

        virtualnetworks = list(self.conn.get_virtualnetworks(nw_id=nw_id))

        if len(virtualnetworks) < 1:
            raise EntityNotFound(_('Virtual Network'), nw_id)

        #UCM Configuration Start
        record = {'name': {'type': constants.DATA_TYPES['string'], 'value': str(virtualnetworks[0].name)},
                  'dmpath': constants.PATH_PREFIX + '.' + self.dmpath}
        try:
            ret_val = _ucm.delete_record(record)
            LOG.debug(_("return value = %s"), str(ret_val))
            if ret_val != 0:
                error = _("Unable to delete Virtual Network record from UCM")
                response.translatable_error = error
                raise wsme.exc.ClientSideError(unicode(error))
        except UCMException, msg:
            LOG.info(_("UCM Exception raised. %s"), msg)
            error = _("Unable to delete Virtual Network record from UCM")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))
        #UCM Configuration End

        self.conn.delete_virtualnetwork(nw_id)
