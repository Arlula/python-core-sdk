from __future__ import annotations
import enum
import json
import string
import textwrap
import typing
import requests

from dataclasses import dataclass
from datetime import date, datetime
from .common import ArlulaObject, Band, Bundle, License, SortDefinition
from .auth import Session
from .exception import ArlulaAPIException
from .orders import DetailedOrderResult
from .util import parse_rfc3339, calculate_price, remove_none, simple_indent

Polygon = typing.List[typing.List[typing.List[float]]]

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
    licenses: typing.List[License]
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
        self.licenses = []
        self.licenses += [License(l) for l in data["licenses"]]

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
            if b.key == bundle_key:
                bundle = b
        
        for l in self.licenses:
            if l.href == license_href:
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
        licenses = simple_indent(''.join([str(l) for l in self.licenses]), 2, 2)
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
            f"Licenses: \n"\
            f"{licenses}"
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

class ArchiveSearchSortFields(str, enum.Enum):
    """
        An enumeration of fields that can be sorted by on archive search requests.
    """

    scene_id = "sceneID"
    supplier = "supplier"
    date = "date"
    cloud = "cloud"
    off_nadir = "offNadir"
    gsd = "gsd"
    area = "area"
    overlap = "overlap"
    overlap_area = "overlap.area"
    overlap_percent = "overlap.percent"
    fulfillment = "fulfillment"

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
    sort_definition: SortDefinition[ArchiveSearchSortFields]

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
            polygon: typing.Optional[Polygon] = None,
            sort_definition: typing.Optional[SortDefinition[ArchiveSearchSortFields]] = None,
        ):
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
        self.sort_definition = sort_definition

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
    
    def set_sort_definition(self, sort_definition: SortDefinition[ArchiveSearchSortFields]):
        self.sort_definition = sort_definition
        return self

    def valid_point_of_interest(self) -> bool:
        return self.lat != None and self.long != None

    def valid_area_of_interest(self) -> bool:
        return self.north != None and self.south != None and self.east != None and self.west != None
    
    def valid(self) -> bool:
        return (self.valid_area_of_interest() or self.valid_point_of_interest) and self.start != None and self.gsd != None
    
    def dict(self):
        d = {
            "start": str(self.start) if self.start != None else None, 
            "end": str(self.end) if self.end != None else None,
            "gsd": self.gsd, 
            "cloud": self.cloud,
            "offNadir": self.off_nadir,
            "supplier": self.supplier,
        }

        # Add the polygon if not None
        if self.polygon != None:
            d["polygon"] = self.polygon if isinstance(self.polygon, list) else self.polygon
        # Add boundingBox if all related not None
        elif self.north != None and self.east != None and self.west != None and self.south != None:
            d["boundingBox"] = {
                "north": self.north,
                "east": self.east,
                "west": self.west,
                "south": self.south,
            }
        # Add latLong if all related not None
        elif self.lat != None and self.long != None:
            d["latLong"] = {
                "latitude": self.lat,
                "longitude": self.long,
            }
        
        if self.sort_definition is not None:
            d["sort"] = self.sort_definition.dict()

        return remove_none(d)

class OrderRequest(ArlulaObject):

    id: str
    eula: str
    bundle_key: str
    webhooks: typing.List[str]
    emails: typing.List[str]
    team: str
    payment: str

    def __init__(self,
            id: str,
            eula: str,
            bundle_key: str,
            webhooks: typing.Optional[typing.List[str]] = [],
            emails: typing.Optional[typing.List[str]] = [],
            team: typing.Optional[str] = None,
            payment: typing.Optional[str] = None):
        self.id = id
        self.eula = eula
        self.bundle_key = bundle_key
        self.webhooks = webhooks
        self.emails = emails
        self.team = team
        self.payment = payment
    
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
    
    def set_payment(self, payment: str) -> "OrderRequest":
        self.payment = payment
        return payment

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
            "payment": None if self.payment == "" else self.payment,
        })

class BatchOrderRequest():

    orders: typing.List[OrderRequest]
    webhooks: typing.List[str]
    emails: typing.List[str]
    team: str
    payment: str

    def __init__(
        self, 
        orders: typing.Optional[typing.List[OrderRequest]] = [],
        webhooks: typing.Optional[typing.List[str]] = [],
        emails: typing.Optional[typing.List[str]] = [],
        team: typing.Optional[str] = None,
        payment: typing.Optional[str] = None):

        self.orders = orders
        self.webhooks = webhooks
        self.emails = emails
        self.team = team
        self.payment = payment

    def add_order(self, order: OrderRequest) -> "BatchOrderRequest":
        self.orders.append(order)
        return self
    
    def set_orders(self, orders: typing.List[OrderRequest]) -> "BatchOrderRequest":
        self.orders = orders
        return self

    def add_webhook(self, webhook: str) -> "BatchOrderRequest":
        self.webhooks.append(webhook)
        return self
    
    def set_webhooks(self, webhooks: typing.List[str]) -> "BatchOrderRequest":
        self.webhooks = webhooks
        return self

    def add_email(self, email: str) -> "BatchOrderRequest":
        self.emails.append(email)
        return self
    
    def set_emails(self, emails: typing.List[str]) -> "BatchOrderRequest":
        self.emails = emails
        return self

    def set_team(self, team: str) -> "BatchOrderRequest":
        self.team = team
        return self
    
    def set_payment(self, payment: str) -> "BatchOrderRequest":
        self.payment = payment
        return self

    def dict(self):
        d = {
            "orders": [o.dict() for o in self.orders],
            "webhooks": self.webhooks,
            "emails": self.emails,
            "team": None if self.team == "" else self.team,
            "payment": None if self.payment == "" else self.payment,
        }

        return remove_none(d)



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
            "POST", url,
            headers=self.session.header,
            data=json.dumps(request.dict()))
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
        
    def batch_order(self, request: BatchOrderRequest) -> typing.List[DetailedOrderResult]:
        '''
            Order multiple scenes from the Arlula imagery archive
        '''

        url = self.url + "/order/batch"

        response = requests.request(
            "POST",
            url,
            data=json.dumps(request.dict()),
            headers=self.session.header,
        )

        if response.status_code != 200:
            raise ArlulaAPIException(response)
        else:
            return [DetailedOrderResult(r) for r in json.loads(response.text)]
