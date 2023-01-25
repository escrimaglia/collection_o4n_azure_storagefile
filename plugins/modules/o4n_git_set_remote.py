#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

DOCUMENTATION = """
---
module: o4n_git_set_remote
version_added: "2.0"
author: "Ed Scrimaglia"
short_description: set git branch and it remote in a directory
description:
    - Detect if already exists a remote git linked to the directory
    - Set the origin/remote link
    - Set the main branch
notes:
    - Testeado en linux
options:
    state:
        description:
            set or unset git remote
        required: True
    origin:
        description:
            the origin
        required: False
        default: origin
    branch:
        description:
            branch to be used
        required: True
        default: M
    remote:
        description:
            repository to be set as remote by git
        required: True
    path:
        description:
            directory where to set the remote
        required: False
        default: ./
"""

EXAMPLES = """
tasks:
  - name: Set remote
      o4n_git_remote:
        state: present
        origin: origin
        branch: main
        remote: git@github.com:repository.git
        path: /src/path
      register: salida

  - name: Delete git remote
     o4n_git_remote:
        state: absent
        remote: git@github.com:repository.git
        path: /src/path
    register: salida
"""

# Python Modules
import os
from ansible.module_utils.basic import AnsibleModule


# Functions
def get_remote(_origin, _repo, _path):
    ret_msg = ""
    exist_remote = False
    success = False
    try:
        os.chdir(_path)
        with os.popen("git remote -v") as f:
            lines = f.readlines()
        if len(lines) == 2:
            push = lines[1]
            repo = push.split("\t")
            if _origin in repo[0] and _repo in repo[1]:
                exist_remote = True
                ret_msg = f"remote {_origin} / {_repo} already exist"
            else:
                exist_remote = False
                ret_msg = f"remote {_origin} / {_repo} is unset"
        else:
            ret_msg = f"remote {_origin} / {_repo} is unset"
        success = True
    except Exception as error:
        success = False
        ret_msg = f"Git remote status can not be gathered, error: {error}"

    return ret_msg, exist_remote, success


def set_remote(_path, _state, _origin, _remote_repo, _branch):
    try:
        if _state == 'present':
            os.chdir(_path)
            os.system("git init")
            os.system("git config user.name 'oction automation'")
            os.system("git config user.email 'oction@octupus.com'")
            set_branch_command = f"git branch -M {_branch}"
            os.system(set_branch_command)
            set_remote_command = f"git remote add {_origin} {_remote_repo}"
            os.system(set_remote_command)
            success = True
            msg = f"Remote {_remote_repo} set successfully, branch {_branch}"
        else:
            set_remote_command = f"git remote remove {_origin}"
            os.system(set_remote_command)
            success = True
            msg = f"Remote {_remote_repo} removed"
    except Exception as error:
        success = False
        msg = f"Remote can not be set, error: {error}"

    return msg, success


# Main
def main():
    Output = {}
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(required=True, type='str', choices=["present", "absent"]),
            origin=dict(required=False, type='str', default='origin'),
            branch=dict(required=False, type='str', default='main'),
            remote=dict(required=True),
            path=dict(required=False, default='./')
        )
    )

    state = module.params.get("state")
    origin = module.params.get("origin")
    branch = module.params.get("branch")
    remote = module.params.get("remote")
    path = module.params.get("path")

# Lógica del modulo
    module_success = False
    msg_get_remote, exist_remote, result = get_remote(origin, remote, path)
    if exist_remote and state == 'present':
        Output['state'] = 'present'
        Output['msg'] = msg_get_remote
        Output['remote'] = remote
        module_success = True
    elif exist_remote and state == 'absent':
        msg_remote, success = set_remote(path, state, origin, remote, branch)
        if success:
            Output['state'] = 'absent'
            Output['msg'] = msg_remote
            Output['remote'] = remote
            module_success = True
        else:
            Output['state'] = 'absent'
            Output['msg'] = msg_remote
            Output['remote'] = remote
    elif not exist_remote and state == 'absent':
        Output['state'] = 'absent'
        Output['msg'] = f"remote {remote} is unset, can not be removed"
        Output['remote'] = remote
        module_success = True
    else:
        msg_remote, success = set_remote(path, state, origin, remote, branch)
        if success:
            Output['state'] = 'present'
            Output['msg'] = msg_remote
            Output['remote'] = remote
            module_success = True
        else:
            Output['state'] = 'present'
            Output['msg'] = msg_remote
            Output['remote'] = remote

# Retorno del módulo
    if module_success:
        module.exit_json(failed=False, content=Output)
    else:
        module.exit_json(failed=True, content=Output)


if __name__ == "__main__":
    main()
