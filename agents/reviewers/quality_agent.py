"""
agents/reviewers/quality_agent.py — Code Quality & Best Practices Agent
"""

import json
from langchain_core.messages import SystemMessage, HumanMessage
from agents.utils.llm_factory import build_llm
from agents.tools.pylint_scan_tool import pylint_scan_tool
from agents.tools.naming_convention_tool import naming_convention_tool
from models.schemas import AgentReport, Finding

SYSTEM_PROMPT = """You are a Code Quality & Best Practices Agent. Your job is to analyze code for PEP8 compliance, styling violations, bad naming conventions, code smells, and general best practices.
You will be provided with code and raw static-analysis tool results.
Your output must contain an explanation of each issue, its impact, and a suggestion for improving quality.
Provide your final output in a valid JSON format conforming to the AgentReport schema:
{
  "agent_name": "Code Quality & Best Practices Agent",
  "findings": [
    {
      "category": "quality",
      "severity": "critical" | "high" | "medium" | "low" | "info",
      "title": "Finding title",
      "description": "Why this is a quality/style issue",
      "line_number": 12,
      "suggestion": "How to align with conventions/best practices"
    }
  ],
  "summary": "1-3 sentences summary of code quality health",
  "status": "success"
}
Output ONLY raw JSON. No markdown backticks, no comments, no extra text.
"""

class QualityAgent:
    def __init__(self, provider: str = "groq", model: str = "llama-3.3-70b-versatile", temperature: float = 0.0):
        self.llm = build_llm(provider, model, temperature)

    def run(self, code: str, filename: str = "", context: str = "") -> AgentReport:
        try:
            pylint_res = pylint_scan_tool.invoke(code)
            naming_res = naming_convention_tool.invoke(code)

            prompt = ""
            if context:
                prompt += f"Memory & Context:\n{context}\n\n"
            prompt += f"Source Code:\n{code}\n\nPylint Results:\n{pylint_res}\n\nNaming Convention Check:\n{naming_res}\n"
            messages = [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=prompt)
            ]
            response = self.llm.invoke(messages)
            content = response.content.strip()

            if content.startswith("```"):
                lines = content.splitlines()
                if lines[0].startswith("```json") or lines[0].startswith("```"):
                    content = "\n".join(lines[1:-1]).strip()

            data = json.loads(content)
            findings = []
            for f in data.get("findings", []):
                findings.append(Finding(
                    category="quality",
                    severity=f.get("severity", "medium"),
                    title=f.get("title", ""),
                    description=f.get("description", ""),
                    line_number=f.get("line_number"),
                    suggestion=f.get("suggestion", "")
                ))

            return AgentReport(
                agent_name="Code Quality & Best Practices Agent",
                findings=findings,
                summary=data.get("summary", "Quality review finished."),
                status="success"
            )
        except Exception as e:
            return AgentReport(
                agent_name="Code Quality & Best Practices Agent",
                findings=[],
                summary="Failed to run quality review.",
                status="failed",
                error_message=str(e)
            )
