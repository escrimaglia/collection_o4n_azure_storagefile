#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

__metaclass__ = type

ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'octupus',
                    'metadata_version': '1.1'}

DOCUMENTATION = """
---
module: o4n_azure_list_files
short_description: List Files in a File Share
description:
  - Connect to Azure Storage file using connection string method
  - List Files in a File Share
  - Return a list of Files in a File Share
version_added: "1.0"
author: "Ed Scrimaglia"
notes:
  - Testeado en linux
requirements:
  - ansible >= 2.10
options:
  connection_string:
    description:
      String that include URL & Token to connect to Azure Storage Account. Provided by Azure Portal
      Storage Account -> Access Keys -> Connection String
    required: true
    type: string
  account_name:
    description:
      Storage Account Name Provided by Azure Portal
    required: true
    type: string
  share:
    description:
      Name of the share to be managed
    required: true
    type: string
  path:
    description:
      path, directory, whose files must be listed
    required: false
    type: string
"""

EXAMPLES = """
tasks:
  - name: Delete files
    o4n_azure_list_files:
      account_name: "{{ account_name }}"
      connection_string: "{{ connection_string }}"
      share: "{{ share }}"
      path = /dir1/dir2
    register: output
"""

from ansible.module_utils.basic import AnsibleModule
import re
from ansible_collections.escrimaglia.o4n_azure_storagefile_test.plugins.module_utils.util_list_files import list_files_in_share


def main():
  module = AnsibleModule(
    argument_spec=dict(
      account_name=dict(required=True, type='str'),
      share=dict(required=True, type='str'),
      connection_string=dict(required=True, type='str'),
      path=dict(required=False, type='str', default=''),
    )
  )

  share = module.params.get("share")
  connection_string = module.params.get("connection_string")
  account_name = module.params.get("account_name")
  path = module.params.get("path")
  path_sub = re.sub(r"^\/", "", path)
  path_sub = re.sub(r"\/$", "", path_sub)

  success, msg_ret, output = list_files_in_share(account_name, connection_string, share, path_sub)

  if success:
      module.exit_json(failed=False, msg=msg_ret, content=output)
  else:
      module.fail_json(failed=False, msg=msg_ret, content=output)


if __name__ == "__main__":
    main()