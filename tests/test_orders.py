import os
import tempfile
import unittest

import arlulacore
from .util import create_test_session

class TestOrders(unittest.TestCase):

    def test_order_list(self):
        session = create_test_session()
        api = arlulacore.ArlulaAPI(session)
        response = api.ordersAPI().list()
    
    def test_order_get(self):
        session = create_test_session()
        api = arlulacore.ArlulaAPI(session)
        response = api.ordersAPI().get(os.getenv("API_ORDER_ID"))
    


    def test_order_resource_as_file(self):
        session = create_test_session()
        api = arlulacore.ArlulaAPI(session)
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, "temp")
            api.ordersAPI().get_resource_as_file(os.getenv("API_RESOURCE_ID"), "temp").close()
            self.assertTrue(os.path.getsize(filepath) > 0)
                
    def test_order_resource_directory(self):
        session = create_test_session()
        api = arlulacore.ArlulaAPI(session)
        with tempfile.TemporaryDirectory() as temp_dir:
            api.ordersAPI().get_resource_as_file(os.getenv("API_RESOURCE_ID"), suppress=True, directory=temp_dir).close()
            self.assertTrue(len(os.listdir(temp_dir)) == 1)

    def test_order_resource_as_memory(self):
        session = create_test_session()
        api = arlulacore.ArlulaAPI(session)
        b = api.ordersAPI().get_resource_as_memory(os.getenv("API_RESOURCE_ID"))
