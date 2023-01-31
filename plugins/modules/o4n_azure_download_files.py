from azure.storage.fileshare import ShareClient
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



def download_files(_account_name, _connection_string, _share, _source_path, _source_file, _dest_path):
    found_files = []
    _source_path_cast = _source_path
    # casting some vars
    if _source_path == "":
        _source_path_cast = "."
    # check if share and path exist in Account Storage
    try:
        status, msg_ret, output = list_shares_in_service()
        if status:
            share_exist = [share['name'] for share in output['shares'] if share['name'] == _share]
            if len(share_exist) != 1:
                status = False
                msg_ret = f"Invalid File Share name: <{_share}>. Does not exist in Account Storage <{account_name}>"
                return (status, msg_ret, found_files)
    except Exception as error:
        status = False
        msg_ret = f"Invalid File Share name: <{_share}>. Listing Shares process failed"
        return (status, msg_ret, found_files)
    # Download files
    try:
        # Instantiate the ShareFileClient from a connection string
        share = ShareClient.from_connection_string(self.connection_string, _share)
        status, msg_ret_pattern, files_in_share = self.list_files_in_share(_account_name, _connection_string,_share, _source_path_cast)
        if status:
            sf = SelectFiles()
            status, msg_ret, found_files = sf.select_files(_source_file,
                                                           [file['name'] for file in files_in_share if file])
            if len(found_files) > 1:
                for file_name in found_files:
                    file = share.get_file_client(_source_path + "/" + file_name)
                    # Download the file
                    with open(_dest_path + "/" + file_name, "wb") as data:
                        stream = file.download_file()
                        data.write(stream.readall())
                status = True
                msg_ret = {"msg": f"File <{found_files}> downloaded to Directory <{_dest_path}> from share <{_share}>"}
            elif len(found_files) == 1:
                file = share.get_file_client(_source_path + "/" + found_files[0])
                # Download the file
                with open(_dest_path + "/" + found_files[0], "wb") as data:
                    stream = file.download_file()
                    data.write(stream.readall())
                status = True
                msg_ret = {
                    "msg": f"File <{found_files[0]}> downloaded to Directory <{_dest_path}> from share <{_share}>"}
            else:
                status = False
                msg_ret = {
                    "msg": f"File <{found_files}> not downloaded to Directory <{_dest_path}> from share <{_share}>. No file to download"}
        else:
            msg_ret = f"Invalid Directory: <{_source_path}> in File Share <{_share}>"
            status = False
    except Exception as error:
        msg_ret = {"msg": f"File <{found_files}> not downloaded to Directory <{_dest_path}>", "error": f"<{error}>"}
        status = False

    return status, msg_ret, found_files