'''
    Defines the TaskingAPI and relevant search and order entities.
'''

import enum
import json
import typing
import requests
import datetime

from .order import Order
from .archive import Polygon
from .common import ArlulaObject, Band, Bundle, License, SortDefinition, get_bundle_key, get_license_href
from .auth import Session
from .exception import ArlulaAPIException
from .util import parse_rfc3339, calculate_price, remove_none

class TaskingSearchFailureType(str, enum.Enum):
    """
        An enumeration of types of tasking search failure types.
        They are intended to give further information on why a result was infeasible.
    """

    insufficient_los = "insufficient-los"
    """
        Returned when the supplier/platform combination does not have enough line of 
        sight opportunities between the requested start/end date, less than the provided off nadir.
        Try increasing those values to get a result. 
    """

    no_priorities = "no-priorities"
    """
        There was sufficient line of sight however the supplier has other restrictions. 
        Try increasing the time between the searched start/end dates.
    """

    no_cloud = "no-cloud"
    """
        There was sufficient line of sight however the supplier cannot provide imagery
        at your requested cloud coverage.
        Try decreasing the requested cloud level.
    """

    too_wide = "too-wide"
    """
        The AOI is too wide to capture in one campaign.
        Try splitting the scene into numerous smaller campaigns.
    """

    too_tall = "too-tall"
    """
        The AOI is too tall to capture in one campaign.
        Try splitting the scene into numerous smaller campaigns.
    """

    too_large = "too-large"
    """
        The AOI is too large to capture in one campaign.
        Try splitting the scene into numerous smaller campaigns.
    """

    too_short = "too-short"
    """
        The requested time period is too short for this supplier/platform
        combination.
        Try increasing the time span.
    """

    supplier_error = "supplier-error"
    """
        There is currently an issue with the supplier API.
        Try again in the future or contact support.
    """

class TaskingSearchSortFields(str, enum.Enum):
    """
        An enumeration of fields that can be sorted by on tasking search requests.
    """

    duration = "duration"
    supplier = "supplier"
    start = "start"
    end = "end"
    max_off_nadir = "maxOffNadir"
    areas_scene = "areas.scene"
    areas_target = "areas.target"

class TaskingSearchRequest(ArlulaObject):
    start: datetime.datetime
    """The start time of the period of interest. Must be in the future."""

    end: datetime.datetime
    """The end time of the period of interest. Must be in the future and after start."""

    gsd: float
    """The maximum nadir gsd of the sensor."""

    lat: float
    """Latitude of a point of interest."""

    long: float
    """Longitude of a point of interest."""

    north: float
    """Northernmost point of a bounding box."""

    south: float
    """Southernmost point of a bounding box."""

    east: float
    """Easternmost point of a bounding box."""

    west: float
    """Westernmost point of a bounding box."""

    polygon: Polygon
    """Polygon of interest."""

    supplier: typing.List[str]
    """Suppliers of interest."""

    off_nadir: float
    """The maximum off-nadir acceptable for capture. Results will not have an off nadir greater than this."""

    sort_defintion: SortDefinition[TaskingSearchSortFields]
    """the desired field to sort results by, and if that sort should be ascending or descending"""
    
    def __init__(self, 
            start: datetime.datetime,
            end: datetime.datetime,
            gsd: float,
            off_nadir: float,
            lat: typing.Optional[float] = None,
            long: typing.Optional[float] = None,
            north: typing.Optional[float] = None,
            south: typing.Optional[float] = None,
            east: typing.Optional[float] = None,
            west: typing.Optional[float] = None,
            supplier: typing.Optional[typing.List[str]] = None,
            polygon: typing.Optional[Polygon] = None,
            sort_definition: typing.Optional[SortDefinition[TaskingSearchSortFields]] = None,
        ):
        self.start = start
        self.end = end
        self.gsd = gsd
        self.off_nadir = off_nadir
        self.lat = lat
        self.long = long
        self.north = north
        self.south = south
        self.east = east
        self.west = west
        self.supplier = supplier
        self.polygon = polygon
        self.sort_definition = sort_definition

    def set_point_of_interest(self, lat: float, long: float) -> "TaskingSearchRequest":
        self.lat = lat
        self.long = long
        return self
    
    def set_area_of_interest(self, north: float, south: float, east: float, west: float) -> "TaskingSearchRequest":
        self.north = north
        self.south = south
        self.west = west
        self.east = east
        return self
    
    def set_polygon(self, polygon: Polygon) -> "TaskingSearchRequest":
        self.polygon = polygon
        return self

    def set_supplier(self, supplier: str) -> "TaskingSearchRequest":
        self.supplier = supplier
        return self

    def set_gsd(self, gsd: float) -> "TaskingSearchRequest":
        self.gsd = gsd
        return self

    def set_start(self, start: datetime.datetime) -> "TaskingSearchRequest":
        self.start = start
        return self

    def set_end(self, end: datetime.datetime) -> "TaskingSearchRequest":
        self.end = end
        return self
    
    def set_between_dates(self, start: datetime.datetime, end: datetime.datetime) -> "TaskingSearchRequest":
        self.start = start
        self.end = end
        return self
    
    def set_maximum_off_nadir(self, off_nadir: float) -> "TaskingSearchRequest":
        self.off_nadir = off_nadir
        return self
    
    def set_sort_definition(self, sort_definition: SortDefinition[TaskingSearchSortFields]):
        self.sort_definition = sort_definition
        return self

    def valid_point_of_interest(self) -> bool:
        return self.lat != None and self.long != None

    def valid_area_of_interest(self) -> bool:
        return self.north != None and self.south != None and self.east != None and self.west != None
    
    def valid(self) -> bool:
        return (self.valid_area_of_interest() or self.valid_point_of_interest()) and self.start != None and self.gsd != None
    
    def dict(self):
        d = {
            "start": self.start.isoformat() if self.start != None else None, 
            "end": self.end.isoformat() if self.end != None else None,
            "gsd": self.gsd, 
            "supplier": self.supplier, 
            "offNadir": self.off_nadir,
        }

        if self.polygon != None:
            d["polygon"] = self.polygon
        elif self.north != None and self.south != None and self.east != None and self.west != None:
            d["boundingBox"] = {
                "north": self.north,
                "south": self.south,
                "east": self.east,
                "west": self.west,
            }
        elif self.lat != None and self.long != None:
            d["latLong"] = {
                "latitude": self.lat,
                "longitude": self.long,
            }
        else:
            raise ValueError("No point of interest or area of interest provided")
        
        if self.sort_definition is not None:
            d["sort"] = self.sort_definition.dict()

        return remove_none(d)


class TaskingSearchFailure(ArlulaObject):
    """
        Describes why a supplier/platform combination failed to return results. 
    """

    type: str
    """The type of failure reported by the supplier"""

    message: str
    """Human readable message for the reason why they were unable to satisfy the search"""

    supplier: str
    """The supplier that was unable to satisfy the search."""

    platforms: typing.List[str]
    """The platforms that were unable to satisfy the search."""

    def __init__(self, data):
        self.type = data["type"]
        self.message = data["message"]
        self.supplier = data["supplier"]
        self.platforms = data["platforms"]

class TaskingMetrics(ArlulaObject):
    
    data: dict

    windowsAvailable: int
    """The number of capture passes available in the requested period."""

    windowsRequired: int
    """The number of capture passes required to capture the target aoi."""

    orderArea: float
    """The estimated deliverable scene size."""

    moq: float
    """The minimum order quantity for this purchase (the polygon will be inflated to this size if it is smaller than required)"""

    def __init__(self, data):
        self.data = data
        self.windowsAvailable = data["windowsAvailable"]
        self.windowsRequired = data["windowsRequired"]
        self.orderArea = data["orderArea"]
        self.moq = data["moq"]

    def __dict__(self) -> dict:
        return self.data
    
class CloudLevel(ArlulaObject):

    data: dict

    name: str
    """A human readable name to refer to this cloud coverage level"""

    max: int
    """The maximum cloud cover (0-100) a capture may have to be considered successful if ordered under this coverage level"""
    
    description: str
    """A brief description of this coverage level and any additional considerations it provides."""

    loadingPercent: float
    """The percentage loading this coverage level applies to the bundle's price"""

    loadingAmount: int
    """The static amount (in US cents) this coverage level adds to the bundle's price"""

    def __init__(self, data: dict):
        self.data = data
        self.name = data["name"]
        self.max = data["max"]
        self.description = data["description"]
        self.loadingPercent = data["loadingPercent"]
        self.loadingAmount = data["loadingAmount"]

    def __dict__(self) -> dict:
        return self.data
    
def get_cloud(cloud_level: typing.Union[int, CloudLevel]) -> int:
    """
        Helper function to get a cloud level from a union type
    """
    
    if isinstance(cloud_level, int):
        return cloud_level
    elif isinstance(cloud_level, CloudLevel):
        return cloud_level
    else:
        raise TypeError("Invalid type for `cloud`")
    
class Priority(ArlulaObject):
    data: dict
    key: str
    """The priority key that is to be provided to the order endpoint to purchase the bundle at this priority"""

    name: str
    """A human readable name to refer to this priority level"""
    
    description: str
    """A brief description of this priority level and any additional considerations it provides."""

    loadingPercent: float
    """The percentage loading this priority applies to the bundle's price"""

    loadingAmount: int
    """The static amount (in US cents) this priority adds to the bundle's price"""

    def __init__(self, data: dict):
        self.data = data
        self.key = data["key"]
        self.name = data["name"]
        self.description = data["description"]
        self.loadingPercent = data["loadingPercent"]
        self.loadingAmount = data["loadingAmount"]

    def __dict__(self) -> dict:
        return self.data
    
def get_priority_key(priority: typing.Union[str, Priority]) -> str:
    """
        Helper function to get a priority key from a union type
    """
    
    if isinstance(priority, str):
        return priority
    elif isinstance(priority, Priority):
        return priority.key
    else:
        raise TypeError("Invalid type for `priority`")

class TaskingSearchResult(ArlulaObject):
    polygon: typing.List[typing.List[typing.List[float]]]
    """Polygon representing the area to be ordered from the supplier, inflated to meet any supplier minimum order requirements as a valid order."""
    
    start: datetime
    """The start time for an order created from this result."""

    end: datetime
    """The end time for a campaign created from this result."""

    metrics: TaskingMetrics
    """Container for metrics about the request such as the number of captures needed for coverage and the total area to be ordered."""

    gsd: float
    """The highest nadir GSD for this result."""

    supplier: str
    """The supplier that provides this capture opportunity."""

    ordering_id: str
    """The OrderingID for this result. Pass this to the ordering endpoint, along with a suitable bundle key, license eula, cloud level and priority key to order this result."""

    off_nadir: float
    """The maximum off nadir requested for this result."""

    bands: typing.List[Band]
    """List of the Spectral Bands captured in this scene"""

    bundles: typing.List[Bundle]
    """Ordering bundles representing the available ways to order the imagery"""

    licenses: typing.List[License]
    """License options this imagery may be purchased under, and the terms and pricing that apply"""

    priorities: typing.List[Priority]
    """Options for order priority relevant to your order. Only those available for your order criteria will be presented."""

    cloud: typing.List[CloudLevel]
    """Requirement options the supplier provides, guaranteeing capture of a cloud coverage of this percentage or less. Options vary by supplier, and lower guarantees may reduce the likelihood of capture being successful in the required period."""

    platforms: typing.List[str]
    """A list indicating the satellites and/or constellations that will fulfil this request."""

    annotations: typing.List[str]
    """Annotates results with information, such as what modifications were made to the search to make it valid for this supplier."""
    
    def __init__(self, data):
        self.polygon = data["polygon"]
        self.start = parse_rfc3339(data["startDate"])
        self.end = parse_rfc3339(data["endDate"])
        self.metrics = TaskingMetrics(data["metrics"])
        self.gsd = data["gsd"]
        self.supplier = data["supplier"]
        self.ordering_id = data["orderingID"]
        self.off_nadir = data["offNadir"]
        self.bands = [Band(x) for x in data["bands"]]
        self.bundles = [Bundle(x) for x in data["bundles"]]
        self.licenses = [License(x) for x in data["licenses"]]
        self.clouds = [CloudLevel(x) for x in data["cloud"]]
        self.priorities = [Priority(x) for x in data["priorities"]]
        self.platforms = data["platforms"]
        self.annotations = data["annotations"]


class TaskingSearchResponse(ArlulaObject):
    results: typing.List[TaskingSearchResult]
    """
        Details candidate tasking opportunities.
    """

    failures: typing.List[TaskingSearchFailure]
    """
        Details reasons why suppliers could not fulfil the requested tasking.
    """

    def __init__(self, data):
        self.results = [TaskingSearchResult(x) for x in data["results"]] if "results" in data else []
        self.failures = [TaskingSearchFailure(x) for x in data["errors"]] if "errors" in data else []

class TaskingOrderRequest(ArlulaObject):

    id: str
    """Unique ID of the imagery to purchase, provided in the search endpoint"""

    eula: str
    """The eula string provided in the search results to confirm acceptance. (the href of the license of interest)"""

    bundle_key: str
    """The key of the bundle you wish to purchase from the scene"""

    priority: str
    """Priority code to order this tasking campaign at. Must be chosen from those available in the corresponding result's priorities list."""

    cloud: int
    """Maximum cloudiness (0-100) acceptable for this scene. Must be chosen from those available in the corresponding result's clouds list."""

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
            priority: typing.Union[str, Priority],
            cloud: typing.Union[str, CloudLevel],
            webhooks: typing.Optional[typing.List[str]] = [],
            emails: typing.Optional[typing.List[str]] = [],
            team: typing.Optional[str] = None,
            payment: typing.Optional[str] = None,
        ):
        self.id = id
        self.eula = get_license_href(license)
        self.bundle_key = get_bundle_key(bundle)
        self.priority = get_priority_key(priority)
        self.cloud = get_cloud(cloud)
        self.webhooks = webhooks
        self.emails = emails
        self.team = team
        self.payment = payment

    def set_bundle(self, bundle: typing.Union[str, Bundle]) -> "TaskingOrderRequest":
        self.bundle_key = get_bundle_key(bundle)
        return self
    
    def set_eula(self, license: typing.Union[str, License]) -> "TaskingOrderRequest":
        self.eula = get_license_href(license)
        return self
    
    def set_priority(self, priority: typing.Union[str, Priority]) -> "TaskingOrderRequest":
        self.priority = get_priority_key(priority)
        return self

    def set_cloud(self, cloud: typing.Union[str, CloudLevel]) -> "TaskingOrderRequest":
        self.cloud = get_cloud(cloud)
        return self
    
    def add_webhook(self, webhook: str) -> "TaskingOrderRequest":
        self.webhooks.append(webhook)
        return self
    
    def set_webhooks(self, webhooks: typing.List[str]) -> "TaskingOrderRequest":
        self.webhooks = webhooks
        return self

    def add_email(self, email: str) -> "TaskingOrderRequest":
        self.emails.append(email)
        return self
    
    def set_emails(self, emails: typing.List[str]) -> "TaskingOrderRequest":
        self.emails = emails
        return self

    def set_team(self, team: str) -> "TaskingOrderRequest":
        self.team = team
        return self
    
    def set_payment(self, payment: str) -> "TaskingOrderRequest":
        self.payment = payment
        return payment

    def valid(self) -> bool:
        return self.id != None and self.eula != None and self.bundle_key != None and self.priority != None and self.cloud != None

    def dict(self):
        return remove_none({
            "id": self.id,
            "eula": self.eula,
            "bundleKey": self.bundle_key,
            "cloud": self.cloud,
            "priorityKey": self.priority,
            "webhooks": self.webhooks,
            "emails": self.emails,
            "team": self.team,
            "payment": None if self.payment == "" else self.payment,
        })

class TaskingBatchOrderRequest():

    orders: typing.List[TaskingOrderRequest]
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
        orders: typing.Optional[typing.List[TaskingOrderRequest]] = [],
        webhooks: typing.Optional[typing.List[str]] = [],
        emails: typing.Optional[typing.List[str]] = [],
        team: typing.Optional[str] = None,
        payment: typing.Optional[str] = None):

        self.orders = orders
        self.webhooks = webhooks
        self.emails = emails
        self.team = team
        self.payment = payment

    def add_order(self, order: TaskingOrderRequest) -> "TaskingBatchOrderRequest":
        self.orders.append(order)
        return self
    
    def set_orders(self, orders: typing.List[TaskingOrderRequest]) -> "TaskingBatchOrderRequest":
        self.orders = orders
        return self

    def add_webhook(self, webhook: str) -> "TaskingBatchOrderRequest":
        self.webhooks.append(webhook)
        return self
    
    def set_webhooks(self, webhooks: typing.List[str]) -> "TaskingBatchOrderRequest":
        self.webhooks = webhooks
        return self

    def add_email(self, email: str) -> "TaskingBatchOrderRequest":
        self.emails.append(email)
        return self
    
    def set_emails(self, emails: typing.List[str]) -> "TaskingBatchOrderRequest":
        self.emails = emails
        return self

    def set_team(self, team: str) -> "TaskingBatchOrderRequest":
        self.team = team
        return self
    
    def set_payment(self, payment: str) -> "TaskingBatchOrderRequest":
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

class TaskingAPI:
    '''
        The TaskingAPI class is used to interface with the Arlula Tasking REST API
    '''

    def __init__(self, session: Session):
        self.session = session
        self.url = self.session.baseURL + "/api/tasking"

    def search(self, request: TaskingSearchRequest) -> TaskingSearchResponse:
        '''
            Search the Arlula tasking API for capturing opportunities.
        '''

        url = self.url+"/search"
        
        # Send request and handle responses
        response = requests.request(
            "POST", 
            url,
            headers=self.session.header,
            data=json.dumps(request.dict())
        )
        if response.status_code != 200:
            raise ArlulaAPIException(response)
        else:
            return TaskingSearchResponse(json.loads(response.text))

    def order(self, request: TaskingOrderRequest) -> Order:
        '''
            Order a tasking result from the Arlula tasking API.
        '''

        url = self.url + "/order"
        response = requests.request(
            "POST",
            url,
            data=json.dumps(request.dict()),
            headers=self.session.header
        )

        if response.status_code != 200:
            raise ArlulaAPIException(response)
        else:
            return Order(json.loads(response.text))
    
    def batch_order(self, request: TaskingBatchOrderRequest) -> Order:
        '''
            Order multiple results from the Arlula tasking API.
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
