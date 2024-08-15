from datetime import date
import datetime
import json
import os
import unittest
import arlulacore
from .util import create_test_session

class TestTaskingSearchRequest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._session = create_test_session()
        cls._api = arlulacore.ArlulaAPI(cls._session)

    def test_to_dict(self):
        '''
            Tests TaskingSearchRequest construction methods
        '''
        pass    

    def test_search_point(self):
        """
            Tests searching a point of interest on the tasking API
        """
        result = self._api.taskingAPI().search(
            arlulacore.TaskingSearchRequest(
                datetime.datetime.now(datetime.timezone.utc), 
                datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30),
                10,
                40,
            )
            .set_point_of_interest(-33, 151)
        )
                
        self.assertTrue(
            len(result.results) > 0
        )

    def test_search_aoi(self):
        """
            Tests searching an area of interest on the tasking API
        """
                
        result = self._api.taskingAPI().search(
            arlulacore.TaskingSearchRequest(
                datetime.datetime.now(datetime.timezone.utc), 
                datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30),
                10,
                40,
            )
            .set_area_of_interest(-33, -33.1, 150.1, 150)
        )
                
        self.assertTrue(
            len(result.results) > 0
        )

    def test_search_polygon_array(self):
        """
            Tests searching a polygon on the tasking API
        """

        result = self._api.taskingAPI().search(
            arlulacore.TaskingSearchRequest(
                datetime.datetime.now(datetime.timezone.utc), 
                datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30),
                10,
                40,
            )
            .set_polygon([[[151.17592271889822,-33.90012296148858],[151.18776360157415,-33.94086373059308],[151.22992869598534,-33.938946954784306],[151.25823129360515,-33.91546294929382],[151.25736488755598,-33.88765718887135],[151.2085573467637,-33.87902597130201],[151.17592271889822,-33.90012296148858]]])
        )
                
        self.assertTrue(
            len(result.results) > 0
        )

class TestOrderRequest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._session = create_test_session()
        cls._api = arlulacore.ArlulaAPI(cls._session)
    
    def test_order(self):
        """
            Tests placing a tasking order
        """
        order = self._api.taskingAPI().order(arlulacore.TaskingOrderRequest(
            os.getenv("API_TASKING_ORDERING_ID_1"),
            os.getenv("API_TASKING_LICENSE_HREF_1"),
            os.getenv("API_TASKING_BUNDLE_KEY_1"),
            os.getenv("API_TASKING_PRIORITY_KEY_1"),
            int(os.getenv("API_TASKING_CLOUD_1")),
        ))

        self.assertEqual(len(order.campaigns), 1)

    def test_order_batch(self):
        """
            Tests placing a tasking batch order
        """

        req = arlulacore.TaskingBatchOrderRequest(
            [arlulacore.TaskingOrderRequest(
                os.getenv("API_TASKING_ORDERING_ID_1"),
                os.getenv("API_TASKING_LICENSE_HREF_1"),
                os.getenv("API_TASKING_BUNDLE_KEY_1"),
                os.getenv("API_TASKING_PRIORITY_KEY_1"),
                int(os.getenv("API_TASKING_CLOUD_1")),
            )],
        )

        req.add_order(arlulacore.TaskingOrderRequest(
            os.getenv("API_TASKING_ORDERING_ID_2"),
            os.getenv("API_TASKING_LICENSE_HREF_2"),
            os.getenv("API_TASKING_BUNDLE_KEY_2"),
            os.getenv("API_TASKING_PRIORITY_KEY_2"),
            int(os.getenv("API_TASKING_CLOUD_2")),
        ))

        order = self._api.taskingAPI().batch_order(req)

        self.assertEqual(len(order.campaigns), 2)