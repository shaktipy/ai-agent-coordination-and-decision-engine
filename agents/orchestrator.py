"""
agents/orchestrator.py — Master Orchestrator (Decision Automation System)
"""

import sys
from typing import Literal
from langchain_core.messages import SystemMessage, HumanMessage
from agents.utils.llm_factory import build_llm
from agents.reviewers.security_agent import SecurityAgent
from agents.reviewers.performance_agent import PerformanceAgent
from agents.reviewers.quality_agent import QualityAgent
from agents.reviewers.docs_test_agent import DocsTestAgent
from models.schemas import AgentReport

ROUTER_SYSTEM_PROMPT = """You are an intent classification router for an enterprise workflow platform.
Classify the user's intent into EXACTLY ONE of the following categories:
- SECURITY: If the user specifically mentions security, keys, credentials, or vulnerabilities.
- PERFORMANCE: If the user specifically mentions speed, efficiency, performance, complexity, loops, or scale.
- QUALITY: If the user specifically mentions PEP8, styling, conventions, best practices, variables, naming, or quality.
- DOCS: If the user specifically mentions docstrings, comments, readme, tests, or documentation.
- FULL: If the user does not mention a specific area (e.g. general "review my code" or "analyze this").

Output ONLY the category name: SECURITY, PERFORMANCE, QUALITY, DOCS, or FULL.
Do not write anything else.
"""

class MasterOrchestrator:
    def __init__(self, provider: str = "groq", model: str = "llama-3.3-70b-versatile"):
        self.router_llm = build_llm(provider, "llama-3.1-8b-instant", 0.0)
        self.security_agent = SecurityAgent(provider, model)
        self.performance_agent = PerformanceAgent(provider, model)
        self.quality_agent = QualityAgent(provider, model)
        self.docs_agent = DocsTestAgent(provider, model)

    def route_request(self, user_prompt: str) -> str:
        prompt_lower = user_prompt.lower()
        if any(w in prompt_lower for w in ["security", "credential", "password", "api key", "token", "secret", "vulnerability"]):
            return "SECURITY"
        if any(w in prompt_lower for w in ["speed", "efficiency", "performance", "complexity", "nested loop", "radon"]):
            return "PERFORMANCE"
        if any(w in prompt_lower for w in ["pep8", "style", "convention", "naming", "quality", "pylint"]):
            return "QUALITY"
        if any(w in prompt_lower for w in ["docstring", "comment", "readme", "test", "coverage"]):
            return "DOCS"

        messages = [
            SystemMessage(content=ROUTER_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt)
        ]
        res = self.router_llm.invoke(messages)
        choice = res.content.strip().upper()
        if choice in ("SECURITY", "PERFORMANCE", "QUALITY", "DOCS", "FULL"):
            return choice
        return "FULL"

    def run_review(self, code: str, filename: str = "", focus: str = "FULL") -> list[AgentReport]:
        reports = []
        if focus == "FULL":
            reports.append(self.security_agent.run(code, filename))
            reports.append(self.performance_agent.run(code, filename))
            reports.append(self.quality_agent.run(code, filename))
            reports.append(self.docs_agent.run(code, filename))
        elif focus == "SECURITY":
            reports.append(self.security_agent.run(code, filename))
        elif focus == "PERFORMANCE":
            reports.append(self.performance_agent.run(code, filename))
        elif focus == "QUALITY":
            reports.append(self.quality_agent.run(code, filename))
        elif focus == "DOCS":
            reports.append(self.docs_agent.run(code, filename))
        return reports
