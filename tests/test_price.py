import unittest
import arlulacore

class TestSearchRequest(unittest.TestCase):

    def test_calculate(self):
        self.assertEqual(arlulacore.calculate_price(100, 0, 0), 100)
        self.assertEqual(arlulacore.calculate_price(100, 50, 0), 200)
        self.assertEqual(arlulacore.calculate_price(100, 50, 100), 300)
        self.assertEqual(arlulacore.calculate_price(100, 75, 124), 300)
        self.assertEqual(arlulacore.calculate_price(100, 75, 126), 400)
