from nscs.nscsas.api.resources.base import BaseController
from pecan import request, expose, abort

import re


class ViewController(BaseController):
    ATTRIBUTES = {
        'attrib_name': {'type': 'string', 'mandatory': True, 'key': True}
    }

    #TODO: Need to fix the dmpath
    def __init__(self, dmpath):
        self.name = "view"
        self.dmpath = re.subn(r'\{\%s\}', '', dmpath)[0] + '.view'

    @expose('json')
    def get_one(self, *args):
        abort(404)

    @expose('json')
    def get_all(self):
        abort(404)

    @expose('json')
    def put(self, *args):
        abort(404)

    @expose('json')
    def post(self):
        abort(404)
