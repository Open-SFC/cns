from nscs.nscsas.api.resources.base import BaseController


class AttributeController(BaseController):
    ATTRIBUTES = {
        'name': {'type': 'string', 'mandatory': True, 'key': True},
        'value': {'type': 'string', 'mandatory': True}
    }

    def __init__(self,dmpath):
        self.name = "attribute"
        self.dmpath = dmpath + '{%s}.attribute'
