#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

__metaclass__=type

ANSIBLE_METADATA={'status': ['preview'],
                    'supported_by': 'octupus',
                    'metadata_version': '1.1'}

DOCUMENTATION=r'''
---
module: o4n_azure_download_files
short_description: Download files to a local File System
description:
  - Connect to Azure Storage file using connection string method
  - Download files to a Local File System
  - Return a list of uploaded files
version_added: "1.0"
author: "Ed Scrimaglia"
notes:
  - Testeado en linux
requirements:
  - ansible >= 2.10
options:
  account_name:
    description:
      Storage Account Name Provided by Azure Portal
    required: true
    type: string
  connection_string:
    description:
      String that include URL & Token to connect to Azure Storage Account. Provided by Azure Portal
      Storage Account -> Access Keys -> Connection String
    required: true
    type: string
  share:
    description:
      Name of the share to be managed
    required: true
    type: string
  files:
    description:
      files to deleted from File ShRE
    required: true
    choices:
      - file*
      - file*.txt
      - file*.tx*
      - file*.*
      - file.tx*
      - *.txt
      - file.*
      - *.*
      - file.txt
    type: str
  local_path:
    description:
      path, directory, where files must be downloaded
    required: false
    type: string
'''

EXAMPLES=r'''
tasks:
  - name: Download files
    o4n_azure_download_files:
      account_name: "{{ connection_string }}"
      share: share-to-test
      connection_string: "{{ connection_string }}"
      source_path: /dir1/dir2
      files: file*.txt
    register: output

  - name: Download files
    o4n_azure_download_files:
      account_name: "{{ connection_string }}"
      share: share-to-test
      connection_string: "{{ connection_string }}"
      files: file*.t*
      local_path: /dir1/dir2
    register: output

  - name: Download files
    o4n_azure_download_files:
      account_name: "{{ connection_string }}"
      share: share-to-test
      connection_string: "{{ connection_string }}"
      source_path: /dir1/dir2
      files: file*.t*
      local_path: /files
    register: output

  - name: Download files
    o4n_azure_download_files:
      account_name: "{{ connection_string }}"
      share: share-to-test
      connection_string: "{{ connection_string }}"
      files: file*.t*
    register: output
'''

from azure.storage.fileshare import ShareClient
import re
import sys
import os
from o4n_azure_list_shares import list_shares_in_service
from o4n_azure_list_files import list_files_in_share
from ansible.module_utils.basic import AnsibleModule


def add_module_utils_to_syspath():
    module_path_name=(os.path.split(os.path.abspath(__file__)))
    os.chdir(module_path_name[0]+"/..")
    module_utils_path=os.getcwd()
    os.chdir(module_path_name[0])
    sys.path.insert(1, module_utils_path)
  

def download_files(_account_name, _connection_string, _share, _source_path, _files, _local_path):
    from module_utils.util_select_files_pattern import select_files
    found_files=[]
    # casting some vars
    _source_path=re.sub(r"^\/*", "", _source_path)
    # check if share and path exist in Account Storage
    try:
        status, msg_ret, output=list_shares_in_service(_account_name,_connection_string)
        if status:
            share_exist=[share['name'] for share in output['shares'] if share['name'] == _share]
            if len(share_exist) != 1:
                status=False
                msg_ret=f"Invalid File Share name: <{_share}>. Does not exist in Account Storage <{_account_name}>"
                return (status, msg_ret, found_files)
    except Exception as error:
        status=False
        msg_ret=f"Invalid File Share name: <{_share}>. Listing Shares process failed"
        return (status, msg_ret, found_files)
    # Download files
    try:
        # Instantiate the ShareFileClient from a connection string
        share=ShareClient.from_connection_string(_connection_string, _share)
        status, msg_ret_pattern, files_in_share=list_files_in_share(_account_name, _connection_string,_share, _source_path)
        if status:
            status, msg_ret, found_files=select_files(_files,
                                                            [file['name'] for file in files_in_share if file])
            l_path=_local_path + "/" if _local_path else ""
            s_path=_source_path + "/" if _source_path else ""
            if len(found_files) > 1:
                for file_name in found_files:
                    file=share.get_file_client(s_path + file_name)
                    # Download the file
                    with open(l_path + file_name, "wb") as data:
                        stream=file.download_file()
                        data.write(stream.readall())
                status=True
                msg_ret={"msg": f"File <{found_files}> downloaded to Directory <{_local_path}> from share <{_share}>"}
            elif len(found_files) == 1:
                file=share.get_file_client(s_path + found_files[0])
                # Download the file
                with open(l_path + found_files[0], "wb") as data:
                    stream=file.download_file()
                    data.write(stream.readall())
                status=True
                msg_ret={
                    "msg": f"File <{found_files[0]}> downloaded to Directory <{_local_path}> from share <{_share}>"}
            else:
                status=False
                msg_ret={
                    "msg": f"File <{found_files}> not downloaded to Directory <{_local_path}> from share <{_share}>. No file to download"}
        else:
            msg_ret=f"Invalid Directory: <{_source_path}> in File Share <{_share}>"
            status=False
    except Exception as error:
        msg_ret={"msg": f"File <{found_files}> not downloaded to Directory <{_local_path}>", "error": f"<{error}>"}
        status=False

    return status, msg_ret, found_files


def main():
    add_module_utils_to_syspath()
    module=AnsibleModule(
        argument_spec=dict (
            account_name=dict(required=True, type='str'),
            share=dict(required=True, type='str'),
            connection_string=dict(required=True, type='str'),
            source_path=dict(required=False, type='str', default=''),
            files=dict(required=True, type='str'),
            local_path=dict(required=False, type='str', default='')
        )
    )

    account_name = module.params.get("account_name")
    share = module.params.get("share")
    connection_string = module.params.get("connection_string")
    source_path = module.params.get("source_path")
    files = module.params.get("files")
    local_path = module.params.get("dest_path")

    success, msg_ret, output=download_files(account_name, connection_string, share, source_path, files, local_path)

    if success:
        module.exit_json(failed=False, msg=msg_ret, content=output)
    else:
        module.fail_json(failed=True, msg=msg_ret, content=output)


if __name__ == "__main__":
    main()