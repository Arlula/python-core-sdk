'''
    Defines the ArchiveAPI and relevant search/order entities.
'''

from __future__ import annotations
import enum
import json
import typing
import requests

from datetime import date, datetime

from .order import Order
from .common import ArlulaObject, Band, Bundle, License, SortDefinition, get_bundle_key, get_license_href
from .auth import Session
from .exception import ArlulaAPIException
from .util import parse_rfc3339, calculate_price, remove_none, simple_indent

Polygon = typing.List[typing.List[typing.List[float]]]

class CenterPoint(ArlulaObject):
    data: dict
    long: float
    """Center longitude"""

    lat: float
    """Center latitude"""

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
    """percent of the whole scene the polygon represents"""

    search: float
    """percent of the original search area (if bounding box) the AOI represents. This will be -1 for a point search, and may be greater than 100% if the original search is less than the suppliers minimum order"""

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
    """area in sq km of the overlap between search and result"""

    percent: Percent
    """details percentage coverage"""

    polygon: typing.List[typing.List[typing.List[float]]]
    """polygon of overlap area. This polygon is what will be ordered if the supplier supports ordering an area of interest"""

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
    """ID for the suppliers image capture, can be used to identify the same source imagery between searches"""

    supplier: str
    """identifies the supplier of the imagery, used in ordering the imagery"""

    platform: str
    """The platform which captured the imagery, generally identifies the constellation, or specific satellite that captured the imagery."""

    date: datetime
    """date the imagery was captured"""

    thumbnail: str
    """URL of a low resolution JPEG thumbnail of the imagery that will be provided"""

    cloud: float
    """estimated percentage of the imagery that is cloud cover"""

    off_nadir: float
    """The degrees away from Nadir (straight down) the satellite was oriented during capture"""

    gsd: float
    """spatial resolution of the imagery in meters per pixel"""

    bands: typing.List[Band]
    """List of the Spectral Bands captured in this scene"""

    area: float
    """area the scene covers in square kilometers"""

    center: CenterPoint
    """center coordinates of the imagery"""

    bounding: typing.List[typing.List[typing.List[float]]]
    """bounding polygon of the imagery in the geoJSON ([long, lat]) notation"""

    overlap: Overlap
    """overlap between the imagery and the interest area, or an area constructed from it to meet minimum order requirements"""

    fulfillment_time: float
    """estimated time to fulfill an order of this imagery in hours, 0 is instant"""

    ordering_id: str
    """ordering ID for this scene and Area Of Interest, used to order the imagery"""

    bundles: typing.List[Bundle]
    """ordering bundles representing the available ways to order the imagery"""

    licenses: typing.List[License]
    """License options this imagery may be purchased under, and the terms and pricing that apply"""

    annotations: typing.List[str]
    """annotates result with information, such as what modifications were made to your search to make a valid order"""

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

    def calculate_price(self, license_href: str, bundle_key: str) -> int:
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
    state: str
    errors: typing.List[str]
    warnings: typing.List[str]
    results: typing.List[SearchResult]
    """Results for the search conducted."""

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
    """Date of interest, or start of an interest period"""

    gsd: float
    """Desired ground sample distance of imagery, all imagery will be of this GSD or better"""
    
    end: date
    """End of an interest period"""

    lat: float
    """Latitude of the point of interest for which imagery is requested"""
    
    long: float
    """Longitude of the point of interest for which imagery is requested"""

    north: float
    """Northern boundary of an interest area for which imagery is requested"""
    
    south: float
    """Southern boundary of an interest area for which imagery is requested"""
    
    east: float
    """Eastern boundary of an interest area for which imagery is requested"""
    
    west: float
    """Western boundary of an interest area for which imagery is requested"""
    
    polygon: Polygon
    """Polygon demarking an interest area for which imagery is requested."""
    
    supplier: str
    """Restrict results to only the given (space separated) suppliers"""
    
    off_nadir: float
    """Only return imagery with the off nadir angle during capture less than the specified criteria"""
    
    cloud: float
    """Only return imagery with average total cloud percentage less than the specified criteria"""
    
    sort_definition: SortDefinition[ArchiveSearchSortFields]
    """The desired field to sort results by, and if that sort should be ascending or descending"""

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
        """Filter the suppliers to search. To set multiple, use a space separated list."""
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

class ArchiveOrderRequest(ArlulaObject):

    id: str
    """Unique ID of the imagery to purchase, provided in the search endpoint"""

    eula: str
    """The eula string provided in the search results to confirm acceptance. (the href of the license of interest)"""

    bundle_key: str
    """The key of the bundle you wish to purchase from the scene"""

    webhooks: typing.List[str]
    """A list of http/https addresses that the order details will be sent to once the order is complete and ready for collection"""

    emails: typing.List[str]
    """A list of email addresses (strings) that the order details will be sent to once the order is complete and ready for collection"""

    team: str
    """The ID of the team to attach the order to, if other than the default team for the API (used to control shared access to the order)"""

    payment: str
    """The ID of the payment method to charge this order to (if not free). If not specified, the APIs default billing method will be charged."""

    def __init__(self,
            id: str,
            license: typing.Union[str, License],
            bundle: typing.Union[str, Bundle],
            webhooks: typing.Optional[typing.List[str]] = [],
            emails: typing.Optional[typing.List[str]] = [],
            team: typing.Optional[str] = None,
            payment: typing.Optional[str] = None):
        self.id = id
        self.eula = get_license_href(license)
        self.bundle_key = get_bundle_key(bundle)
        self.webhooks = webhooks
        self.emails = emails
        self.team = team
        self.payment = payment

    def set_bundle(self, bundle: typing.Union[str, Bundle]) -> ArchiveOrderRequest:
        self.bundle_key = get_bundle_key(bundle)
        return self
    
    def set_eula(self, license: typing.Union[str, License]) -> ArchiveOrderRequest:
        self.eula = get_license_href(license)
        return self
    
    def add_webhook(self, webhook: str) -> "ArchiveOrderRequest":
        self.webhooks.append(webhook)
        return self
    
    def set_webhooks(self, webhooks: typing.List[str]) -> "ArchiveOrderRequest":
        self.webhooks = webhooks
        return self

    def add_email(self, email: str) -> "ArchiveOrderRequest":
        self.emails.append(email)
        return self
    
    def set_emails(self, emails: typing.List[str]) -> "ArchiveOrderRequest":
        self.emails = emails
        return self

    def set_team(self, team: str) -> "ArchiveOrderRequest":
        self.team = team
        return self
    
    def set_payment(self, payment: str) -> "ArchiveOrderRequest":
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

class ArchiveBatchOrderRequest():

    orders: typing.List[ArchiveOrderRequest]
    """Orders to be placed in batch request."""

    webhooks: typing.List[str]
    """A list of http/https addresses that the order details will be sent to once the order is complete and ready for collection"""

    emails: typing.List[str]
    """A list of email addresses (strings) that the order details will be sent to once the order is complete and ready for collection"""

    team: str
    """The ID of the team to attach the order to, if other than the default team for the API (used to control shared access to the order)"""

    payment: str
    """The ID of the payment method to charge this order to (if not free). If not specified, the APIs default billing method will be charged."""

    def __init__(
        self, 
        orders: typing.Optional[typing.List[ArchiveOrderRequest]] = [],
        webhooks: typing.Optional[typing.List[str]] = [],
        emails: typing.Optional[typing.List[str]] = [],
        team: typing.Optional[str] = None,
        payment: typing.Optional[str] = None):

        self.orders = orders
        self.webhooks = webhooks
        self.emails = emails
        self.team = team
        self.payment = payment

    def add_order(self, order: ArchiveOrderRequest) -> "ArchiveBatchOrderRequest":
        self.orders.append(order)
        return self
    
    def set_orders(self, orders: typing.List[ArchiveOrderRequest]) -> "ArchiveBatchOrderRequest":
        self.orders = orders
        return self

    def add_webhook(self, webhook: str) -> "ArchiveBatchOrderRequest":
        self.webhooks.append(webhook)
        return self
    
    def set_webhooks(self, webhooks: typing.List[str]) -> "ArchiveBatchOrderRequest":
        self.webhooks = webhooks
        return self

    def add_email(self, email: str) -> "ArchiveBatchOrderRequest":
        self.emails.append(email)
        return self
    
    def set_emails(self, emails: typing.List[str]) -> "ArchiveBatchOrderRequest":
        self.emails = emails
        return self

    def set_team(self, team: str) -> "ArchiveBatchOrderRequest":
        self.team = team
        return self
    
    def set_payment(self, payment: str) -> "ArchiveBatchOrderRequest":
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

    def order(self, request: ArchiveOrderRequest) -> Order:
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
            return Order(json.loads(response.text))
        
    def batch_order(self, request: ArchiveBatchOrderRequest) -> Order:
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
            return Order(json.loads(response.text))
