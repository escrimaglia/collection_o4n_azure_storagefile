

def list_files_in_share(_account_name, _connection_string, _share, _dir):
    import re
    import azure.core.exceptions as aze
    from azure.storage.fileshare import ShareClient

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