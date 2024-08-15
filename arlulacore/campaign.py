'''
    Defines the Campaign Entity
'''

from datetime import datetime
import typing

from .dataset import Dataset
from .util import parse_rfc3339
from .common import ArlulaObject

class Campaign(ArlulaObject):
    """
        Tasking orders are represented as a campaign for capture.
        The campaign persists details of the requested coverage and capture conditions, and will present details of the campaign's status, and the datasets created from each capture in the campaign, representing delivered data.
    """

    data: dict
    id: str
    """UUID to uniquely identify the campaign"""

    createdAt: datetime
    """datetime the campaign was created at (UTC timezone)"""

    updatedAt: datetime
    """datetime of the last update to the campaign (UTC timezone)"""

    status: str
    """	current status of the campaign"""

    orderingID: str
    """ID used to order the campaign"""

    bundle: str
    """Key of the bundle ordered for this tasking campaign"""

    license: str
    """License this tasking campaign was ordered under"""

    priority: str
    """Priority code this campaign was ordered under"""

    total: int
    """total price of the campaign in US cents"""

    discount: int
    """Amount in US cents discounted from this campaign by coupon usage"""

    tax: int
    """Tax collected on this tasking campaign in US cents"""

    refunded: typing.Optional[int]
    """Amount in US cents refunded on this campaign."""

    order: str
    """UUID of the order the campaign belongs to"""

    site: typing.Optional[str]
    """UUID of the saved site the campaign is of (or null)"""

    monitor: typing.Optional[str]
    """Identifier for the monitor this campaign delivers data to"""

    start: datetime
    """Datetime at which this capture campaign is to begin capture"""

    end: datetime
    """Datetime that this campaign will be considered complete"""

    aoi: typing.List[typing.List[typing.List[int]]]
    """The polygon defining the Area Of Interest that this campaign is targeting"""

    cloud: int
    """The maximum allowable cloud cover for captures in this campaign"""

    offNadir: float
    """The maximum allowable off nadir angle for captures in this campaign"""

    supplier: str
    """The supplier fulfilling this campaign"""

    platforms: typing.List[str]
    """The list of acceptable capture platforms for this campaign"""

    gsd: float
    """Ground sample distance requirement for captures in this campaign"""

    datasets: typing.List[Dataset]
    """The list of delivered datasets captured as part of this campaign"""

    def __init__(self, data: dict):
        self.data = data
        self.id = data["id"]
        self.created_at = parse_rfc3339(data["createdAt"])
        self.updated_at = parse_rfc3339(data["updatedAt"])
        self.status = data["status"]
        self.ordering_id = data["orderingID"]
        self.bundle = data["bundle"]
        self.license = data["license"]
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
    