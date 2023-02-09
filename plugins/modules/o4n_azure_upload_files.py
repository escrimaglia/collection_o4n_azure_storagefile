#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'octupus',
                    'metadata_version': '1.1'}

DOCUMENTATION = """
---
module: o4n_azure_upload_files
short_description: Upload files to a share Storage File
description:
  - Connect to Azure Storage file using connection string method
  - Upload files to a share in a Storage File account
  - Return a list of uploaded files
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
  source_path:
    description:
      path, local directory where files to be uploaded are 
  dest_path:
    description:
      path, directory where files must be uploaded
    required: false
    type: string
"""

RETURN = """
"output": {
    "changed": false,
    "content": [
        "o4n_azure_list_files.py",
        "o4n_azure_list_shares.py",
        "o4n_azure_download_files.py",
        "o4n_azure_manage_shares.py",
        "__init__.py",
        "o4n_azure_manage_directory.py",
        "o4n_azure_upload_files.py",
        "o4n_azure_delete_files.py",
        "o4n_azure_list_directories.py"
    ],
    "failed": false,
    "msg": "Files uploaded to Directory </dir1> in share <share-to-test2>"
}
"""

EXAMPLES = """
tasks:
  - name: Upload files
    o4n_azure_upload_files:
      account_name: "{{ connection_string }}"
      share: share-to-test
      connection_string: "{{ connection_string }}"
      source_path: /dir1/dir2
      files: file*.txt
    register: output

  - name: Upload files
    o4n_azure_upload_files:
      account_name: "{{ connection_string }}"
      share: share-to-test
      connection_string: "{{ connection_string }}"
      files: file*.t*
      dest_path: /dir1/dir2
    register: output

  - name: Upload files
    o4n_azure_upload_files:
      account_name: "{{ connection_string }}"
      share: share-to-test
      connection_string: "{{ connection_string }}"
      source_path: /files
      files: file*.t*
      dest_path: /dir1/dir2
      register: output

  - name: Upload files
    o4n_azure_upload_files:
      account_name: "{{ connection_string }}"
      share: share-to-test
      connection_string: "{{ connection_string }}"
      files: file*.t*
      register: output
"""


import os
from azure.storage.fileshare import ShareClient
from ansible.module_utils.basic import AnsibleModule
import re
from ansible_collections.escrimaglia.o4n_azure_storagefile_test.plugins.module_utils.util_list_shares import list_shares_in_service
from ansible_collections.escrimaglia.o4n_azure_storagefile_test.plugins.module_utils.util_select_files_pattern import select_files


def upload_files(_account_name, _share, _connection_string, _source_path, _source_file, _dest_path):
  found_files = []
  # casting some vars
  _dest_path = re.sub(r"^\/", "", _dest_path)
  _dest_path = re.sub(r"\/$", "", _dest_path)
  try:
      # get files form local file system
      base_dir = os.getcwd() + "/" + _source_path + "/"
      search_dir = os.path.dirname(base_dir)
      files_in_dir = os.listdir(search_dir)
      # Instantiate the ShareClient from a connection string
      status, msg_ret, shares_in_service = list_shares_in_service(_account_name, _connection_string)
      if status:
        share_exist = [share_name for share_name in shares_in_service if share_name == _share]
      if len(share_exist) == 1:
        share = ShareClient.from_connection_string(_connection_string, _share)
        status, msg_ret, found_files = select_files(_source_file, files_in_dir)
        source_path = _source_path + "/" if _source_path else ""
        dest_path = _dest_path + "/" if _dest_path else ""
        if len(found_files) > 0:
            for file_name in found_files:
                file = share.get_file_client(dest_path + file_name)
                # Upload files
                with open(source_path + file_name, "rb") as source_file:
                    file.upload_file(source_file)
            status = True
            msg_ret = f"Files uploaded to Directory <{_dest_path}> in share <{_share}>"
        else:
            status = False
            msg_ret = f"Files not uploaded to Directory <{_dest_path}> in share <{_share}>. No file to upload"
      else:
        msg_ret = f"Files not uploaded to Directory <{_dest_path}>. Error: Share <{_share}> not found"
        status = False
  except Exception as error:
      msg_ret = f"File not uploaded to Directory <{_dest_path}> in share <{_share}>. Error: <{error}>"
      status = False

  return status, msg_ret, found_files


def main():
  module = AnsibleModule(
      argument_spec = dict(
          account_name=dict(required=True, type='str'),
          share = dict(required = True, type = 'str'),
          connection_string = dict(required = True, type='str'),
          source_path = dict(required = False, type = 'str', default = ''),
          files = dict(required = True, type = 'str'),
          dest_path = dict(required = False, type = 'str', default = '')
      )
  )

  account_name = module.params.get("account_name")
  share = module.params.get("share")
  connection_string = module.params.get("connection_string")
  source_path = module.params.get("source_path")
  files = module.params.get("files")
  dest_path = module.params.get("dest_path")

  success, msg_ret, output = upload_files(account_name, share, connection_string, source_path, files, dest_path)

  if success:
      module.exit_json(failed=False, msg=msg_ret, content=output)
  else:
      module.fail_json(failed=True, msg=msg_ret, content=output)

if __name__ == "__main__":
    main() 

    
