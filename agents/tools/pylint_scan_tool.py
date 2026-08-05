"""
agents/tools/pylint_scan_tool.py — Pylint Code Quality Scanner
"""

import ast
import json
import os
import subprocess
import sys
import tempfile

from langchain_core.tools import tool

_TYPE_MAP = {
    "C": "convention",
    "R": "refactor",
    "W": "warning",
    "E": "error",
    "F": "fatal",
    "I": "info",
}

@tool
def pylint_scan_tool(code: str) -> str:
    """
    Run pylint on Python source code and return structured findings.
    """
    try:
        ast.parse(code)
    except SyntaxError as exc:
        return json.dumps({
            "tool": "pylint",
            "status": "syntax_error",
            "message": f"Cannot parse code: {exc}",
            "findings": [],
        })

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(code)
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            [
                sys.executable, "-m", "pylint",
                "--output-format=json",
                "--disable=all",
                "--enable=E,W,R,C",
                "--disable=C0114,C0115,C0116,C0301,C0303,W0611",
                tmp_path,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        output = result.stdout.strip()
        if not output or output == "[]":
            return json.dumps({
                "tool": "pylint",
                "status": "clean",
                "message": "No pylint issues detected.",
                "findings": [],
            })

        raw = json.loads(output)
        findings = []
        for msg in raw:
            type_code = msg.get("type", "?")[0].upper()
            findings.append({
                "message_id": msg.get("message-id"),
                "type":       _TYPE_MAP.get(type_code, type_code),
                "symbol":     msg.get("symbol"),
                "line":       msg.get("line"),
                "column":     msg.get("column"),
                "message":    msg.get("message"),
            })

        return json.dumps({
            "tool": "pylint",
            "status": "findings",
            "count": len(findings),
            "findings": findings,
        })
    except Exception as exc:
        return json.dumps({
            "tool": "pylint",
            "status": "error",
            "message": str(exc),
            "findings": [],
        })
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
