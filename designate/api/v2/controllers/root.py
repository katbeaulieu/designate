# Copyright 2013 Hewlett-Packard Development Company, L.P.
#
# Author: Kiall Mac Innes <kiall@hp.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
from oslo.config import cfg
from stevedore import named

from designate import exceptions
from designate.openstack.common import log as logging
from designate.api.v2.controllers import limits
from designate.api.v2.controllers import reverse
from designate.api.v2.controllers import schemas
from designate.api.v2.controllers import tlds
from designate.api.v2.controllers import zones
from designate.api.v2.controllers import blacklists

from pecan import expose

LOG = logging.getLogger(__name__)


class RootController(object):
    """
    This is /v2/ Controller. Pecan will find all controllers via the object
    properties attached to this.
    """

    def __init__(self):
        enabled_ext = cfg.CONF['service:api'].enabled_extensions_v2
        if len(enabled_ext) > 0:
            self._mgr = named.NamedExtensionManager(
                namespace='designate.api.v2.extensions',
                names=enabled_ext,
                invoke_on_load=True)
            for ext in self._mgr:
                controller = self
                path = ext.obj.get_path()
                for p in path.split('.')[:-1]:
                    if p != '':
                        controller = getattr(controller, p)
                setattr(controller, path.split('.')[-1], ext.obj)

    limits = limits.LimitsController()
    schemas = schemas.SchemasController()
    reverse = reverse.ReverseController()
    tlds = tlds.TldsController()
    zones = zones.ZonesController()
    blacklists = blacklists.BlacklistsController()

    @expose(content_type='text/plain')
    @expose(content_type='text/dns')
    @expose(content_type='application/json')
    def not_found(self):
        raise exceptions.NotFound

    @expose(content_type='text/plain')
    @expose(content_type='text/dns')
    @expose(content_type='application/json')
    def method_not_allowed(self):
        raise exceptions.MethodNotAllowed
