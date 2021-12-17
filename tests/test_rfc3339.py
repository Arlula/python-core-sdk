import unittest
import arlulacore
from arlulacore.util import parse_rfc3339

class TestRFC3339(unittest.TestCase):

    def test_correct_sec_frac(self):
        self.assertEqual(str(parse_rfc3339("2021-10-18T22:38:10.123456Z")),
            "2021-10-18 22:38:10.123456+00:00"
        )

    def test_long_sec_frac(self):
        self.assertEqual(str(parse_rfc3339("2021-10-18T22:38:10.123456789Z")),
            "2021-10-18 22:38:10.123456+00:00"
        )
    
    def test_short_sec_frac(self):
        self.assertEqual(str(parse_rfc3339("2021-10-18T22:38:10.123Z")),
            "2021-10-18 22:38:10.123000+00:00"
        )
    
    def test_no_sec_frac(self):
        self.assertEqual(str(parse_rfc3339("2021-10-18t22:38:10Z")),
            "2021-10-18 22:38:10+00:00"
        )

    def test_lower_z(self):
        self.assertEqual(str(parse_rfc3339("2021-10-18T22:38:10.123456z")),
            "2021-10-18 22:38:10.123456+00:00"
        )

    def test_lower_t(self):
        self.assertEqual(str(parse_rfc3339("2021-10-18t22:38:10.123456Z")),
            "2021-10-18 22:38:10.123456+00:00"
        )
    
    def test_positive_offset(self):
        self.assertEqual(str(parse_rfc3339("2021-10-18T22:38:10.123456+04:45")),
            "2021-10-18 22:38:10.123456+04:45"
        )
    
    def test_negative_offset(self):
        self.assertEqual(str(parse_rfc3339("2021-10-18T22:38:10.123456-04:45")),
            "2021-10-18 22:38:10.123456-04:45"
        )

    # Most error cases should be handled by python itself

    def test_offset_too_big(self):
        self.assertEqual(parse_rfc3339("2021-10-18T22:38:10.123456+25:00"), None)

    def test_no_input(self):
        self.assertEqual(parse_rfc3339(""), None)
