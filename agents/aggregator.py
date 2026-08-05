"""
agents/aggregator.py — Aggregator & Summary Agent
"""

import uuid
from datetime import datetime, timezone
from langchain_core.messages import SystemMessage, HumanMessage
from agents.utils.llm_factory import build_llm
from models.schemas import AgentReport, FinalReviewReport

AGGREGATOR_SYSTEM_PROMPT = """You are a Senior Software Architect and Review Aggregator.
You will be given a list of reports from various specialized code review agents.
Your task is to write a cohesive, professional, and structured Executive Summary of the overall findings.
Read like a senior engineer's Pull Request review comment. Be constructive, specify critical issues if any, and summarize overall code health.
Provide a 3-5 sentence summary. Do not output any markdown formatting, just plain text.
"""

class Aggregator:
    def __init__(self, provider: str = "groq", model: str = "llama-3.3-70b-versatile"):
        self.llm = build_llm(provider, model, 0.0)

    def aggregate(self, reports: list[AgentReport]) -> FinalReviewReport:
        score = 100
        agents_run = []

        for report in reports:
            agents_run.append(report.agent_name)
            if report.status == "success":
                for finding in report.findings:
                    sev = finding.severity.lower()
                    if sev == "critical":
                        score -= 15
                    elif sev == "high":
                        score -= 8
                    elif sev == "medium":
                        score -= 4
                    elif sev == "low":
                        score -= 1

        score = max(0, min(100, score))

        reports_content = ""
        for report in reports:
            reports_content += f"Agent: {report.agent_name}\n"
            reports_content += f"Summary: {report.summary}\n"
            reports_content += "Findings:\n"
            for f in report.findings:
                reports_content += f"- [{f.severity.upper()}] {f.title}: {f.description} (Line {f.line_number})\n"
            reports_content += "\n"

        messages = [
            SystemMessage(content=AGGREGATOR_SYSTEM_PROMPT),
            HumanMessage(content=f"Review Reports:\n{reports_content}")
        ]
        try:
            res = self.llm.invoke(messages)
            summary = res.content.strip()
        except Exception as e:
            summary = f"Summary generation failed: {e}."

        return FinalReviewReport(
            report_id=str(uuid.uuid4()),
            overall_score=score,
            agents_run=agents_run,
            reports=reports,
            executive_summary=summary,
            generated_at=datetime.now(timezone.utc)
        )
