from select_files_from_pattern import SelectFiles
from azure.storage.fileshare import ShareClient

def download_files(self, _share, _source_path, _source_file, _dest_path):
    found_files = []
    _source_path_cast = _source_path
    # casting some vars
    if _source_path == "":
        _source_path_cast = "."
    # check if share and path exist in Account Storage
    try:
        status, msg_ret, output = self.list_shares_in_service()
        if status:
            share_exist = [share['name'] for share in output['shares'] if share['name'] == _share]
            if len(share_exist) != 1:
                status = False
                msg_ret = f"Invalid File Share name: <{_share}>. Does not exist in Account Storage <{self.account_name}>"
                return (status, msg_ret, found_files)
    except Exception as error:
        status = False
        msg_ret = f"Invalid File Share name: <{_share}>. Listing Shares process failed"
        return (status, msg_ret, found_files)
    # Download files
    try:
        # Instantiate the ShareFileClient from a connection string
        share = ShareClient.from_connection_string(self.connection_string, _share)
        status, msg_ret_pattern, files_in_share = self.list_files_in_share(_share, _source_path_cast)
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