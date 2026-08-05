"""
agents/tools/nested_loop_tool.py — Nested Loop Detector
"""

import ast
import json

from langchain_core.tools import tool

class _LoopDepthVisitor(ast.NodeVisitor):
    def __init__(self):
        self.findings = []
        self._loop_stack = []

    def _enter_loop(self, node):
        self._loop_stack.append(node.lineno)
        depth = len(self._loop_stack)
        if depth >= 2:
            self.findings.append({
                "type":        "nested_loop",
                "depth":       depth,
                "line":        node.lineno,
                "outer_lines": list(self._loop_stack[:-1]),
                "reason": (
                    f"Loop nested {depth} levels deep starting at line {node.lineno}. "
                    f"This may indicate O(n^{depth}) time complexity."
                ),
            })
        self.generic_visit(node)
        self._loop_stack.pop()

    def visit_For(self, node):
        self._enter_loop(node)

    def visit_While(self, node):
        self._enter_loop(node)

@tool
def nested_loop_detector_tool(code: str) -> str:
    """
    Detect deeply nested loops in Python code.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return json.dumps({
            "tool": "nested_loop_detector",
            "status": "syntax_error",
            "message": f"Cannot parse code: {exc}",
            "findings": [],
        })

    visitor = _LoopDepthVisitor()
    visitor.visit(tree)

    if not visitor.findings:
        return json.dumps({
            "tool": "nested_loop_detector",
            "status": "clean",
            "message": "No deeply nested loops detected.",
            "findings": [],
        })

    return json.dumps({
        "tool": "nested_loop_detector",
        "status": "findings",
        "count": len(visitor.findings),
        "findings": visitor.findings,
    })
