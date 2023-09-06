import enum
import json
import typing
import requests
import datetime

from .archive import BatchOrderRequest, OrderRequest, Polygon
from .common import Band, Bundle, License, SortDefinition
from .auth import Session
from .exception import ArlulaAPIException
from .orders import DetailedOrderResult
from .util import parse_rfc3339, calculate_price, remove_none, simple_indent

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

class TaskingSearchRequest():
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


class TaskingError:

    supplier: str
    """The supplier that is unable to capture the requested specification"""

    platforms: typing.List[str]
    """The platforms of the supplier that are unable to capture the requested specification"""

    message: str
    """The reason why this supplier is unable to capture the requested specification"""

    def __init__(self, data):
        self.supplier = data["supplier"]
        self.platforms = data["platforms"]
        self.message = data["message"]

class TaskingAreas():
    scene: float
    """The estimated deliverable scene size."""

    target: float
    """The target polygon size."""

    def __init__(self, data):
        self.scene = data["scene"]
        self.target = data["target"]

class TaskingSearchResult():
    polygons: typing.List[typing.List[typing.List[typing.List[float]]]]
    """Each polygon represents a single orbital pass which could be captured, with the full set showing the coverage requested from the supplier."""
    
    start: datetime
    """The start time for an order created from this result. It may be later than the searched start time, depending on the supplier's minimum notice period."""

    end: datetime
    """The end time for an order created from this result. It may be earlier than the searched period, depending on the supplier's maximum notice period."""

    areas: TaskingAreas
    """Container for area information including estimated scene area and target area."""

    gsd: float
    """The nadir GSD for this result."""

    supplier: str
    """The supplier that provides this capture opportunity."""

    ordering_id: str
    """The OrderingID for this result. Pass this to the ordering endpoint, along with a suitable bundle key and license eula to order this result."""

    off_nadir: float
    """The maximum off nadir requested for this result."""

    bands: typing.List[Band]
    """List of the Spectral Bands captured in this scene"""

    bundles: typing.List[Bundle]
    """Ordering bundles representing the available ways to order the imagery"""

    licenses: typing.List[License]
    """License options this imagery may be purchased under, and the terms and pricing that apply"""

    platforms: typing.List[str]
    """A list indicating the satellites and/or constellations that will fulfil this request."""

    annotations: typing.List[str]
    """Annotates results with information, such as what modifications were made to the search to make it valid for this supplier."""
    
    def __init__(self, data):
        self.polygons = data["polygons"]
        self.start = parse_rfc3339(data["startDate"])
        self.end = parse_rfc3339(data["endDate"])
        self.areas = TaskingAreas(data["areas"])
        self.gsd = data["gsd"]
        self.supplier = data["supplier"]
        self.ordering_id = data["orderingID"]
        self.off_nadir = data["offNadir"]
        self.bands = [Band(x) for x in data["bands"]]
        self.bundles = [Bundle(x) for x in data["bundles"]]
        self.licenses = [License(x) for x in data["licenses"]]
        self.platforms = data["platforms"]
        self.annotations = data["annotations"]

class TaskingSearchResponse():
    results: typing.List[TaskingSearchResult]
    """The tasking result. Each result indicates a supplier, platform combination that can capture the requested specification."""

    errors: typing.List[TaskingError]
    """The tasking errors. Details which supplier, platform combinations are unable to fulfil the requested specification."""

    def __init__(self, data):
        self.results = [TaskingSearchResult(x) for x in data["results"]] if "results" in data else []
        self.errors = [TaskingError(x) for x in data["errors"]] if "errors" in data else []

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
        print(json.dumps(request.dict()))
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

    def order(self, request: OrderRequest) -> DetailedOrderResult:
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
            return DetailedOrderResult(json.loads(response.text))
    
    def batch_order(self, request: BatchOrderRequest) -> typing.List[DetailedOrderResult]:
        '''
            Order multiple scenes from the Arlula tasking API.
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
