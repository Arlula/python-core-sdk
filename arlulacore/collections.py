import abc
import json
import typing
import requests
import enum
import datetime

from .auth import Session
from .exception import ArlulaAPIException
from .util import parse_rfc3339, remove_none

class Provider():
    name: str
    """The name of the provider"""

    description: typing.Optional[str]
    """A description of the provider and their data"""

    roles: typing.List[str]
    """A list of providing roles they fulfil (i.e. licensor, producer, processor or host)"""

    url: str
    """Link to the providers homepage"""

    def __init__(self, data):
        self.name = data["name"]
        self.description = data["description"] if "description" in data else None
        self.roles = data["roles"]
        self.url = data["url"]

class BBox():
    south: float
    west: float
    north: float
    east: float

    def __init__(self, data):
        self.south = data[0]
        self.west = data[1]
        self.north = data[2]
        self.east = data[3]

class Interval():
    start: typing.Optional[datetime.datetime]
    """Start time for the collection overall"""

    end: typing.Optional[datetime.datetime]
    """End time for the collection overall. None if no items in this collection."""

    def __init__(self, data):
        self.start = data["start"] if "start" in data and data["start"] is not None else None
        self.end = data["end"] if "end" in data and data["end"] is not None else None

class SpatialExtents():
    bbox: typing.List[BBox]
    """A list of bounding boxes representing spatial data extents within the collection (with the first being total extent of all data)"""

    def __init__(self, data):
        self.bbox = [BBox(x) for x in data["bbox"]] if "bbox" in data and data["bbox"] is not None else []
    
class TemporalExtents():
    interval: typing.List[Interval]
    """A list of time intervals with a start and end date (or null for an open interval) where the first entry will be the total temporal extent of all data in the collection"""

    def __init__(self, data):
        self.interval = [Interval(x) for x in data["interval"]] if "interval" in data and data["interval"] is not None else []

class Extent():
    
    spatial: SpatialExtents
    """Wraps the spatial extents of the collection"""

    temporal: TemporalExtents
    """Wraps the temporal extents of the collection"""

    def __init__(self, data):
        self.spatial = SpatialExtents(data["spatial"]) 
        self.temporal = TemporalExtents(data["temporal"])

class Asset():
    """
        Assets represent a discrete file resource associated with a Collection or Item, and provides the details for its retrieval.
        Some assets may have more fields than just `href`, `type`, and `roles` depending on stac extensions it adheres to, in which case,
        they can be accessed on `data`.
    """

    href: str
    """Url of the asset"""

    title: typing.Optional[str]
    """Optional title or name of the asset"""

    description: typing.Optional[str]
    """Optional description of the asset"""

    type: str
    """IANA media type (MIME type) of the asset"""

    roles: typing.List[str]
    """List of semantic roles this asset satisfies (see resource reference for more details)"""

    data: dict
    """All values this asset describes. Some assets may have extra asset fields to adhere to it's corresponding stac extensions."""

    def __init__(self, data):
        # TODO consider taking stac_extensions here and use to validate expected values.

        self.href = data["href"]
        self.type = data["type"]
        self.roles = data["roles"]

        self.data = data

class Link():
    href: typing.Optional[str]
    """The URL of the linked media"""

    rel: typing.Optional[str]
    """The type of relationship the media has to the current document. (i.e. parent, next result, the associated licence. etc)"""

    type: typing.Optional[str]
    """The IANA Media Type (MIME) of the linked media"""

    title: typing.Optional[str]
    """An optional title to describe the linked media"""

    def __init__(self, data):
        self.href = data["href"] if "href" in data else None
        self.rel = data["rel"] if "rel" in data else None
        self.type = data["type"] if "type" in data else None
        self.title = data["title"] if "title" in data else None

class Collection():
    id: str
    """The unique identifier for this collection"""

    type: str
    """Part of the STAC standard to conform with GeoJSON, will always be 'Collection'"""

    stac_version: str
    """The version of the STAC standard being adhered to"""

    stac_extensions: typing.List[str]
    """A list of STAC extension schemas this collection complies with"""

    title: str
    """A descriptive title of the collection"""

    description: str
    """A more detailed description of the collection and its contents"""

    keywords: typing.List[str]
    """Identifying keywords for the collection"""

    license: str
    """SPDX License identifier, various if multiple licenses apply or proprietary for all other cases"""

    providers: typing.List[Provider]
    """A list of providers that are the source of or that manage data in this collection"""

    extent: Extent
    """The spatial and temporal extents of items in this collection"""

    assets: typing.Dict[str, Asset]
    """A list of any assets related to this collection but not to any specific items within it"""

    summaries: typing.Optional[typing.Dict[str, typing.Union[dict, list]]]
    """Summaries of the range or values of common properties of items in this collection"""

    links: typing.List[Link]
    """Links to resources and media associated with this collection"""

    def __init__(self, data: dict):
        self.id = data["id"]
        self.type = data["type"]
        self.stac_version = data["stac_version"] if "stac_version" in data else ""
        self.stac_extensions = data["stac_extensions"] if "stac_extensions" in data else ""
        self.title = data["title"]
        self.description = data["description"]
        self.keywords = data["keywords"] if "keywords" in data else []
        self.license = data["license"]
        self.providers = [Provider(x) for x in data["providers"]] if "providers" in data and data["providers"] is not None else []
        self.extent = Extent(data["extent"])
        self.assets = {k : Asset(v) for k, v in data["assets"].items()} if "assets" in data else None
        self.summaries = data["summaries"] if "summaries" in data else None
        # TODO add better support for summaries definitions
        self.links = [Link(x) for x in data["links"]] if "links" in data and data["links"] is not None else []

class CollectionItem():
    type: str
    """Part of the STAC standard to conform with GeoJSON, will always be 'Feature'"""

    stac_version: str
    """The version of the STAC standard being adhered to"""

    stac_extensions: typing.List[str]
    """A list of STAC extension schemas this item complies with"""

    id: str
    """ID of the order the item corresponds to"""

    crs: typing.Optional[str]
    """The Coordinate Reference System for all geometry of this item"""
    
    geometry: dict
    """The polygon defining coverage of this item in the given CRS."""

    bbox: typing.List[float]
    """The total bounding box of the item"""

    properties: dict
    """The list of properties of this item"""

    assets: typing.Dict[str, Asset]
    """A list of any assets related to this item, including all resources from the source order"""

    links: typing.List[Link]
    """Links to resources and media associated with this collection"""

    collection: str
    """The ID of the collection this item is from"""

    def __init__(self, data):
        self.type = data["type"]
        self.stac_version = data["stac_version"]
        self.stac_extensions = data["stac_extensions"]
        self.crs = data["crs"] if "crs" in data else None,
        self.id = data["id"]
        self.bbox = data["bbox"]
        self.geometry = data["geometry"]
        self.properties = data["properties"]
        self.assets = {k : Asset(v) for k, v in data["assets"].items()}
        self.links = [Link(x) for x in data["links"]]

# CollectionList classes
class CollectionListResponseContext:
    page: int
    """The index of this page"""

    limit: int
    """The page size"""

    matched: int
    """The total number of items matched"""

    returned: int
    """The number of items returned in this request"""

    def __init__(self, data):
        self.page = data["page"]
        self.limit = data["limit"]
        self.matched = data["matched"]
        self.returned = data["returned"]

class CollectionListResponse:
    collections: typing.List[Collection]
    """A list of collections matching the request specifications"""

    links: typing.List[Link]
    """Links to resources and media associated with this collection"""

    context: CollectionListResponseContext
    """Details about data returned and the number of results remaining"""

    def __init__(self, data):
        self.collections = [Collection(x) for x in data["collections"]]
        self.links = [Link(x) for x in data["links"]]
        self.context = CollectionListResponseContext(data["context"])


# CollectionListItems Classes
class CollectionListItemsResponse:
    
    type: str
    """Part of the STAC standard to conform with GeoJSON, will always be 'FeatureCollection'"""

    features: typing.List[CollectionItem]
    """A list of collection items coinciding with the search"""

    links: typing.List[Link]
    """Links to resources and media associated with this collection"""
    
    timestamp: datetime.datetime
    """The time at which this search was conducted"""

    number_matched: int
    """The total number of items matched"""

    number_returned: int
    """The total number of items returned on this page"""

    def __init__(self, data):
        self.type = data["type"]
        self.features = [CollectionItem(x) for x in data["features"]]
        self.links = [Link(x) for x in data["links"]]
        self.timestamp = parse_rfc3339(data["timeStamp"])
        self.number_matched = data["numberMatched"]
        self.number_returned = data["numberReturned"]

class CollectionListItemsRequest:
    page: typing.Optional[int]
    """The page of data to display, where each page is 'limit' items in length (if not specified, the default is 0)"""

    limit: typing.Optional[int]
    """The number of results per page. The default is 100."""

    bbox: typing.Optional[typing.List[int]]
    """A bounding box to only return results within. The elements define the south, west, north and east longitude and latitude boundaries, in that order."""

    start: typing.Optional[datetime.datetime]
    """The start of a period of interest. If not provided when end is provided, it specifies an open interval"""

    end: typing.Optional[datetime.datetime]
    """The end of a period of interest. If not provided when start is provided, it specifies an open interval"""

    datetime: typing.Optional[datetime.datetime]
    """Matches the same date"""

    collection_id: str

    def __init__(
        self,
        collection: typing.Union[Collection, str],
        page: typing.Optional[int] = 0,
        limit: typing.Optional[int] = 100,
        bbox: typing.Optional[typing.List[int]] = None,
        start: typing.Optional[datetime.datetime] = None,
        end: typing.Optional[datetime.datetime] = None,
        datetime: typing.Optional[datetime.datetime] = None,
    ):
        self.collection_id = get_collection_id(collection)
        self.page = page
        self.limit = limit
        self.bbox = bbox
        self.start = start
        self.end = end
        self.datetime = datetime

    def set_collection(self, collection: typing.Union[Collection, str]) -> "CollectionListItemsRequest":
        self.collection_id = get_collection_id(collection)
        return self
    
    def set_start(self, start: datetime.datetime) -> "CollectionListItemsRequest":
        self.start = start
        return self
    
    def set_end(self, end: datetime.datetime) -> "CollectionListItemsRequest":
        self.end = end
        return self
    
    def set_between_dates(self, start: datetime.datetime, end: datetime.datetime) -> "CollectionListItemsRequest":
        self.start = start
        self.end = end
        return self
    
    def set_datetime(self, datetime: datetime.datetime) -> "CollectionListItemsRequest":
        self.datetime = datetime
        return self
    
    def set_page(self, page: int) -> "CollectionListItemsRequest":
        self.page = page
        return self
    
    def set_limit(self, limit: int) -> "CollectionListItemsRequest":
        self.limit = limit
        return self
    
    def _to_interval(self) -> typing.Optional[str]:
        if self.datetime is not None:
            return self.datetime.isoformat()
        elif self.start is not None or self.end is not None:
            return f"{self.start.isoformat() if self.start is not None else '..'}/{self.end.isoformat() if self.end is not None else '..'}"
        else:
            return None

    def _bbox(self) -> typing.Optional[str]:
        if self.bbox is not None:
            return f"{self.bbox[0]},{self.bbox[1]},{self.bbox[2]},{self.bbox[3]}"
        else:
            return None
    
    def set_bbox(
        self,
        south: typing.Optional[float],
        west: typing.Optional[float],
        north: typing.Optional[float],
        east: typing.Optional[float],
        bbox: typing.Optional[typing.List[float]]
    ) -> "CollectionListItemsRequest":
        """
            Set the bounding box, must provide either all of `south`, `west`, `north`, and `east`, or `bbox`
        """
        if bbox != None:
            self.bbox = bbox
        else:
            self.bbox = [south, west, north, east]
        return self
    
    def dict(self) -> dict:
        return remove_none({
            "page": self.page,
            "limit": self.limit,
            "bbox": self.bbox,
            "datetime": self._to_interval(),
        })

class CollectionConformanceResponse:

    conforms_to: typing.List[str]
    """List of uris of JSON schema documents that this API conforms to"""

    def __init__(self, data):
        self.conforms_to = data["conformsTo"]


class QueryFieldNumber(str, enum.Enum):
    gsd = "gsd"
    """The ground sample distance of this item (smallest distance is multiple, i.e. from a multi-spectral sensor)"""

    cloud_cover = "eo:cloud_cover"
    """The percentage cloud cover of this item"""
    
    snow_cover = "eo:snow_cover"
    """The percentage snow cover of this item (if provided)"""

    types = "arl:types"	
    """The imagery types this item contains (i.e. visual, optical, SAR, etc)"""

class QueryFieldString(str, enum.Enum):
    provider_key = "providers.key"
    """Matches against a provider (supplier) of this imagery"""

    supplier = "supplier"
    """A shorthand alias for the provider_key"""

    platform = "platform"
    """The identifier for the platform that captured this item"""

    instruments	= "instruments"
    """The list of instruments used to capture this item"""
    
    band_common_name = "eo:bands.common_name"
    """The list of spectral band common names that are available in this item"""

    band = "band"
    """A shorthand alias for the above"""

    types = "arl:types"	
    """The imagery types this item contains (i.e. visual, optical, SAR, etc)"""


class Query(abc.ABC):
    
    @abc.abstractmethod
    def dict(self):
        pass

class StringQuery():

    def __init__(
        self,
        eq: typing.Optional[str] = None,
        like: typing.Optional[str] = None,
    ):
        self.eq = eq
        self.like = like
    
    def dict(self):
        return remove_none({
            "eq": self.eq,
            "like": self.like,
        })

class NumericalQuery(Query):

    def __init__(
        self,
        eq: typing.Optional[float] = None,
        lt: typing.Optional[float] = None,
        lte: typing.Optional[float] = None,
        gt: typing.Optional[float] = None,
        gte: typing.Optional[float] = None,
        range: typing.Optional[typing.Tuple[float, float]] = None,
    ):
        self.eq = eq
        self.lt = lt
        self.lte = lte
        self.gt = gt
        self.gte = gte
        self.range = range
    
    def dict(self):
        d = {
            "eq": self.eq,
            "lt": self.lt,
            "lte": self.lte,
            "gt": self.gt,
            "gte": self.gte,
        }

        if self.range is not None:
            d["range"] = {
                "minimum": self.range[0],
                "maximum": self.range[1],
            }

        return remove_none(d)


class CollectionSearchRequest():
    """
        Complete an in-depth search of a collection's items
    """

    page: typing.Optional[int]
    """The page of data to display, where each page is 'limit' items in length (if not specified, the default is 0)"""

    limit: typing.Optional[int]
    """The number of results per page. The default is 100."""

    bbox: typing.Optional[typing.List[float]]
    """A bounding box to only return results within. The elements define the south, west, north and east longitude and latitude boundaries, in that order."""

    start: typing.Optional[datetime.datetime]
    """The start of a period of interest. If not provided when end is provided, it specifies an open interval"""

    end: typing.Optional[datetime.datetime]
    """The end of a period of interest. If not provided when start is provided, it specifies an open interval"""

    datetime: typing.Optional[datetime.datetime]
    """Matches the same date"""

    ids: typing.Optional[typing.List[str]]
    """A list of Item ids you wish to retrieve"""

    intersects: typing.Optional[dict]
    """A GeoJSON geometry object, consisting of the geometry type (point, polygon, etc) and coordinates."""

    queries: typing.Optional[typing.Dict[typing.Union[QueryFieldString, QueryFieldNumber], Query]]
    """A list of field queries to restrict results to matching the provided conditions"""

    collection_id: str

    def __init__(
        self, 
        collection: typing.Union[str, Collection],
        page: typing.Optional[int] = 0,
        limit: typing.Optional[int] = 100,
        bbox: typing.Optional[typing.List[float]] = None,
        start: typing.Optional[datetime.datetime] = None,
        end: typing.Optional[datetime.datetime] = None,
        datetime: typing.Optional[datetime.datetime] = None,
        ids: typing.Optional[typing.List[str]] = None,
        intersects: typing.Optional[dict] = None,
        queries: typing.Optional[typing.Dict[typing.Union[QueryFieldString, QueryFieldNumber], Query]] = None,
    ):
        self.collection_id = get_collection_id(collection)
        self.page = page
        self.limit = limit
        self.bbox = bbox
        self.start = start
        self.end = end
        self.datetime = datetime
        self.ids = ids
        self.intersects = intersects
        self.queries = queries

    def set_collection(self, collection: typing.Union[str, Collection]) -> "CollectionSearchRequest":
        self.collection_id = get_collection_id(collection)
        return self

    def set_page(self, page: int) -> "CollectionSearchRequest":
        self.page = page
        return self

    def set_limit(self, limit: int) -> "CollectionSearchRequest":
        self.limit = limit
        return self

    def _to_interval(self) -> typing.Optional[str]:
        if self.datetime is not None:
            return self.datetime.isoformat()
        elif self.start is not None or self.end is not None:
            return f"{self.start.isoformat() if self.start is not None else '..'}/{self.end.isoformat() if self.end is not None else '..'}"
        else:
            return None

    def set_bbox(
        self,
        south: typing.Optional[float],
        west: typing.Optional[float],
        north: typing.Optional[float],
        east: typing.Optional[float],
        bbox: typing.Optional[typing.List[float]]
    ) -> "CollectionListItemsRequest":
        """
            Set the bounding box, must provide either all of `south`, `west`, `north`, and `east`, or `bbox`
        """
        if bbox != None:
            self.bbox = bbox
        else:
            self.bbox = [south, west, north, east]
        return self

    def set_start(self, start: typing.Optional[datetime.datetime]) -> "CollectionSearchRequest":
        self.start = start
        return self

    def set_end(self, end: typing.Optional[datetime.datetime]) -> "CollectionSearchRequest":
        self.end = end
        return self
    
    def set_between_dates(
        self, 
        start: typing.Optional[datetime.datetime], 
        end: typing.Optional[datetime.datetime]
    ) -> "CollectionListItemsRequest":
        self.start = start
        self.end = end
        return self

    def set_datetime(self, datetime: datetime.datetime) -> "CollectionSearchRequest":
        self.datetime = datetime
        return self

    def set_ids(self, ids: typing.List[str]) -> "CollectionSearchRequest":
        self.ids = ids
        return self

    def add_id(self, id: str) -> "CollectionSearchRequest":
        self.ids.append(id)
        return self
    
    def set_point(self, long: float, lat: float) -> "CollectionSearchRequest":
        self.intersects = {
            "type": "Point",
            "coordinates": [
                long,
                lat
            ],
        }
        return self
    
    def set_polygon(self, polygon: typing.List[typing.List[typing.List[float]]]) -> "CollectionSearchRequest":
        self.intersects = {
            "type": "Polygon",
            "coordinates": polygon
        }
        return self

    def set_intersects(self, intersects: dict) -> "CollectionSearchRequest":
        # TODO add a proper GeoJSON definition
        self.intersects = intersects
        return self

    def add_query(self, field: typing.Union[QueryFieldNumber, QueryFieldString], query: Query):
        self.queries[field] = query

    def dict(self):
        return remove_none({
            "page": self.page,
            "limit": self.limit,
            "bbox": self.bbox,
            "datetime": self._to_interval(),
            "ids": self.ids,
            "intersects": self.intersects,
            "queries": {k.value: v.dict() for k, v in self.queries.items()} if self.queries is not None else None,
        })

class CollectionSearchResponseContext():
    limit: int
    matched: int
    returned: int

    def __init__(self, data):
        self.limit = data["limit"]
        self.matched = data["matched"]
        self.returned = data["returned"]

class CollectionSearchResponse():
    
    type: str
    """Part of the STAC standard to conform with GeoJSON, will always be 'FeatureCollection'"""

    stac_version: str
    """The version of the STAC standard being adhered to"""

    stac_extensions: str
    """A list of STAC extension schemas this collection complies with"""

    context: str
    """Details about data returned and the number of results remaining"""

    number_matched: int
    """The total number of items matched"""

    number_returned: int
    """The total number of items returned on this page"""

    links: typing.List[int]
    """Links to resources and media associated with this collection"""

    features: typing.List[CollectionItem]
    """A list of collection items coinciding with the search"""
    

    def __init__(self, data):
        self.type = data["type"]
        self.stac_version = data["stac_version"]
        self.stac_extensions = data["stac_extensions"]
        self.context = CollectionSearchResponseContext(data["context"])
        self.number_matched = data["numberMatched"]
        self.number_returned = data["numberReturned"]
        self.links = data["links"]
        self.features = data["features"]


class CollectionCreateRequest:

    title: str
    """A title/name for the collection to identify it"""

    description: str
    """A description of the collection, such as its purpose, or the location of interest."""

    keywords: typing.List[str]
    """A list of keywords that describe the collections content for organisational purposes"""

    team: typing.Optional[str]
    """The team that will be the owner of the collection (defaults to the requesting API directly)"""

    def __init__(
        self,
        title: str,
        description: str,
        keywords: typing.Optional[typing.List[str]] = [],
        team: typing.Optional[str] = None, 
    ):
        self.title = title
        self.description = description
        self.keywords = keywords
        self.team = team
    
    def set_title(self, title: str) -> "CollectionCreateRequest":
        self.title = title
        return self
    
    def set_description(self, description: str) -> "CollectionCreateRequest":
        self.description = description
        return self
    
    def set_keywords(self, keywords: typing.List[str]) -> "CollectionCreateRequest":
        self.keywords = keywords
        return self

    def add_keyword(self, keyword: str) -> "CollectionCreateRequest":
        self.keywords.append(keyword)
        return self
    
    def set_team(self, team: str) -> "CollectionCreateRequest":
        self.team = team
        return self
    
    def dict(self):
        return remove_none({
            "title": self.title,
            "description": self.description,
            "keywords": self.keywords,
            "team": self.team,
        })

class CollectionUpdateRequest:
    collection_id: str
    """Collection to update"""

    title: typing.Optional[str]
    """A title/name for the collection to identify it"""

    description: typing.Optional[str]
    """A description of the collection, such as its purpose, or the location of interest."""

    keywords: typing.Optional[typing.List[str]]
    """A list of keywords that describe the collections content for organisational purposes"""

    def __init__(
        self,
        collection: typing.Union[Collection, str],
        title: typing.Optional[str] = None,
        description: typing.Optional[str] = None,
        keywords: typing.Optional[typing.List[str]] = None,
    ):
        self.collection_id = get_collection_id(collection)
        self.title = title
        self.description = description
        self.keywords = keywords
    
    def set_title(self, title: str) -> "CollectionUpdateRequest":
        self.title = title
        return self
    
    def set_description(self, description: str) -> "CollectionUpdateRequest":
        self.description = description
        return self
    
    def set_keywords(self, keywords: typing.List[str]) -> "CollectionUpdateRequest":
        self.keywords = keywords
        return self

    def add_keyword(self, keyword: str) -> "CollectionUpdateRequest":
        self.keywords.append(keyword)
        return self

    def dict(self) -> dict:
        return remove_none({
            "title": self.title,
            "description": self.description,
            "keywords": self.keywords,
        })

# Helper function to type check a collection argument (str or collection)
def get_collection_id(collection: typing.Union[str, Collection]) -> str:
    if isinstance(collection, str):
        return collection
    elif isinstance(collection, Collection):
        return collection.id
    else:
        raise TypeError("Invalid type for `collection`")

# Helper function to type check an item argument (str or collection) 
def get_item_id(item: typing.Union[str, CollectionItem]) -> str:
    if isinstance(item, str):
        return item
    elif isinstance(item, CollectionItem):
        return item.id
    else:
        raise TypeError("Invalid type for `item`")

class CollectionsAPI:

    '''
        CollectionsAPI is used to interface with the Arlula Collections API
    '''

    def __init__(self, session: Session):
        self.session = session
        self.url = self.session.baseURL + "/api/collections"


    def list(self, page: typing.Optional[int] = 0, size: typing.Optional[int] = 100) -> CollectionListResponse:
        """
            List all STAC collections the requesting API has access to.
        """

        url = self.url

        response = requests.request(
            "GET",
            url,
            params={"page": page, "size": size},
            headers=self.session.header)

        if response.status_code != 200:
            raise ArlulaAPIException(response)
        else:
            return CollectionListResponse(json.loads(response.text))

    def detail(self, collection: typing.Union[str, Collection]) -> Collection:
        """
            Returns the details of the specified STAC collection.
        """

        url = f"{self.url}/{get_collection_id(collection)}"

        response = requests.request(
            "GET",
            url,
            headers=self.session.header)

        if response.status_code != 200:
            raise ArlulaAPIException(response)
        else:
            return Collection(json.loads(response.text))

    def list_items(self, request: CollectionListItemsRequest) -> CollectionListItemsResponse:
        """
            Paginate STAC Items within the collection.
        """

        url = f"{self.url}/{request.collection_id}/items"
        
        response = requests.request(
            "GET",
            url,
            params=request.dict(),
            headers=self.session.header,
        )
        
        if response.status_code != 200:
            raise ArlulaAPIException(response)
        else:
            return CollectionListItemsResponse(json.loads(response.text))

    def get_item(self, collection: typing.Union[str, Collection], item: typing.Union[str, CollectionItem]) -> CollectionItem:
        """
            Retrieve an individual item from a collection
        """

        url = f"{self.url}/{get_collection_id(collection)}/items/{get_item_id(item)}"

        response = requests.request(
            "GET",
            url,
            headers=self.session.header
        )

        if response.status_code != 200:
            raise ArlulaAPIException(response)
        else:
            return CollectionItem(json.loads(response.text))

    def search_items(self, request: CollectionSearchRequest) -> CollectionSearchResponse:
        """
            Perform a detailed search of items within a collection.
        """

        url = f"{self.url}/{request.collection_id}/search"

        response = requests.request(
            "POST",
            url,
            data=json.dumps(request.dict()),
            headers=self.session.header
        )

        if response.status_code != 200:
            raise ArlulaAPIException(response)
        else:
            return CollectionSearchResponse(json.loads(response.text))
        
    def import_order(self, collection: typing.Union[str, Collection], order_id: str) -> None:
        """
            Import an order from the Orders API into a collection
        """

        url = f"{self.url}/{get_collection_id(collection)}/items"

        response = requests.request(
            "POST",
            url,
            data=json.dumps({"order": order_id}),
            headers=self.session.header
        )

        if response.status_code != 200:
            raise ArlulaAPIException(response)


    def remove_item(self, collection: typing.Union[str, Collection], item: typing.Union[str, CollectionItem]) -> None:
        """
            Remove an item from a collection
        """
        url = f"{self.url}/{get_collection_id(collection)}/items/{get_item_id(item)}"
        
        response = requests.request(
            "DELETE",
            url,
            headers=self.session.header
        )

        if response.status_code != 200:
            raise ArlulaAPIException(response)

    def create(self, request: CollectionCreateRequest) -> Collection:
        """
            Create a new collection to add imagery to
        """
        
        response = requests.request(
            "POST",
            self.url,
            data=json.dumps(request.dict()),
            headers=self.session.header
        )

        if response.status_code != 200:
            raise ArlulaAPIException(response)
        else:
            return Collection(json.loads(response.text))
        
    def update(self, request: CollectionUpdateRequest) -> Collection:
        """
            Update the details of an existing collection
        """

        url = f"{self.url}/{request.collection_id}"

        response = requests.request(
            "POST",
            url,
            data=json.dumps(request.dict()),
            headers=self.session.header
        )
        if response.status_code != 200:
            raise ArlulaAPIException(response)
        else:
            return Collection(json.loads(response.text))

    def delete(self, collection: typing.Union[str, Collection]) -> None:
        """
            Delete an imagery collection
        """

        collection_id = get_collection_id(collection)

        url = f"{self.url}/{collection_id}"

        response = requests.request(
            "DELETE",
            url,
            headers=self.session.header)

        if response.status_code != 200:
            raise ArlulaAPIException(response)
    
    def request_access_item(
            self, 
            collection: typing.Union[Collection, str], 
            item: typing.Union[CollectionItem, str],
            team: str,
            message: str,
        ):
        """
            Request access to an item in the collection that the caller does not have resource access permission to.
        """
        collection_id = get_collection_id(collection)
        item_id = get_item_id(item)

        url = f"{self.url}/{collection_id}/{item_id}/access-request"

        response = requests.request(
            "POST",
            url,
            data=json.dumps({"team": team, "message": message}),
            headers=self.session.header,
        )

        if response.status_code != 200:
            raise ArlulaAPIException(response)

    def conformance(self) -> CollectionConformanceResponse:
        """
            The conformance endpoint is a required component of the STAC standard, and lists the set of JSON Schema documents that 
            the API and its output data is in conformance with. These schemas often indicate support for some extension upon the base 
            STAC specification.
        """
        url = f"{self.url}/conformance"

        response = requests.request(
            "GET",
            url,
            headers=self.session.header
        )

        if response.status_code != 200:
            raise ArlulaAPIException(response)
        else:
            return CollectionConformanceResponse(json.loads(response.text))
