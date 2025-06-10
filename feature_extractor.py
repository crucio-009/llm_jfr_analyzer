import datetime

def extract_features(events):
    """
    Given parsed JFR events or stack traces, extracts features or key event sequences
    to summarize as LLM input.
    Returns a cleaned/summarized dictionary or string for LLM prompt injection.
    """
    features = {
        "num_events": len(events),
        "time_range": None,
        "stuck_threads": [],
        "hot_threads": [],
        "longest_gc_pause": None,
        "top_sql": [],
        "high_usage_periods": []
    }
    # This is a minimal MVP, you can add mechanisms to filter large input for LLMs:
    times = []
    top_sql = []
    stuck_threads = []
    gc_pauses = []

    for e in events:
        if 'startTime' in e:
            # Convert ISO string to datetime if present
            try:
                times.append(datetime.datetime.fromisoformat(e['startTime'].replace("Z", "+00:00")))
            except Exception:
                pass

        if e.get('event') == 'jdk.ThreadStuck':
            stuck_threads.append(e)
        # Hot SQL (rough): look for JDBC or SQL fields
        if 'sql' in e or 'SQL' in str(e):
            top_sql.append(str(e))
        # GC pause
        if e.get('event', '').startswith("jdk.GarbageCollection"):
            pause = e.get('longestPause', 0)
            if pause:
                gc_pauses.append(pause)

    if times:
        features["time_range"] = f"{min(times)} --> {max(times)}"
    features["stuck_threads"] = stuck_threads[:5]
    features["top_sql"] = top_sql[:5]
    features["longest_gc_pause"] = max(gc_pauses) if gc_pauses else None

    # For the LLM, we can return BOTH a feature dict and a plain summary string
    summary = f"""
JFR Summary:
Events: {features['num_events']}
Time Range: {features['time_range']}
Stuck Threads: {len(stuck_threads)}
Example Top SQL: {features['top_sql'][:2]}
Longest GC Pause(ms): {features['longest_gc_pause']}
"""
    return summary
