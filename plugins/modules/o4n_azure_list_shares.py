from azure.storage.fileshare import ShareServiceClient

def list_shares_in_service(_account_name, _connection_string):
    output = {}
    try:
        # Instantiate the ShareServiceClient from a connection string
        file_service = ShareServiceClient.from_connection_string(_connection_string)
        # List the shares in the file service
        output = {"shares": list(file_service.list_shares())}
        status = True
        msg_ret = {"msg": f"List of Shares created in account <{_account_name}>"}
    except Exception as error:
        status = False
        msg_ret = {"msg": f"List of Shares not created in account <{_account_name}>", "error": f"<{error.args}>"}

    return status, msg_ret, output