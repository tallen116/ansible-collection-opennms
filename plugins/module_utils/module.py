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
        host=dict(type='str', required=True),
        username=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
        validate_certs=dict(type='bool')
    )

    host = '127.0.0.1'
    username = None
    password = None
    validate_certs = True

    def __init__(self, argument_spec=None, **kwargs):
        full_argspec = {}
        full_argspec.update(ONMSModule.AUTH_ARGSPEC)
        full_argspec.update(argument_spec)

        kwargs['supports_check_mode'] = True

        super(ONMSModule, self).__init__(full_argspec, **kwargs)

        self.host = self.params['host']

        if not re.match('^https?://', self.host):
            self.fail_json(msg="URL Scheme is expecting http or https.")

        # Basic validation
        # Validate url structure
        try:
            self.url = urlparse(self.host)
        except Exception as e:
            self.fail_json(msg="Unable to parse host as a URL ({1}): {0}".format(self.host, e))

        hostname = self.url.netloc.split(':')[0]
        try:
            gethostbyname(hostname)
        except Exception as e:
            self.fail_json(msg="Unable to resolve host ({1}): {0}".format(hostname, e))

    def build_url(self, interface, query_params=None):
        """
        Build the URL for the REST calls.
        Base URL is http(s)://opennms:8980/opennms/rest/
        """
        pass
