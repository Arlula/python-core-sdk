import sys
import platform
import base64
import typing
import requests

from .exception import ArlulaSessionError

# Package Name
name = "arlulacore"

# User agent setting
sdk_version = "2.0.3"
py_version = sys.version.split(' ')[0]
os_version = platform.platform()
def_ua = "core-sdk " + \
    sdk_version + " python " + py_version + " OS " + os_version

# Expected API version
x_api_version = '2021-09'

class Session:
    '''
        Session handles authentication for the arlula API.
    '''

    def __init__(self,
                 key: str,
                 secret: str,
                 user_agent: typing.Optional[str] = def_ua,
                 url: typing.Optional[str] = "https://api.arlula.com"
                 ):
        # Encode the key and secret
        def atob(x): return x.encode('utf-8')
        self.token = base64.b64encode(atob(
            key + ':' + secret)).decode('utf-8')
        self.header = {
            'Authorization': "Basic "+self.token,
            'User-Agent': user_agent,
            'X-API-Version': x_api_version
        }
        self.baseURL = url
        self.validate_creds()

    # Check the credentials are valid
    def validate_creds(self):
        url = self.baseURL+"/api/test"

        headers = self.header

        response = requests.request("GET", url, headers=headers)

        if response.status_code != 200:
            raise ArlulaSessionError(response.text)
