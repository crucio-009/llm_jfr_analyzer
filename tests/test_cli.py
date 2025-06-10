import os
import sys
import subprocess
import unittest

class TestClicliEndToEnd(unittest.TestCase):
    def setUp(self):
        self.project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.main_py = os.path.join(self.project_dir, "main.py")
        self.sample_json = os.path.join(self.project_dir, "sample_data", "event_snippets.json")
        self.sample_jfr = os.path.join(self.project_dir, "sample_data", "sample_test.jfr")
        self.output_file = os.path.join(self.project_dir, "tests", "test_cli_output.md")

    def tearDown(self):
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

    def test_cli_json(self):
        # Run CLI with JSON sample
        p = subprocess.run([
            sys.executable, self.main_py,
            "--jfr", self.sample_json,
            "--uselocal",
            "--llmmodel", "google/gemma-2b-it",
            "--output", self.output_file
        ], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
        with open(self.output_file, "r", encoding="utf-8") as f:
            output = f.read()
        self.assertIn("JVM Diagnostics Report", output)
        self.assertIn("Executive Summary", output)

    def test_cli_real_jfr(self):
        # Only runs if a real sample JFR is present
        if not os.path.exists(self.sample_jfr):
            self.skipTest("sample_data/sample_test.jfr not present for JFR CLI test (add a real JFR to enable)")
        p = subprocess.run([
            sys.executable, self.main_py,
            "--jfr", self.sample_jfr,
            "--uselocal",
            "--llmmodel", "google/gemma-2b-it",
            "--output", self.output_file
        ], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
        with open(self.output_file, "r", encoding="utf-8") as f:
            output = f.read()
        self.assertIn("JVM Diagnostics Report", output)
        self.assertIn("Executive Summary", output)

if __name__ == "__main__":
    unittest.main()
