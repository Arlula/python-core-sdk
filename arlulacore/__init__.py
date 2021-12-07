import base64
import requests
import json
import sys
import platform
import typing

from archive import OrderRequest, SearchResult, SearchRequest
from common import DetailedOrderResult, OrderResult

# Package Name
name = "arlulacore"

# User agent setting
sdk_version = "1.0.1"
py_version = sys.version.split(' ')[0]
os_version = platform.platform()
def_ua = "core-sdk " + \
    sdk_version + " python " + py_version + " OS " + os_version

# Expected API version
x_api_version = '2020-12'

# Custom Exception Class

class ArlulaSessionError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

# Custom Warning Class


class ArlulaSessionWarning(Warning):
    pass


# ArlulaSession handles the authentication method and holds subclasses for each
class Session:

    def __init__(self,
                 key: str,
                 secret: str,
                 user_agent: str = def_ua):
        # Encode the key and secret
        def atob(x): return x.encode('utf-8')
        self.token = base64.b64encode(atob(
            key + ':' + secret)).decode('utf-8')
        self.header = {
            'Authorization': "Basic "+self.token,
            'User-Agent': user_agent,
            'X-API-Version': x_api_version
        }
        self.baseURL = "https://api.arlula.com/testing"
        self.validate_creds()

    # Check the credentials are valid
    def validate_creds(self):
        url = self.baseURL+"/api/test"

        headers = self.header

        response = requests.request("GET", url, headers=headers)

        if response.status_code != 200:
            raise ArlulaSessionError(response.text)

# Archive uses the Session class to interface with the Arlula Archive API


class Archive:

    def __init__(self,
                 session: Session):
        self.session = session
        self.url = self.session.baseURL + "/api/archive"

    def search(self, request: SearchRequest) -> typing.List[SearchResult]:
        '''
            Search the Arlula imagery archive.
            Requires one of (lat, long) or (north, south, east, west).
        '''

        url = self.url+"/search"

        # Send request and handle responses
        response = requests.request(
            "GET", url,
            headers=self.session.header,
            params=request.dict())
        if response.status_code != 200:
            raise ArlulaSessionError(response.text)
        else:
            # Break result into a list of objects
            return [SearchResult(x) for x in json.loads(response.text)]

    def order(self, request: OrderRequest) -> DetailedOrderResult:
        '''
            Order from the Arlula imagery archive
        '''

        url = self.url + "/order"

        response = requests.request(
            "POST",
            url,
            data=request.dumps(),
            headers=self.session.header)

        if response.status_code != 200:
            raise ArlulaSessionError(response.text)
        else:
            return DetailedOrderResult(json.loads(response.text))

# Orders uses the Session class to interface with the Arlula Orders API


class Orders:

    def __init__(self,
                 session: Session):
        self.session = session
        self.url = self.session.baseURL + "/api/order"

    def get(self,
            id: str) -> DetailedOrderResult:
        '''
            Get details on a prior order by it's id.
        '''

        url = self.url + "/get"

        querystring = {"id": id}

        response = requests.request(
            "GET",
            url,
            headers=self.session.header,
            params=querystring)

        if response.status_code != 200:
            raise ArlulaSessionError(response.text)
        else:
            return DetailedOrderResult(json.loads(response.text))

    def list(self) -> typing.List[OrderResult]:
        '''
            List all orders made
        '''

        url = self.url+"/list"

        response = requests.request(
            "GET",
            url,
            headers=self.session.header)

        if response.status_code != 200:
            raise ArlulaSessionError(response.text)
        else:
            return [OrderResult(r) for r in json.loads(response.text)]

    # Downloads an order resource to the specified filepath
    def get_resource_as_file(self,
                     id: str,
                     filepath: str,
                     suppress: bool = False,
                     # an optional generator that yields float or None
                     progress_generator: typing.Optional[typing.Generator[typing.Optional[float], None, None]] = None) -> typing.BinaryIO:
        '''
            Get a resource. If filepath is specified, it will be streamed to that file. If filepath is omitted it will
            be stored in memory (not recommended for large files).
        '''
        url = self.url + "/resource/get"

        if filepath is None:
            raise ArlulaSessionError(
                "You must specify a filepath for the download")
        
        querystring = {"id": id}
        if progress_generator is not None:
            next(progress_generator)

        f = open(filepath, 'wb')

        # Stream response
        response = requests.request(
            "GET",
            url,
            headers=self.session.header,
            params=querystring,
            stream=True)

        total = response.headers.get('content-length')

        if response.status_code != 200:
            raise ArlulaSessionError(response.text)

        if total is None:
            f.write(response.content)
        else:
            # Write the response in chunks
            # Chunk size is the larger of 0.1% of the filesize or 1MB
            downloaded = 0
            total = int(total)
            
            for data in response.iter_content(chunk_size=max(int(total/1000), 1024*1024)):
                downloaded += len(data)
                f.write(data)

                # Track progress of download
                done = int(50*downloaded/total)
                if not suppress:
                    sys.stdout.write('\r[{}{}]{:.2%}'.format(
                        '█' * done, '.' * (50-done), downloaded/total))
                    sys.stdout.flush()
                if progress_generator is not None:
                    progress_generator.send(downloaded/total)

        if not suppress:
            sys.stdout.write('\n')
            sys.stdout.write('download complete\n')
        
        return f

    def get_resource_as_memory(self, id: str) -> bytes:
        '''
            Get a resource. If filepath is specified, it will be streamed to that file. If filepath is omitted it will
            be stored in memory (not recommended for large files).
        '''
        url = self.url + "/resource/get"

        querystring = {"id": id}

        response = requests.request(
            "GET",
            url,
            headers=self.session.header,
            params=querystring)
        
        return response.content
