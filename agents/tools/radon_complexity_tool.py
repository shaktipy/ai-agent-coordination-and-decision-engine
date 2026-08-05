"""
agents/tools/radon_complexity_tool.py — Cyclomatic Complexity & Maintainability
"""

import ast
import json
import os
import subprocess
import sys
import tempfile

from langchain_core.tools import tool

def _write_temp(code: str) -> str:
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(code)
        return tmp.name

def _cleanup(path: str) -> None:
    try:
        os.unlink(path)
    except OSError:
        pass

@tool
def cyclomatic_complexity_tool(code: str) -> str:
    """
    Compute cyclomatic complexity for each function/method in Python code using `radon cc`.
    """
    try:
        ast.parse(code)
    except SyntaxError as exc:
        return json.dumps({"tool": "radon_cc", "status": "syntax_error", "message": str(exc), "findings": []})

    tmp = _write_temp(code)
    try:
        result = subprocess.run(
            [sys.executable, "-m", "radon", "cc", "-s", "-j", tmp],
            capture_output=True, text=True, timeout=30,
        )
        data = json.loads(result.stdout or "{}")
        findings = []
        for _file, funcs in data.items():
            for fn in funcs:
                findings.append({
                    "name":       fn.get("name"),
                    "type":       fn.get("type"),
                    "line_start": fn.get("lineno"),
                    "complexity": fn.get("complexity"),
                    "grade":      fn.get("rank"),
                    "is_complex": fn.get("complexity", 0) >= 10,
                })

        return json.dumps({
            "tool": "radon_cc",
            "status": "success",
            "count": len(findings),
            "findings": findings,
        })
    except Exception as exc:
        return json.dumps({
            "tool": "radon_cc", "status": "error", "message": str(exc), "findings": [],
        })
    finally:
        _cleanup(tmp)

@tool
def maintainability_index_tool(code: str) -> str:
    """
    Compute the Maintainability Index (MI) for Python code using `radon mi`.
    """
    try:
        ast.parse(code)
    except SyntaxError as exc:
        return json.dumps({"tool": "radon_mi", "status": "syntax_error", "message": str(exc), "findings": []})

    tmp = _write_temp(code)
    try:
        result = subprocess.run(
            [sys.executable, "-m", "radon", "mi", "-s", "-j", tmp],
            capture_output=True, text=True, timeout=30,
        )
        data = json.loads(result.stdout or "{}")
        findings = []
        for _file, info in data.items():
            findings.append({
                "mi_score": round(info.get("mi", 0), 2),
                "grade":    info.get("rank"),
            })

        return json.dumps({
            "tool": "radon_mi",
            "status": "success",
            "findings": findings,
        })
    except Exception as exc:
        return json.dumps({
            "tool": "radon_mi", "status": "error", "message": str(exc), "findings": [],
        })
    finally:
        _cleanup(tmp)
