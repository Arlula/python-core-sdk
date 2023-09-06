
import unittest
import os

class TestEnv(unittest.TestCase):
    '''
        Test the environment is setup correctly.
    '''
    def test_host(self):
        self.assertNotEqual(os.getenv("API_HOST"), None)
    def test_key(self):
        self.assertNotEqual(os.getenv("API_KEY"), None)
    def test_secret(self):
        self.assertNotEqual(os.getenv("API_SECRET"), None)
    def test_order_license_href(self):
        self.assertNotEqual(os.getenv("API_ORDER_LICENSE_HREF"), None)
    def test_order_bundle_key(self):
        self.assertNotEqual(os.getenv("API_ORDER_BUNDLE_KEY"), None)
    def test_ordering_id(self):
        self.assertNotEqual(os.getenv("API_ORDERING_ID"), None)
    def test_resource_id(self):
        self.assertNotEqual(os.getenv("API_RESOURCE_ID"), None)
    def test_team_id(self):
        self.assertNotEqual(os.getenv("API_TEAM_ID"), None)
    def test_collection_id(self):
        self.assertNotEqual(os.getenv("API_COLLECTION_ID"), None)
    def test_collection_item_id(self):
        self.assertNotEqual(os.getenv("API_COLLECTION_ITEM_ID"), None)
    def tasking_order_1(self):
        self.assertNotEqual(os.getenv("API_TASKING_ORDERING_ID_1"), None)
        self.assertNotEqual(os.getenv("API_TASKING_BUNDLE_KEY_1"), None)
        self.assertNotEqual(os.getenv("API_TASKING_ORDER_LICENSE_HREF_1"), None)
    def tasking_order_2(self):
        self.assertNotEqual(os.getenv("API_TASKING_ORDERING_ID_2"), None)
        self.assertNotEqual(os.getenv("API_TASKING_BUNDLE_KEY_2"), None)
        self.assertNotEqual(os.getenv("API_TASKING_ORDER_LICENSE_HREF_2"), None)