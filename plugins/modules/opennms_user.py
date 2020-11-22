#!/usr/bin/python

# Copyright: (c) 2018, Timothy Allen (@tallen116)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: opennms_user

short_description: Manage OpenNMS users

version_added: "0.1.0"

description: A module to add, modify, delete OpenNMS users.

extends_documentation_fragment: tallen116.opennms.opennms_auth

options:
    name:
        description: The name of the user.
        required: true
        type: str
    password:
        description: The password for the user.
        required: true
        type: str
    password_salt:
        description: The password salt hashing algorithm.
        default: true
        type: bool
    full_name:
        description: The full name of the user.
        type: str
    email:
        description: The email address of the user.
        type: str
    description:
        description: Any comment for the user.
        type: str
    duty_schedule:
        description: The duty schedule for the user.
        type: list
        elements: dict
        suboptions:
            days:
                description: The day of the week for the schedule.
                choices:
                    - Monday
                    - Tuesday
                    - Wednesday
                    - Thursday
                    - Friday
                    - Saturday
                    - Sunday
                type: list
                elements: str
            start_time:
                description: The start time of the schedule depicted in 24 hour.
                type: int
            end_time:
                description: The end time of the schedule depicted in 24 hour.
                type: int
    role:
        description: The roles assigned to the user.
        type: list
        elements: str
    state:
        description:
            - The state of the user.
            - Set to `present` to create or update the user.
            - Set to `absent` to remove the user.
        choices:
            - present
            - absent
        type: str
        default: present

author:
  - Timothy Allen (@tallen116)
'''

EXAMPLES = r'''
- name: Add basic user
  tallen116.opennms.opennms_user:
    name: basic
    password: "{{ lookup('tallen116.opennms.opennms_password', 'ansible', encrypt='salt') }}"
    state: present

- name: Add advance user
  tallen116.opennms.opennms_user:
    name: advance
    password: "{{ lookup('tallen116.opennms.opennms_password', 'ansible', encrypt='salt') }}"
    full_name: Advance User
    email: advance.user@localhost.local
    description: A advance user example
    duty_schedule:
      - days:
          - Monday
        start_time: 0
        end_time: 2359
      - days:
          - Monday
          - Tuesday
          - Wednesday
          - Thursday
          - Sunday
        start_time: 630
        end_time: 1900
      - days:
          - Friday
          - Saturday
        start_time: 1000
        end_time: 1730
    role:
      - ROLE_ADMIN
      - ROLE_USER
    state: present
'''

RETURN = r'''
result:
    description:
      - The created or modified user.  Will be empty in case of deletion.
    returned: success
    type: complex
    contains:
        user:
            description: The user object details.
            returned: success
            type: complex

msg:
    description: The status of the change.
    type: str
    returned: always
    sample: The user john.doe was added.
'''

from ..module_utils.api import ONMSAPIModule
import xml.etree.ElementTree as ET

DAYS_OF_WEEK = {
    'Monday': 'Mo',
    'Tuesday': 'Tu',
    'Wednesday': 'We',
    'Thursday': 'Th',
    'Friday': 'Fr',
    'Saturday': 'Sa',
    'Sunday': 'Su'
}

API_ENDPOINT = '/users'
API_VERSION = 1


class OpennmsUser:

    def __init__(self, module):
        self.module = module
        self.name = module.params.get('name')
        self.password = module.params.get('password')
        self.password_salt = module.params.get('password_salt')
        self.full_name = module.params.get('full_name')
        self.email = module.params.get('email')
        self.description = module.params.get('description')
        self.duty_schedule = module.params.get('duty_schedule')
        self.role = module.params.get('role')
        self.endpoint = API_ENDPOINT + '/' + self.name
        self.api_result = module.get(self.endpoint, version=API_VERSION, ignore_404=True)

    def remove_user(self):
        self.module.delete(self.endpoint)
        return {
            'changed': True,
            'msg': "The user {0} was removed.".format(self.name),
        }

    def add_user(self):
        self.module.post(API_ENDPOINT, version=API_VERSION, data=self.generate_xml(), xml_data=True)
        return {
            'changed': True,
            'msg': "The user {0} was added.".format(self.name),
            'result': {
                'user': {
                    'name': self.name,
                    'full_name': self.full_name,
                    'email': self.email,
                    'description': self.description,
                    'duty_schedule': self.duty_schedule,
                    'role': self.role
                }
            }
        }

    def update_user(self):
        result, user_result = self.compare(self.api_result['json'])
        if result:
            self.module.post(API_ENDPOINT, version=API_VERSION, data=self.generate_xml(), xml_data=True)
            return {
                'changed': True,
                'msg': "The user {0} was modifed.".format(self.name),
                'result': {
                    'user': {
                        'name': self.name,
                        'full_name': self.full_name,
                        'email': self.email,
                        'description': self.description,
                        'duty_schedule': self.duty_schedule,
                        'role': self.role
                    }
                }
            }
        else:
            return {'changed': False}

    def get_user(self):
        return self.api_result

    def exists(self):
        if self.api_result is None:
            return False
        else:
            return True

    def generate_xml(self):
        """Returns XML format of the user."""

        xml_root = ET.Element('user')
        xml_user = ET.SubElement(xml_root, 'user-id')
        xml_user.text = self.name

        if self.full_name is not None:
            xml_full_name = ET.SubElement(xml_root, 'full-name')
            xml_full_name.text = self.full_name

        if self.description is not None:
            xml_description = ET.SubElement(xml_root, 'user-comments')
            xml_description.text = self.description

        if self.email is not None:
            xml_email = ET.SubElement(xml_root, 'email')
            xml_email.text = self.email

        xml_password = ET.SubElement(xml_root, 'password')
        xml_password.text = self.password

        xml_password_salt = ET.SubElement(xml_root, 'passwordSalt')
        xml_password_salt.text = str(self.password_salt).lower()

        if self.duty_schedule is not None:
            for item in self.duty_schedule:
                schedule = self._create_duty_schedule_string(item)
                xml_schedule = ET.SubElement(xml_root, 'duty-schedule')
                xml_schedule.text = schedule

        if self.role is not None:
            for item in self.role:
                xml_role = ET.SubElement(xml_root, 'role')
                xml_role.text = item

        return ET.tostring(xml_root)

    def compare(self, user):
        """Checks if users are equal."""

        response_data = {
            "user-id": self.name,
            "full-name": self.full_name,
            "user-comments": self.description,
            "email": self.email,
            "password": self.password,
            "passwordSalt": self.password_salt,
            "duty-schedule": self._create_duty_schedule_list(self.duty_schedule),
            "role": self.role
        }

        # Format keys to match defaults if info is not provided
        for key, value in dict(response_data).items():
            if key == 'duty-schedule' and value is None:
                response_data[key] = []
            elif key == 'role' and value is None:
                response_data[key] = []
            elif key == 'email' and value is None:
                response_data[key] = ""
            elif value is None:
                del response_data[key]

        if user == response_data:
            result = False
        else:
            result = True

        user_result = {
            "before": user,
            "after": response_data
        }
        return result, user_result

    def _create_duty_schedule_string(self, schedule):
        """Returns the string for the duty schedule for API usage."""

        # schedule_days = [i.lower() for i in schedule['days']]
        schedule_days = schedule['days']
        schedule_start = schedule['start_time']
        schedule_end = schedule['end_time']
        result = ''
        for day in DAYS_OF_WEEK:
            if day in schedule_days:
                result += DAYS_OF_WEEK[day]

        result += str(schedule_start)
        result += '-'
        result += str(schedule_end)
        return result

    def _create_duty_schedule_list(self, schedule=None):
        """Create the list for all duty schedules."""

        if schedule is None:
            return None

        schedule_list = []
        for item in schedule:
            schedule_list.append(
                self._create_duty_schedule_string(item)
            )

        return schedule_list


def main():

    argument_spec = dict(
        name=dict(type='str', required=True),
        password=dict(type='str', required=True, nolog=True),
        password_salt=dict(type='bool', default=True),
        full_name=dict(type='str'),
        email=dict(type='str'),
        description=dict(type='str'),
        duty_schedule=dict(
            type='list',
            elements='dict',
            options=dict(
                days=dict(type='list', elements='str', choices=[
                    'Monday',
                    'Tuesday',
                    'Wednesday',
                    'Thursday',
                    'Friday',
                    'Saturday',
                    'Sunday'
                ]),
                start_time=dict(type='int'),
                end_time=dict(type='int')
            )
        ),
        role=dict(type='list', elements='str'),
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

    opennms_user = OpennmsUser(module=module)

    # User exists
    if opennms_user.exists():
        if module.params['state'] == 'absent':
            # Delete user
            if module.check_mode:
                result['changed'] = True
                module.exit_json(**result)
            result = opennms_user.remove_user()
        elif module.params['state'] == 'present':
            # Update user
            if module.check_mode:
                result['changed'] = True
                module.exit_json(**result)
            result = opennms_user.update_user()
    else:
        if module.params['state'] == 'present':
            # Add user
            if module.check_mode:
                result['changed'] = True
                module.exit_json(**result)
            result = opennms_user.add_user()

    module.exit_json(**result)


if __name__ == '__main__':
    main()
