"""
tests/test_tools.py — New Code Review Tool Tests
=================================================
Covers the 9 specialized static-analysis tools:
    1. secret_pattern_scan_tool
    2. unsafe_function_tool
    3. nested_loop_detector_tool
    4. cyclomatic_complexity_tool
    5. naming_convention_tool
    6. docstring_coverage_tool
"""

import json
import pytest
from agents.tools.secret_pattern_tool import secret_pattern_scan_tool
from agents.tools.unsafe_function_tool import unsafe_function_tool
from agents.tools.nested_loop_tool import nested_loop_detector_tool
from agents.tools.radon_complexity_tool import cyclomatic_complexity_tool
from agents.tools.naming_convention_tool import naming_convention_tool
from agents.tools.docstring_coverage_tool import docstring_coverage_tool


# ── 1. Secret Pattern Scan ─────────────────────────────────────────────────────

def test_secret_clean():
    code = "def add(a, b):\n    return a + b\n"
    res = json.loads(secret_pattern_scan_tool.invoke(code))
    assert res["status"] == "clean"

def test_secret_hardcoded_api_key():
    code = 'api_key = "sk-ABCDEFGH12345678901234567890"\n'
    res = json.loads(secret_pattern_scan_tool.invoke(code))
    assert res["status"] == "findings"
    assert len(res["findings"]) >= 1

def test_secret_password_assignment():
    code = 'password = "super_secret_pass_123"\n'
    res = json.loads(secret_pattern_scan_tool.invoke(code))
    assert res["status"] == "findings"


# ── 2. Unsafe Function Scan ───────────────────────────────────────────────────

def test_unsafe_clean():
    code = "x = 1 + 1\nprint(x)\n"
    res = json.loads(unsafe_function_tool.invoke(code))
    assert res["status"] == "clean"

def test_unsafe_eval():
    code = "result = eval('1 + 1')\n"
    res = json.loads(unsafe_function_tool.invoke(code))
    assert res["status"] == "findings"
    assert any(f["pattern"] == "eval" for f in res["findings"])

def test_unsafe_exec():
    code = "exec('import os')\n"
    res = json.loads(unsafe_function_tool.invoke(code))
    assert res["status"] == "findings"
    assert any(f["pattern"] == "exec" for f in res["findings"])


# ── 3. Nested Loop Detector ───────────────────────────────────────────────────

def test_nested_loop_clean():
    code = "for i in range(10):\n    print(i)\nfor j in range(10):\n    print(j)\n"
    res = json.loads(nested_loop_detector_tool.invoke(code))
    assert res["status"] == "clean"

def test_nested_loop_depth2():
    code = "for i in range(10):\n    for j in range(10):\n        print(i, j)\n"
    res = json.loads(nested_loop_detector_tool.invoke(code))
    assert res["status"] == "findings"
    assert res["findings"][0]["depth"] == 2

def test_nested_loop_depth3():
    code = "for i in range(5):\n    for j in range(5):\n        for k in range(5):\n            pass\n"
    res = json.loads(nested_loop_detector_tool.invoke(code))
    assert res["status"] == "findings"
    assert any(f["depth"] == 3 for f in res["findings"])


# ── 4. Cyclomatic Complexity ──────────────────────────────────────────────────

def test_cc_simple():
    code = "def greet(name):\n    return f'Hello {name}'\n"
    res = json.loads(cyclomatic_complexity_tool.invoke(code))
    assert res["status"] == "success"
    assert res["findings"][0]["complexity"] == 1

def test_cc_branchy():
    code = (
        "def check(x):\n"
        "    if x > 0:\n"
        "        if x > 5:\n"
        "            return 'big'\n"
        "        return 'small'\n"
        "    elif x == 0:\n"
        "        return 'zero'\n"
        "    return 'negative'\n"
    )
    res = json.loads(cyclomatic_complexity_tool.invoke(code))
    assert res["status"] == "success"
    assert res["findings"][0]["complexity"] >= 4


# ── 5. Naming Convention ──────────────────────────────────────────────────────

def test_naming_clean():
    code = "class MyClass:\n    def my_method(self):\n        my_var = 1\n"
    res = json.loads(naming_convention_tool.invoke(code))
    assert res["status"] == "clean"

def test_naming_bad_class():
    code = "class badClass:\n    pass\n"
    res = json.loads(naming_convention_tool.invoke(code))
    assert res["status"] == "findings"
    assert any("class" in f["kind"] for f in res["findings"])

def test_naming_bad_method():
    code = "class Good:\n    def BadMethod(self):\n        pass\n"
    res = json.loads(naming_convention_tool.invoke(code))
    assert res["status"] == "findings"
    assert any("method" in f["kind"] or "function" in f["kind"] for f in res["findings"])


# ── 6. Docstring Coverage ─────────────────────────────────────────────────────

def test_docstring_full():
    code = (
        "class MyClass:\n"
        "    '''A class docstring.'''\n"
        "    def my_method(self):\n"
        "        '''A method docstring.'''\n"
        "        pass\n"
    )
    res = json.loads(docstring_coverage_tool.invoke(code))
    assert res["coverage_pct"] == 100.0

def test_docstring_missing():
    code = "class MyClass:\n    def my_method(self):\n        pass\n"
    res = json.loads(docstring_coverage_tool.invoke(code))
    assert res["status"] == "findings"
    assert res["coverage_pct"] < 100

def test_docstring_no_items():
    code = "x = 1\n"
    res = json.loads(docstring_coverage_tool.invoke(code))
    assert res["status"] == "no_items"
