
from datetime import datetime
import typing

from .dataset import Dataset
from .util import parse_rfc3339
from .common import ArlulaObject

class Campaign(ArlulaObject):
    """
        A campaign represents 
    """

    data: dict
    id: str
    """identifier for this campaign."""

    createdAt: datetime
    """Creation timestamp"""

    updatedAt: datetime
    """Last update timestamp"""

    status: str
    """Campaign status"""

    orderingID: str
    """OrderingID used to order this campaign"""

    bundle: str
    """Bundle/processing level identifier for data delivered from this campaign."""

    license: str
    """URL to the license for data delivered from this campaign."""

    priority: str
    """Priority identifier for this campaign"""

    total: int
    """Total amount paid (US Cents)"""

    discount: int
    """Discount (US Cents)"""

    tax: int
    """Tax (US Cents)"""

    refunded: typing.Optional[int]
    """Amount refunded (US Cents)"""

    order: str
    """Identifier for the order this dataset was placed under"""

    site: typing.Optional[str]
    """Idenfitier of site of this campaign"""

    monitor: typing.Optional[str]
    """Identifier for the monitor this campaign delivers data to"""

    start: datetime
    """Start time of this campaign"""

    end: datetime
    """End time of this campaign"""

    aoi: typing.List[typing.List[typing.List[int]]]
    """Region covered by this campaign"""

    cloud: int
    """Maximum cloud coverage purchased"""

    offNadir: float
    """Maximum off nadir for this campaign"""

    supplier: str
    """Supplier delivering this campaign"""

    platforms: typing.List[str]
    """Platforms to be considered for capturing this campaign"""

    gsd: float
    """Maximum GSD acceptable for this campaign"""

    datasets: typing.List[Dataset]
    """Currently delivered datasets. Not populated if this comes from a list endpoint."""

    def __init__(self, data: dict):
        self.data = data
        self.id = data["id"]
        self.created_at = parse_rfc3339(data["createdAt"])
        self.updated_at = parse_rfc3339(data["updatedAt"])
        self.status = data["status"]
        self.ordering_id = data["orderingID"]
        self.bundle = data["bundle"]
        self.license = data["license"] if "license" in data else print("NOT THERE")
        self.priority = data["priority"]
        self.total = data["total"]
        self.discount = data["discount"]
        self.tax = data["tax"]
        self.refunded = data.get("refunded", None)
        self.order = data["order"]
        self.site = data.get("site", None)
        self.monitor = data.get("monitor", None)
        self.start = parse_rfc3339(data["start"])
        self.end = parse_rfc3339(data["end"])
        self.aoi = data["aoi"]
        self.cloud = data["cloud"]
        self.off_nadir = data["offNadir"]
        self.supplier = data["supplier"]
        self.platforms = data["platforms"]
        self.gsd = data["gsd"]
        self.datasets = [Dataset(x) for x in data.get("datasets", [])]

    def __dict__(self) -> dict:
        return self.dict
    
# Helper function to type check a campaign type
def get_campaign_id(campaign: typing.Union[str, Campaign]) -> str:
    if isinstance(campaign, str):
        return campaign
    elif isinstance(campaign, Campaign):
        return campaign.id
    else:
        raise TypeError("Invalid type for `campaign`")
    