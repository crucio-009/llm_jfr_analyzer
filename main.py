import argparse
import os
import sys

from dotenv import load_dotenv

from jfr_parser import parse_jfr
from feature_extractor import extract_features
from llm_prompter import analyze_with_llm
from report_generator import write_report

SUPPORTED_LLM_MODELS = [
    ("google/gemma-2b-it", "Gemma 2B (Google, Efficient)"),
    ("mistralai/Mistral-7B-Instruct", "Mistral 7B Instruct"),
    ("TinyLlama/TinyLlama-1.1B-Chat-v1.0", "TinyLlama 1.1B Chat v1.0"),
    ("meta-llama/Llama-2-7b-chat-hf", "Llama-2 7B Chat"),
]

def list_llm_choices():
    return '\n'.join(f"  {i+1}. {label} ({model})" for i, (model, label) in enumerate(SUPPORTED_LLM_MODELS))

def main():
    parser = argparse.ArgumentParser(description="LLM JFR Analyzer MVP")
    parser.add_argument(
        '--jfr', type=str, required=True, help='Path to JFR file (in text or .jfr format)')
    parser.add_argument(
        '--output', type=str, default='analysis_report.md', help='Output report file')
    parser.add_argument(
        '--uselocal', action="store_true", help="Force use of local LLM (even if OpenAI config is set)")
    parser.add_argument(
        '--llmmodel', type=str, choices=[m[0] for m in SUPPORTED_LLM_MODELS],
        default=SUPPORTED_LLM_MODELS[0][0],
        help='Local LLM model to use. Options:\n' + list_llm_choices())
    parser.add_argument(
        '--chunkthresh', type=int, default=50, help='Chunking threshold in MB for large JFR files (default: 50)')
    args = parser.parse_args()

    load_dotenv()
    jfr_path = args.jfr

    if not os.path.exists(jfr_path):
        print(f"JFR file not found: {jfr_path}")
        sys.exit(1)

    # Set LLM config at runtime
    if args.uselocal:
        os.environ["USE_LOCAL_LLM"] = "1"
        os.environ["LOCAL_LLM_MODEL"] = args.llmmodel
    else:
        os.environ["USE_LOCAL_LLM"] = "0"

    print("Parsing JFR...")
    events = parse_jfr(jfr_path, chunking_threshold_mb=args.chunkthresh)

    print("Extracting features...")
    features = extract_features(events)

    print("Analyzing with LLM...")
    findings = analyze_with_llm(features)

    print(f"Writing report to {args.output} ...")
    write_report(findings, args.output)

    print("Done.")

if __name__ == '__main__':
    print("Supported local LLM models:\n" + list_llm_choices())
    main()
