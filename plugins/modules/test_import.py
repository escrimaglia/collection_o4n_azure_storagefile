from o4n_azure_upload_files import upload_files
from o4n_azure_download_files import download_files
from vars import connection_string
from vars import account_name
status_up, msg_ret, files = download_files(account_name, connection_string, "share-to-test", "/dir1/dir2", "__cache__", "../../roles")
print (status_up, msg_ret, files)
