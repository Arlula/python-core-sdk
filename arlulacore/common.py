import abc
import json
import typing

from .util import simple_indent

class ArlulaObject(abc.ABC):
    def __repr__(self):
        return str(['{}: {}'.format(attr, value) for attr, value in self.__dict__.items()])[1:-1].replace('\'', '')

    @abc.abstractmethod
    def dict(self):
        pass

    def format(self, format: str) -> str:
        if format == "json":
            return json.dumps(self.dict())
        if format == "text":
            return str(self)
        if format == "pretty-json":
            return json.dumps(self.dict(), indent=1)
        if format == "table":
            return str(self)

class License(ArlulaObject):
    data: dict
    name: str
    href: str
    loading_percent: float
    loading_amount: int

    def __init__(self, data):
        self.data = data
        self.name = data["name"]
        self.href = data["href"]
        self.loading_percent = data["loadingPercent"]
        self.loading_amount = data["loadingAmount"]

    def dict(self) -> dict:
        return self.data

    def __str__(self) -> str:
        return simple_indent(
        f"License ({self.href}):\n"\
        f"Name: {self.name}\n"\
        f"Loading: {self.loading_amount} US Cents + {self.loading_percent}%\n", 0, 2)

class Band(ArlulaObject):
    data: dict
    name: str
    id: str
    min: float
    max: float

    def __init__(self, data):
        self.data = data
        self.name = data["name"]
        self.id = data["id"]
        self.min = data["min"]
        self.max = data["max"]

    def centre(self) -> float:
        '''
            Get the band centre wavelength
        '''
        return (self.max - self.min)/2

    def width(self) -> float:
        '''
            Get the band width
        '''
        return self.max - self.min

    def dict(self) -> dict:
        return self.data

    def __str__(self) -> str:
        return simple_indent(
            f"Band ({self.id}):\n"\
            f"Name: {self.name}\n"\
            f"Bandwidth: {self.min}nm - {self.max}nm\n", 0, 2)

class Bundle(ArlulaObject):
    data: dict
    name: str
    key: str
    bands: typing.List[str]
    price: int

    def __init__(self, data):
        self.data = data
        self.name = data["name"]
        self.key = data["key"]
        self.bands = data["bands"]
        self.price = data["price"]

    def dict(self) -> dict:
        return self.data

    def __str__(self) -> str:
        bands = 'all' if len(self.bands) == 0 else '\n'.join(self.bands)
        return simple_indent(
            f"Bundle ({self.key}):\n"\
            f"Name: {self.name}\n"\
            f"Bands: {bands}\n"\
            f"Price: {self.price} US Cents\n", 0, 2)
