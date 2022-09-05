'''
    Objects specific to the orders api
'''

from datetime import datetime
import typing
import json
import requests
import sys
import textwrap

from .auth import Session
from .exception import ArlulaAPIException, ArlulaSessionError
from .common import ArlulaObject
from .util import parse_rfc3339, simple_indent

class Resource(ArlulaObject):
    data: dict
    id: str
    created_at: datetime
    updated_at: datetime
    order: str
    name: str
    type: str
    format: str
    roles: typing.List[str]
    size: int
    checksum: str

    def __init__(self, data):
        self.data = data
        self.id = data["id"]
        self.created_at = parse_rfc3339(data["createdAt"])
        self.updated_at = parse_rfc3339(data["updatedAt"])
        self.order = data["order"]
        self.name = data["name"]
        self.type = data["type"]
        self.format = data["format"]
        self.roles = data["roles"]
        self.size = data["size"]
        self.checksum = data["checksum"]

    def __str__(self) -> str:
        text = simple_indent(
            f"Resource {self.id}\n"\
            f"Created At: {self.created_at.isoformat()}\n"\
            f"Updated At: {self.updated_at.isoformat()}\n"\
            f"Order ID: {self.order}\n"\
            f"Name: {self.name}\n"\
            f"Type: {self.type}\n"\
            f"Format: {self.format}\n"\
            f"Roles: {self.roles}\n"\
            f"Size: {self.size} Bytes\n"\
            f"Checksum: {self.checksum}\n", 0, 2)
        return text

    def dict(self):
        return self.data

class OrderResult(ArlulaObject):
    data: dict
    id: str
    created_at: datetime
    updated_at: datetime
    supplier: str
    ordering_id: str
    scene_id: str
    status: str
    total: int
    type: str
    expiration: typing.Optional[str]

    def __init__(self, data):
        self.data = data
        self.id = data["id"]
        self.created_at = parse_rfc3339(data["createdAt"])
        self.updated_at = parse_rfc3339(data["updatedAt"])
        self.supplier = data["supplier"]
        self.ordering_id = data["orderingID"]
        self.scene_id = data["sceneID"]
        self.status = data["status"]
        self.total = data["total"]
        self.type = data["type"]
        self.expiration = data["expiration"]

    def __str__(self) -> str:
        text = simple_indent(
            f"Order ({self.id})\n"\
            f"Created At: {self.created_at}\n"\
            f"Updated At: {self.updated_at}\n"\
            f"Supplier: {self.supplier}\n"\
            f"Ordering ID: {self.ordering_id}\n"\
            f"Scene ID: {self.scene_id}\n"\
            f"Status: {self.status}\n"\
            f"Total: {self.total}\n"\
            f"Type: {self.type}\n"\
            f"Expiration: {self.expiration}\n", 0, 2)
        return text

    def dict(self) -> dict:
        return self.data

class DetailedOrderResult(ArlulaObject):
    data: dict
    id: str
    created_at: datetime
    updated_at: datetime
    supplier: str
    ordering_id: str
    scene_id: str
    status: str
    total: int
    type: str
    expiration: typing.Optional[str]
    resources: typing.List[Resource]

    def __init__(self, data):
        self.data = data
        self.id = data["id"]
        self.created_at = parse_rfc3339(data["createdAt"])
        self.updated_at = parse_rfc3339(data["updatedAt"])
        self.supplier = data["supplier"]
        self.ordering_id = data["orderingID"]
        self.scene_id = data["sceneID"]
        self.status = data["status"]
        self.total = data["total"]
        self.type = data["type"]
        self.expiration = data["expiration"]
        self.resources = [Resource(x) for x in data["resources"]]
    
    def __str__(self) -> dict:
        text = simple_indent(
            f"Detailed Order ({self.id})\n"\
            f"Created At: {self.created_at}\n"\
            f"Updated At: {self.updated_at}\n"\
            f"Supplier: {self.supplier}\n"\
            f"Ordering ID: {self.ordering_id}\n"\
            f"Scene ID: {self.scene_id}\n"\
            f"Status: {self.status}\n"\
            f"Total: {self.total}\n"\
            f"Type: {self.type}\n"\
            f"Expiration: {self.expiration}\n", 0, 2)
        for r in self.resources:
            text += simple_indent(str(r), 4, 4)   
        return text

    def dict(self) -> dict:
        return self.data

class OrdersAPI:
    '''
        Orders is used to interface with the Arlula Orders API
    '''

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
            raise ArlulaAPIException(response)
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
            raise ArlulaAPIException(response)
        else:
            return [OrderResult(r) for r in json.loads(response.text)]

    def get_resource_as_file(self,
                     id: str,
                     filepath: str,
                     suppress: bool = False,
                     progress_generator: typing.Optional[typing.Generator[typing.Optional[float], None, None]] = None) -> typing.BinaryIO:
        '''
            Get a resource and stream it to the specified file. If supress is true, it will output extra information to standard output.
            This is recommended for large files. Returns the file, which must be closed. The returned file is seeked back to it's beginning.
        '''

        url = self.url + "/resource/get"

        if filepath is None:
            raise ArlulaSessionError(
                "You must specify a filepath for the download")
        
        querystring = {"id": id}
        if progress_generator is not None:
            next(progress_generator)

        f = open(filepath, "w+b")

        # Stream response
        response = requests.request(
            "GET",
            url,
            headers=self.session.header,
            params=querystring,
            stream=True)

        total = response.headers.get('content-length')

        if response.status_code != 200:
            raise ArlulaAPIException(response)

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

        # So the file is able to be read from the beginning.
        f.seek(0)
        
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
