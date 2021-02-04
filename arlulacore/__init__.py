import base64
import requests
import json
import sys
import warnings
import os
import platform
import typing

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

# Object generator that converts returned JSON into a Python object


class ArlulaObj(object):
    def __init__(self, d):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
                setattr(self, a, [ArlulaObj(x) if isinstance(
                    x, dict) else x for x in b])
            else:
                setattr(self, a, ArlulaObj(b) if isinstance(b, dict) else b)

    def __repr__(self):
        return str(['{}: {}'.format(attr, value) for attr, value in self.__dict__.items()])[1:-1].replace('\'', '')

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
        self.baseURL = "https://api.arlula.com"
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

    # Searches the Arlula Archive
    def search(self,
               start: typing.Optional[str] = None,
               end: typing.Optional[str] = None,
               res: typing.Optional[typing.Union[float, str]] = None,
               lat: typing.Optional[float] = None,
               long: typing.Optional[float] = None,
               north: typing.Optional[float] = None,
               south: typing.Optional[float] = None,
               east: typing.Optional[float] = None,
               west: typing.Optional[float] = None):

        url = self.url+"/search"

        # Build a dict of non-None query parameters
        param_dict = {"start": start, "end": end,
                      "res": res, "lat": lat, "long": long,
                      "north": north, "south": south, "east": east, "west": west}
        query_params = {k: v for k, v in param_dict.items()
                        if v is not None or v == 0}

        # Send request and handle responses
        response = requests.request(
            "GET", url,
            headers=self.session.header,
            params=query_params)
        if response.status_code != 200:
            raise ArlulaSessionError(response.text)
        else:
            # Break result into a list of objects
            return [ArlulaObj(x) for x in json.loads(response.text)]

    # Orders from the Arlula Archive
    def order(self,
              id: typing.Optional[str] = None,
              eula: typing.Optional[str] = None,
              seats: typing.Optional[int] = None,
              webhooks: typing.List[str] = [],
              emails: typing.List[str] = []):

        url = self.url+"/order"

        payload = json.dumps({
            "id": id,
            "eula": eula,
            "seats": seats,
            "webhooks": webhooks,
            "emails": emails
        })

        response = requests.request(
            "POST",
            url,
            data=payload,
            headers=self.session.header)

        if response.status_code != 200:
            raise ArlulaSessionError(response.text)
        else:
            return ArlulaObj(json.loads(response.text))

# Orders uses the Session class to interface with the Arlula Orders API


class Orders:

    def __init__(self,
                 session: Session):
        self.session = session
        self.url = self.session.baseURL + "/api/order"

    # Gets a single order
    def get(self,
            id: typing.Optional[str] = None):

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
            return ArlulaObj(json.loads(response.text))

    # Lists all orders
    def list(self):

        url = self.url+"/list"

        response = requests.request(
            "GET",
            url,
            headers=self.session.header)

        if response.status_code != 200:
            raise ArlulaSessionError(response.text)
        else:
            return [ArlulaObj(r) for r in json.loads(response.text)]

    # Downloads an order resource to the specified filepath
    def get_resource(self,
                     id: typing.Optional[str] = None,
                     filepath: typing.Optional[str] = None,
                     suppress: bool = False,
                     # an optional generator that yields float or None
                     progress_generator: typing.Optional[typing.Generator[typing.Optional[float], None, None]] = None):

        url = self.url + "/resource/get"

        if filepath is None:
            raise ArlulaSessionError(
                "You must specify a filepath for the download")

        if progress_generator is not None:
            next(progress_generator)

        with open(filepath, 'wb') as f:
            querystring = {"id": id}

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
