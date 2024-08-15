import os
import unittest

import arlulacore
from .util import create_test_session

class TestList(unittest.TestCase):
    
    def test_list_json(self):
        inputs = [
            arlulacore.ListRequest(2, 2),
            arlulacore.ListRequest(0, 0),
            arlulacore.ListRequest(),
        ]
        exps = [
            {"page": 2, "size": 2},
            {"page": 0, "size": 20},
            {"page": 0, "size": 20},
        ]

        for inp, exp in zip(inputs, exps):
            self.assertDictEqual(inp.__dict__(), exp)