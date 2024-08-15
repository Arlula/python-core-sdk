'''
    Defines helper base types for list endpoints
'''

import typing

T = typing.TypeVar("T")
class ListResponse(typing.Generic[T]):
    """
        Generic utility type for list responses
    """
    data: dict
    
    content: typing.List[T]
    """List items"""

    page: int
    """Page number"""

    length: int
    """Page size"""

    count: int
    """Total number of results"""

    def __init__(self, data: dict, content: typing.List[T]):
        self.data = data
        self.content = content
        self.page = data["page"]
        self.length = data["length"]
        self.count = data["count"]
    
    def __dict__(self) -> dict:
        return self.data
    
class ListRequest:
    """
        Base list request type
    """

    page: int
    """Page to get results for"""

    size: int
    """Number of results per page"""

    def __init__(self, 
        page: typing.Optional[int] = None, 
        size: typing.Optional[int] = None,
    ):
        self.page = page or 0
        self.size = size or 20
    
    def __dict__(self):
        return {
            "page": self.page,
            "size": self.size,
        }