from __future__ import annotations
import json
import string
import typing
import requests

from dataclasses import dataclass
from datetime import date, datetime
from .common import ArlulaObject
from .auth import Session
from .exception import ArlulaAPIException, ArlulaSessionError
from .orders import DetailedOrderResult
from .util import get_error_message, parse_rfc3339, calculate_price, remove_none

class CenterPoint(ArlulaObject):
    data: dict
    long: float
    lat: float

    def __init__(self, data):
        self.data = data
        self.long = data["long"]
        self.lat = data["lat"]

    def dict(self) -> dict:
        return self.data

class Percent(ArlulaObject):
    data: dict
    scene: float
    search: float

    def __init__(self, data):
        self.data = data
        self.scene = data["scene"]
        self.search = data["search"]

    def dict(self) -> dict:
        return self.data

class Overlap(ArlulaObject):
    data: dict
    area: float
    percent: Percent
    polygon: typing.List[typing.List[typing.List[float]]]

    def __init__(self, data):
        self.data = data
        self.area = data["area"]
        self.percent = data["percent"]
        self.polygon = data["polygon"]

    def dict(self) -> dict:
        return self.data

class License(ArlulaObject):
    data: dict
    name: str
    href: str
    loading_percent: float
    loading_amount: int

    def __init__(self, data):
        self.data = data
        self.name = data["name"]
        self.href = data["href"]
        self.loading_percent = data["loadingPercent"]
        self.loading_amount = data["loadingAmount"]

    def dict(self) -> dict:
        return self.data

class Band(ArlulaObject):
    data: dict
    name: str
    id: str
    min: float
    max: float

    def __init__(self, data):
        self.data = data
        self.name = data["name"]
        self.id = data["id"]
        self.min = data["min"]
        self.max = data["max"]

    def centre(self) -> float:
        '''
            Get the band centre wavelength
        '''
        return (self.max - self.min)/2

    def width(self) -> float:
        '''
            Get the band width
        '''
        return self.max - self.min

    def dict(self) -> dict:
        return self.data

class Bundle(ArlulaObject):
    data: dict
    name: str
    key: str
    bands: typing.List[str]
    price: int

    def __init__(self, data):
        self.data = data
        self.name = data["name"]
        self.key = data["key"]
        self.bands = data["bands"]
        self.price = data["price"]

    def dict(self) -> dict:
        return self.data

class SearchResult(ArlulaObject):
    data: dict
    scene_id: str
    supplier: str
    platform: str
    date: datetime
    thumbnail: str
    cloud: float
    off_nadir: float
    gsd: float
    bands: typing.List[Band]
    area: float
    center: CenterPoint
    bounding: typing.List[typing.List[typing.List[float]]]
    overlap: Overlap
    fulfillment_time: float
    ordering_id: str
    bundles: typing.List[Bundle]
    license: typing.List[License]
    annotations: typing.List[str]

    def __init__(self, data):
        self.data = data
        self.scene_id = data["sceneID"]
        self.supplier = data["supplier"]
        self.platform = data["platform"]
        self.date = parse_rfc3339(data["date"])
        self.thumbnail = data["thumbnail"]
        self.cloud = data["cloud"]
        self.off_nadir = data["offNadir"]

        self.gsd = data["gsd"]

        self.bands = []
        self.bands += [Band(b) for b in data["bands"]]

        self.area = data["area"]
        self.center = CenterPoint(data["center"])
        self.bounding = data["bounding"]
        self.overlap = data["overlap"]
        self.fulfillment_time = data["fulfillmentTime"]

        self.ordering_id = data["orderingID"]
            
        self.bundles = []
        self.bundles += [Bundle(b) for b in data["bundles"]]
        self.license = []
        self.license += [License(l) for l in data["license"]]

        self.annotations = []
        if "annotations" in data:
            self.annotations = data["annotations"]

    def calculate_price(self, license_href: string, bundle_key: string) -> int:
        '''
            Wrapper for util.calculate_price, returns price in US Cents. Raises error in the case of invalid license_name or bundle_key
        '''
        
        bundle = None
        license = None
        
        for b in self.bundles:
            if bundle.key == bundle_key:
                bundle = b
        
        for l in self.license:
            if license.href == license_href:
                license = l

        if bundle == None:
            raise ValueError("Invalid bundle_key")

        if license == None:
            raise ValueError("Invalid license_href")

        return calculate_price(bundle.price, license.loading_percent, license.loading_amount)

    def dict(self) -> dict:
        return self.data

class SearchResponse(ArlulaObject):
    data: dict
    state: string
    errors: typing.List[str]
    warnings: typing.List[str]
    results: typing.List[SearchResult]

    def __init__(self, data):
        self.data = data
        self.state = ""
        self.errors = []
        self.warnings = []
        self.results = []

        if "state" in data:
            self.state = data["state"]
        if "errors" in data:
            self.errors += data["errors"]
        if "warnings" in data:
            self.warnings += data["warnings"]
        if "results" in data:
            self.results = [SearchResult(e) for e in data["results"]]

    def dict(self) -> dict:
        return self.data

class SearchRequest():
    start: date
    gsd: float
    end: date
    lat: float
    long: float
    north: float
    south: float
    east: float
    west: float
    supplier: str
    off_nadir: float
    cloud: float

    def __init__(self, start: date,
            gsd: float,
            cloud: typing.Optional[float] = None,
            end: typing.Optional[date] = None,
            lat: typing.Optional[float] = None,
            long: typing.Optional[float] = None,
            north: typing.Optional[float] = None,
            south: typing.Optional[float] = None,
            east: typing.Optional[float] = None,
            west: typing.Optional[float] = None,
            supplier: typing.Optional[str] = None,
            off_nadir: typing.Optional[float] = None):
        self.start = start
        self.cloud = cloud
        self.gsd = gsd
        self.end = end
        self.lat = lat
        self.long = long
        self.north = north
        self.south = south
        self.east = east
        self.west = west
        self.supplier = supplier
        self.off_nadir = off_nadir

    def set_point_of_interest(self, lat: float, long: float) -> "SearchRequest":
        self.lat = lat
        self.long = long
        return self
    
    def set_area_of_interest(self, north: float, south: float, east: float, west: float) -> "SearchRequest":
        self.north = north
        self.south = south
        self.west = west
        self.east = east
        return self

    def set_supplier(self, supplier: str) -> "SearchRequest":
        self.supplier = supplier
        return self

    def set_maximum_gsd(self, gsd: float) -> "SearchRequest":
        self.gsd = gsd
        return self

    def set_start(self, start: date) -> "SearchRequest":
        self.start = start
        return self

    def set_end(self, end: date) -> "SearchRequest":
        self.end = end
        return self
    
    def set_between_dates(self, start: date, end: date) -> "SearchRequest":
        self.start = start
        self.end = end
        return self
    
    def set_maximum_off_nadir(self, off_nadir: float) -> "SearchRequest":
        self.off_nadir = off_nadir
        return self

    def set_maximum_cloud_cover(self, cloud: float) -> "SearchRequest":
        self.cloud = cloud
        return self

    def valid_point_of_interest(self) -> bool:
        return self.lat != None and self.long != None

    def valid_area_of_interest(self) -> bool:
        return self.north != None and self.south != None and self.east != None and self.west != None
    
    def valid(self) -> bool:
        return (self.valid_area_of_interest() or self.valid_point_of_interest) and self.start != None and self.gsd != None
    
    def dict(self):
        param_dict = {
            "start": str(self.start) if self.start != None else None, 
            "end": str(self.end) if self.end != None else None,
            "gsd": self.gsd, "cloud": self.cloud,
            "lat": self.lat, "long": self.long,
            "north": self.north, "south": self.south, "east": self.east, 
            "west": self.west, "supplier": self.supplier, "off-nadir": self.off_nadir}

        query_params = {k: v for k, v in param_dict.items()
            if v is not None}

        return remove_none(query_params)

class OrderRequest(ArlulaObject):

    id: str
    eula: str
    bundle_key: str
    webhooks: typing.List[str]
    emails: typing.List[str]

    def __init__(self,
            id: str,
            eula: str,
            bundle_key: str,
            webhooks: typing.List[str] = [],
            emails: typing.List[str] = []):
        self.id = id
        self.eula = eula
        self.bundle_key = bundle_key
        self.webhooks = webhooks
        self.emails = emails
    
    def add_webhook(self, webhook: str) -> "OrderRequest":
        self.webhooks.append(webhook)
        return self
    
    def set_webhooks(self, webhooks: typing.List[str]) -> "OrderRequest":
        self.webhooks = webhooks
        return self

    def add_email(self, email: str) -> "OrderRequest":
        self.emails.append(email)
        return self
    
    def set_emails(self, emails: typing.List[str]) -> "OrderRequest":
        self.emails = emails
        return self

    def valid(self) -> bool:
        return self.id != None and self.eula != None and self.bundle_key != None

    def dict(self):
        return remove_none({
            "id": self.id,
            "eula": self.eula,
            "bundleKey": self.bundle_key,
            "webhooks": self.webhooks,
            "emails": self.emails
        })


class ArchiveAPI:
    '''
        Archive is used to interface with the Arlula Archive API
    '''

    def __init__(self,
                 session: Session):
        self.session = session
        self.url = self.session.baseURL + "/api/archive"

    def search(self, request: SearchRequest) -> SearchResponse:
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
            raise ArlulaAPIException(response)
        else:
            resp_data = json.loads(response.text)
            # Construct an instance of `SearchResponse`
            return SearchResponse(resp_data)

    def order(self, request: OrderRequest) -> DetailedOrderResult:
        '''
            Order from the Arlula imagery archive
        '''

        url = self.url + "/order"

        response = requests.request(
            "POST",
            url,
            data=json.dumps(request.dict()),
            headers=self.session.header)

        if response.status_code != 200:
            raise ArlulaAPIException(response)
        else:
            return DetailedOrderResult(json.loads(response.text))
