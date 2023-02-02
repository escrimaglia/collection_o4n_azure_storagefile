#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

__metaclass__ = type

ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'octupus',
                    'metadata_version': '1.1'}

DOCUMENTATION = r'''
---
module: o4n_azure_manage_directory
short_description: Create and Delete Directories and Sub Directory in a share Storage File
description:
  - Connect to Azure Storage file using connection string method
  - Create a Directory in a share in a Storage File account when state param is eq to present 
  - Delete a Directory in a share in a Storage File account when state param is eq to absent
  - Create a Sub Directory under a parent Directory in a share in a Storage File account when state param is eq to present
  - Delete a Sub Directory under a parent Directory in a share in a Storage File account when state param is eq to absent
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
      String that include URL & Token to connect to Azure Storage Account. Provided by Azure Portal
      Storage Account -> Access Keys -> Connection String
    required: true
    type: string
  account_name:
    description:
      Storage Account Name Provided by Azure Portal
    required: true
    type: string
  state:
    description:
      Create or delete a Directory a Sub Directory
    required: false
    type: string
    choices:
      - present
      - absent
    default: present
  path:
    description:
      path, directory, to create or delete
    required: true
    type: string
  parent_path:
    description:
      parent path, directory, where directory must be created or deleted
    required: false
    type: string
'''

EXAMPLES = r'''
tasks:
  - name: Create Directory
    o4n_azure_manage_directory:
      account_name: "{{ account_name }}"
      share: share-to-test
      connection_string: "{{ connection_string }}"
      path: /dir1
    register: output

  - name: Create Sub Directory
    o4n_azure_manage_directory:
      account_name: "{{ account_name }}"
      share: share-to-test
      connection_string: "{{ connection_string }}"
      path: /dir2
      parent_path: /dir1
    register: output
    
  - name: Delete Directory
    o4n_azure_manage_directory:
      account_name: "{{ account_name }}"
      share: share-to-test
      connection_string: "{{ connection_string }}"
      path: /dir1
      state: absent
      register: output

  - name: Delete Sub Directory
    o4n_azure_manage_directory:
      account_name: "{{ account_name }}"
      share: share-to-test
      connection_string: "{{ connection_string }}"
      path: /dir2
      parent_path: /dir1
      state: absent
    register: output
'''

from azure.storage.fileshare import ShareClient
import azure.core.exceptions as aze
from ansible.module_utils.basic import AnsibleModule
import re
import sys
import os

def add_module_utils_to_syspath():
    module_path_name =  (os.path.split(os.path.abspath(__file__)))
    os.chdir(module_path_name[0]+"/..")
    module_utils_path = os.getcwd()
    os.chdir(module_path_name[0])
    sys.path.insert(1, module_utils_path)


def create_directory(_connection_string, _share, _directory, _state):
    action = "none"
    share = ShareClient.from_connection_string(_connection_string, _share)
    try:
        new_directory = share.get_directory_client(directory_path=_directory)
        if _state.lower() == "present":
            action = "created"
            new_directory.create_directory()
            msg_ret = f"Directory </{_directory}> created in share <{_share}>"
        elif _state.lower() == "absent":
            action = "deleted"
            new_directory.delete_directory()
        status = True
        msg_ret = f"Directory </{_directory}> <{action}> in share <{_share}>"
    except aze.ResourceExistsError:
        status = False
        msg_ret = {"msg": f"Directory </{_directory}> not <{action}> in share <{_share}>", "error": "<The specified resource already exist>"}
    except aze.ResourceNotFoundError:
        status = False
        msg_ret = {"msg": f"Directory </{_directory}> not <{action}> in share <{_share}>", "error": "<The specified resource does not exist>"}
    except Exception as error:
        msg_ret = {"msg": f"Error managing Directory </{_directory}> in share <{_share}>", "error": f"<{error}>"}
        status = False

    return status, msg_ret, _directory


def create_subdirectory(_connection_string, _share, _directory, _parent_directory, _state):
    share = ShareClient.from_connection_string(_connection_string, _share)
    action = "none"
    try:
        parent_dir = share.get_directory_client(directory_path=_parent_directory)
        if _state.lower() == "present":
            action = "created"
            parent_dir.create_subdirectory(_directory)
        elif _state.lower() == "absent":
            action = "deleted"
            parent_dir.delete_subdirectory(_directory)
        status = True
        msg_ret = {"msg": f"Sub Directory </{_directory}> <{action}> under Directory </{_parent_directory}> in share <{_share}>"}
    except aze.ResourceExistsError as error:
        status = True
        msg_ret = {"msg": f"Sub Directory </{_directory}> not <{action}>. Parent Directory </{_parent_directory}>, share <{_share}>", "error": "<The specified resource already exist>"}
    except aze.ResourceNotFoundError:
        status = True
        msg_ret = {"msg": f"Sub Directory </{_directory}> not <{action}>. Parent Directory </{_parent_directory}>, share <{_share}>", "error": "<The specified resource does not exist>"}   
    except Exception as error:
        msg_ret = {"msg": f"Error managing Sub Directory </{_directory}>. Parent Directory </{_parent_directory}>, share <{_share}>", "error": f"<{error}>"}
        status = False

    return status, msg_ret, "/" + _parent_directory + "/"+ _directory


def main():
    add_module_utils_to_syspath()
    module = AnsibleModule(
        argument_spec=dict(
            share = dict(required = True, type = 'str'),
            connection_string = dict(required = True, type='str'),
            account_name=dict(required=True, type='str'),
            path = dict(required = False, type = 'str', default = ''),
            parent_path = dict(required = False, type = 'str', default = ''),
            state = dict(required = False, type = 'str', choices = ["present", "absent"], default = 'present'),
        )
    )

    share = module.params.get("share")
    connection_string = module.params.get("connection_string")
    path = module.params.get("path")
    parent_path = module.params.get("parent_path")
    state = module.params.get("state")
    account_name = module.params.get("account_name")
    path_sub = re.sub(r"^\/*", "", path)
    parent_path_sub = re.sub(r"^\/*", "", parent_path)

    if parent_path_sub and parent_path:
        from module_utils.util_list_directories import list_directories_in_share
        success, msg_ret, output = list_directories_in_share(account_name, connection_string, share, parent_path_sub)
        if not success and str(state).lower() == "present":
          success, msg_ret, output = create_directory(connection_string, share, parent_path_sub, state)
          if success:
              success, msg_ret, output = create_subdirectory(connection_string, share, path_sub, parent_path_sub, state)
    elif not parent_path_sub and parent_path:
        success, msg_ret, output = create_directory(connection_string, share, path_sub, state)
    else:
      success = False
      msg_ret = {"msg": f"Invalid sub Directory </{path}>, Directory </{parent_path}> in share <{share}>"}
      output= []

    if success:
        module.exit_json(failed=False, msg=msg_ret, content=output)
    else:
        module.fail_json(failed=True, msg=msg_ret, content=output)


if __name__ == "__main__":
    main()