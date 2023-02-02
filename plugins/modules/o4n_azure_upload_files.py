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

EXAMPLES = """
tasks:
  - name: Upload files
    o4n_azure_upload_files:
      share: share-to-test
      connection_string: "{{ connection_string }}"
      source_path: /dir1/dir2
      files: file*.txt
    register: output

  - name: Upload files
    o4n_azure_upload_files:
      share: share-to-test
      connection_string: "{{ connection_string }}"
      files: file*.t*
      dest_path: /dir1/dir2
    register: output

  - name: Upload files
    o4n_azure_upload_files:
      share: share-to-test
      connection_string: "{{ connection_string }}"
      source_path: /files
      files: file*.t*
      dest_path: /dir1/dir2
      register: output

  - name: Upload files
    o4n_azure_upload_files:
      share: share-to-test
      connection_string: "{{ connection_string }}"
      files: file*.t*
      register: output
"""

import os
from azure.storage.fileshare import ShareClient
from ansible.module_utils.basic import AnsibleModule
import re


def upload_files(_share, _connection_string, _source_path, _source_file, _dest_path):
  found_files = []
  # casting some vars
  _dest_path = re.sub(r"^\/*", "", _dest_path)
  try:
      # get files form local file system
      base_dir = os.getcwd() + "/" + _source_path + "/"
      search_dir = os.path.dirname(base_dir)
      files_in_dir = os.listdir(search_dir)
      # Instantiate the ShareClient from a connection string
      share = ShareClient.from_connection_string(_connection_string, _share)
      # search files to upload
      status, msg_ret, found_files = select_files(_source_file, files_in_dir)
      source_path = _source_path + "/" if _source_path else ""
      dest_path = _dest_path + "/" if _source_path else ""
      if len(found_files) > 0:
          for file_name in found_files:
              file = share.get_file_client(dest_path + file_name)
              # Upload files
              with open(source_path + file_name, "rb") as source_file:
                  file.upload_file(file_name)
          status = True
          msg_ret = {"msg": f"File <{found_files}> uploaded to Directory </{_dest_path}> in share <{_share}>"}
      else:
          status = False
          msg_ret = {
              "msg": f"File <{found_files}> not uploaded to Directory </{_dest_path}> in share <{_share}>. No file to upload"}
  except Exception as error:
      msg_ret = {"msg": f"File <{found_files}> not uploaded to Directory </{_dest_path}> in share <{_share}>",
                  "error": f"<{error}>"}
      status = False

  return status, msg_ret, found_files


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
      argument_spec = dict(
          share = dict(required = True, type = 'str'),
          connection_string = dict(required = True, type='str'),
          source_path = dict(required = False, type = 'str', default = ''),
          files = dict(required = True, type = 'str'),
          dest_path = dict(required = False, type = 'str', default = '')
      )
  )

  share = module.params.get("share")
  connection_string = module.params.get("connection_string")
  source_path = module.params.get("source_path")
  files = module.params.get("files")
  dest_path = module.params.get("dest_path")

  success, msg_ret, output = upload_files(share, connection_string, source_path, files, dest_path)

  if success:
      module.exit_json(failed=False, msg=msg_ret, content=output)
  else:
      module.fail_json(failed=True, msg=msg_ret, content=output)

if __name__ == "__main__":
    main() 

    
