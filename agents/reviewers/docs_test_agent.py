"""
agents/reviewers/docs_test_agent.py — Documentation & Test Coverage Agent
"""

import json
from langchain_core.messages import SystemMessage, HumanMessage
from agents.utils.llm_factory import build_llm
from agents.tools.docstring_coverage_tool import docstring_coverage_tool
from agents.tools.test_presence_tool import test_presence_tool
from models.schemas import AgentReport, Finding

SYSTEM_PROMPT = """You are a Documentation & Test Coverage Agent. Your job is to check public functions/classes for docstrings, and check if appropriate tests exist.
You will be provided with code and raw static-analysis tool results.
Your output must contain suggestions on what needs documentation or tests, including test stub examples.
Provide your final output in a valid JSON format conforming to the AgentReport schema:
{
  "agent_name": "Documentation & Test Coverage Agent",
  "findings": [
    {
      "category": "docs_tests",
      "severity": "critical" | "high" | "medium" | "low" | "info",
      "title": "Finding title",
      "description": "Why documentation or test is missing/inadequate",
      "line_number": 12,
      "suggestion": "Example docstring or test stub code"
    }
  ],
  "summary": "1-3 sentences summary of docs and test coverage health",
  "status": "success"
}
Output ONLY raw JSON. No markdown backticks, no comments, no extra text.
"""

class DocsTestAgent:
    def __init__(self, provider: str = "groq", model: str = "llama-3.3-70b-versatile", temperature: float = 0.0):
        self.llm = build_llm(provider, model, temperature)

    def run(self, code: str, filename: str = "") -> AgentReport:
        try:
            docs_res = docstring_coverage_tool.invoke(code)
            test_res = test_presence_tool.invoke(filename)

            prompt = f"Source Code:\n{code}\n\nDocstring Coverage:\n{docs_res}\n\nTest Presence:\n{test_res}\n"
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
                    category="docs_tests",
                    severity=f.get("severity", "medium"),
                    title=f.get("title", ""),
                    description=f.get("description", ""),
                    line_number=f.get("line_number"),
                    suggestion=f.get("suggestion", "")
                ))

            return AgentReport(
                agent_name="Documentation & Test Coverage Agent",
                findings=findings,
                summary=data.get("summary", "Documentation and test presence review finished."),
                status="success"
            )
        except Exception as e:
            return AgentReport(
                agent_name="Documentation & Test Coverage Agent",
                findings=[],
                summary="Failed to run documentation and test presence review.",
                status="failed",
                error_message=str(e)
            )
