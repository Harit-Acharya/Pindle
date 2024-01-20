#!/usr/bin/python3
from __future__ import unicode_literals
import onedrivesdk
#from onedrivesdk.helpers import GetAuthCodeServer, http_provider_with_proxy



def Authenticate():
    base_url = 'https://api.onedrive.com/v1.0/'
    redirect_uri = "http://localhost:8080/"
    client_secret = 'ews~S-~G8qr459UdX.juBHi6HoDdC~101m'
    scopes = ['wl.signin', 'wl.offline_access', 'onedrive.readwrite']
    client_id = 'cb1a2f6a-8c5d-43d9-ba34-3dab767fa0ac'
    client = onedrivesdk.get_default_client(client_id, scopes=scopes)
    auth_url = client.auth_provider.get_auth_url(redirect_uri)
    http = onedrivesdk.HttpProvider()
    code = GetAuthCodeServer.get_auth_code(auth_url, redirect_uri)
    auth_provider = onedrivesdk.AuthProvider(http_provider=http,
                                             client_id=client_id,
                                             scopes=scopes)
    auth_provider.authenticate(code, redirect_uri, client_secret)
    # Save the session for later
    auth_provider.save_session()
    return client


def LoadSession():
    base_url = 'https://api.onedrive.com/v1.0/'
    http = onedrivesdk.HttpProvider()
    client_id = 'cb1a2f6a-8c5d-43d9-ba34-3dab767fa0ac'
    scopes = ['wl.signin', 'wl.offline_access', 'onedrive.readwrite']
    auth_provider = onedrivesdk.AuthProvider(http_provider=http,
                                             client_id=client_id,
                                             scopes=scopes)
    auth_provider.load_session()
    auth_provider.refresh_token()
    client = onedrivesdk.OneDriveClient(base_url, auth_provider, http)

    # return client_saved
    return client


if __name__ == "__main__":
    Authenticate()
