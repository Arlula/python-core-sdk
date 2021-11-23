from dataclasses import dataclass
from common import ArlulaObject, Resource
import typing

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
    polygon: typing.List[typing.List[float]]

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
    supplier: str
    eula: str
    id: str
    scene_id: str
    platform: str
    date: str
    center: CenterPoint
    bounding: typing.List[typing.List[float]]
    area: float
    overlap: Overlap
    price: Price
    fulfillment_time: float
    resolution: float
    thumbnail: str
    off_nadir: float
    annotations: typing.List[str]

    def __init__(self, data):
        self.supplier = data["supplier"]
        self.eula = data["eula"]
        self.id = data["id"]
        self.scene_id = data["sceneID"]
        # self.platform = data["platform"]
        self.date = data["date"]
        self.center = CenterPoint(**data["center"])
        self.bounding = data["bounding"]
        self.area = data["area"]
        self.overlap = data["overlap"]
        self.price = Price(**data["price"])
        self.fulfillment_time = data["fulfillmentTime"]
        self.resolution = data["resolution"]
        self.off_nadir = data["offNadir"]
        self.annotations = data["annotations"]