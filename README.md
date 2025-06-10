# LLM JFR Analyzer

A side-project template for a Large Language Model-powered Java Flight Recorder (JFR) analysis tool that summarizes and diagnoses JVM performance issues from JFR files. 

**Features:**
- Supports both paid API-based (OpenAI) and free, open-source HuggingFace models (Gemma, Mistral, Llama, TinyLlama, etc.)
- Automatic setup and download of selected local LLM on demand
- Flexible local LLM choice via environment variable, web UI, or CLI at runtime
- FastAPI-based web UI for uploading `.jfr`/`.json`, model selection, downloadable Markdown reports, and setting the chunking threshold
- CLI support for headless automation, with model & chunk size selection at runtime
- Handles large `.jfr` files robustly by chunking them with `jfr disassemble` (JDK 17+), with user-configurable chunking threshold (MB)
- Clear Python code ready for production adaptation

---

## Requirements

- Python 3.8+
- **Java JDK 17 or newer** (required for direct parsing of `.jfr` files via `jfr print --json`; see [Oracle JDK 17 jfr docs](https://docs.oracle.com/en/java/javase/17/docs/specs/man/jfr.html))
    - For large `.jfr` files, we **automatically use `jfr disassemble`** to split the recording into chunks before analysis (since Java 17). The chunking threshold (MB) is user-settable in the web UI or CLI.
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

Copy `.env.example` to `.env` and set as needed. (You do **not** need to set `LOCAL_LLM_MODEL` in `.env` anymore if you use CLI/UI selection.)

### 4. Run the Web UI (model & chunk size selection included)

```bash
uvicorn webui:app --reload --port 8080
```
Go to http://localhost:8080, upload a `.jfr` or `.json` file, select your LLM from a dropdown list, and set the chunking threshold (in MB, default 50). Files over this threshold will be chunked before analysis.

### 5. Or, use the CLI (with runtime LLM and chunk size selection)

```bash
python main.py --jfr myfile.jfr --uselocal --llmmodel google/gemma-2b-it --chunkthresh 50
```
- Use `--llmmodel` to select any of these supported local LLM models at runtime:
  - `google/gemma-2b-it` (default)
  - `mistralai/Mistral-7B-Instruct`
  - `TinyLlama/TinyLlama-1.1B-Chat-v1.0`
  - `meta-llama/Llama-2-7b-chat-hf`

- Use `--chunkthresh` to set the chunk size threshold in MB for `.jfr` disassembly.

---

## Model Selection

- Any HuggingFace-supported text-generation model in the supported models list can be used locally—choose via web UI or CLI (`--llmmodel`) at runtime.
- If using OpenAI, set the API key and model in `.env` as before.

---

## How It Works

1. Parses/extracts events from your JFR/json file. For large `.jfr` files, they are chunked (user-set threshold) and aggregated chunk-wise.
2. Summarizes threads, GC, SQL, etc. for LLM-friendly prompt.
3. LLM (OpenAI **or** local) analyzes and returns diagnostic output.
4. The tool writes a report (Markdown/HTML) with plain-English JVM analysis.

---

## Advanced Usage and Notes

- Only tested and supported models for JVM diagnostics are exposed for user/runtime selection.
- On first use, the tool will automatically download the chosen local model if not found.
- The parser and UI ensure only compatible, proven models are selectable per analysis session.
- The parser handles text and JSON JFR files; large files are safely chunked with a threshold set at runtime.
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
