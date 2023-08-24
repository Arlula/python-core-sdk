import json
import requests

from arlulacore.exception import ArlulaAPIException


class Collection:
    pass

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
        pass

    def detail_item(self, request: CollectionDetailItemRequest) -> CollectionDetailItemResponse:
        pass

    def search_collections(self, request: CollectionSearchRequest) -> CollectionSearchResponse:
        pass

    def create_collection(self, request: CollectionCreateRequest) -> CollectionCreateResponse:
        pass

    def add_item_to_collection(self, request: CollectionAddItemRequest) -> CollectionAddItemResponse:
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



