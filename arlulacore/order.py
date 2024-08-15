'''
    Defines the Order entity
'''

from datetime import datetime
import typing

from .util import parse_rfc3339
from .campaign import Campaign
from .dataset import Dataset
from .common import ArlulaObject

class Order(ArlulaObject):
    data: dict

    id: str
    """UUID to uniquely identify the order"""

    created_at: datetime
    """datetime the order was created at (UTC timezone)"""

    updated_at: datetime
    """datetime of the last update to the order (UTC timezone)"""

    status: str
    """current status of the order"""

    total: int
    """The total price of the order in US cents"""

    discount: int
    """The discount applied to the order by any order or user coupons"""

    tax: int
    """The tax paid on the order"""

    refunded: int
    """Amount in US cents refunded on this order."""

    payment_method: typing.Optional[str]
    """Identifier for the billing account used to place this order"""

    monitor: typing.Optional[str]
    """The monitor created for this order if any"""

    campaigns: typing.List[Campaign]
    """A list of all campaigns created for this order. *Not populated in list endpoints*"""
    
    datasets: typing.List[Dataset]
    """A list of all datasets created for this order (including those delivered to campaigns within this order). *Not populated in list endpoints*"""

    def __init__(self, data: dict):
        self.data = data
        self.id = data["id"]
        self.created_at = parse_rfc3339(data["createdAt"])
        self.updated_at = parse_rfc3339(data["updatedAt"])
        self.status = data["status"]
        self.total = data["total"]
        self.discount = data["discount"]
        self.tax = data["tax"]
        self.refunded = data.get("refunded", None)
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