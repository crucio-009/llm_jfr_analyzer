import os
import tempfile

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

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

app = FastAPI(
    title="LLM JFR Analyzer Web UI",
    description="Analyze Java Flight Recorder (.jfr, .json) files with a local or cloud LLM, via web interface."
)

# Enable CORS for browser-based access if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

def render_llm_model_select(selected="google/gemma-2b-it"):
    html = '<label for="llmmodel">LLM Model (local, supported for JVM diagnostics):</label><br>'
    html += '<select id="llmmodel" name="llmmodel">'
    for model, label in SUPPORTED_LLM_MODELS:
        s = "selected" if model == selected else ""
        html += f'<option value="{model}" {s}>{label} ({model})</option>'
    html += '</select><br>'
    return html

@app.get("/", response_class=HTMLResponse)
async def index():
    return f"""
    <html>
        <head><title>LLM JFR Analyzer</title></head>
        <body style="font-family:sans-serif; margin:2em;">
            <h1>LLM JFR Analyzer (Web UI)</h1>
            <form action="/analyze" method="post" enctype="multipart/form-data">
                <label for="jfrfile">JFR File (.jfr or .json):</label><br>
                <input type="file" id="jfrfile" name="jfrfile" accept=".jfr,.json" required><br><br>
                {render_llm_model_select()}
                <label for="chunkthresh">Chunking Threshold (MB, for large .jfrs):</label><br>
                <input type="number" id="chunkthresh" name="chunkthresh" value="50" min="1" max="1024" step="1"><br>
                <label>
                    <input type="checkbox" name="uselocal" value="1" checked> Use Local LLM (no API key required)
                </label><br><br>
                <input type="submit" value="Analyze JFR">
                <p><i>Large .jfr files over the chosen threshold will be chunked via <code>jfr disassemble</code>.</i></p>
            </form>
        </body>
    </html>
    """

@app.post("/analyze")
async def analyze_jfr(
    jfrfile: UploadFile = File(...),
    llmmodel: str = Form("google/gemma-2b-it"),
    chunkthresh: int = Form(50),
    uselocal: str = Form("1")
):
    # Load environment
    load_dotenv()

    # Set local LLM/model config for this run - only accept supported!
    if uselocal in ("1", "true", "yes", "on"):
        os.environ["USE_LOCAL_LLM"] = "1"
        # Ensure only supported models are allowed
        allowed_models = [m[0] for m in SUPPORTED_LLM_MODELS]
        model_to_use = llmmodel if llmmodel in allowed_models else allowed_models[0]
        os.environ["LOCAL_LLM_MODEL"] = model_to_use
    else:
        os.environ["USE_LOCAL_LLM"] = "0"

    # Save uploaded JFR to a temp file
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        content = await jfrfile.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        events = parse_jfr(tmp_path, chunking_threshold_mb=chunkthresh)
        summary = extract_features(events)
        findings = analyze_with_llm(summary)
        # Write findings to a temp markdown file for download
        report_path = tmp_path + "_report.md"
        write_report(findings, report_path)
        with open(report_path, "r", encoding="utf-8") as f:
            report_md = f.read()
    finally:
        os.remove(tmp_path)

    # Present result as HTML, link to download markdown
    return HTMLResponse(f"""
    <html>
    <head>
    <title>LLM JFR Analyzer Results</title>
    <style>
        body {{ font-family: sans-serif; margin:2em; }}
        pre {{ background:#eee; padding:1em; }}
        .box {{ background:#f9f9f9; border:1px solid #ccc; padding:1em; margin:1em 0; }}
    </style>
    </head>
    <body>
        <h2>Analysis Results</h2>
        <div class="box"><pre>{findings}</pre></div>
        <h3>Download</h3>
        <a href="/download?path={report_path}" download="jfr_report.md">Download Report as Markdown</a><br>
        <a href="/">Analyze another file</a>
        <br>
        <p><small>Note: If your file was larger than the chosen threshold, it was automatically chunked (via <code>jfr disassemble</code>) and the result aggregated for analysis.</small></p>
    </body>
    </html>
    """)

@app.get("/download")
def download(path: str):
    return FileResponse(path, filename="jfr_report.md", media_type="text/markdown")
