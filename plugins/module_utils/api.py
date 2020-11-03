# Copyright: (c) 2020, Timothy Allen (@tallen116)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from .module import ONMSModule
from ansible.module_utils.urls import Request, SSLValidationError, ConnectionError
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.six import PY2
import json


class ONMSAPIModule(ONMSModule):

    request = None

    def __init__(self, argument_spec, **kwargs):
        super(ONMSAPIModule, self).__init__(argument_spec=argument_spec, **kwargs)
        self.request = Request()

    def make_request(self, method, endpoint, *args, **kwargs):

        if not method:
            raise Exception("The HTTP method must be defined")

        headers = {}
        headers['Accept'] = "application/json"
        validate_certs = self.params.get('validate_certs')
        username = self.params.get('username')
        password = self.params.get('password')
        force_basic_auth = True
        data = kwargs.get('data', None)
        version = kwargs.get('version', 1)
        url = self.build_url(endpoint, version=version)
        status_code = None

        try:
            response = self.request.open(
                method,
                url.geturl(),
                headers=headers,
                url_username=username,
                url_password=password,
                force_basic_auth=force_basic_auth,
                validate_certs=validate_certs,
                data=data,
                follow_redirects=True
            )
        except(SSLValidationError) as ssl_error:
            self.fail_json(msg="Could not establish a secure connection to {0}: {1}".format(self.url.geturl(), ssl_error))
        except(ConnectionError) as ce:
            self.fail_json(msg="Failed to connect to {0}: {1}".format(self.url.geturl(), ce))
        except(HTTPError) as he:
            if he.code >= 500:
                self.fail_json(msg="The host responded with a server error ({1}): {0}".format(url.netloc, he.code))
            if he.code == 401:
                self.fail_json(msg="An authentication error has occured with user: {0}".format(username))
            if he.code == 403:
                self.fail_json(msg="A forbidden request was sent to the host ({1}): {0}".format(url.netloc, he.msg))
            if he.code == 404:
                self.fail_json(msg="The requested resource does not exist at {0}".format(url.path))
            if he.code == 405:
                self.fail_json(msg="The host responded that method {0} is not allowed to this endpoint {1}".format(method, url.path))
        except(Exception) as e:
            self.fail_json(msg="There was an unknown error when calling {0}: {1}.".format(self.url.geturl(), e))

        response_body = ''

        try:
            response_body = response.read()
        except(Exception) as e:
            self.fail_json(msg="Failed to read response body: {0}".format(e))

        response_json = {}
        if response_body and response_body != '':
            try:
                response_json = json.loads(response_body)
            except(Exception) as e:
                self.fail_json(msg="Failed to parse the response json: {0}".format(e))

        if PY2:
            status_code = response.getcode()
        else:
            status_code = response.status
        return {'status_code': status_code, 'json': response_json}
