import json
import requests

from arlulacore.exception import ArlulaAPIException
class Provider():
    name: str
    """The name of the provider"""
    description: str
    """A description of the provider and their data"""
    roles: typing.List[str]
    """A list of providing roles they fulfil (i.e. licensor, producer, processor or host)"""
    url: str
    """Link to the providers homepage"""

    def __init__(self, data):
        self.name = data["name"]
        self.description = data["description"]
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
    start: datetime
    end: datetime

    def __init__(self, data):
        self.start = data[0]
        self.end = data[1]

class SpatialExtents():
    bbox: typing.List[BBox]

    def __init__(self, data):
        self.bbox = [BBox(x) for x in data["bbox"]]
    
class TemporalExtents():
    interval: typing.List[Interval]

    def __init__(self, data):
        self.interval = [Interval(x) for x in data["interval"]]

class Extent():
    
    spatial: SpatialExtents
    temporal: TemporalExtents

    def __init__(self, data):
        self.spatial = SpatialExtents(data["spatial"]) 
        self.temporal = TemporalExtents(data["temporal"])

class Asset():
    href: str
    """Url of the asset"""

    title: str
    """Title or name of the asset"""

    description: str
    """Optional description of the asset"""

    type: str
    """IANA media type (MIME type) of the asset"""

    roles: typing.List[str]
    """List of semantic roles this asset satisfies (see resource reference for more details)"""

    def __init__(self, data):
        self.href = data["href"]
        self.title = data["title"]
        self.description = data["description"]
        self.type = data["type"]
        self.roles = data["roles"]

class Summary():
    pass

class Link():
    href: str
    """The URL of the linked media"""

    rel: str
    """The type of relationship the media has to the current document. (i.e. parent, next result, the associated licence. etc)"""

    type: str
    """The IANA Media Type (MIME) of the linked media"""

    title: str
    """An optional title to describe the linked media"""

    def __init__(self, data):
        self.href = data["href"]
        self.rel = data["rel"]
        self.type = data["type"]
        self.title = data["title"]

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

    summaries: typing.Dict[str, typing.Union[dict, list]]
    """Summaries of the range or values of common properties of items in this collection"""

    links: typing.List[Link]
    """Links to resources and media associated with this collection"""

    def __init__(self, data: dict):
        self.id = data["id"]
        self.type = data["type"]
        self.stac_version = data["stac_version"]
        self.stac_extensions = data["stac_extensions"]
        self.title = data["title"]
        self.description = data["description"]
        self.keywords = data["keywords"]
        self.license = data["license"]
        self.providers = [Provider(x) for x in data["providers"]]
        self.extent = Extent(data["extent"])
        self.assets = {k : Asset(v) for k, v in data["assets"].items()}
        self.summaries = {k : v for k, v in data["summaries"].items()}
        self.links = [Link(x) for x in data["links"]]

class CollectionItem():
    type: str
    """Part of the STAC standard to conform with GeoJSON, will always be 'Feature'"""

    stac_version: str
    """The version of the STAC standard being adhered to"""

    stac_extensions: typing.List[str]
    """A list of STAC extension schemas this item complies with"""

    id: str
    """ID of the order the item corresponds to"""

    crs: str
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
        self.crs = data["crs"]
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
    
    timestamp: datetime
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
    page: int
    limit: int
    bbox: typing.Optional[typing.List[int]]
    """bounding box """

    start: typing.Optional[datetime]
    """The start of a period of interest. If not provided when end is provided, it specifies an open interval"""

    end: typing.Optional[datetime]
    """The end of a period of interest. If not provided when start is provided, it specifies an open interval"""

    datetime: typing.Optional[datetime]
    """Matches the same date"""

    def __init__(
        self, 
        page: typing.Optional[int] = 0,
        limit: typing.Optional[int] = 100,
        bbox: typing.Optional[typing.List[int]] = None,
        start: typing.Optional[datetime] = None,
        end: typing.Optional[datetime] = None,
        datetime: typing.Optional[datetime] = None,
    ):
        self.page = page
        self.limit = limit
        self.bbox = bbox
        self.start = start
        self.end = end
        self.datetime = datetime
    
    def set_start(self, start: datetime) -> "CollectionListItemsRequest":
        self.start = start
        return self
    
    def set_end(self, end: datetime) -> "CollectionListItemsRequest":
        self.end = end
        return self
    
    def set_between_dates(self, start: datetime, end: datetime) -> "CollectionListItemsRequest":
        self.start = start
        self.end = end
        return self
    
    def set_datetime(self, datetime: datetime) -> "CollectionListItemsRequest":
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
            return str(self.datetime)
        elif self.start is not None or self.end is not None:
            return f"{self.start if self.start is not None else '..'}/{self.end if self.end is not None else '..'}"
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

    def list(self, page: typing.Optional[int] = 0, size: typing.Optional[int] = 100) -> CollectionListResponse:
        
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

    def detail_collection(self, request: CollectionDetailRequest) -> CollectionDetailResponse:

        url = self.url+"/detail"

        params = {
            "page": request.page or 1,
            "size": request.size or 100,
        }

        response = requests.request(
            "GET",
            url,
            params=params,
            headers=self.session.header)

        if response.status_code != 200:
            raise ArlulaAPIException(response)
        else:
            return CollectionListResponse(json.loads(response.text))

    def list_items(self, request: CollectionListItemsRequest) -> CollectionListItemsResponse:
        url = f"{self.url}/{request.id}/items"

        response = requests.request(
            "GET",
            url,
            params=request.dict(),
            headers=self.session.header)

        if response.status_code != 200:
            raise ArlulaAPIException(response)
        else:
            return CollectionListItemsResponse(json.loads(response.text))

    def get_item(self, collection: typing.Union[str, Collection], item: typing.Union[str, CollectionItem]) -> CollectionItem:

        url = f"{self.url}/{get_collection_id(collection)}/items/{get_item_id(item)}"

        response = requests.request(
            "GET",
            url,
            headers=self.session.header)

        if response.status_code != 200:
            raise ArlulaAPIException(response)
        else:
            return CollectionItem(json.loads(response.text))

    def remove_item(self, collection: typing.Union[str, Collection], item: typing.Union[str, CollectionItem]) -> None:

        url = f"{self.url}/{get_collection_id(collection)}/items/{get_item_id(item)}"
        
        response = requests.request(
            "DELETE",
            url,
            headers=self.session.header
        )

        if response.status_code != 200:
            raise ArlulaAPIException(response)

    def create(self, request: CollectionCreateRequest) -> Collection:
        
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
        collection_id = get_collection_id(collection)

        url = f"{self.url}/{collection_id}"

        response = requests.request(
            "DELETE",
            url,
            headers=self.session.header)

        if response.status_code != 200:
            raise ArlulaAPIException(response)
        else:
            return Collection(json.loads(response.text))
    
        pass

    def conformance(self) -> CollectionConformanceResponse:
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

    def request_access_to_item(self, request: CollectionRequestAccessToItemRequest) -> CollectionRequestI:
        pass

    def conformance(self):
        pass



