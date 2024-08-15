import os
import tempfile
import unittest

import arlulacore
from .util import create_test_session

class TestOrders(unittest.TestCase):
    
    # Download Resource As File Tests
    def test_resource_download_as_file_filepath_success(self):
        api = arlulacore.ArlulaAPI(create_test_session())
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, "temp")
            api.ordersAPI().download_resource_as_file(os.getenv("API_RESOURCE_ID"), filepath, suppress=True).close()
            self.assertTrue(os.path.getsize(filepath) > 0)
    
    def test_resource_download_as_file_directory_success(self):
        api = arlulacore.ArlulaAPI(create_test_session())
        with tempfile.TemporaryDirectory() as temp_dir:
            api.ordersAPI().download_resource_as_file(os.getenv("API_RESOURCE_ID"), suppress=True, directory=temp_dir).close()
            self.assertTrue(len(os.listdir(temp_dir)) == 1)
    
    def test_resource_download_as_file_invalid(self):
        api = arlulacore.ArlulaAPI(create_test_session())
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, "temp")
            with self.assertRaises(arlulacore.ArlulaAPIException) as e:
                # random uuid
                api.ordersAPI().download_resource_as_file("3f475f34-2ee6-47d0-8707-ec9d80c25516", filepath, suppress=True).close()
            # self.assertEqual(e.exception.response.status_code, 401)
                
    # Download Resource as memory
    def test_resource_download_as_memory_success(self):
        api = arlulacore.ArlulaAPI(create_test_session())
        resource = api.ordersAPI().download_resource_as_memory(os.getenv("API_RESOURCE_ID"))
    
    def test_resource_download_as_memory_unauth(self):
        api = arlulacore.ArlulaAPI(create_test_session())
        with self.assertRaises(arlulacore.ArlulaAPIException) as e:
            resource = api.ordersAPI().download_resource_as_memory("3f475f34-2ee6-47d0-8707-ec9d80c25516")
        # self.assertEqual(e.exception.response.status_code, 401)

    # List Success Tests

    def test_dataset_list_success(self):
        api = arlulacore.ArlulaAPI(create_test_session())
        datasets = api.ordersAPI().list_datasets()
        self.assertNotEqual(len(datasets.content), 0)

    def test_campaign_list_success(self):
        api = arlulacore.ArlulaAPI(create_test_session())
        campaigns = api.ordersAPI().list_campaigns()
        self.assertNotEqual(len(campaigns.content), 0)

    def test_order_list_success(self):
        api = arlulacore.ArlulaAPI(create_test_session())
        orders = api.ordersAPI().list_orders()
        self.assertNotEqual(len(orders.content), 0)

    # Sublist Success Tests

    def test_order_list_campaigns_success(self):
        api = arlulacore.ArlulaAPI(create_test_session())
        campaigns = api.ordersAPI().list_order_campaigns(os.getenv("API_ORDER_ID_CAMPAIGNS"))
        self.assertNotEqual(len(campaigns.content), 0)

    def test_order_list_datasets_success(self):
        api = arlulacore.ArlulaAPI(create_test_session())
        datasets = api.ordersAPI().list_order_datasets(os.getenv("API_ORDER_ID_DATASETS"))
        self.assertNotEqual(len(datasets.content), 0)

    def test_campaign_list_datasets_success(self):
        api = arlulacore.ArlulaAPI(create_test_session())
        datasets = api.ordersAPI().list_campaign_datasets(os.getenv("API_CAMPAIGN_ID"))

    # Sublist Failure Tests

    def test_order_list_campaigns_bad_request(self):
        api = arlulacore.ArlulaAPI(create_test_session())
        # random uuid
        with self.assertRaises(arlulacore.ArlulaAPIException) as e:
            api.ordersAPI().list_order_campaigns("r568729oijnbds")
        # self.assertEqual(e.exception.response.status_code, 400)

    def test_order_list_datasets_bad_request(self):
        api = arlulacore.ArlulaAPI(create_test_session())
        # random uuid
        with self.assertRaises(arlulacore.ArlulaAPIException) as e:
            api.ordersAPI().list_order_datasets("r568729oijnbds")
        # self.assertEqual(e.exception.response.status_code, 400)

    def test_campaign_list_datasets_bad_request(self):
        api = arlulacore.ArlulaAPI(create_test_session())
        # keyboard mash
        with self.assertRaises(arlulacore.ArlulaAPIException) as e:
            api.ordersAPI().list_campaign_datasets("r568729oijnbds")
        # self.assertEqual(e.exception.response.status_code, 400)

    # Get Success Tests

    def test_dataset_get_success(self):
        api = arlulacore.ArlulaAPI(create_test_session())
        dataset = api.ordersAPI().get_dataset(os.getenv("API_DATASET_ID"))

    def test_campaign_get_success(self):
        api = arlulacore.ArlulaAPI(create_test_session())
        campaign = api.ordersAPI().get_campaign(os.getenv("API_CAMPAIGN_ID"))

    def test_resource_get(self):
        api = arlulacore.ArlulaAPI(create_test_session())
        resource = api.ordersAPI().get_resource(os.getenv("API_RESOURCE_ID"))

    def test_order_get_campaigns_success(self):
        api = arlulacore.ArlulaAPI(create_test_session())
        order = api.ordersAPI().get_order(os.getenv("API_ORDER_ID_CAMPAIGNS"))
        self.assertNotEqual(len(order.campaigns), 0)
    
    def test_order_get_datasets_success(self):
        api = arlulacore.ArlulaAPI(create_test_session())
        order = api.ordersAPI().get_order(os.getenv("API_ORDER_ID_DATASETS"))
        self.assertNotEqual(len(order.datasets), 0)

    # Get Failure Tests

    def test_campaign_get_unauth(self):
        api = arlulacore.ArlulaAPI(create_test_session())
        # random uuid
        with self.assertRaises(arlulacore.ArlulaAPIException) as e:
            api.ordersAPI().get_campaign("3f475f34-2ee6-47d0-8707-ec9d80c25516")
        self.assertEqual(e.exception.response.status_code, 401)

    def test_order_get_unauth(self):
        api = arlulacore.ArlulaAPI(create_test_session())
        # random uuid
        with self.assertRaises(arlulacore.ArlulaAPIException) as e:
            api.ordersAPI().get_campaign("3f475f34-2ee6-47d0-8707-ec9d80c25516")
        self.assertEqual(e.exception.response.status_code, 401)

    def test_dataset_get_unauth(self):
        api = arlulacore.ArlulaAPI(create_test_session())
        # random uuid
        with self.assertRaises(arlulacore.ArlulaAPIException) as e:
            api.ordersAPI().get_campaign("3f475f34-2ee6-47d0-8707-ec9d80c25516")
        self.assertEqual(e.exception.response.status_code, 401)
    
    def test_resource_get_unauth(self):
        api = arlulacore.ArlulaAPI(create_test_session())
        # random uuid
        with self.assertRaises(arlulacore.ArlulaAPIException) as e:
            api.ordersAPI().get_resource("3f475f34-2ee6-47d0-8707-ec9d80c25516")
        # self.assertEqual(e.exception.response.status_code, 401)
    
    def test_campaign_get_bad_request(self):
        api = arlulacore.ArlulaAPI(create_test_session())
        # keyboard mash
        with self.assertRaises(arlulacore.ArlulaAPIException) as e:
            api.ordersAPI().get_campaign("r568729oijnbds")
        self.assertEqual(e.exception.response.status_code, 400)

    def test_order_get_bad_request(self):
        api = arlulacore.ArlulaAPI(create_test_session())
        # keyboard mash
        with self.assertRaises(arlulacore.ArlulaAPIException) as e:
            api.ordersAPI().get_campaign("r568729oijnbds")
        self.assertEqual(e.exception.response.status_code, 400)

    def test_dataset_get_bad_request(self):
        api = arlulacore.ArlulaAPI(create_test_session())
        # keyboard mash
        with self.assertRaises(arlulacore.ArlulaAPIException) as e:
            api.ordersAPI().get_campaign("r568729oijnbds")
        self.assertEqual(e.exception.response.status_code, 400)
    
    def test_resource_get_bad_request(self):
        api = arlulacore.ArlulaAPI(create_test_session())
        # keyboard mash
        with self.assertRaises(arlulacore.ArlulaAPIException) as e:
            api.ordersAPI().get_resource("r568729oijnbds")
        self.assertEqual(e.exception.response.status_code, 400)