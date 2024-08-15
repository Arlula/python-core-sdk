
import unittest
import os

class TestEnv(unittest.TestCase):
    '''
        Test the environment is setup correctly.
    '''

    # Auth

    def test_host(self):
        self.assertNotEqual(os.getenv("API_HOST"), None)
    def test_key(self):
        self.assertNotEqual(os.getenv("API_KEY"), None)
    def test_secret(self):
        self.assertNotEqual(os.getenv("API_SECRET"), None)

    # Entity identifiers

    def test_order_id_campaigns(self):
        """Order with campaigns associated with it"""
        self.assertNotEqual(os.getenv("API_ORDER_ID_CAMPAIGNS"), None)
    def test_order_id_datasets(self):
        """Order with datasets associated with it"""
        self.assertNotEqual(os.getenv("API_ORDER_ID_CAMPAIGNS"), None)
    def test_dataset_id(self):
        self.assertNotEqual(os.getenv("API_DATASET_ID"), None)
    def test_campaign_id(self):
        self.assertNotEqual(os.getenv("API_CAMPAIGN_ID"), None)
    def test_resource_id(self):
        self.assertNotEqual(os.getenv("API_RESOURCE_ID"), None)
    def test_collection_id(self):
        self.assertNotEqual(os.getenv("API_COLLECTION_ID"), None)
    def test_collection_item_id(self):
        self.assertNotEqual(os.getenv("API_COLLECTION_ITEM_ID"), None)

    # Details for placing orders

    def test_archive_order_1(self):
        self.assertNotEqual(os.getenv("API_ARCHIVE_ORDERING_ID_1"), None)
        self.assertNotEqual(os.getenv("API_ARCHIVE_LICENSE_HREF_1"), None)
        self.assertNotEqual(os.getenv("API_ARCHIVE_BUNDLE_KEY_1"), None)

    def test_archive_order_2(self):
        self.assertNotEqual(os.getenv("API_ARCHIVE_ORDERING_ID_2"), None)
        self.assertNotEqual(os.getenv("API_ARCHIVE_LICENSE_HREF_2"), None)
        self.assertNotEqual(os.getenv("API_ARCHIVE_BUNDLE_KEY_2"), None)
    
    def test_tasking_order_1(self):
        self.assertNotEqual(os.getenv("API_TASKING_ORDERING_ID_1"), None)
        self.assertNotEqual(os.getenv("API_TASKING_BUNDLE_KEY_1"), None)
        self.assertNotEqual(os.getenv("API_TASKING_LICENSE_HREF_1"), None)
        self.assertNotEqual(os.getenv("API_TASKING_PRIORITY_KEY_1"), None)
        self.assertNotEqual(os.getenv("API_TASKING_CLOUD_1"), None)
    
    def test_tasking_order_2(self):
        self.assertNotEqual(os.getenv("API_TASKING_ORDERING_ID_2"), None)
        self.assertNotEqual(os.getenv("API_TASKING_BUNDLE_KEY_2"), None)
        self.assertNotEqual(os.getenv("API_TASKING_LICENSE_HREF_2"), None)
        self.assertNotEqual(os.getenv("API_TASKING_PRIORITY_KEY_2"), None)
        self.assertNotEqual(os.getenv("API_TASKING_CLOUD_2"), None)
