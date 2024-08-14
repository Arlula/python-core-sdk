import unittest
import arlulacore

class TestCalculatePrice(unittest.TestCase):

    def test_calculate_archive(self):
        self.assertEqual(arlulacore.calculate_price(100, 0, 0), 100)
        self.assertEqual(arlulacore.calculate_price(100, 50, 0), 200)
        self.assertEqual(arlulacore.calculate_price(100, 50, 100), 300)
        self.assertEqual(arlulacore.calculate_price(100, 75, 124), 300)
        self.assertEqual(arlulacore.calculate_price(100, 75, 126), 400)
    
    def test_calculate_tasking(self):
        self.assertEqual(arlulacore.calculate_price(100, 0, 0, 0, 0, 0, 0), 100)
        self.assertEqual(arlulacore.calculate_price(100, 50, 0, 50, 0, 50, 0), 300)
        self.assertEqual(arlulacore.calculate_price(100, 0, 1000, 0, 600, 0, 165), 1900)
        self.assertEqual(arlulacore.calculate_price(100, 75, 124, 12, 322, 432, 321), 1400)
        self.assertEqual(arlulacore.calculate_price(100, 25, 100, 400, 1600, 3200, 6400), 11900)
