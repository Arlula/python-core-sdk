from datetime import date, datetime
import typing

class Provider():
    name: str
    description: str
    roles: typing.List[str]
    url: str

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
    start: date
    end: date

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


class Extents():
    
    spatial: SpatialExtents
    temporal: TemporalExtents

    def __init__(self, data):
        self.spatial = SpatialExtents(data["spatial"]) 
        self.temporal = TemporalExtents(data["temporal"])

class Asset():
    href: str
    title: str
    description: str
    type: str
    roles: typing.List[str]

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
    rel: str
    type: str
    title: str

    def __init__(self, data):
        self.href = data["href"]
        self.rel = data["rel"]
        self.type = data["type"]
        self.title = data["title"]

class Collection():
    id: str
    type: str
    stac_version: str
    stac_extensions: typing.List[str]
    title: str
    description: str
    keywords: typing.List[str]
    license: str
    providers: typing.List[Provider]
    extent: typing.List[Extents]
    assets: typing.List[Asset]
    summaries: typing.Dict[str, Summary]
    links: typing.List[Link]

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
        self.extent = []
