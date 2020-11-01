# Copyright: (c) 2020, Timothy Allen (@tallen116)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from .module import ONMSModule
# from ansible.module_utils.urls import Request


class ONMSAPIModule(ONMSModule):

    def __init__(self, argument_spec, **kwargs):
        super(ONMSAPIModule, self).__init__(argument_spec=argument_spec, **kwargs)
