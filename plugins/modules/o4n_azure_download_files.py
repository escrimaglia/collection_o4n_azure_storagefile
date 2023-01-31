from azure.storage.fileshare import ShareClient
import re, sys, os
from o4n_azure_list_shares import list_shares_in_service
from o4n_azure_list_files import list_files_in_share

module_path_name =  (os.path.split(os.path.abspath(__file__)))
os.chdir(module_path_name[0])
os.chdir("..")
module_utils_path = os.getcwd()
os.chdir(module_path_name[0])
sys.path.insert(1, module_utils_path)

from module_utils.util_select_files_pattern import select_files

__metaclass__ = type

ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'octupus',
                    'metadata_version': '1.1'}

DOCUMENTATION = """
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
        required: True
        type: str
    connection_string:
        description:
            String that include URL & Token to connect to Azure Storage Account. Provided by Azure Portal
            Storage Account -> Access Keys -> Connection String
        required: True
        type: str
    share:
        description:
            Name of the share to be managed
        required: True
        type: str
    source_path:
        description:
            path (directory) where files to be downloaded are
        required: False
        type: str
    files:
        description:
            files to deleted from File ShRE
        required: True
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
            path (directory) where files must be downloaded
        required: False
        type: str
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


def download_files(_account_name, _connection_string, _share, _source_path, _files, _local_path):
    found_files = []
    # casting some vars
    _dest_path = re.sub(r"^\/*", "", _dest_path)
    # check if share and path exist in Account Storage
    try:
        status, msg_ret, output = list_shares_in_service()
        if status:
            share_exist = [share['name'] for share in output['shares'] if share['name'] == _share]
            if len(share_exist) != 1:
                status = False
                msg_ret = f"Invalid File Share name: <{_share}>. Does not exist in Account Storage <{_account_name}>"
                return (status, msg_ret, found_files)
    except Exception as error:
        status = False
        msg_ret = f"Invalid File Share name: <{_share}>. Listing Shares process failed"
        return (status, msg_ret, found_files)
    # Download files
    try:
        # Instantiate the ShareFileClient from a connection string
        share = ShareClient.from_connection_string(_connection_string, _share)
        status, msg_ret_pattern, files_in_share = list_files_in_share(_account_name, _connection_string,_share, _source_path)
        if status:
            status, msg_ret, found_files = select_files(_files,
                                                           [file['name'] for file in files_in_share if file])
            if len(found_files) > 1:
                for file_name in found_files:
                    file = share.get_file_client(_source_path + "/" + file_name)
                    # Download the file
                    with open(_local_path + "/" + file_name, "wb") as data:
                        stream = file.download_file()
                        data.write(stream.readall())
                status = True
                msg_ret = {"msg": f"File <{found_files}> downloaded to Directory <{_local_path}> from share <{_share}>"}
            elif len(found_files) == 1:
                file = share.get_file_client(_source_path + "/" + found_files[0])
                # Download the file
                with open(_local_path + "/" + found_files[0], "wb") as data:
                    stream = file.download_file()
                    data.write(stream.readall())
                status = True
                msg_ret = {
                    "msg": f"File <{found_files[0]}> downloaded to Directory <{_local_path}> from share <{_share}>"}
            else:
                status = False
                msg_ret = {
                    "msg": f"File <{found_files}> not downloaded to Directory <{_local_path}> from share <{_share}>. No file to download"}
        else:
            msg_ret = f"Invalid Directory: <{_source_path}> in File Share <{_share}>"
            status = False
    except Exception as error:
        msg_ret = {"msg": f"File <{found_files}> not downloaded to Directory <{_local_path}>", "error": f"<{error}>"}
        status = False

    return status, msg_ret, found_files