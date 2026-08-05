"""
agents/tools/test_presence_tool.py — Test File Presence Checker
"""

import json
import os

from langchain_core.tools import tool

@tool
def test_presence_tool(filename: str) -> str:
    """
    Check whether a unit-test file exists for the given source file path.
    """
    if not filename or not filename.strip():
        return json.dumps({
            "tool": "test_presence",
            "status": "snippet_mode",
            "message": "Snippet mode — test presence check skipped.",
            "test_found": False,
        })

    abs_path = os.path.abspath(filename)
    if not os.path.isfile(abs_path):
        return json.dumps({
            "tool": "test_presence",
            "status": "file_not_found",
            "message": f"Source file '{filename}' not found.",
            "test_found": False,
        })

    base = os.path.basename(abs_path)
    stem = os.path.splitext(base)[0]
    src_dir = os.path.dirname(abs_path)
    tests_dir = os.path.join(src_dir, "tests")

    candidates = [
        os.path.join(src_dir,   f"test_{stem}.py"),
        os.path.join(src_dir,   f"{stem}_test.py"),
        os.path.join(tests_dir, f"test_{stem}.py"),
        os.path.join(tests_dir, f"{stem}_test.py"),
    ]

    found = [c for c in candidates if os.path.isfile(c)]

    if found:
        return json.dumps({
            "tool": "test_presence",
            "status": "found",
            "test_found": True,
            "test_files": found,
            "message": f"Test file(s) found: {', '.join(found)}",
        })

    return json.dumps({
        "tool": "test_presence",
        "status": "missing",
        "test_found": False,
        "checked_paths": candidates,
        "message": f"No test file found for '{base}'.",
    })
