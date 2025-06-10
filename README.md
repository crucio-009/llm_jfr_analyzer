# LLM JFR Analyzer

A side-project template for a Large Language Model-powered Java Flight Recorder (JFR) analysis tool that summarizes and diagnoses JVM performance issues from JFR files. 

**Features:**
- Supports both paid API-based (OpenAI) and free, open-source HuggingFace models (Gemma, Mistral, Llama, TinyLlama, etc.)
- Automatic setup and download of selected local LLM on demand
- Flexible local LLM choice via environment variable or web UI
- FastAPI-based web UI for uploading `.jfr`/`.json`, model selection, downloadable Markdown reports, and setting the chunking threshold
- CLI support for headless automation
- Handles large `.jfr` files robustly by chunking them with `jfr disassemble` (JDK 17+), with user-configurable chunking threshold (MB)
- Clear Python code ready for production adaptation

---

## Requirements

- Python 3.8+
- **Java JDK 17 or newer** (required for direct parsing of `.jfr` files via `jfr print --json`; see [Oracle JDK 17 jfr docs](https://docs.oracle.com/en/java/javase/17/docs/specs/man/jfr.html))
    - For large `.jfr` files, we **automatically use `jfr disassemble`** to split the recording into chunks before analysis (also available since Java 17). This chunking threshold (in MB) is now user-settable in the web UI.
    - If you only process pre-extracted `.json` files (see `sample_data/event_snippets.json`), Java is not required.
- See `requirements.txt` for Python dependencies.

---

## Project Structure

llm_jfr_analyzer/
├── README.md                      # Project info and usage
├── requirements.txt               # Python dependencies
├── .env.example                   # Example environment (API keys, model names)
├── main.py                        # CLI entry point
├── webui.py                       # FastAPI Web UI
├── jfr_parser.py                  # JFR → events extractor (handles chunking)
├── feature_extractor.py           # JFR events → features/summary
├── llm_prompter.py                # Handles OpenAI/local LLM prompt logic and switching
├── report_generator.py            # Writes Markdown/HTML report from LLM output
├── utils.py                       # Support helpers
├── tests/
│   ├── __init__.py
│   ├── test_parser.py             # JFR parsing test
│   ├── test_features.py           # Feature extraction test
├── sample_data/
│   ├── event_snippets.json        # Example event snippets for testing
│   └── example.jfr                # Placeholder for JFR file
└── feature_extractor.py

---

## Quickstart

### 1. Install Python requirements

```bash
pip install -r requirements.txt
```
### 2. Install Java 17+ (for `.jfr` file parsing)

**You need Java 17 or newer for direct `.jfr` (binary) handling, due to the `jfr print --json` and `jfr disassemble` requirements.**
- [Download OpenJDK 17+](https://jdk.java.net/17/)
- Make sure `jfr` is in your PATH (`java -version` should show 17 or above)

### 3. Configure your environment

Copy `.env.example` to `.env` and set as needed.

### 4. Run the Web UI (supports large file chunking, with threshold selection)

```bash
uvicorn webui:app --reload --port 8080
```
Go to http://localhost:8080, upload a `.jfr` or `.json` file, select your LLM (if desired), and set the chunking threshold (in MB, default 50). Files over this threshold will be chunked before further analysis.

### 5. Or, use the CLI

```bash
python main.py --jfr sample_data/event_snippets.json
```
---

## Model Selection

- Any HuggingFace-supported text-generation model can be used locally—set via `LOCAL_LLM_MODEL` in your `.env` **or in the web UI**.
- Example:  
  - `google/gemma-2b-it` (default)
  - `mistralai/Mistral-7B-Instruct`
  - `TinyLlama/TinyLlama-1.1B-Chat-v1.0`
  - `meta-llama/Llama-2-7b-chat-hf`

> On first use, the tool will automatically download the selected local model if not found.

---

## How It Works

1. Parses/extracts events from your JFR/json file. For large `.jfr` files, they are chunked (according to the user-set threshold) and aggregated chunk-wise.
2. Summarizes threads, GC, SQL, etc. for LLM-friendly prompt.
3. LLM (OpenAI **or** local) analyzes and returns diagnostic output.
4. The tool writes a report (Markdown/HTML) with plain-English JVM analysis.

---

## Advanced Usage and Notes

- The tool works with either standard JDK 17+ installed locally, or with `.json` exports if you run the conversion elsewhere.
- Output includes human-readable reports, with a web UI for convenience and sharing.
- The parser handles text and JSON JFR files; for large files, the user can set the chunk size threshold in the web UI.
- For more on the JSON and disassemble options, see [JDK 17 man page](https://docs.oracle.com/en/java/javase/17/docs/specs/man/jfr.html).

---

## Future Improvements

- Visualization/charts for performance stats
- Interactive web diagnostics, further tuning, & project integration
- Multi-file and scheduled batch processing
- Feedback-driven report refinement

---

## License

MIT
