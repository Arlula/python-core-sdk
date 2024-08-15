import datetime
import os
import random
import string
import unittest

import arlulacore
from .util import create_test_session


class TestCollectionItemsListRequest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._session = create_test_session()
        cls._api = arlulacore.ArlulaAPI(cls._session)
    
    def test_list_basic(self):
        list = self._api.collectionsAPI().list_items(arlulacore.CollectionListItemsRequest(
            collection=os.getenv("API_COLLECTION_ID"),
        ))
        self.assertTrue(len(list.features) > 0)

    def test_list_complex(self):
        items = self._api.collectionsAPI().list_items(arlulacore.CollectionListItemsRequest(
            os.getenv("API_COLLECTION_ID"),
            bbox=[-10, -10, 10, 10],
            start=datetime.datetime(2020, 1, 1, 10, 10, 10, tzinfo=datetime.timezone.utc),
            end=datetime.datetime(2023, 1, 1, tzinfo=datetime.timezone.utc),
        ))
    
    def test_to_dict(self):
        reqs = [
            arlulacore.CollectionListItemsRequest(
                os.getenv("API_COLLECTION_ID")
            ).dict(),
            arlulacore.CollectionListItemsRequest(
                os.getenv("API_COLLECTION_ID"),
                page=1,
                limit=1,
                start=datetime.datetime(2020, 1, 2, 3, 4, 5, 6, tzinfo=datetime.timezone.utc),
                bbox=[1, 2, 3, 4],
            ).dict()
        ]

        exps = [
            {"limit": 100, "page": 0},
            {"limit": 1, "page": 1, "bbox":[1, 2, 3, 4], "datetime":"2020-01-02T03:04:05.000006+00:00/.."}
        ]

        for req, exp in zip(reqs, exps):
            self.assertDictEqual(req, exp)

    def test_time_not_provided(self):
        self.assertEqual(
            arlulacore.CollectionListItemsRequest(
                os.getenv("API_COLLECTION_ID")
            )._to_interval(),
            None
        )

    def test_time_open_start(self):
        self.assertEqual(
            arlulacore.CollectionListItemsRequest(
                os.getenv("API_COLLECTION_ID"), 
                end=datetime.datetime(2023, 1, 2, 3, 4, 5, 6, tzinfo=datetime.timezone.utc)
            )._to_interval(),
            "../2023-01-02T03:04:05.000006+00:00"
        )


    def test_time_open_end(self):
        self.assertEqual(
            arlulacore.CollectionListItemsRequest(
                os.getenv("API_COLLECTION_ID"), 
                end=datetime.datetime(2023, 1, 2, 3, 4, 5, 6, tzinfo=datetime.timezone.utc)
            )._to_interval(),
            "../2023-01-02T03:04:05.000006+00:00"
        )

    def test_time_closed(self):
        self.assertEqual(
            arlulacore.CollectionListItemsRequest(
                os.getenv("API_COLLECTION_ID"), 
                end=datetime.datetime(2021, 1, 2, 3, 4, 5, 6, tzinfo=datetime.timezone.utc),
                start=datetime.datetime(2023, 1, 2, 3, tzinfo=datetime.timezone.utc),
            )._to_interval(),
            "2023-01-02T03:00:00+00:00/2021-01-02T03:04:05.000006+00:00"
        )

    def test_time_single(self):
        self.assertEqual(
            arlulacore.CollectionListItemsRequest(
                os.getenv("API_COLLECTION_ID"), 
                datetime=datetime.datetime(2023, 1, 2, 3, tzinfo=datetime.timezone.utc),
            )._to_interval(),
            "2023-01-02T03:00:00+00:00"
        )

class TestCollectionSearchItems(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._session = create_test_session()
        cls._api = arlulacore.ArlulaAPI(cls._session)

    def test_search_basic(self):
        list = self._api.collectionsAPI().search_items(arlulacore.CollectionSearchRequest(
            collection=os.getenv("API_COLLECTION_ID"),
            ids=[os.getenv("API_COLLECTION_ITEM_ID")]
        ))
        self.assertTrue(len(list.features) > 0)

    def test_search_complex(self):
        items = self._api.collectionsAPI().search_items(arlulacore.CollectionSearchRequest(
            os.getenv("API_COLLECTION_ID"),
            bbox=[-10, -10, 10, 10],
            start=datetime.datetime(2020, 1, 1, 10, 10, 10, tzinfo=datetime.timezone.utc),
            end=datetime.datetime(2023, 1, 1, tzinfo=datetime.timezone.utc),
        ))
    
    def test_to_dict(self):
        reqs = [
            arlulacore.CollectionSearchRequest(
                os.getenv("API_COLLECTION_ID")
            ).dict(),
            arlulacore.CollectionSearchRequest(
                os.getenv("API_COLLECTION_ID"),
                page=1,
                limit=1,
                start=datetime.datetime(2020, 1, 2, 3, 4, 5, 6, tzinfo=datetime.timezone.utc),
                bbox=[1, 2, 3, 4],
                queries={
                    arlulacore.QueryFieldNumber.cloud_cover: arlulacore.NumericalQuery(lt=90),
                    arlulacore.QueryFieldString.band: arlulacore.StringQuery(eq="red"),
                    arlulacore.QueryFieldNumber.gsd: arlulacore.NumericalQuery(range=(0.4, 0.5))
                }
            ).dict()
        ]

        exps = [
            {
                "limit": 100, 
                "page": 0
            },
            {
                "limit": 1, 
                "page": 1, 
                "datetime":"2020-01-02T03:04:05.000006+00:00/..",
                "bbox":[1, 2, 3, 4], 
                "queries": {
                    "eo:cloud_cover": {
                        "lt": 90
                    },
                    "band": {
                        "eq": "red"
                    },
                    "gsd": {
                        "range": {
                            "minimum": 0.4,
                            "maximum": 0.5
                        }
                    }
                }
            }
        ]

        for req, exp in zip(reqs, exps):
            self.assertDictEqual(req, exp)

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
        self._api.collectionsAPI().import_order(os.getenv("API_COLLECTION_ID"), os.getenv("API_DATASET_ID"))


class TestCollections(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._session = create_test_session()
        cls._api = arlulacore.ArlulaAPI(cls._session)

    def test_create(self):
        """
            Test creating a collection and then deleting it
        """
        reqs = [
            arlulacore.CollectionCreateRequest(
                title="Test Collection Title",
                description="Test Collection Description",
                keywords=["test"],
            ),
        ]
        resps = []

        try:
            for req in reqs:
                resp = self._api.collectionsAPI().create(req)
                resps.append(resp)

                self.assertEqual(resp.title, req.title)
                self.assertEqual(resp.description, req.description)
                self.assertEqual(resp.keywords, req.keywords)
        except Exception as e:
            raise e
        finally:
            for resp in resps:
                self._api.collectionsAPI().delete(resp)

    def test_detail_existing(self):
        """
            Test that the predefined collection can be retrieved successfully
        """
        self._api.collectionsAPI().detail(os.getenv("API_COLLECTION_ID"))

    def test_detail_nonexisting(self):
        """
            Test that a collection that does not exist cannot be retrieved
        """
        with self.assertRaises(arlulacore.ArlulaAPIException) as e:
            self._api.collectionsAPI().detail("f6caab9f-acd3-400f-8a92-012ffa2d8d69")

    def test_update(self):
        """
            Test that the predefined collection can be updated successfully
        """

        # Generate a random string
        random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

        before = self._api.collectionsAPI().detail(os.getenv("API_COLLECTION_ID"))

        update = self._api.collectionsAPI().update(arlulacore.CollectionUpdateRequest(
            collection=before,
            title="Test Collection Title", 
            description=random_string,
        ))

        after = self._api.collectionsAPI().detail(os.getenv("API_COLLECTION_ID"))
        
        self.assertEqual(update.description, random_string)
        self.assertEqual(after.description, random_string)

