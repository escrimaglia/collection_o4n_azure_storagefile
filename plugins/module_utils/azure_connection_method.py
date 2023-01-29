from azure.storage.fileshare import ShareClient
from azure.storage.fileshare import ShareServiceClient

class FileAuthSamples():

    def authentication_connection_string(self, _conn_string):
        # Instantiate the ShareServiceClient from a connection string
        share_service_client = ShareServiceClient.from_connection_string(_conn_string)

        return share_service_client


    def authentication_shared_access_key(self, _account_url, _access_key):
        # Instantiate a ShareServiceClient using a shared access key
        share_service_client = ShareServiceClient(
            account_url=_account_url,
            credential=_access_key
        )
        
        return share_service_client
