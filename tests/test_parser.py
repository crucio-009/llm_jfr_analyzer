import unittest
import os
from jfr_parser import parse_jfr

class TestJfrParser(unittest.TestCase):
    def test_parse_invalid_file(self):
        result = parse_jfr("not_a_real_file.jfr")
        self.assertEqual(result, [])

    def test_parse_sample_json(self):
        # Valid JSON input
        result = parse_jfr(os.path.join("sample_data", "event_snippets.json"))
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIn("event", result[0])

    def test_chunking_threshold(self):
        # Should not chunk small files; always loads JSON
        sample_json = os.path.join("sample_data", "event_snippets.json")
        result = parse_jfr(sample_json, chunking_threshold_mb=0.001)  # Threshold lower than file size (but JSON shortcut should happen)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_parse_empty_json(self):
        # An empty list file
        empty_json = os.path.join("sample_data", "empty.json")
        with open(empty_json, "w") as f:
            f.write("[]")
        result = parse_jfr(empty_json)
        self.assertIsInstance(result, list)
        self.assertEqual(result, [])
        os.remove(empty_json)

if __name__ == '__main__':
    unittest.main()
