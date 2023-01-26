#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
from azure.storage.fileshare import ShareClient
from ansible.module_utils.basic import AnsibleModule



DOCUMENTATION = """
---
module: o4n_azure_create_share
version_added: "2.0"
author: "Ed Scrimaglia"
short_description: Create a share in a Azure Storage File
description:
    - Connecto to Azure Storage file using connection string method
    - Create a file share in a Storage File account when status param is present
    - Return an ivalid operation if the share already exist
notes:
    - Testeado en linux
options:
    state:
        description:
            Create or delete a share
        required: False
        default: present

    share:
        description:
            Name of the share to be managed
        required: True
    connection_string:
        description:
            String that include URL & Token to connect to Azure Storage Account. Provided by Azure
        required: True
    account_name:
        description:
            Storage Account Name provided by Azure
        required: True
"""

EXAMPLES = """
tasks:
  - name: Create a share
      o4n_azure_manage_share:
        account_name: "{{ account_name }}"
        share: share-to-test
        connection_string: "{{ connection_string }}"
      register: output

   - name: Delete a share
      o4n_azure_manage_share:
        account_name: "{{ account_name }}"
        status: absent
        share: share-to-test
        connection_string: "{{ connection_string }}"
      register: output
"""

# Methods
def manage_file_share(_share, _conn_string, _account_name, _status):
    output = {}
    try:
        # Instantiate the ShareClient from a connection string
        share = ShareClient.from_connection_string(_conn_string, share_name=_share)
        # Create or Delete the share
        if _status.lower() == "present":
            share.create_share()
            output = {"properties": share.get_share_properties()}
            action = "created"
        else:
            share.delete_share()
            action = "deleted"
        status = True
        msg_ret = {"msg", f"File Share <{_share}> <{action}> in account <{_account_name}>"}
    except Exception as error:
        msg_ret = {"msg": f"File Share <{_share}> not managed in <{_account_name}>", "error": f"<{error}>"}
        status = False

    return status, msg_ret, output

def main():
    Output = {}
    module = AnsibleModule(
        argument_spec=dict(
            account_name=dict(required=True, type='str'),
            state=dict(required=False, type='str', choices=["present", "absent"], default='present'),
            share=dict(required=False, type='str'),
            connection_string=dict(required=True, type='str'),
        )
    )

    state = module.params.get("state")
    share = module.params.get("share")
    connection_string = module.params.get("connection_string")
    account_name = module.params.get("account_name")

    success, msg_ret, output = manage_file_share(share,connection_string,account_name,state)
    if success:
        module.exit_json(failed=False, msg=msg_ret, content=output)
    else:
        module.exit_json(failed=True, msg=msg_ret, content=output)

if  __name__ == "__main__":
    main()
