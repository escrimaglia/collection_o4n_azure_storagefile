from azure.storage.fileshare import ShareClient
import azure.core.exceptions as aze

def list_directories_in_share(_account_name, _connection_string, _share, _dir):
    output = []
    status, msg_ret, shares_in_service = list_shares_in_service(_account_name, _connection_string)
    if status:
        share_exist = [share_name for share_name in shares_in_service if share_name == _share]
    if len(share_exist) == 1:
        share = ShareClient.from_connection_string(_connection_string, _share)
        try:
            # List directories in share
            my_files = {"results": list(share.list_directories_and_files(directory_name=_dir))}
            status = True
            msg_ret = f"List of Directories created for Directory </{_dir}> in share <{_share}>"
            output = [{"name": file['name'],"file_id": file['file_id'],"is_directory": file['is_directory']} for file in my_files['results'] if file['is_directory']]
        except aze.ResourceNotFoundError:
            msg_ret = f"List of Directories not created for Directory </{_dir}> in share <{_share}>. Error: Directory not found"
            status = False
        except Exception as error:
            status = False
            msg_ret = f"List of Directories not created for Directory </{_dir}> in share <{_share}>. Error: <{error}>"
    else:
        msg_ret = f"List of Directories not created for Directory </{_dir}> in share <{_share}>. Error: Share not found"
        status = False

    return status, msg_ret, output