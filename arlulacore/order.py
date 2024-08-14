

from datetime import datetime
import typing

from .util import parse_rfc3339
from .campaign import Campaign
from .dataset import Dataset
from .common import ArlulaObject

class Order(ArlulaObject):
    data: dict

    id: str
    created_at: datetime
    updated_at: datetime
    status: str
    total: int
    discount: int
    tax: int
    payment_method: typing.Optional[str]
    monitor: typing.Optional[str]
    campaigns: typing.List[Campaign]
    datasets: typing.List[Dataset]

    def __init__(self, data: dict):
        self.data = data
        self.id = data["id"]
        self.created_at = parse_rfc3339(data["createdAt"])
        self.updated_at = parse_rfc3339(data["updatedAt"])
        self.status = data["status"]
        self.total = data["total"]
        self.discount = data["discount"]
        self.tax = data["tax"]
        self.payment_method = data["paymentMethod"]
        self.monitor = data.get("monitor", None)
        self.campaigns = data.get("campaigns", [])
        self.campaigns = [Campaign(x) for x in data.get("campaigns", [])]
        self.datasets = [Dataset(x) for x in data.get("datasets", [])]
    
    def __dict__(self) -> dict:
        return self.data
    
def get_order_id(order: typing.Union[str, Order]) -> str:
    """
        Helper function to get an order id from a union type
    """
    
    if isinstance(order, str):
        return order
    elif isinstance(order, Order):
        return order.id
    else:
        raise TypeError("Invalid type for `order`")