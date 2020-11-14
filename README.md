# Ansible Collection - tallen116.opennms

[![Build Status](https://travis-ci.com/tallen116/ansible-collection-opennms.svg?branch=main)](https://travis-ci.com/tallen116/ansible-collection-opennms)

This repo hosts the `tallen116.opennms` Ansible Collection.

This collection includes a variety of Ansible content to automate the installation and management of OpenNMS.  OpenNMS is an enterprise network monitoring system.

<!--start requires_ansible-->
## Ansible version compatibility

This collection has been tested against following Ansible versions: **>=2.9.10,<2.11**.

Plugins and modules within a collection may be tested with only specific Ansible versions.
A collection may contain metadata that identifies these versions.
PEP440 is the schema used to describe the versions of Ansible.
<!--end requires_ansible-->

<!--start collection content-->
### Lookup plugins
Name | Description
--- | ---
[tallen116.opennms.opennms_password](https://github.com/tallen116/ansible-collection-opennms/blob/main/docs/tallen116.opennms.opennms_password_lookup.rst)|generate a password to use with opennms

### Modules
Name | Description
--- | ---
[tallen116.opennms.opennms_user](https://github.com/tallen116/ansible-collection-opennms/blob/main/docs/tallen116.opennms.opennms_user_module.rst)|Manage OpenNMS users

<!--end collection content-->

## Contributing

### Generating plugin docs

The module docs are generated using the [collection_prep_add_docs](https://github.com/ansible-network/collection_prep) module.

```
COLLECTION_PATH=path/to/collection
cd /tmp
git clone https://github.com/ansible-network/collection_prep.git
cd collection_prep
python -m venv collection_prep_venv
source collection_prep_venv/bin/activate
pip install .
collection_prep_add_docs -p $COLLECTION_PATH
```
