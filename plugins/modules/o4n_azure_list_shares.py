#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

__metaclass__ = type

ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'octupus',
                    'metadata_version': '1.1'}

DOCUMENTATION = """
---
module: o4n_azure_list_shares
short_description: List File Shares in Storage Account
description:
  - Connecto to Azure Storage file using connection string method
  - List File Shares in service
  - Return a list of Shares in Service
version_added: "1.0"
author: "Ed Scrimaglia"
notes:
  - Testeado en linux
requirements:
  - ansible >= 2.10
options:
  connection_string:
    description:
      - String that include URL & Token to connect to Azure Storage Account. Provided by Azure Portal
      - Storage Account -> Access Keys -> Connection String
    required: true
    type: string
  account_name:
    description:
      Storage Account Name Provided by Azure Portal
    required: true
    type: string
"""

EXAMPLES = """
tasks:
  - name: Delete files
    o4n_azure_list_shares:
      account_name: "{{ account_name }}"
      connection_string: "{{ connection_string }}"
    register: output
"""

#from azure.storage.fileshare import ShareServiceClient
from ansible.module_utils.basic import AnsibleModule
import os
import sys

# def add_module_utils_to_syspath():
#     module_utils_path =  "~/.ansible/collections/ansible_collections/escrimaglia/o4n_azure_storagefile/plugins/module_utils"
#     # os.chdir(module_path_name[0]+"/..")
#     # module_utils_path = os.getcwd()
#     # os.chdir(module_path_name[0])
#     sys.path.insert(1, module_utils_path)
#     print (sys.path)


# def list_shares_in_service(_account_name, _connection_string):
#     output = []
#     try:
#         # Instantiate the ShareServiceClient from a connection string
#         file_service = ShareServiceClient.from_connection_string(_connection_string)
#         # List the shares in the file service
#         my_shares = list(file_service.list_shares())
#         output = [share['name'] for share in my_shares if share]
#         status = True
#         msg_ret = {"msg": f"List of Shares created in account <{_account_name}>"}
#     except Exception as error:
#         status = False
#         msg_ret = {"msg": f"List of Shares not created in account <{_account_name}>", "error": f"<{error}>"}

#     return status, msg_ret, output


def main():
    #add_module_utils_to_syspath()
    module=AnsibleModule(
        argument_spec=dict(
            account_name=dict(required=True, type='str'),
            connection_string=dict(requiered=True, type='str')
        )
    )

    connection_string = module.params.get("connection_string")
    account_name = module.params.get("account_name")

    from module_utils.util_list_shares import list_shares_in_service
    
    success, msg_ret, output = list_shares_in_service(account_name, connection_string)

    if success:
        module.exit_json(failed=False, msg=msg_ret, content=output)
    else:
        module.fail_json(failed=True, msg=msg_ret, content=output)


if __name__ == "__main__":
    main()