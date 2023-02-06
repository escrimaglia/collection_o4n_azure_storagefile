#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

__metaclass__ = type

ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'octupus',
                    'metadata_version': '1.1'}

DOCUMENTATION = r'''
---
module: test_include_utils
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
'''

EXAMPLES = r'''
tasks:
  - name: Delete files
    o4n_azure_list_files:
      account_name: "{{ account_name }}"
      connection_string: "{{ connection_string }}"
      share: "{{ share }}"
      path = /dir1/dir2
    register: output
'''

from azure.storage.fileshare import ShareClient
import azure.core.exceptions as aze
from ansible.module_utils.basic import AnsibleModule
import re
from azure.storage.fileshare import ShareServiceClient
from ansible_collections.escrimaglia.o4n_azure_storagefile_test.plugins.module_utils.util_list_shares import list_shares_in_service



def list_files_in_share(_account_name, _connection_string, _share, _dir):
  _dir = re.sub(r"^\/*", "", _dir)
  output = {}
  status, msg_ret, shares_in_service = list_shares_in_service(_account_name, _connection_string)
  if status:
      share_exist = [share_name for share_name in shares_in_service if share_name == _share]
  if len(share_exist) == 1:
      share = ShareClient.from_connection_string(_connection_string, _share)
      try:
          # List files in the directory
          my_files = {"results": list(share.list_directories_and_files(directory_name=_dir))}
          status = True
          msg_ret = f"List of Files created for Directory </{_dir}> in share <{_share}>"
          output = [{"name": file['name'], "size": file['size'], "file_id": file['file_id'],
                      "is_directory": file['is_directory']} for file in my_files['results'] if
                    not file['is_directory']]
      except aze.ResourceNotFoundError:
          msg_ret = f"No files to list in Directory </{_dir}> in share <{_share}>. Error: Directory not found"
          status = False
      except Exception as error:
          status = False
          msg_ret = f"List of Files not created for Directory </{_dir}> in share <{_share}>. Error: <{error}>"
  else:
      msg_ret = f"List of Files not created for Directory </{_dir}> in share <{_share}>. Error: Share not found"
      status = False

  return status, msg_ret, output

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
  path_sub = re.sub(r"^\/*", "", path)

  success, msg_ret, output = list_files_in_share(account_name, connection_string, share, path_sub)

  if success:
      module.exit_json(failed=False, msg=msg_ret, content=output)
  else:
      module.fail_json(failed=False, msg=msg_ret, content=output)


if __name__ == "__main__":
    main()