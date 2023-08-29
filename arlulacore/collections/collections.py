import json
import requests

from arlulacore.exception import ArlulaAPIException


class Collection:
    pass

class CollectionCreateRequest:

    title: str
    """A title/name for the collection to identify it"""

    description: str
    """A description of the collection, such as its purpose, or the location of interest."""

    keywords: typing.List[str]
    """A list of keywords that describe the collections content for organisational purposes"""

    team: typing.Optional[str]
    """The team that will be the owner of the collection (defaults to the requesting API directly)"""

    def __init__(
        self,
        title: str,
        description: str,
        keywords: typing.Optional[typing.List[str]] = [],
        team: typing.Optional[str] = None, 
    ):
        self.title = title
        self.description = description
        self.keywords = keywords
        self.team = team
    
    def set_title(self, title: str) -> "CollectionCreateRequest":
        self.title = title
        return self
    
    def set_description(self, description: str) -> "CollectionCreateRequest":
        self.description = description
        return self
    
    def set_keywords(self, keywords: typing.List[str]) -> "CollectionCreateRequest":
        self.keywords = keywords
        return self

    def add_keyword(self, keyword: str) -> "CollectionCreateRequest":
        self.keywords.append(keyword)
        return self
    
    def set_team(self, team: str) -> "CollectionCreateRequest":
        self.team = team
        return self
class CollectionsAPI:

    def list_collections(self, request: CollectionListRequest) -> CollectionListResponse:
        
        url = self.url+"/list"

        response = requests.request(
            "GET",
            url,
            params=request.dict(),
            headers=self.session.header)

        if response.status_code != 200:
            raise ArlulaAPIException(response)
        else:
            return CollectionListResponse(json.loads(response.text))

    def detail_collection(self, request: CollectionDetailRequest) -> CollectionDetailResponse:

        url = self.url+"/detail"

        params = {
            "page": request.page or 1,
            "size": request.size or 100,
        }

        response = requests.request(
            "GET",
            url,
            params=params,
            headers=self.session.header)

        if response.status_code != 200:
            raise ArlulaAPIException(response)
        else:
            return CollectionListResponse(json.loads(response.text))

    def list_items(self, request: CollectionListItemsRequest) -> CollectionListItemsResponse:
    def create(self, request: CollectionCreateRequest) -> Collection:
        
        response = requests.request(
            "POST",
            self.url,
            data=json.dumps(request.dict()),
            headers=self.session.header
        )

        if response.status_code != 200:
            raise ArlulaAPIException(response)
        else:
            return Collection(json.loads(response.text))
        
        pass

    def remove_collection(self, request: CollectionRemoveRequest) -> CollectionRemoveResponse:
        pass

    def update_collection(self, request: CollectionUpdateRequest) -> CollectionUpdateResponse:
        pass

    def delete_collection(self, request: CollectionDeleteRequest) -> CollectionDeleteResponse:
        pass

    def request_access_to_item(self, request: CollectionRequestAccessToItemRequest) -> CollectionRequestI:
        pass

    def conformance(self):
        pass



