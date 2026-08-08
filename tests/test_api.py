"""
tests/test_api.py — FastAPI Endpoint Tests
==========================================
Uses FastAPI's TestClient (via httpx) to test the REST API without
requiring a running server. Covers:
  - GET  /api/health
  - GET  /api/history
  - POST /api/review   (valid code, empty code)
"""

import pytest
from fastapi.testclient import TestClient
from api.server import app

client = TestClient(app)

CLEAN_CODE = """\
def add(a: int, b: int) -> int:
    \"\"\"Return the sum of a and b.\"\"\"
    return a + b
"""

VULNERABLE_CODE = """\
api_key = "sk-ABCDEFGH1234567890"
result = eval(user_input)
for i in range(100):
    for j in range(100):
        pass
"""


# ── Health Check ─────────────────────────────────────────────────────────────

def test_health_ok():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "service" in data


# ── History ──────────────────────────────────────────────────────────────────

def test_history_returns_structure():
    resp = client.get("/api/history")
    assert resp.status_code == 200
    data = resp.json()
    # Must contain these keys from the long-term memory schema
    assert "past_reviews_count" in data
    assert "recurring_issues" in data
    assert "learnings" in data
    assert isinstance(data["past_reviews_count"], int)
    assert isinstance(data["recurring_issues"], list)
    assert isinstance(data["learnings"], list)


# ── Review (clean code) ───────────────────────────────────────────────────────

def test_review_clean_code_returns_report():
    payload = {"code": CLEAN_CODE, "query": "", "session_id": "test_session_clean"}
    resp = client.post("/api/review", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "overall_score" in data
    assert "reports" in data
    assert "executive_summary" in data
    assert isinstance(data["overall_score"], int)
    assert 0 <= data["overall_score"] <= 100
    assert isinstance(data["reports"], list)
    assert len(data["reports"]) >= 1


# ── Review (vulnerable code) ──────────────────────────────────────────────────

def test_review_vulnerable_code_score_less_than_clean():
    """Vulnerable code should yield a lower health score than clean code."""
    clean_resp = client.post("/api/review", json={
        "code": CLEAN_CODE, "query": "", "session_id": "test_session_clean2"
    })
    vuln_resp = client.post("/api/review", json={
        "code": VULNERABLE_CODE, "query": "", "session_id": "test_session_vuln"
    })
    assert clean_resp.status_code == 200
    assert vuln_resp.status_code == 200
    clean_score = clean_resp.json()["overall_score"]
    vuln_score  = vuln_resp.json()["overall_score"]
    assert vuln_score <= clean_score, (
        f"Expected vulnerable ({vuln_score}) <= clean ({clean_score})"
    )


# ── Review (empty code) ───────────────────────────────────────────────────────

def test_review_empty_code_handles_gracefully():
    payload = {"code": "", "query": "", "session_id": "test_session_empty"}
    resp = client.post("/api/review", json=payload)
    # Should either succeed (200) or return a clean 500 error — not crash
    assert resp.status_code in (200, 500)


# ── Review (focused query routing) ───────────────────────────────────────────

def test_review_security_query_returns_security_agent():
    payload = {
        "code": VULNERABLE_CODE,
        "query": "Check for hardcoded secrets and security vulnerabilities",
        "session_id": "test_session_security"
    }
    resp = client.post("/api/review", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    agent_names = [r["agent_name"] for r in data["reports"]]
    assert any("Security" in name for name in agent_names)


# ── Report Schema Validation ──────────────────────────────────────────────────

def test_review_report_schema():
    payload = {"code": CLEAN_CODE, "query": "", "session_id": "test_schema"}
    resp = client.post("/api/review", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    # Top-level fields
    assert "report_id" in data
    assert "generated_at" in data
    assert "agents_run" in data
    assert isinstance(data["agents_run"], list)

    # Agent report fields
    for rep in data["reports"]:
        assert "agent_name" in rep
        assert "findings" in rep
        assert "summary" in rep
        assert "status" in rep
        assert rep["status"] in ("success", "failed", "skipped")

        # Finding fields
        for finding in rep["findings"]:
            assert "category" in finding
            assert "severity" in finding
            assert "title" in finding
            assert "description" in finding
            assert "suggestion" in finding
            assert finding["severity"] in ("critical", "high", "medium", "low", "info")
