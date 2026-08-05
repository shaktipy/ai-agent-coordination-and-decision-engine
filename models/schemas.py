"""
models/schemas.py — Shared Pydantic Models
"""

from __future__ import annotations
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field

class Finding(BaseModel):
    category: Literal["security", "performance", "quality", "docs_tests"]
    severity: Literal["critical", "high", "medium", "low", "info"]
    title: str
    description: str
    line_number: Optional[int] = None
    suggestion: str

class AgentReport(BaseModel):
    agent_name: str
    findings: list[Finding] = []
    summary: str
    status: Literal["success", "failed", "skipped"] = "success"
    error_message: Optional[str] = None

class FinalReviewReport(BaseModel):
    report_id: str
    overall_score: int
    agents_run: list[str]
    reports: list[AgentReport]
    executive_summary: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
