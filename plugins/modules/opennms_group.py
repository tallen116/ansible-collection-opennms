#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2018, Timothy Allen (@tallen116)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: opennms_group

short_description: Manage OpenNMS groups

version_added: "0.1.0"

description: A module to add, modify, delete OpenNMS groups.

extends_documentation_fragment: tallen116.opennms.opennms_auth

options:
    name:
        description: The name of the group.
        required: true
        type: str
    description:
        description: Any comment for the group.
        type: str
    users:
        description: The users assigned to the group.
        type: list
        elements: str
    categories:
        description: The categories assigned to the group.
        type: list
        elements: str
    state:
        description:
            - The state of the group.
            - Set to `present` to create or update the group.
            - Set to `absent` to remove the group.
        choices:
            - present
            - absent
        type: str
        default: present

author:
  - Timothy Allen (@tallen116)
'''

EXAMPLES = r'''
'''

RETURN = r''' # '''

from ..module_utils.api import ONMSAPIModule
import xml.etree.ElementTree as ET

API_ENDPOINT = '/users'
API_VERSION = 1


def main():

    argument_spec = dict(
        name=dict(type='str', required=True),
        description=dict(type='str'),
        users=dict(type='list'),
        categories=dict(type='list'),
        state=dict(type='str', choices=['present', 'absent'], default='present')
    )

    result = dict(
        changed=False,
        failed=False
    )

    module = ONMSAPIModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )


if __name__ == '__main__':
    main()
