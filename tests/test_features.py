import unittest
from feature_extractor import extract_features

class TestFeatureExtractor(unittest.TestCase):
    def test_empty_events(self):
        summary = extract_features([])
        self.assertIn("Events: 0", summary)
        self.assertIn("Stuck Threads: 0", summary)

    def test_minimal_event(self):
        # Minimal example with a stuck thread and GC
        events = [
            {"event":"jdk.ThreadStuck","threadName":"test-thread"},
            {"event":"jdk.GarbageCollection","startTime":"2025-01-01T00:00:00.000Z","longestPause":150}
        ]
        summary = extract_features(events)
        self.assertIn("Stuck Threads: 1", summary)
        self.assertIn("Longest GC Pause(ms): 150", summary)

    def test_top_sql(self):
        # Test SQL detection in event
        events = [
            {"event":"other"},
            {"sql":"SELECT foo FROM bar"},
        ]
        summary = extract_features(events)
        self.assertIn("Example Top SQL: ['{\"event\": \"other\"}', '{\"sql\": \"SELECT foo FROM bar\"}']", summary)

if __name__ == '__main__':
    unittest.main()
