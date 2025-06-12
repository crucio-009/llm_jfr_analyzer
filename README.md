# LLM JFR Analyzer

A side-project template for a Large Language Model-powered Java Flight Recorder (JFR) analysis tool that summarizes and diagnoses JVM performance issues from JFR files.

**Features:**
- Analyze Java Flight Recorder files (binary `.jfr` or pre-extracted `.json`) using LLMs.
- Supports both paid API-based (OpenAI) and free, open-source HuggingFace models (Gemma, Mistral, Llama, TinyLlama, etc.).
- Choice of model and chunking threshold at runtime via web UI or CLI.
- Automatic local model setup/download and transparent chunking for large profiles.
- FastAPI web UI: upload files, select models, and view/download human-readable diagnostic reports.
- CLI support: run full batch analyses, automate jobs, and control all parameters.
- Robust handling of large `.jfr` files via `jfr disassemble` (Java 17+).
- Thorough and modular test suite, including parser/feature/unit, web UI e2e, and CLI e2e coverage.
- Clear Python code, extensible architecture, and no uploading of actual model weights/checkpoints to git.

---

## Requirements

- Python 3.8+
- **Java JDK 17 or newer**  
  Required for direct parsing of `.jfr` binary files via `jfr print --json`.<br>
  [Full JDK 17 jfr doc: Oracle](https://docs.oracle.com/en/java/javase/17/docs/specs/man/jfr.html)
  - For large JFR files, uses `jfr disassemble` to split/repair files before analysis (also requires Java 17+).
  - If using only extracted `.json`, Java is not required.
- See `requirements.txt` for Python dependencies (including FastAPI, Transformers, OpenAI, etc.).

---

## Project Structure
```
llm_jfr_analyzer/
├── README.md
├── requirements.txt
├── .env.example
├── main.py                  # CLI entry point
├── webui.py                 # FastAPI web UI backend
├── jfr_parser.py            # Extraction and chunking w/ disassemble
├── feature_extractor.py     # Feature/summary generator for LLM
├── llm_prompter.py          # Handles OpenAI/local LLM prompt logic
├── report_generator.py      # Markdown/HTML report generator
├── utils.py                 # Helpers
├── tests/
│   ├── __init__.py
│   ├── test_parser.py       # Unit tests for parser
│   ├── test_features.py     # Unit tests for feature extraction logic
│   ├── test_webui.py        # End-to-end web UI file upload/diagnostic test
│   └── test_cli.py          # End-to-end CLI diagnostics test
├── sample_data/
│   ├── event_snippets.json  # Example valid event snippets (for testing)
│   ├── example.jfr          # Placeholder for ignored test JFRs (see below)
│   └── sample_test.jfr      # Place a REAL .jfr file here for full tests
└── feature_extractor.py
```
---

## Quickstart

### 1. Install Python requirements

```bash
pip install -r requirements.txt
```
### 2. Install Java 17+ (for `.jfr` file parsing)

[Download OpenJDK 17+](https://jdk.java.net/17/) and ensure it is in your PATH:
```
java -version
jfr --help
```
### 3. Configure your environment

Copy `.env.example` to `.env` and set/override secrets as needed (*not needed for local/default use*).

---

## Usage

### Web UI (Recommended for exploration/interactivity)

```bash
uvicorn webui:app --reload --port 8080
```
Then open [http://localhost:8080](http://localhost:8080), upload a `.jfr` or `.json`, set chunking threshold & model, and generate a full LLM report from your browser.

### CLI (For headless/batch/automation)

```bash
python main.py --jfr path/to/file.jfr --uselocal --llmmodel google/gemma-2b-it --chunkthresh 50
```
All model and chunking options at runtime. Output report is saved to the path specified by `--output`, defaulting to `analysis_report.md`.

---

## Model Selection

- Choose any local supported model in either web UI or CLI:
  - `google/gemma-2b-it` (default)
  - `mistralai/Mistral-7B-Instruct`
  - `TinyLlama/TinyLlama-1.1B-Chat-v1.0`
  - `meta-llama/Llama-2-7b-chat-hf`
- OpenAI/GPT requires config in `.env`.

---

## How It Works

1. Upload or point the tool at `.jfr`/`.json` data.
2. (Optionally) Automatically chunk large `.jfr` files.
3. Extracts features (GC/threads/SQL etc.) for LLM prompt context.
4. LLM analyses and outputs summary/recommendations.
5. Human-readable report is produced for download/CI/share.

---

## Testing

All tests in the `tests/` directory. To run everything:

```bash
python -m unittest discover -s tests
```
**Covers:**
- Unit and integration tests for parsing, feature extraction.
- End-to-end test for web UI (`test_webui.py`):
  - Simulates uploading JSON and (optionally) a real JFR (`sample_data/sample_test.jfr`) for round-trip diagnostic to output.
- End-to-end test for CLI (`test_cli.py`):
  - Runs the CLI on JSON and (optionally) a real JFR (`sample_data/sample_test.jfr`) and checks the written report.
  - **To fully enable end-to-end tests with binary JFRs:**  
    - Place a real Java Flight Recorder `.jfr` file in `sample_data/sample_test.jfr` (this file is .gitignored by default and not included in the repo).

---

## Notes & Guidelines

- All JFR files and large binaries (`*.jfr`) are git-ignored; include them only locally for your own regression tests.
- Model weights/checkpoints are not uploaded to the repo—these are always downloaded on-demand via HuggingFace.
- You can adapt or extend this project for different JVM event filtering, prompt engineering, or model selection.
- As with all AI assistants, human review of LLM findings for production/mission-critical scenarios is recommended.

---

## Future Improvements

- JVM performance visualization/charts
- Advanced prompt customization and feedback loops in UI
- Support for continuous/batch monitoring and thresholds
- Custom LLM/rule/plugin integrations

---

## License

MIT
