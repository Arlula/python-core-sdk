import os
import tempfile
import unittest

import arlulacore
from .util import create_test_session

class TestAuth(unittest.TestCase):
    
    def test_valid_auth_success(self):
        create_test_session()

    def test_invalid_auth_failure(self):
        with self.assertRaises(arlulacore.ArlulaSessionError) as e:
            arlulacore.Session("invalid_key", "invalid_pass", url=os.getenv("API_HOST"))
        