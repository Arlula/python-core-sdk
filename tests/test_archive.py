from datetime import date
import unittest
import arlulacore
from arlulacore import arlula
from tests.util import create_test_session

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
                "res": 100
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
                "res": 100,
            }
        )

        self.assertEqual(
            arlulacore.SearchRequest(date(2021, 1, 1), 100)
            .set_point_of_interest(0, 10)
            .dict(),
            {
                "start": "2021-01-01",
                "res": 100,
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
                "res": 100,
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
                "res": 0,
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

    def test_search(self):
        session = create_test_session()
        api = arlulacore.ArlulaAPI(session)
        result = api.archiveAPI().search(
            arlulacore.SearchRequest(date(2020, 1, 1), 100)
            .set_point_of_interest(-33, 151)
            .set_end(date(2020, 2, 1))
        )
                
        self.assertTrue(
            len(result) > 0
        )