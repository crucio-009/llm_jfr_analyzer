from jinja2 import Template

def write_report(findings, output_path):
    """
    Writes the LLM analysis results to a Markdown file.
    """
    html_template = """
# JVM Diagnostics Report

## Executive Summary

{{ findings }}

---

*Generated by LLM JFR Analyzer MVP*
    """
    report = Template(html_template).render(findings=findings)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
