'''
    Defines the Resource entity
'''

from datetime import datetime
import typing
from .common import ArlulaObject
from .util import parse_rfc3339, simple_indent


class Resource(ArlulaObject):
    data: dict
    id: str
    """Identifier for this resource"""

    created_at: datetime
    """Creation timestamp"""

    updated_at: datetime
    """Last update timestamp"""

    dataset: str
    """Identifier for the dataset this resource belongs to"""

    name: str
    """Human readable name for this resource"""

    type: str
    """Indicator for type of resource"""

    format: str
    """TODO Format"""

    roles: typing.List[str]
    """TODO Roles"""

    size: int
    """File size (bytes)"""

    checksum: str
    """Checksum for the file `method:"hash"` """

    def __init__(self, data):
        self.data = data
        self.id = data["id"]
        self.created_at = parse_rfc3339(data["createdAt"])
        self.updated_at = parse_rfc3339(data["updatedAt"])
        self.dataset = data["dataset"]
        self.name = data["name"]
        self.type = data["type"]
        self.format = data["format"]
        self.roles = data["roles"]
        self.size = data["size"]
        self.checksum = data["checksum"]

    def __str__(self) -> str:
        text = simple_indent(
            f"Resource ({self.id}):\n"\
            # f"Created At: {self.created_at.isoformat()}\n"\
            # f"Updated At: {self.updated_at.isoformat()}\n"\
            # f"Order ID: {self.order}\n"\
            f"Name: {self.name}\n"\
            f"Type: {self.type}\n"\
            f"Format: {self.format}\n"\
            f"Roles: {', '.join(self.roles)}\n"\
            f"Size: {self.size} Bytes\n"\
            f"Checksum: {self.checksum}\n", 0, 2)
        return text

    def dict(self):
        return self.data


# Helper function to type check a resource type 
def get_resource_id(resource: typing.Union[str, Resource]) -> str:
    if isinstance(resource, str):
        return resource
    elif isinstance(resource, Resource):
        return resource.id
    else:
        raise TypeError("Invalid type for `resource`")
    
