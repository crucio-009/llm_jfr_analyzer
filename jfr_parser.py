import subprocess
import json
import os
import tempfile
import glob

def disassemble_jfr(jfr_path, output_dir=None, max_size_mb=50):
    """
    If the JFR file is large, uses 'jfr disassemble' to chunk it before parsing.
    Returns a list of chunk file paths (including just the original if not chunked).
    Requires JDK 17+.
    """
    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="jfr_chunks_")
    # Check file size
    size_mb = os.path.getsize(jfr_path) / (1024 * 1024)
    chunk_files = []
    if size_mb > max_size_mb:
        # Disassemble into chunks using max size
        dis_cmd = [
            "jfr", "disassemble",
            "--output", output_dir,
            "--max-size", f"{int(max_size_mb)}m",
            jfr_path
        ]
        try:
            print(f"Disassembling {jfr_path} into chunks (directory {output_dir}) ...")
            subprocess.run(dis_cmd, check=True)
            chunk_files = sorted(glob.glob(os.path.join(output_dir, "*.jfr")))
            print(f"Chunked into {len(chunk_files)} files.")
        except Exception as e:
            print(f"Error in jfr disassemble: {e}")
            chunk_files = [jfr_path]
    else:
        chunk_files = [jfr_path]
    return chunk_files

def parse_jfr(jfr_path, chunking_threshold_mb=None):
    """
    Extracts events or stack traces from a JFR file using `jfr print` (JDK 17+ recommended).
    If the file is a .json/text file, loads the JSON or text directly.
    For large .jfr files, chunks and aggregates from all chunks.

    Parameters:
    - jfr_path: Path to the JFR or JSON file
    - chunking_threshold_mb: Threshold size in MB above which to chunk (default 50 MB)
    """
    if chunking_threshold_mb is None:
        chunking_threshold_mb = 50
    # If a .json, read as already-prepared snippet
    if jfr_path.endswith('.json'):
        with open(jfr_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    # For .jfr, disassemble if large
    chunk_files = disassemble_jfr(jfr_path, max_size_mb=chunking_threshold_mb)
    all_events = []
    for cfile in chunk_files:
        output_file = cfile + ".json"
        try:
            print(f"Converting {cfile} to JSON: {output_file}")
            subprocess.run(
                ["jfr", "print", "--json", "--categories", "Java Application,Threads,GC,Socket,IO,JVM", cfile],
                check=True,
                stdout=open(output_file, "w", encoding="utf-8")
            )
            with open(output_file, "r", encoding="utf-8") as f:
                raw = json.load(f)
                all_events.extend(raw)
            os.remove(output_file)
        except Exception as e:
            print(f"Error processing JFR chunk {cfile}: {e}")
            continue
    return all_events
