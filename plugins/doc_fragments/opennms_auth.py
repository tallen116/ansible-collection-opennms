# Copyright: (c) 2020, Timothy Allen (@tallen116)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):

    # Authentication documentation
    DOCUMENTATION = r'''
    options:
        onms_host:
            description: The hostname or IP address of the OpenNMS server.
            type: str
            required: true
        onms_username:
            description: The username of the OpenNMS server.
            type: str
            required: true
        onms_password:
            description: The password of the OpenNMS server.
            type: str
            required: true
        validate_certs:
            description:
              - Allow connection when SSL certificates are not valid.
              - Set to C(false) when certificates are not trusted.
            type: bool
            default: true
    '''
