"""
agents/reviewers/performance_agent.py — Performance & Complexity Agent
"""

import json
from langchain_core.messages import SystemMessage, HumanMessage
from agents.utils.llm_factory import build_llm
from agents.tools.radon_complexity_tool import cyclomatic_complexity_tool, maintainability_index_tool
from agents.tools.nested_loop_tool import nested_loop_detector_tool
from models.schemas import AgentReport, Finding

SYSTEM_PROMPT = """You are a Performance & Complexity Agent. Your job is to analyze code for cyclomatic complexity, deeply nested loops, O(n²) or worse operations, and other performance inefficiencies.
You will be provided with code and raw static-analysis tool results.
Your output must contain an explanation of each issue, why it is problematic, and a suggestion for refactoring.
Provide your final output in a valid JSON format conforming to the AgentReport schema:
{
  "agent_name": "Performance & Complexity Agent",
  "findings": [
    {
      "category": "performance",
      "severity": "critical" | "high" | "medium" | "low" | "info",
      "title": "Finding title",
      "description": "Why this is a performance issue",
      "line_number": 12,
      "suggestion": "How to refactor/optimize"
    }
  ],
  "summary": "1-3 sentences summary of performance and complexity health",
  "status": "success"
}
Output ONLY raw JSON. No markdown backticks, no comments, no extra text.
"""

class PerformanceAgent:
    def __init__(self, provider: str = "groq", model: str = "llama-3.3-70b-versatile", temperature: float = 0.0):
        self.llm = build_llm(provider, model, temperature)

    def run(self, code: str, filename: str = "", context: str = "") -> AgentReport:
        try:
            cc_res = cyclomatic_complexity_tool.invoke(code)
            mi_res = maintainability_index_tool.invoke(code)
            loops_res = nested_loop_detector_tool.invoke(code)

            prompt = ""
            if context:
                prompt += f"Memory & Context:\n{context}\n\n"
            prompt += f"Source Code:\n{code}\n\nCyclomatic Complexity:\n{cc_res}\n\nMaintainability Index:\n{mi_res}\n\nNested Loops:\n{loops_res}\n"
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
                    category="performance",
                    severity=f.get("severity", "medium"),
                    title=f.get("title", ""),
                    description=f.get("description", ""),
                    line_number=f.get("line_number"),
                    suggestion=f.get("suggestion", "")
                ))

            return AgentReport(
                agent_name="Performance & Complexity Agent",
                findings=findings,
                summary=data.get("summary", "Performance review finished."),
                status="success"
            )
        except Exception as e:
            return AgentReport(
                agent_name="Performance & Complexity Agent",
                findings=[],
                summary="Failed to run performance review.",
                status="failed",
                error_message=str(e)
            )
