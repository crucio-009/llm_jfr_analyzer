import unittest
from jfr_parser import parse_jfr

class TestJfrParser(unittest.TestCase):
    def test_parse_invalid_file(self):
        result = parse_jfr("not_a_real_file.jfr")
        self.assertEqual(result, [])

    # Add more tests here for sample .json or .jfr files as needed

if __name__ == '__main__':
    unittest.main()
