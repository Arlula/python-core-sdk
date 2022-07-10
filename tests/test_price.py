import unittest
import arlulacore

class TestSearchRequest(unittest.TestCase):

    def test_calculate(self):
        self.assertEqual(arlulacore.calculate_price(100, 0, 0), 100)
        self.assertEqual(arlulacore.calculate_price(100, 50, 0), 150)
        self.assertEqual(arlulacore.calculate_price(100, 50, 50), 200)
