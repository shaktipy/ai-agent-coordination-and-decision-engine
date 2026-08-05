"""
agents/reviewers/security_agent.py — Security Review Agent
"""

import json
from langchain_core.messages import SystemMessage, HumanMessage
from agents.utils.llm_factory import build_llm
from agents.tools.bandit_scan_tool import bandit_scan_tool
from agents.tools.secret_pattern_tool import secret_pattern_scan_tool
from agents.tools.unsafe_function_tool import unsafe_function_tool
from models.schemas import AgentReport, Finding

SYSTEM_PROMPT = """You are a Security Review Agent. Your job is to analyze code for potential vulnerabilities, hardcoded secrets, and unsafe function usage.
You will be provided with code and raw static-analysis tool results.
Your output must contain an explanation of each issue, why it is risky, and a suggestion for a fix.
Provide your final output in a valid JSON format conforming to the AgentReport schema:
{
  "agent_name": "Security Review Agent",
  "findings": [
    {
      "category": "security",
      "severity": "critical" | "high" | "medium" | "low" | "info",
      "title": "Finding title",
      "description": "Why this is a risk",
      "line_number": 12,
      "suggestion": "How to fix it"
    }
  ],
  "summary": "1-3 sentences summary of security health",
  "status": "success"
}
Output ONLY raw JSON. No markdown backticks, no comments, no extra text.
"""

class SecurityAgent:
    def __init__(self, provider: str = "groq", model: str = "llama-3.3-70b-versatile", temperature: float = 0.0):
        self.llm = build_llm(provider, model, temperature)

    def run(self, code: str, filename: str = "") -> AgentReport:
        try:
            bandit_res = bandit_scan_tool.invoke(code)
            secrets_res = secret_pattern_scan_tool.invoke(code)
            unsafe_res = unsafe_function_tool.invoke(code)

            prompt = f"Source Code:\n{code}\n\nBandit Results:\n{bandit_res}\n\nSecrets Scan:\n{secrets_res}\n\nUnsafe Functions:\n{unsafe_res}\n"
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
                    category="security",
                    severity=f.get("severity", "medium"),
                    title=f.get("title", ""),
                    description=f.get("description", ""),
                    line_number=f.get("line_number"),
                    suggestion=f.get("suggestion", "")
                ))

            return AgentReport(
                agent_name="Security Review Agent",
                findings=findings,
                summary=data.get("summary", "Security review finished."),
                status="success"
            )
        except Exception as e:
            return AgentReport(
                agent_name="Security Review Agent",
                findings=[],
                summary="Failed to run security review.",
                status="failed",
                error_message=str(e)
            )
