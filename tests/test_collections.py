import datetime
import os
import random
import string
import tempfile
import unittest

import arlulacore
from .util import create_test_session


class TestCollectionItemsListRequest(unittest.TestCase):
    
    def test_to_dict(self):
        reqs = [
            arlulacore.CollectionListItemsRequest().dict(),
            arlulacore.CollectionListItemsRequest(
                page=1,
                limit=1,
                bbox=[1, 2, 3, 4],
            )
        ]

        exps = [
            {"limit": 100, "page": 0},
            {"limit": 1, "page": 1, "bbox":[1, 2, 3, 4]}
        ]

        for req, exp in zip(reqs, exps):
            pass

    def test_time_not_provided(self):

        self.assertEqual(
            arlulacore.CollectionListItemsRequest()._to_interval(),
            None
        )

    def test_time_open_start(self):
        self.assertEqual(
            arlulacore.CollectionListItemsRequest(end=datetime.datetime(2023, 1, 2, 3, 4, 5, 6))._to_interval(),
            "/.."
        )


    def test_time_open_end(self):
        pass

    def test_time_closed(self):
        pass

    def test_time_single(self):
        pass


class TestOther(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls._session = create_test_session()
        cls._api = arlulacore.ArlulaAPI(cls._session)

    def test_conformance(self):
        self._api.collectionsAPI().conformance()
    
    def test_request_item_access(self):
        # self._api.collectionsAPI().request_access_item()
        pass

class TestCollectionItem(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls._session = create_test_session()
        cls._api = arlulacore.ArlulaAPI(cls._session)

    def test_get_item(self):
        """
            Test getting a predefined item 
        """
        self._api.collectionsAPI().get_item(os.getenv("API_COLLECTION_ID"), os.getenv("API_COLLECTION_ITEM_ID"))

    def test_import(self):
        """
            Test importing a predefined order
        """
        self._api.collectionsAPI().import_order(os.getenv("API_COLLECTION_ID"), os.getenv("API_ORDER_ID"))


