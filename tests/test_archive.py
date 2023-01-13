from datetime import date
import json
import os
import unittest
import arlulacore
from .util import create_test_session

class TestSearchRequest(unittest.TestCase):

    def test_to_dict(self):
        '''
            Tests SearchRequest construction methods
        '''

        self.assertEqual(
            arlulacore.SearchRequest(date(2021, 1, 1), 100)
            .dict(), 
            {
                "start": "2021-01-01",
                "gsd": 100
            }
        )

        self.assertEqual(
            arlulacore.SearchRequest(date(2021, 1, 1), 100)
            .set_area_of_interest(-10, 0, 10, 20)
            .dict(),
            {
                "start": "2021-01-01",
                "north": -10,
                "south": 0,
                "east": 10,
                "west": 20,
                "gsd": 100,
            }
        )

        self.assertEqual(
            arlulacore.SearchRequest(date(2021, 1, 1), 100)
            .set_point_of_interest(0, 10)
            .dict(),
            {
                "start": "2021-01-01",
                "gsd": 100,
                "lat": 0,
                "long": 10,
            }
        )

        self.assertEqual(
            arlulacore.SearchRequest(date(2021, 1, 1), 100)
            .set_point_of_interest(0, 10)
            .set_end(date(2021, 2, 1))
            .set_maximum_cloud_cover(10)
            .set_maximum_off_nadir(20)
            .set_supplier("landsat")
            .dict(),
            {
                "start": "2021-01-01",
                "end": "2021-02-01",
                "gsd": 100,
                "lat": 0,
                "long": 10,
                "cloud": 10,
                "off-nadir": 20,
                "supplier": "landsat"
            }
        )

        self.assertEqual(
            arlulacore.SearchRequest(date(2021, 1, 1), 0, 10, date(2021, 2, 1), 20, 30, 40, 50, 60, 70, "landsat", 80)
            .dict(),
            {
                "start": "2021-01-01",
                "end": "2021-02-01",
                "gsd": 0,
                "cloud": 10,
                "lat": 20,
                "long": 30,
                "north": 40,
                "south": 50,
                "east": 60,
                "west": 70,
                "supplier": "landsat",
                "off-nadir": 80,
            }
        )

    def test_search_point(self):
        session = create_test_session()
        api = arlulacore.ArlulaAPI(session)
        result = api.archiveAPI().search(
            arlulacore.SearchRequest(date(2020, 1, 1), 100)
            .set_point_of_interest(-33, 151)
            .set_end(date(2020, 2, 1))
        )
                
        self.assertTrue(
            len(result.results) > 0
        )

    def test_search_aoi(self):
        session = create_test_session()
        api = arlulacore.ArlulaAPI(session)
        result = api.archiveAPI().search(
            arlulacore.SearchRequest(date(2020, 1, 1), 100)
            .set_area_of_interest(-33, -33.1, 150.1, 150)
            .set_end(date(2020, 2, 1))
        )
                
        self.assertTrue(
            len(result.results) > 0
        )

    def test_search_polygon_wkt(self):
        session = create_test_session()
        api = arlulacore.ArlulaAPI(session)
        result = api.archiveAPI().search(
            arlulacore.SearchRequest(date(2020, 1, 1), 100)
            .set_polygon("POLYGON((151.17454501612775 -33.90059831814348,151.16355868800275 -33.91769420996655,151.18724795802228 -33.93549878391787,151.19531604273908 -33.90700967940383,151.19359942896955 -33.89247656841645,151.17454501612775 -33.90059831814348))")
            .set_end(date(2020, 2, 1))
        )
                
        self.assertTrue(
            len(result.results) > 0
        )
    
    def test_search_polygon_array(self):
        session = create_test_session()
        api = arlulacore.ArlulaAPI(session)
        result = api.archiveAPI().search(
            arlulacore.SearchRequest(date(2020, 1, 1), 100)
            .set_polygon([[[151.17592271889822,-33.90012296148858],[151.18776360157415,-33.94086373059308],[151.22992869598534,-33.938946954784306],[151.25823129360515,-33.91546294929382],[151.25736488755598,-33.88765718887135],[151.2085573467637,-33.87902597130201],[151.17592271889822,-33.90012296148858]]])
            .set_end(date(2020, 2, 1))
        )
                
        self.assertTrue(
            len(result.results) > 0
        )

class TestOrderRequest(unittest.TestCase):

    def test_dumps(self):
        
        self.assertEqual(json.dumps(arlulacore.OrderRequest("id", "eula", "bundle_key").dict()), 
            json.dumps({
                "id": "id",
                "eula": "eula",
                "bundleKey": "bundle_key",
                "webhooks": [],
                "emails": [],
            })
        )
        
        self.assertEqual(json.dumps(arlulacore.OrderRequest("id", "eula", "bundle_key", ["https://test1.com", "https://test2.com"], ["test1@gmail.com", "test2@gmail.com"]).dict()),
            json.dumps({
                "id": "id",
                "eula": "eula",
                "bundleKey": "bundle_key",
                "webhooks": ["https://test1.com", "https://test2.com"],
                "emails": ["test1@gmail.com", "test2@gmail.com"],
            })
        )

        self.assertEqual(json.dumps(arlulacore.OrderRequest("id", "eula", "bundle_key", ["https://test1.com"], ["test1@gmail.com"])
            .add_email("test2@gmail.com")
            .add_webhook("https://test2.com")
            .dict()),
            json.dumps({
                "id": "id",
                "eula": "eula",
                "bundleKey": "bundle_key",
                "webhooks": ["https://test1.com", "https://test2.com"],
                "emails": ["test1@gmail.com", "test2@gmail.com"],
            })
        )
    
    def test_order(self):

        # This will throw an exception on failure
        session = create_test_session()
        api = arlulacore.ArlulaAPI(session)
        response = api.archiveAPI().order(arlulacore.OrderRequest(os.getenv("API_ORDERING_ID"), os.getenv("API_ORDER_LICENSE_HREF"), os.getenv("API_ORDER_BUNDLE_KEY"), team=os.getenv("API_TEAM_ID")))
