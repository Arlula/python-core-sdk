
from datetime import datetime
import typing

from .resource import Resource
from .util import parse_rfc3339, simple_indent
from .common import ArlulaObject

class Dataset(ArlulaObject):
    """
        Datasets represent 
    """

    data: dict
    id: str
    """Identifier for this dataset"""

    created_at: datetime
    """Date of creation"""

    updated_at: datetime
    """Date of last update"""
    
    type: str
    """Type of this dataset"""

    status: str
    """Status of this dataset"""

    supplier: str
    """Key of the supplier of this dataset"""

    ordering_id: str
    """Ordering ID used to purchase this dataset"""

    scene_id: str
    """Supplier scene identifier"""

    bundle: str
    """Processing level/bundle type"""

    eula: str
    """URL to the eula for this dataset"""

    total: int
    """Total amount (US Cents) paid for this dataset"""

    discount: int
    """Discount (US Cents)"""

    tax: int
    """Tax (US Cents)"""

    refunded: typing.Optional[int]
    """Amount (US Cents) refunded for this order"""

    order: str
    """Identifier for the order this dataset was placed under"""

    campaign: typing.Optional[str]
    """Identifier for the campaign this dataset was created by."""

    expiration: typing.Optional[datetime]
    """Time of expiration (If applicable)"""

    resources: typing.List[Resource]
    """Resources of this dataset. Note they will not be returned when listing."""

    def __init__(self, data: dict):
        self.data = data

        self.id = data["id"]
        self.created_at = parse_rfc3339(data["createdAt"])
        self.updated_at = parse_rfc3339(data["updatedAt"])
        self.type = data["type"]
        self.status = data["status"]
        self.supplier = data["supplier"]
        self.ordering_id = data["orderingID"]
        self.scene_id = data["sceneID"]
        self.bundle = data["bundle"]
        self.eula = data["eula"]
        self.total = data["total"]
        self.discount = data["discount"]
        self.tax = data["tax"]
        self.refunded = data.get("refunded", None)
        self.order = data["order"]
        self.campaign = data.get("campaign", None)
        self.expiration = parse_rfc3339(data["expiration"]) if "expiration" in data else None
        self.resources = [Resource(x) for x in data.get("resources", [])]

    def __dict__(self) -> dict:
        return self.data
    
# Helper function to type check a dataset type 
def get_dataset_id(dataset: typing.Union[str, Dataset]) -> str:
    if isinstance(dataset, str):
        return dataset
    elif isinstance(dataset, Dataset):
        return dataset.id
    else:
        raise TypeError("Invalid type for `dataset`")