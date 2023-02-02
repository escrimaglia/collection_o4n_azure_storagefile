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
import azure.core.exceptions as aze
from ansible.module_utils.basic import AnsibleModule
from azure.storage.fileshare import ShareServiceClient


def delete_files(_account_name, _connection_string, _share, _path, _files):
    _path = re.sub(r"^\/*", "", _path)
    found_files = []
    # check if share and path exist in Account Storage
    try:
      status, msg_ret, output = list_shares_in_service(_account_name, _connection_string)
      if status:
          share_exist = [share for share in output if share == _share]
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


def list_shares_in_service(_account_name, _connection_string):
    output = []
    try:
        # Instantiate the ShareServiceClient from a connection string
        file_service = ShareServiceClient.from_connection_string(_connection_string)
        # List the shares in the file service
        my_shares = list(file_service.list_shares())
        output = [share['name'] for share in my_shares if share]
        status = True
        msg_ret = {"msg": f"List of Shares created in account <{_account_name}>"}
    except Exception as error:
        status = False
        msg_ret = {"msg": f"List of Shares not created in account <{_account_name}>", "error": f"<{error}>"}

    return status, msg_ret, output


def list_files_in_share(_account_name, _connection_string, _share, _dir):
    _dir = re.sub(r"^\/*", "", _dir)
    output = {}
    status, msg_ret, shares_in_service = list_shares_in_service(_account_name, _connection_string)
    if status:
        share_exist = [share_name['name'] for share_name in shares_in_service['shares'] if share_name['name'] == _share]
    if len(share_exist) == 1:
        share = ShareClient.from_connection_string(_connection_string, _share)
        try:
            # List files in the directory
            my_files = {"results": list(share.list_directories_and_files(directory_name=_dir))}
            status = True
            msg_ret = {"msg": f"List of Files created for Directory </{_dir}> in share <{_share}>"}
            output = [{"name": file['name'], "size": file['size'], "file_id": file['file_id'],
                        "is_directory": file['is_directory']} for file in my_files['results'] if
                        not file['is_directory']]
        except aze.ResourceNotFoundError:
            msg_ret = {"msg": f"No files to list in Directory </{_dir}> in share <{_share}>",
                        "error": "Directory not found"}
            status = False
        except Exception as error:
            status = False
            msg_ret = {"msg": f"List of Files not created for Directory </{_dir}> in share <{_share}>",
                        "error": f"<{error}>"}
    else:
        msg_ret = {"msg": f"List of Files not created for Directory </{_dir}> in share <{_share}>",
                    "error": "Share not found"}
        status = False

    return status, msg_ret, output


def select_files(_file_pattern, _files_in_dir):
    msg_ret = f"Files selection done for <{_file_pattern}>"
    status = True
    name_and_exension_pattern = re.split(r"\.", _file_pattern)
    pattern_file_ext = name_and_exension_pattern[1] if len(name_and_exension_pattern) == 2 else []
    pattern_file_name = name_and_exension_pattern[0]
    try:
        if _file_pattern == "*.*":  # *.*
            return status, msg_ret, _files_in_dir
        elif len(name_and_exension_pattern) == 1:  # file*
            file_name_pattern = re.split(r"\*", pattern_file_name)[0]
            return status, msg_ret, [file for file in _files_in_dir if re.split(r"\.", file)[0].startswith(file_name_pattern)]
        elif len(name_and_exension_pattern) == 2:
            if pattern_file_name.startswith("*") and not "*" in pattern_file_ext:  # *.txt
                return status, msg_ret, [file for file in _files_in_dir if len(re.split(r"\.", file)) == 2 and
                                            pattern_file_ext == re.split(r"\.", file)[1]]
            elif pattern_file_ext.startswith("*") and not "*" in pattern_file_name:  # file.*
                return status, msg_ret, [file for file in _files_in_dir if pattern_file_name == re.split(r"\.", file)[0]]
            elif "*" in pattern_file_name and not "*" in pattern_file_ext:  # file*.txt
                name_pattern = re.split(r"\*", pattern_file_name)[0]
                return status, msg_ret, [file for file in _files_in_dir if
                                            len(re.split(r"\.", file)) == 2 and file.startswith(name_pattern) and
                                            pattern_file_ext == re.split(r"\.", file)[1]]
            elif not "*" in pattern_file_name and "*" in pattern_file_ext:  # file.t*
                file_ext_pattern = re.split(r"\*", pattern_file_ext)[0]
                return status, msg_ret, [file for file in _files_in_dir if pattern_file_name == re.split(r"\.", file)[0]
                                            and len(re.split(r"\.", file)) == 2 and 
                                            file_ext_pattern in re.split(r"\.", file)[1]]
            elif "*" in pattern_file_name and "*" in pattern_file_ext:  # file*.t*
                file_name_pattern = re.split(r"\*", pattern_file_name)[0]
                file_ext_pattern = re.split(r"\*", pattern_file_ext)[0]
                return status, msg_ret, [file for file in _files_in_dir if re.split(r"\.", file)[0].startswith(file_name_pattern)
                                            and re.split(r"\.", file)[1].startswith(file_ext_pattern)]
            elif "*" in pattern_file_name and pattern_file_ext == "*":  # file*.*
                file_name_pattern = re.split(r"\*", pattern_file_name)[0]
                file_ext_pattern = pattern_file_ext
                return status, msg_ret, [file for file in _files_in_dir if
                                            re.split(r"\.", file)[0].startswith(file_name_pattern)
                                            and re.split(r"\.", file)[1] == "*"]
            elif not "*" in pattern_file_name and not "*" in pattern_file_ext:  # file.txt
                file_name_pattern = pattern_file_name
                file_ext_pattern = pattern_file_ext
                return status, msg_ret, [file for file in _files_in_dir if file_name_pattern == re.split(r"\.", file)[0]
                                            and len(re.split(r"\.", file)) == 2 and 
                                            file_ext_pattern == re.split(r"\.", file)[1]]
            else:
                status = False
                msg_ret = f"Invalid file name: <{_file_pattern}>"
                return status, msg_ret, []
        else:
            status = False
            msg_ret = f"Invalid file name: <{_file_pattern}>"
            return status, msg_ret, []
    except Exception as error:
        status = False
        msg_ret = f"Files selection failed for <{_file_pattern}> pattern, error: <{error.args}>"
        return status, msg_ret, []


def main():
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