# Copyright: (c) 2020, Timothy Allen (@tallen116)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves.urllib.parse import urlparse  # urlencode
from socket import gethostbyname
import re


class ONMSModule(AnsibleModule):

    AUTH_ARGSPEC = dict(
        onms_host=dict(type='str', required=True),
        onms_username=dict(type='str', required=True),
        onms_password=dict(type='str', required=True, no_log=True),
        validate_certs=dict(type='bool')
    )

    # Define defaults
    host = '127.0.0.1'
    username = None
    password = None
    validate_certs = True

    def __init__(self, argument_spec=None, **kwargs):
        self._debug = True
        full_argspec = {}
        full_argspec.update(ONMSModule.AUTH_ARGSPEC)
        full_argspec.update(argument_spec)

        kwargs['supports_check_mode'] = True

        super(ONMSModule, self).__init__(full_argspec, **kwargs)

        self.host = self.params['onms_host']
        self.username = self.params.get('onms_username')
        self.password = self.params.get('onms_password')

        # Validate
        if not re.match('^https?://', self.host):
            self.fail_json(msg="URL Scheme is expecting http or https.")

        try:
            self.url = urlparse(self.host)
        except Exception as e:
            self.fail_json(msg="Unable to parse host as a URL ({1}): {0}".format(self.host, e))

        hostname = self.url.netloc.split(':')[0]
        try:
            self._resolvehost = gethostbyname(hostname)
            self.debug(msg="Host resolved to {}".format(self._resolvehost))
        except Exception as e:
            self.fail_json(msg="Unable to resolve host ({1}): {0}".format(hostname, e))

    def build_url(self, endpoint, query_params=None, version=1):
        """
        Build the URL for the REST calls.
        Base URL is http(s)://opennms:8980/opennms/rest/
        Base V2 URL is http(s)://opennms:8980/opennms/api/v2/
        """
        if not endpoint.startswith("/"):
            endpoint = "/{0}".format(endpoint)
        if version < 1:
            self.fail_json(msg="Invalid API version provided")
        if version > 1:
            endpoint = "/v{1}{0}".format(endpoint, version)
        if not endpoint.startswith("/rest/") and version == 1:
            endpoint = "/rest{0}".format(endpoint)
        if not endpoint.startswith("/api/") and version > 1:
            endpoint = "/api{0}".format(endpoint)
        if not endpoint.startswith("/opennms/"):
            endpoint = "/opennms{0}".format(endpoint)

        url = self.url._replace(path=endpoint)
        return url
