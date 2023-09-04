import abc
import json
import typing

from .util import remove_none, simple_indent

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
    """A human readable name to refer to this license type (i.e. 'internal', or 'enterprise')"""

    href: str
    """A URL at which the terms of the license can be read, use this value in the ordering endpoints “eula” field to select this license for ordering"""

    loading_percent: float
    """The percentage loading this license applies to the bundle's price"""

    loading_amount: int
    """The static amount (in US cents) this license adds to the bundle's price"""

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
    """the common name of the band frequently used to identify it in a human readable manner (i.e. 'Red' or 'Short Wave InfraRed')"""

    id: str
    """A short form identifier for the band used to identify the band in references."""

    min: float
    """the minimum wavelength that makes up the band in nanometers (nm)"""

    max: float
    """the maximum wavelength that makes up the band in nanometers (nm)"""

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
    """Name of this bundle."""

    key: str
    """The bundle key that is to be provided to the order endpoint to purchase this bundle"""

    bands: typing.List[str]
    """The list of bands included in this level as a list of the bands 'id' property, if the list is empty, all bands are provided."""
    
    price: int
    """The base price for this bundle in US cents"""

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

Field = typing.TypeVar("Field")

class SortDefinition(typing.Generic[Field]):
    ascending: bool
    """Whether the sort should be ascending or descending in order"""

    field: Field
    """The field to sort by"""

    def __init__(self, field: Field, ascending: bool):
        self.ascending = ascending
        self.field = field

    def dict(self):
        return remove_none({
            "ascending": self.ascending,
            "field": self.field, 
        })