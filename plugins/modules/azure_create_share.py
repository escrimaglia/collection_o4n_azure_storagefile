from azure.storage.fileshare import ShareClient

def create_file_share(self, _share):
    output = {}
    try:
        # Instantiate the ShareClient from a connection string
        share = ShareClient.from_connection_string(self.connection_string, share_name=_share)
        # Create the share
        share.create_share()
        output = {"properties": share.get_share_properties()}
        status = True
        msg_ret = {"msg", f"File Share <{_share}> created in account <{self.account_name}>"}
    except Exception as error:
        msg_ret = {"msg": f"File Share <{_share}> not created in <{self.account_name}>", "error": f"<{error}>"}
        status = False

    return status, msg_ret, output