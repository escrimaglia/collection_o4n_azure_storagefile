from __future__ import (absolute_import, division, print_function)
import os
from azure.storage.fileshare import ShareClient
from ansible.module_utils.basic import AnsibleModule
import re

class SelectFiles():
    def select_files(self, _file_pattern, _files_in_dir):
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
                    return status, msg_ret, [file for file in _files_in_dir if pattern_file_ext == re.split(r"\.", file)[1]]
                elif pattern_file_ext.startswith("*") and not "*" in pattern_file_name:  # file.*
                    return status, msg_ret, [file for file in _files_in_dir if pattern_file_name == re.split(r"\.", file)[0]]
                elif "*" in pattern_file_name and not "*" in pattern_file_ext:  # file*.txt
                    name_pattern = re.split(r"\*", pattern_file_name)[0]
                    return status, msg_ret, [file for file in _files_in_dir if
                                             file.startswith(name_pattern) and pattern_file_ext == re.split(r"\.", file)[1]]
                elif not "*" in pattern_file_name and "*" in pattern_file_ext:  # file.t*
                    file_ext_pattern = re.split(r"\*", pattern_file_ext)[0]
                    return status, msg_ret, [file for file in _files_in_dir if pattern_file_name == re.split(r"\.", file)[0]
                                             and file_ext_pattern in re.split(r"\.", file)[1]]
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
                                             and file_ext_pattern == re.split(r"\.", file)[1]]
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


def upload_files(_source_path, _source_file, _share, _dest_path):
    found_files = []
    # casting some text
    if _dest_path == "":
        _dest_path = "."
    try:
        # get files form local file system
        base_dir = os.getcwd() + "/" + _source_path + "/"
        search_dir = os.path.dirname(base_dir)
        files_in_dir = os.listdir(search_dir)
        # Instantiate the ShareClient from a connection string
        share = ShareClient.from_connection_string(self.connection_string, _share)
        # search files to upload
        sf = SelectFiles()
        status, msg_ret, found_files = sf.select_files(_source_file, files_in_dir)
        if len(found_files) > 0:
            for file_name in found_files:
                file = share.get_file_client(_dest_path + "/" + file_name)
                # Upload files
                with open(_source_path + "/" + file_name, "rb") as source_file:
                    file.upload_file(file_name)
            status = True
            msg_ret = {"msg": f"File <{found_files}> uploaded to Directory <{_dest_path}> in share <{_share}>"}
        else:
            status = False
            msg_ret = {
                "msg": f"File <{found_files}> not uploaded to Directory <{_dest_path}> in share <{_share}>. No file to upload"}
    except Exception as error:
        msg_ret = {"msg": f"File <{found_files}> not uploaded to Directory <{_dest_path}> in share <{_share}>",
                   "error": f"<{error}>"}
        status = False

    return status, msg_ret, found_files

