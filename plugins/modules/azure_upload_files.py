import os
from azure.storage.fileshare import ShareClient
from ansible.module_utils.basic import AnsibleModule


def upload_files(self, _source_path, _source_file, _share, _dest_path):
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