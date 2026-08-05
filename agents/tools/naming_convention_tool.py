"""
agents/tools/naming_convention_tool.py — Naming Convention Checker
"""

import ast
import json
import re

from langchain_core.tools import tool

_SNAKE_CASE    = re.compile(r"^[a-z_][a-z0-9_]*$")
_PASCAL_CASE   = re.compile(r"^[A-Z][a-zA-Z0-9]*$")
_UPPER_SNAKE   = re.compile(r"^[A-Z_][A-Z0-9_]*$")
_SKIP_FUNCTIONS = frozenset({"__init__", "__str__", "__repr__", "__len__", "__eq__"})

class _NamingVisitor(ast.NodeVisitor):
    def __init__(self):
        self.findings = []

    def _flag(self, line: int, name: str, kind: str, expected: str):
        self.findings.append({
            "line":     line,
            "name":     name,
            "kind":     kind,
            "expected": expected,
            "reason":   f"'{name}' ({kind}) does not follow PEP 8 {expected} convention.",
        })

    def visit_FunctionDef(self, node: ast.FunctionDef):
        name = node.name
        if name not in _SKIP_FUNCTIONS and not _SNAKE_CASE.match(name):
            self._flag(node.lineno, name, "function/method", "snake_case")
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        if not _PASCAL_CASE.match(node.name):
            self._flag(node.lineno, node.name, "class", "PascalCase")
        self.generic_visit(node)

@tool
def naming_convention_tool(code: str) -> str:
    """
    Check Python source code for PEP 8 naming convention violations.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return json.dumps({
            "tool": "naming_convention",
            "status": "syntax_error",
            "message": f"Cannot parse code: {exc}",
            "findings": [],
        })

    visitor = _NamingVisitor()
    visitor.visit(tree)

    if not visitor.findings:
        return json.dumps({
            "tool": "naming_convention",
            "status": "clean",
            "message": "All names follow PEP 8 conventions.",
            "findings": [],
        })

    return json.dumps({
        "tool": "naming_convention",
        "status": "findings",
        "count": len(visitor.findings),
        "findings": visitor.findings,
    })
