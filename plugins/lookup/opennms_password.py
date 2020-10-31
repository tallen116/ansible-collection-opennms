# Copyright: (c) 2020, Timothy Allen
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
    name: opennms_password
    author: Timothy Allen (@tallen116)
    short_description: generate a password to use with opennms
    description:
      - Generates a password utilizing md5 or salt hash.
    options:
      _terms:
        description:
          - Plain text password to hash.
        required: True
      encrypt:
        description:
          - Which hash scheme to encrypt the returning password.
        choices:
          - md5
          - salt
        default: md5
      salt:
        description:
          - Salt string used for salt encryption type.
          - If not provided, the salt will be randomly generated.
        type: string
"""

EXAMPLES = """
- name: Generate md5 password for opennms
  set_fact:
    opennms_password: "{{ lookup('opennms_password', 'password') }}"

- name: Generate salt password for opennms
  set_fact:
    opennms_password: "{{ lookup('opennms_password', 'password', encrypt='salt') }}"

- name: Generate salt password for opennms with the a defined salt string
  set_fact:
    opennms_password: "{{ lookup('tallen116.opennms.opennms_password', 'password', encrypt='salt', salt='changeme') }}"
"""

RETURN = """
_raw:
  description:
    - The hashed password.
  type: string
"""

from hashlib import sha256
from hashlib import md5
import base64
import random

from ansible.plugins.lookup import LookupBase
from ansible.module_utils._text import to_text
from ansible.utils.display import Display

display = Display()


SALT_SIZE = 16
HASH_ITER = 100000


def md5_digest(message):
    """
    This hashes a md5 password for OpenNMS users.
    Not recommended.  Use salted hash instead.

    """
    input = bytearray(message, 'utf_8')

    message_digest = md5(input).digest()

    return message_digest.hex().upper()


def salt_digest(message, salt_size, iter, salt_string=None):
    """
    This hashes a salted password for OpenNMS users.

    message = The string to convert to the salt hash.
    salt_size = The size of the salt to use.
    iter = The amount of times to iterate using the hash.
    salt_string = Use a predefined salt that gets hashed using MD5.

    The steps taken for creating the digest
    1. The string message is converted to byte array
    2. A random 16 byte salt is generated
    3. The salt bytes are added to the message (salt + message)
    4. The sha256 hash function is applied to the salt and message
    5. The results of the hash will be iterated 100000 times
    6. The salt and final result of the hash are concatenated (salt + hash)
    7. The concatenation is encoded in BASE64 and returned as a string

    References
    http://www.jasypt.org/api/jasypt/1.8/org/jasypt/util/password/StrongPasswordEncryptor.html#constructor_detail
    https://github.com/jboss-fuse/jasypt/blob/master/jasypt/src/main/java/org/jasypt/digest/StandardStringDigester.java
    https://github.com/jboss-fuse/jasypt/blob/master/jasypt/src/main/java/org/jasypt/digest/StandardByteDigester.java
    https://github.com/jboss-fuse/jasypt/blob/master/jasypt/src/main/java/org/jasypt/util/password/StrongPasswordEncryptor.java
    """
    input = bytearray(message, 'utf_8')

    if salt_string is None:
        salt_array = bytearray()
        for i in range(0, salt_size):
            salt_array.append(random.randint(0, 255))
    else:
        _salt_md5 = md5(bytes(salt_string, 'utf_8')).digest()
        salt_array = bytearray(_salt_md5)

    salt = salt_array

    message_digest = salt + input

    _hash = message_digest
    for i in range(0, iter):
        _hash = sha256(message_digest).digest()
        message_digest = _hash

    final_digest = salt_array + message_digest

    message_base64 = base64.b64encode(final_digest)

    return message_base64.decode('utf_8')


class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):

        self.set_options(direct=kwargs)

        if self.get_option('encrypt') is None:
            encrypt = 'md5'
        else:
            encrypt = self.get_option('encrypt')

        salt = self.get_option('salt')

        ret = []
        for term in terms:
            display.vvv("Current password to hash is %s" % term)

            if encrypt == 'md5':
                password_hash = md5_digest(term)
            else:
                if salt is None:
                    password_hash = salt_digest(term, salt_size=SALT_SIZE, iter=HASH_ITER)
                else:
                    password_hash = salt_digest(term, salt_size=SALT_SIZE, iter=HASH_ITER, salt_string=salt)

            ret.append(to_text(password_hash))
        return ret
