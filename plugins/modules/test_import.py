from o4n_azure_upload_files import upload_files
from vars import connection_string

status_up, msg_ret, files = upload_files("share-to-test", connection_string, "", "*.py", "")
print (status_up, msg_ret, files)
