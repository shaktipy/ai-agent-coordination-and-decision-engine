"""
agents/tools/secret_pattern_tool.py — Hardcoded Secret Scanner
"""

import json
import re

from langchain_core.tools import tool

_SECRET_PATTERNS = [
    ("AWS Access Key ID",          re.compile(r"AKIA[0-9A-Z]{16}", re.I)),
    ("AWS Secret Access Key",      re.compile(r"aws.{0,20}secret.{0,20}['\"][0-9a-zA-Z/+]{40}['\"]", re.I)),
    ("Google API Key",             re.compile(r"AIza[0-9A-Za-z_-]{35}")),
    ("Groq / OpenAI API Key",      re.compile(r"(gsk|sk|rsk)[_-][a-zA-Z0-9]{20,60}")),
    ("Generic API Key assignment", re.compile(r"(api[_-]?key|apikey)\s*[=:]\s*['\"][^'\"]{8,}['\"]", re.I)),
    ("Password assignment",        re.compile(r"(password|passwd|pwd)\s*[=:]\s*['\"][^'\"]{4,}['\"]", re.I)),
    ("Secret assignment",          re.compile(r"(secret|token)\s*[=:]\s*['\"][^'\"]{6,}['\"]", re.I)),
    ("Database connection string", re.compile(r"(mysql|postgresql|postgres|mongodb|redis)://[^'\"\s]{6,}", re.I)),
    ("Private key block",          re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----")),
]

@tool
def secret_pattern_scan_tool(code: str) -> str:
    """
    Scan the provided source code for hardcoded secrets.
    """
    findings = []
    lines = code.splitlines()
    for line_no, line in enumerate(lines, start=1):
        for label, pattern in _SECRET_PATTERNS:
            matches = pattern.findall(line)
            if matches:
                redacted = re.sub(r"['\"][^'\"]{4,}['\"]", "'***REDACTED***'", line.strip())
                findings.append({
                    "label":       label,
                    "line":        line_no,
                    "line_content": redacted,
                    "match_count": len(matches),
                })

    if not findings:
        return json.dumps({
            "tool": "secret_pattern_scan",
            "status": "clean",
            "message": "No hardcoded secrets detected.",
            "findings": [],
        })

    return json.dumps({
        "tool": "secret_pattern_scan",
        "status": "findings",
        "count": len(findings),
        "findings": findings,
    })
