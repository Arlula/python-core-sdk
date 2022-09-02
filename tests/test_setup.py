
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