import unittest
from feature_extractor import extract_features

class TestFeatureExtractor(unittest.TestCase):
    def test_empty_events(self):
        summary = extract_features([])
        self.assertIn("Events: 0", summary)
        self.assertIn("Stuck Threads: 0", summary)

if __name__ == '__main__':
    unittest.main()
