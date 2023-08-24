from __future__ import annotations
import json
import string
import textwrap
import typing
import requests

from dataclasses import dataclass
from datetime import date, datetime

from arlulacore.archive import OrderRequest, Polygon
from .common import ArlulaObject
from .auth import Session
from .exception import ArlulaAPIException
from .orders import DetailedOrderResult
from .util import parse_rfc3339, calculate_price, remove_none, simple_indent

class TaskingSearchRequest():
    start: date
    end: date
    gsd: float
    lat: float
    long: float
    north: float
    south: float
    east: float
    west: float
    polygon: Polygon
    supplier: str
    off_nadir: float
    
    def __init__(self, 
            start: date,
            end: date,
            gsd: float,
            off_nadir: float,
            lat: typing.Optional[float] = None,
            long: typing.Optional[float] = None,
            north: typing.Optional[float] = None,
            south: typing.Optional[float] = None,
            east: typing.Optional[float] = None,
            west: typing.Optional[float] = None,
            supplier: typing.Optional[str] = None,
            polygon: Polygon = None):
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

    def set_start(self, start: date) -> "TaskingSearchRequest":
        self.start = start
        return self

    def set_end(self, end: date) -> "TaskingSearchRequest":
        self.end = end
        return self
    
    def set_between_dates(self, start: date, end: date) -> "TaskingSearchRequest":
        self.start = start
        self.end = end
        return self
    
    def set_maximum_off_nadir(self, off_nadir: float) -> "TaskingSearchRequest":
        self.off_nadir = off_nadir
        return self

    def valid_point_of_interest(self) -> bool:
        return self.lat != None and self.long != None

    def valid_area_of_interest(self) -> bool:
        return self.north != None and self.south != None and self.east != None and self.west != None
    
    def valid(self) -> bool:
        return (self.valid_area_of_interest() or self.valid_point_of_interest()) and self.start != None and self.gsd != None
    
    def dict(self):
        d = {
            "start": str(self.start) if self.start != None else None, 
            "end": str(self.end) if self.end != None else None,
            "gsd": self.gsd, 
            "longLat": remove_none({"lat": self.lat, "long": self.long}),
            "boundingBox": remove_none({"west": self.west, "north": self.north, "south": self.south, "east": self.east}), 
            "supplier": self.supplier, "off-nadir": self.off_nadir,
            "polygon": json.dumps(self.polygon) if isinstance(self.polygon, list) else self.polygon
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
        
        return remove_none(d)

class TaskingSearchResponse():
    pass

class TaskingSearchResult():
    pass

class TaskingAPI:
    '''
        The TaskingAPI class is used to interface with the Arlula Tasking REST API
    '''

    def __init__(self,
                 session: Session):
        self.session = session
        self.url = self.session.baseURL + "/api/tasking"

    def search(self, request: TaskingSearchRequest) -> TaskingSearchResponse:
        '''
            Search the Arlula imagery archive.
            Requires one of (lat, long) or (north, south, east, west).
        '''

        url = self.url+"/search"

        # Send request and handle responses
        response = requests.request(
            "POST", url,
            headers=self.session.header,
            params=request.dict())
        if response.status_code != 200:
            raise ArlulaAPIException(response)
        else:
            resp_data = json.loads(response.text)
            # Construct an instance of `SearchResponse`
            return TaskingSearchResponse(resp_data)

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
