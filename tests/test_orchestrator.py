"""
tests/test_orchestrator.py — Orchestrator routing + Aggregator score tests
"""

import pytest
from agents.orchestrator import MasterOrchestrator
from agents.aggregator import Aggregator
from models.schemas import AgentReport, Finding


# ── Routing ───────────────────────────────────────────────────────────────────

def test_routing_full():
    orc = MasterOrchestrator()
    assert orc.route_request("Please review my code thoroughly") == "FULL"

def test_routing_security():
    orc = MasterOrchestrator()
    assert orc.route_request("Scan for hardcoded secrets and vulnerability") == "SECURITY"

def test_routing_performance():
    orc = MasterOrchestrator()
    assert orc.route_request("Check the code for nested loop complexity") == "PERFORMANCE"

def test_routing_quality():
    orc = MasterOrchestrator()
    assert orc.route_request("Validate pep8 naming convention style") == "QUALITY"

def test_routing_docs():
    orc = MasterOrchestrator()
    assert orc.route_request("Are there any missing docstrings or test coverage?") == "DOCS"


# ── Aggregator Score Deductions ───────────────────────────────────────────────

def test_aggregator_perfect_score():
    agg = Aggregator()
    reports = [
        AgentReport(agent_name="Test", findings=[], summary="ok", status="success")
    ]
    result = agg.aggregate(reports)
    assert result.overall_score == 100

def test_aggregator_score_deductions():
    agg = Aggregator()
    reports = [
        AgentReport(
            agent_name="Security",
            findings=[
                Finding(category="security", severity="critical", title="A", description="", line_number=1, suggestion=""),
                Finding(category="security", severity="high", title="B", description="", line_number=2, suggestion=""),
            ],
            summary="ok", status="success"
        ),
        AgentReport(
            agent_name="Performance",
            findings=[
                Finding(category="performance", severity="medium", title="C", description="", line_number=3, suggestion=""),
                Finding(category="performance", severity="low", title="D", description="", line_number=4, suggestion=""),
            ],
            summary="ok", status="success"
        )
    ]
    # 100 - 15(critical) - 8(high) - 4(medium) - 1(low) = 72
    result = agg.aggregate(reports)
    assert result.overall_score == 72

def test_aggregator_score_floored_at_zero():
    agg = Aggregator()
    findings = [
        Finding(category="security", severity="critical", title=f"Issue {i}", description="", line_number=i, suggestion="")
        for i in range(10)  # 10 x critical = -150 → floored at 0
    ]
    reports = [AgentReport(agent_name="Security", findings=findings, summary="ok", status="success")]
    result = agg.aggregate(reports)
    assert result.overall_score == 0
