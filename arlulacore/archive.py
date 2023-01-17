from __future__ import annotations
import json
import string
import textwrap
import typing
import requests

from dataclasses import dataclass
from datetime import date, datetime
from .common import ArlulaObject
from .auth import Session
from .exception import ArlulaAPIException
from .orders import DetailedOrderResult
from .util import parse_rfc3339, calculate_price, remove_none, simple_indent

Polygon = typing.Union[typing.List[typing.List[typing.List[float]]], str]

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

    def __str__(self) -> str:
        return f"Center: {self.long} {'E' if self.long < 0 else 'W'}, {self.lat} {'S' if self.lat < 0 else 'N'}"

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
    
    def __str__(self) -> str:
        return f"Coverage: {self.scene}% of scene, {self.search}% of search"

class Overlap(ArlulaObject):
    data: dict
    area: float
    percent: Percent
    polygon: typing.List[typing.List[typing.List[float]]]

    def __init__(self, data):
        self.data = data
        self.area = data["area"]
        self.percent = Percent(data["percent"])
        self.polygon = data["polygon"]

    def dict(self) -> dict:
        return self.data
    
    def __str__(self) -> str:
        return simple_indent(
        f"Overlap:\n"\
        f"Area: {self.area} sqkm\n"\
        f"{str(self.percent)}\n"\
        f"Geometry: {self.polygon}", 0, 2)

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

    def __str__(self) -> str:
        return simple_indent(
        f"License ({self.href}):\n"\
        f"Name: {self.name}\n"\
        f"Loading: {self.loading_amount} US Cents + {self.loading_percent}%\n", 0, 2)

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

    def __str__(self) -> str:
        return simple_indent(
            f"Band ({self.id}):\n"\
            f"Name: {self.name}\n"\
            f"Bandwidth: {self.min}nm - {self.max}nm\n", 0, 2)

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

    def __str__(self) -> str:
        bands = 'all' if len(self.bands) == 0 else '\n'.join(self.bands)
        return simple_indent(
            f"Bundle ({self.key}):\n"\
            f"Name: {self.name}\n"\
            f"Bands: {bands}\n"\
            f"Price: {self.price} US Cents\n", 0, 2)

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
        self.overlap = Overlap(data["overlap"])
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

    def __str__(self) -> str:

        bundles = simple_indent(''.join([str(b) for b in self.bundles]), 2, 2)
        bands = simple_indent(''.join([str(b) for b in self.bands]), 2, 2)
        license = simple_indent(''.join([str(l) for l in self.license]), 2, 2)
        return simple_indent(
            f"Result ({self.ordering_id}):\n"\
            f"Scene ID: {self.scene_id}\n"\
            f"Supplier: {self.supplier}\n"\
            f"Platform: {self.platform}\n"\
            f"Capture Date: {self.date.strftime('%Y-%m-%d')}\n"\
            f"Thumbnail URL: {self.thumbnail}\n"\
            f"Cloud Coverage: {self.cloud}%\n"\
            f"Off Nadir: {self.off_nadir} degrees\n"\
            f"Ground Sample Distance: {self.gsd} m\n"\
            f"Fulfillment Time: {self.fulfillment_time}\n"\
            f"Area: {self.area} sqkm\n"\
            f"{str(self.center)}\n"\
            f"Bounding: {self.bounding}\n"\
            f"{str(self.overlap)}"\
            f"Bands:\n"\
            f"{bands}"
            f"Bundles: \n"\
            f"{bundles}"
            f"License: \n"\
            f"{license}"
            f"Annotations: {', '.join(self.annotations)}\n", 0, 2)

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

    def __str__(self) -> str:
        s = ""
        for r in self.results:
            s += str(r)
        return s

    
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
    polygon: Polygon
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
            off_nadir: typing.Optional[float] = None,
            polygon: Polygon = None):
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
        self.polygon = polygon

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
    
    def set_polygon(self, polygon: Polygon) -> "SearchRequest":
        self.polygon = polygon
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
            "west": self.west, "supplier": self.supplier, "off-nadir": self.off_nadir,
            "polygon": json.dumps(self.polygon) if isinstance(self.polygon, list) else self.polygon}

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
            webhooks: typing.Optional[typing.List[str]] = [],
            emails: typing.Optional[typing.List[str]] = [],
            team: typing.Optional[str] = None):
        self.id = id
        self.eula = eula
        self.bundle_key = bundle_key
        self.webhooks = webhooks
        self.emails = emails
        self.team = team
    
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

    def set_team(self, team: str) -> "OrderRequest":
        self.team = team
        return self

    def valid(self) -> bool:
        return self.id != None and self.eula != None and self.bundle_key != None

    def dict(self):
        return remove_none({
            "id": self.id,
            "eula": self.eula,
            "bundleKey": self.bundle_key,
            "webhooks": self.webhooks,
            "emails": self.emails,
            "team": None if self.team == "" else self.team,
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
