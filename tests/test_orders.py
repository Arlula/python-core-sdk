import os
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

        with api.ordersAPI().get_resource_as_file(os.getenv("API_RESOURCE_ID"), "temp") as f:
            pass
        os.remove("temp")

    def test_order_resource_as_memory(self):
        session = create_test_session()
        api = arlulacore.ArlulaAPI(session)
        b = api.ordersAPI().get_resource_as_memory(os.getenv("API_RESOURCE_ID"))
