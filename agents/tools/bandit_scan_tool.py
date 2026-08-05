"""
agents/tools/bandit_scan_tool.py — Bandit Security Scanner Tool
"""

import ast
import json
import os
import subprocess
import sys
import tempfile

from langchain_core.tools import tool


@tool
def bandit_scan_tool(code: str) -> str:
    """
    Run the bandit Python security linter on the provided code snippet.
    """
    try:
        ast.parse(code)
    except SyntaxError as exc:
        return json.dumps({
            "tool": "bandit",
            "status": "syntax_error",
            "message": f"Code has a syntax error — cannot parse: {exc}",
            "findings": [],
        })

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(code)
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            [sys.executable, "-m", "bandit", "-f", "json", "-q", tmp_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = result.stdout.strip()

        if not output:
            return json.dumps({
                "tool": "bandit",
                "status": "clean",
                "message": "No security issues detected by bandit.",
                "findings": [],
            })

        data = json.loads(output)
        findings = []
        for issue in data.get("results", []):
            findings.append({
                "test_id":   issue.get("test_id"),
                "test_name": issue.get("test_name"),
                "severity":  issue.get("issue_severity", "").lower(),
                "confidence":issue.get("issue_confidence", "").lower(),
                "line":      issue.get("line_number"),
                "col":       issue.get("col_offset"),
                "text":      issue.get("issue_text"),
                "code":      issue.get("code", "").strip(),
            })

        return json.dumps({
            "tool": "bandit",
            "status": "findings",
            "count": len(findings),
            "findings": findings,
        })

    except FileNotFoundError:
        return json.dumps({
            "tool": "bandit",
            "status": "not_installed",
            "message": "bandit is not installed. Run: pip install bandit.",
            "findings": [],
        })
    except Exception as exc:
        return json.dumps({
            "tool": "bandit",
            "status": "error",
            "message": str(exc),
            "findings": [],
        })
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
