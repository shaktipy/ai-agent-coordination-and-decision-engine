"""
agents/tools/docstring_coverage_tool.py — Docstring Coverage Analyser
"""

import ast
import json

from langchain_core.tools import tool

def _has_docstring(node) -> bool:
    return (
        isinstance(node.body, list)
        and node.body
        and isinstance(node.body[0], ast.Expr)
        and isinstance(node.body[0].value, ast.Constant)
        and isinstance(node.body[0].value.value, str)
    )

@tool
def docstring_coverage_tool(code: str) -> str:
    """
    Analyse docstring coverage of public entities in Python source code.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return json.dumps({
            "tool": "docstring_coverage",
            "status": "syntax_error",
            "message": f"Cannot parse code: {exc}",
            "findings": [],
        })

    total      = 0
    documented = 0
    missing = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("_"):
                continue
            total += 1
            if _has_docstring(node):
                documented += 1
            else:
                missing.append({
                    "kind": "function",
                    "name": node.name,
                    "line": node.lineno,
                })
        elif isinstance(node, ast.ClassDef):
            if node.name.startswith("_"):
                continue
            total += 1
            if _has_docstring(node):
                documented += 1
            else:
                missing.append({
                    "kind": "class",
                    "name": node.name,
                    "line": node.lineno,
                })

    if total == 0:
        return json.dumps({
            "tool": "docstring_coverage",
            "status": "no_items",
            "message": "No public items found.",
            "coverage_pct": 100,
            "findings": [],
        })

    coverage = round((documented / total) * 100, 1)
    status = "clean" if coverage == 100 else "findings"

    return json.dumps({
        "tool": "docstring_coverage",
        "status": status,
        "total_items": total,
        "documented":  documented,
        "coverage_pct": coverage,
        "missing_count": len(missing),
        "findings": missing,
    })
