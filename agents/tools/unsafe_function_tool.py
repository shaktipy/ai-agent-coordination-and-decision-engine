"""
agents/tools/unsafe_function_tool.py — Unsafe Function Detector
"""

import ast
import json

from langchain_core.tools import tool

_DANGEROUS_CALLS = {
    "eval":         "eval() executes arbitrary Python expressions — a remote code execution risk.",
    "exec":         "exec() executes arbitrary Python code — avoid unless absolutely necessary.",
}

_DANGEROUS_ATTR_CALLS = [
    ("pickle",      "loads",  "pickle.loads() can execute arbitrary code during deserialisation."),
    ("os",          "system", "os.system() passes commands directly to the shell — prefer subprocess."),
]

class _UnsafeVisitor(ast.NodeVisitor):
    def __init__(self):
        self.findings = []

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name):
            name = node.func.id
            if name in _DANGEROUS_CALLS:
                self.findings.append({
                    "line":    node.lineno,
                    "pattern": name,
                    "reason":  _DANGEROUS_CALLS[name],
                })
        elif isinstance(node.func, ast.Attribute):
            obj = ""
            if isinstance(node.func.value, ast.Name):
                obj = node.func.value.id
            attr = node.func.attr

            for mod, fn, reason in _DANGEROUS_ATTR_CALLS:
                if obj == mod and attr == fn:
                    self.findings.append({
                        "line":    node.lineno,
                        "pattern": f"{mod}.{fn}",
                        "reason":  reason,
                    })

        self.generic_visit(node)

@tool
def unsafe_function_tool(code: str) -> str:
    """
    Scan Python source code for dangerous built-ins and patterns.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return json.dumps({
            "tool": "unsafe_function_scan",
            "status": "syntax_error",
            "message": f"Cannot parse code: {exc}",
            "findings": [],
        })

    visitor = _UnsafeVisitor()
    visitor.visit(tree)

    if not visitor.findings:
        return json.dumps({
            "tool": "unsafe_function_scan",
            "status": "clean",
            "message": "No dangerous function calls detected.",
            "findings": [],
        })

    return json.dumps({
        "tool": "unsafe_function_scan",
        "status": "findings",
        "count": len(visitor.findings),
        "findings": visitor.findings,
    })
