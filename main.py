import argparse
import os
import sys

from dotenv import load_dotenv

from jfr_parser import parse_jfr
from feature_extractor import extract_features
from llm_prompter import analyze_with_llm
from report_generator import write_report

def main():
    parser = argparse.ArgumentParser(description="LLM JFR Analyzer MVP")
    parser.add_argument(
        '--jfr', type=str, required=True, help='Path to JFR file (in text or .jfr format)'
    )
    parser.add_argument(
        '--output', type=str, default='analysis_report.md', help='Output report file'
    )
    args = parser.parse_args()

    load_dotenv()
    jfr_path = args.jfr

    if not os.path.exists(jfr_path):
        print(f"JFR file not found: {jfr_path}")
        sys.exit(1)

    print("Parsing JFR...")
    events = parse_jfr(jfr_path)

    print("Extracting features...")
    features = extract_features(events)

    print("Analyzing with LLM...")
    findings = analyze_with_llm(features)

    print(f"Writing report to {args.output} ...")
    write_report(findings, args.output)

    print("Done.")

if __name__ == '__main__':
    main()
