#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

__metaclass__ = type

ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'octupus',
                    'metadata_version': '1.1'}

DOCUMENTATION = """
---
module: o4n_azure_delete_files
short_description: Delete files in a share Storage File
description:
  - Connect to Azure Storage file using connection string method
  - Delete files in share in a Storage File account
  - Return a list of deleted files
version_added: "1.0"
author: "Ed Scrimaglia"
notes:
  - Testeado en linux
requirements:
  - ansible >= 2.10
options:
  share:
    description:
      Name of the share to be managed
    required: true
    type: string
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
  path:
    description:
      path, directory, where files must be deleted
    required: false
    type: string
  files:
    description:
      files to deleted from File ShRE
    required: true
    choices:
      - 'file*'
      - 'file*.txt'
      - 'file*.tx*'
      - 'file*.*'
      - file.tx*
      - '*.txt'
      - 'file.*'
      - '*.*'
      - 'file.txt'
    type: string
"""

EXAMPLES = """
tasks:
  - name: Delete files
    o4n_azure_delete_files:
      account_name: "{{ account_name }}"
      share: share-to-test
      connection_string: "{{ connection_string }}"
      path: /dir1/dir2
      files: file*.txt
    register: output

  - name: Delete files
    o4n_azure_delete_files:
      account_name: "{{ account_name }}"
      share: share-to-test
      connection_string: "{{ connection_string }}"
      files: file*.*
    register: output
"""

from azure.storage.fileshare import ShareClient
import re
import os
import sys
import azure.core.exceptions as aze
from ansible.module_utils.basic import AnsibleModule
from o4n_azure_list_shares import list_shares_in_service
from o4n_azure_list_files import list_files_in_share


def add_module_utils_to_syspath():
    module_path_name =  (os.path.split(os.path.abspath(__file__)))
    os.chdir(module_path_name[0]+"/..")
    module_utils_path = os.getcwd()
    os.chdir(module_path_name[0])
    sys.path.insert(1, module_utils_path)


def delete_files(_account_name, _connection_string, _share, _path, _files):
    from module_utils.util_select_files_pattern import select_files
    _path = re.sub(r"^\/*", "", _path)
    found_files = []
    # check if share and path exist in Account Storage
    try:
      status, msg_ret, output = list_shares_in_service(_account_name, _connection_string)
      if status:
          share_exist = [share['name'] for share in output['shares'] if share['name'] == _share]
          if len(share_exist) != 1:
              status = False
              msg_ret = f"Invalid File Share name: <{_share}>. File does not exist in Account Storage <{_account_name}>"
              return (status, msg_ret, found_files)
    except Exception as error:
        status = False
        msg_ret = f"Invalid File Share name: <{_share}>. Listing Shares process failed"
        return (status, msg_ret, found_files)
    # Delete files
    try:
      # Instantiate the ShareFileClient from a connection string
      share = ShareClient.from_connection_string(_connection_string, _share)
      status, msg_ret_pattern, files_in_share = list_files_in_share(_account_name, _connection_string, _share, _path)
      if status:
          status, msg_ret, found_files = select_files(_files,
                                          [file['name'] for file in files_in_share if file])
          path = _path + "/" if _path else ""
          if len(found_files) > 1:
              for file_name in found_files:
                  file = share.get_file_client(path + file_name)
                  # delete the file
                  file.delete_file()
              status = True
              msg_ret = {"msg": f"File <{found_files}> deleted from Directory </{_path}> in share <{_share}>"}
          elif len(found_files) == 1:
              file = share.get_file_client(path + found_files[0])
              # delete the file
              file.delete_file()
              status = True
              msg_ret = {
                  "msg": f"File <{found_files[0]}> deleted from Directory </{_path}> in share <{_share}>"}
          else:
              status = True
              msg_ret = {
                  "msg": f"File <{found_files}> not deleted from Directory </{_path}> in share <{_share}>. No file to delete"}
      else:
          msg_ret = f"Invalid Directory: <{_path}> in File Share <{_share}>"
          status = False
    except aze.ResourceNotFoundError:
      msg_ret = {"msg": f"File <{found_files}> not deleted from Directory </{_path}> in share <{_share}>",
                  "error": "Resource not found"}
      status = False
    except Exception as error:
      msg_ret = {"msg": f"File <{found_files}> not deleted from Directory </{_path}> in share <{_share}>",
                  "error": f"<{error}>"}
      status = False

    return status, msg_ret, found_files


def main():
    add_module_utils_to_syspath()
    module = AnsibleModule(
        argument_spec=dict(
            account_name=dict(required=True, type='str'),
            shar= dict(required=True, type='str'),
            connection_string=dict(required=True, type='str'),
            path=dict(required=False, type='str', default=''),
            files=dict(required=True, type='str')
        )
    )

    share = module.params.get("share")
    connection_string = module.params.get("connection_string")
    account_name = module.params.get("account_name")
    path = module.params.get("path")
    files = module.params.get("files")

    success, msg_ret, output = delete_files(account_name, connection_string, share, path, files)

    if success:
        module.exit_json(failed=False, msg=msg_ret, content=output)
    else:
        module.fail_json(failed=True, msg=msg_ret, content=output)


if __name__ == "__main__":
    main()