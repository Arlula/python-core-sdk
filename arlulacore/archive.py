from dataclasses import dataclass
from datetime import date
import json
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
    supplier: float
    off_nadir: float

    def __init__(self, start: date,
            res: typing.Optional[float] = None,
            end: typing.Optional[date] = None,
            lat: typing.Optional[float] = None,
            long: typing.Optional[float] = None,
            north: typing.Optional[float] = None,
            south: typing.Optional[float] = None,
            east: typing.Optional[float] = None,
            west: typing.Optional[float] = None,
            supplier: typing.Optional[float] = None,
            off_nadir: typing.Optional[float] = None):
        self.start = start
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

    def set_to(self, end: date) -> "SearchRequest":
        self.end = end
        return self
    
    def set_between_dates(self, start: date, end: date) -> "SearchRequest":
        self.start = start
        self.end = end
        return self
    
    def set_maximum_off_nadir(self, off_nadir: float) -> "SearchRequest":
        self.off_nadir = off_nadir
        return self
    
    def dict(self):
        param_dict = {"start": self.start, "end": self.end,
            "res": self.res, "lat": self.lat, "long": self.long,
            "north": self.north, "south": self.south, "east": self.east, 
            "west": self.west, "supplier": self.supplier, "off-nadir": self.off_nadir}

        query_params = {k: v for k, v in param_dict.items()
            if v is not None or v == 0}

        return query_params

class OrderRequest:

    id: str
    eula: str
    seats: int
    webhooks: typing.List[str]
    emails: typing.List[str]

    def __init__(self,
            id: str,
            eula: str,
            seats: int,
            webhooks: typing.List[str] = [],
            emails: typing.List[str] = []):
        self.id = id
        self.eula = eula
        self.seats = seats
        self.webhooks = webhooks
        self.emails = emails
    
    def set_webhook(self, webhook: str) -> "OrderRequest":
        self.webhooks.append(webhook)
        return self
    
    def set_webhooks(self, webhooks: typing.List[str]) -> "OrderRequest":
        self.webhooks = webhooks
        return self

    def set_email(self, email: str) -> "OrderRequest":
        self.webhooks.append(email)
        return self
    
    def set_emails(self, emails: typing.List[str]) -> "OrderRequest":
        self.webhooks = emails
        return self

    def dumps(self):
        return json.dumps({
            "id": self.id,
            "eula": self.eula,
            "seats": self.seats,
            "webhooks": self.webhooks,
            "emails": self.emails
        })