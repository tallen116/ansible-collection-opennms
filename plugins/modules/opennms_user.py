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

        name=dict(type='str', required=True),
        password=dict(type='str', required=True),
        password_salt=dict(type='bool', default=True),
        full_name=dict(),
        email=dict(),
        description=dict(),
        duty_schedule=dict(type='list', elements='dict'),
        role=dict(type='list', elements='str'),
        state=dict(type='str', choices=['present', 'absent'], default='present')

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
                type: str
            start_time:
                description: The start time of the schedule depicted in 24 hour.
                type: int
            end_time:
                description: The end time of the schedule depicted in 24 hour.
                type: int
    role:
        description: The roles assigned to the user.
        type: list
    state:
        description:
            - The state of the user.
            - Set to `present` to create or update the user.
            - Set to `absent` to remove the user.
        choices:
            - present
            - absent

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


def check_user_difference(
    user,
    name,
    password,
    password_salt=True,
    full_name=None,
    email=None,
    description=None,
    duty_schedule=None,
    role=None
):
    """
    Checks for differeneces in user parameters.
    """
    response_data = {
        "user-id": name,
        "full-name": full_name,
        "user-comments": description,
        "email": email,
        "password": password,
        "passwordSalt": password_salt,
        "duty-schedule": create_duty_schedule_list(duty_schedule),
        "role": role
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
        diff = False
    else:
        diff = True

    user_diff = {
        "before": user,
        "after": response_data
    }
    return diff, user_diff


def create_duty_schedule_string(schedule, *args):
    """
    Create the string for the duty schedule for API usage.
    """

    # schedule_days = [i.lower() for i in schedule['days']]
    schedule_days = schedule['days']
    schedule_start = schedule['start_time']
    schedule_end = schedule['end_time']
    schedule_result = ''
    for day in DAYS_OF_WEEK:
        if day in schedule_days:
            schedule_result += DAYS_OF_WEEK[day]

    schedule_result += str(schedule_start)
    schedule_result += '-'
    schedule_result += str(schedule_end)
    return schedule_result


def create_duty_schedule_list(schedule=None):
    """
    Create the list for all duty schedules.
    """
    if schedule is None:
        return None

    schedule_list = []
    for item in schedule:
        schedule_list.append(create_duty_schedule_string(item))

    return schedule_list


def create_user_xml(
    name,
    password,
    password_salt=True,
    full_name=None,
    email=None,
    description=None,
    duty_schedule=None,
    role=None
):
    """
    Create XML specification to use with API.
    """

    xml_root = ET.Element('user')
    xml_user = ET.SubElement(xml_root, 'user-id')
    xml_user.text = name

    if full_name is not None:
        xml_full_name = ET.SubElement(xml_root, 'full-name')
        xml_full_name.text = full_name

    if description is not None:
        xml_description = ET.SubElement(xml_root, 'user-comments')
        xml_description.text = description

    if email is not None:
        xml_email = ET.SubElement(xml_root, 'email')
        xml_email.text = email

    xml_password = ET.SubElement(xml_root, 'password')
    xml_password.text = password

    xml_password_salt = ET.SubElement(xml_root, 'passwordSalt')
    xml_password_salt.text = str(password_salt).lower()

    if duty_schedule is not None:
        for item in duty_schedule:
            schedule = create_duty_schedule_string(item)
            xml_schedule = ET.SubElement(xml_root, 'duty-schedule')
            xml_schedule.text = schedule

    if role is not None:
        for item in role:
            xml_role = ET.SubElement(xml_root, 'role')
            xml_role.text = item

    return ET.tostring(xml_root)


def main():

    API_ENDPOINT = '/users'
    API_VERSION = 1

    argument_spec = dict(
        name=dict(type='str', required=True),
        password=dict(type='str', required=True, nolog=True),
        password_salt=dict(type='bool', default=True),
        full_name=dict(type='str'),
        email=dict(type='str'),
        description=dict(type='str'),
        duty_schedule=dict(
            type='list',
            options=dict(
                days=dict(type=list, elements='str', choices=[
                    'Monday',
                    'Tuesday',
                    'Wednesday',
                    'Thursday',
                    'Friday',
                    'Saturday',
                    'Sunday'
                ]),
                start_time=dict(type=int),
                end_time=dict(type=int)
            )
        ),
        role=dict(type='list', elements='str'),
        state=dict(type='str', choices=['present', 'absent'], default='present')
    )

    result = dict(
        changed=False,
    )

    module = ONMSAPIModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    name = module.params.get('name')
    password = module.params.get('password')
    password_salt = module.params.get('password_salt')
    full_name = module.params.get('full_name')
    email = module.params.get('email')
    description = module.params.get('description')
    duty_schedule = module.params.get('duty_schedule')
    role = module.params.get('role')
    state = module.params.get('state')

    endpoint = API_ENDPOINT + '/' + name

    response = module.get(endpoint, version=API_VERSION, ignore_404=True)

    data = create_user_xml(
        name=name,
        password=password,
        password_salt=password_salt,
        full_name=full_name,
        email=email,
        description=description,
        duty_schedule=duty_schedule,
        role=role
    )
    result['data'] = data
    if response is None and state == 'present':
        if module.check_mode:
            result['changed'] = True
            module.exit_json(**result)

        _response = module.post(API_ENDPOINT, version=API_VERSION, data=data, xml_data=True)
        result['changed'] = True
        result['response'] = _response
        result['message'] = "The user {0} was created.".format(name)
    elif response is not None and state == 'present':
        _user_diff, _user_diff_results = check_user_difference(
            user=response['json'],
            name=name,
            password=password,
            password_salt=password_salt,
            full_name=full_name,
            email=email,
            description=description,
            duty_schedule=duty_schedule,
            role=role
        )
        result['_user_diff_state'] = _user_diff
        result['_user_diff'] = _user_diff_results
        if _user_diff:
            if module.check_mode:
                result['changed'] = True
                module.exit_json(**result)
            _response = module.post(API_ENDPOINT, data=data, xml_data=True)
            result['changed'] = True
            result['response'] = _response
            result['message'] = "The user {0} was modified.".format(name)
    elif response is not None and state == 'absent':
        if module.check_mode:
            result['changed'] = True
            module.exit_json(**result)

        _response = module.delete(endpoint)
        result['changed'] = True
        result['response'] = _response
        result['message'] = "The user {0} was deleted.".format(name)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
