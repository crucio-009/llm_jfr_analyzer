import os
import unittest
from fastapi.testclient import TestClient

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from webui import app

class TestWebUIEndToEnd(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # Preload sample JSON ("JFR") file
        self.sample_json_file = os.path.join("sample_data", "event_snippets.json")
        with open(self.sample_json_file, "rb") as f:
            self.sample_json_bytes = f.read()
        # Preload sample JFR binary (placeholder, must be replaced with real .jfr for realistic test)
        self.sample_jfr_file = os.path.join("sample_data", "sample_test.jfr")
        # If real file is present
        if os.path.exists(self.sample_jfr_file):
            with open(self.sample_jfr_file, "rb") as f:
                self.sample_jfr_bytes = f.read()
        else:
            self.sample_jfr_bytes = None

    def test_upload_and_get_report(self):
        # Emulate uploading a small "JFR" (JSON) file and receiving HTML
        response = self.client.post(
            "/analyze",
            files={"jfrfile": ("event_snippets.json", self.sample_json_bytes, "application/json")},
            data={"llmmodel":"google/gemma-2b-it", "chunkthresh": "10", "uselocal": "1"}
        )
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("Analysis Results", content)
        self.assertIn("Download Report as Markdown", content)

    def test_main_page_and_model_select(self):
        # Check UI renders model options etc.
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn("Gemma 2B", html)
        self.assertIn("Chunking Threshold", html)

    def test_upload_real_jfr(self):
        # This test is skipped unless a real sample .jfr file is present
        if not self.sample_jfr_bytes:
            self.skipTest("No real sample_data/sample_test.jfr provided (replace with a real JFR to enable full e2e test)")
        response = self.client.post(
            "/analyze",
            files={"jfrfile": ("sample_test.jfr", self.sample_jfr_bytes, "application/octet-stream")},
            data={"llmmodel":"google/gemma-2b-it", "chunkthresh": "1", "uselocal": "1"}
        )
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("Analysis Results", content)
        self.assertIn("Download Report as Markdown", content)

if __name__ == "__main__":
    unittest.main()
