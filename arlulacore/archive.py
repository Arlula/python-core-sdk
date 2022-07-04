import json
import string
import typing
import requests

from dataclasses import dataclass
from datetime import date, datetime
from .common import ArlulaObject
from .auth import Session
from .exception import ArlulaSessionError
from .orders import DetailedOrderResult
from .util import parse_rfc3339


@dataclass
class CenterPoint(ArlulaObject):
    long: float
    lat: float

@dataclass
class Percent(ArlulaObject):
    scene: float
    search: float

@dataclass
class Overlap(ArlulaObject):
    area: float
    percent: Percent
    polygon: typing.List[typing.List[typing.List[float]]]

@dataclass
class License(ArlulaObject):
    name: str
    href: str
    loading_percent: float
    loading_amount: int

@dataclass
class Band(ArlulaObject):
    name: str
    id: str
    min: float
    max: float

@dataclass
class BundleOption(ArlulaObject):
    key: str
    bands: typing.List[str]
    price: int

# Legacy Dataclasses
@dataclass
class Seat(ArlulaObject):
    min: int
    max: int
    additional: int

@dataclass
class Price(ArlulaObject):
    base: float
    seats: typing.List[Seat]

class SearchResult(ArlulaObject):
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
    bundles: typing.List[BundleOption]
    license: typing.List[License]
    annotations: typing.List[str]

    def __init__(self, data):
        self.scene_id = data["sceneID"]
        self.supplier = data["supplier"]
        self.platform = data["platform"]
        self.date = parse_rfc3339(data["date"])
        self.thumbnail = data["thumbnail"]
        self.cloud = data["cloud"]
        self.off_nadir = data["offNadir"]

        if ("gsd" in data):
            self.gsd = data["gsd"]
        else:
            self.gsd = data["resolution"] # legacy

        self.bands = []
        if ("bands" in data):
            self.bands += [Band(**e) for e in data["bands"]]

        self.area = data["area"]
        self.center = CenterPoint(**data["center"])
        self.bounding = data["bounding"]
        self.overlap = data["overlap"]
        self.fulfillment_time = data["fulfillmentTime"]

        if ("orderingID" in data):
            self.ordering_id = data["orderingID"]
        else:
            self.ordering_id = data["id"] # legacy
            
        self.bundles = []
        if ("bundles" in data):
            self.bundles += [BundleOption(**e) for e in data["bundles"]]
        self.license = []
        if ("license" in data):
            self.license += [License(**e) for e in data["license"]]

        self.annotations = data["annotations"]

        # Legacy properties (include in new structure if present)
        if ("price" in data):
            tmp = Price(**data["price"])
            self.bundles.append(BundleOption("default", [], tmp.base))
        if ("eula" in data):
            self.license.append(License("default", data["eula"], 0, 0))

class SearchResponse(ArlulaObject):
    state: string
    errors: typing.List[str]
    warnings: typing.List[str]
    results: typing.List[SearchResult]

    def __init__(self, data):
        self.state = ""
        self.errors = []
        self.warnings = []

        if (type(data) == list):
            self.results = data
            return

        if ("state" in data):
            self.state = data["state"]
        if ("errors" in data):
            self.errors += data["errors"]
        if ("warnings" in data):
            self.warnings += data["warnings"]
        self.results = [SearchResult(e) for e in data["results"]]

class SearchRequest(ArlulaObject):
    start: date
    res: float
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
            res: float,
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
        self.res = res
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

    def set_maximum_resolution(self, res: float) -> "SearchRequest":
        self.res = res
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
    
    def dict(self):
        param_dict = {
            "start": str(self.start) if self.start != None else None, 
            "end": str(self.end) if self.end != None else None,
            "res": self.res, "cloud": self.cloud,
            "lat": self.lat, "long": self.long,
            "north": self.north, "south": self.south, "east": self.east, 
            "west": self.west, "supplier": self.supplier, "off-nadir": self.off_nadir}

        query_params = {k: v for k, v in param_dict.items()
            if v is not None}

        return query_params

class OrderRequest:

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

    def dumps(self):
        return json.dumps({
            "id": self.id,
            "eula": self.eula,
            "bundle_key": self.bundle_key,
            "seats": 1, # For legacy support
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
            resp_data = json.loads(response.text)
            # Break result into a list of objects (Legacy)
            if (type(resp_data) == list):
                lst = [SearchResult(x) for x in resp_data]
                return SearchResponse(lst)
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
            data=request.dumps(),
            headers=self.session.header)

        if response.status_code != 200:
            raise ArlulaSessionError(response.text)
        else:
            return DetailedOrderResult(json.loads(response.text))
