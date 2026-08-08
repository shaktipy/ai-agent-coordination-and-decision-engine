"""
agents/orchestrator.py — Master Orchestrator with LangGraph conditional routing
"""

import operator
from typing import Annotated, TypedDict, List, Dict, Any, Literal
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END

from agents.utils.llm_factory import build_llm
from agents.reviewers.security_agent import SecurityAgent
from agents.reviewers.performance_agent import PerformanceAgent
from agents.reviewers.quality_agent import QualityAgent
from agents.reviewers.docs_test_agent import DocsTestAgent
from models.schemas import AgentReport

ROUTER_SYSTEM_PROMPT = """You are an intent classification router for an enterprise workflow platform.
Classify the user's query into EXACTLY ONE of the following categories:
- SECURITY: If the user specifically mentions security, keys, credentials, or vulnerabilities.
- PERFORMANCE: If the user specifically mentions speed, efficiency, performance, complexity, loops, or scale.
- QUALITY: If the user specifically mentions PEP8, styling, conventions, best practices, variables, naming, or quality.
- DOCS: If the user specifically mentions docstrings, comments, readme, tests, or documentation.
- FULL: If the user does not mention a specific area (e.g. general "review my code" or "analyze this").

Output ONLY the category name: SECURITY, PERFORMANCE, QUALITY, DOCS, or FULL.
Do not write anything else.
"""

class AgentState(TypedDict):
    code: str
    filename: str
    query: str
    short_term_context: str
    long_term_context: str
    routed_focus: List[str]   # list of node names chosen by the router
    reports: Annotated[List[AgentReport], operator.add]

class MasterOrchestrator:
    def __init__(self, provider: str = "groq", model: str = "llama-3.3-70b-versatile"):
        self.router_llm = build_llm(provider, "llama-3.1-8b-instant", 0.0)
        self.security_agent = SecurityAgent(provider, model)
        self.performance_agent = PerformanceAgent(provider, model)
        self.quality_agent = QualityAgent(provider, model)
        self.docs_agent = DocsTestAgent(provider, model)

        # Build LangGraph workflow
        workflow = StateGraph(AgentState)

        # Add Nodes
        workflow.add_node("route_node", self._route_node)
        workflow.add_node("security_node", self._security_node)
        workflow.add_node("performance_node", self._performance_node)
        workflow.add_node("quality_node", self._quality_node)
        workflow.add_node("docs_node", self._docs_node)

        # Set Entry Point
        workflow.set_entry_point("route_node")

        # Define conditional routing
        workflow.add_conditional_edges(
            "route_node",
            self._decide_next_nodes,
            {
                "security_node": "security_node",
                "performance_node": "performance_node",
                "quality_node": "quality_node",
                "docs_node": "docs_node"
            }
        )

        # Connect Agent Nodes to END
        workflow.add_edge("security_node", END)
        workflow.add_edge("performance_node", END)
        workflow.add_edge("quality_node", END)
        workflow.add_edge("docs_node", END)

        self.graph = workflow.compile()

    def route_request(self, user_prompt: str) -> str:
        targets = self._route_node({"query": user_prompt})["routed_focus"]
        if len(targets) == 4:
            return "FULL"
        elif len(targets) == 1:
            node = targets[0]
            if node == "security_node": return "SECURITY"
            if node == "performance_node": return "PERFORMANCE"
            if node == "quality_node": return "QUALITY"
            if node == "docs_node": return "DOCS"
        return "FULL"

    def _route_node(self, state: AgentState) -> Dict[str, Any]:
        query = state.get("query") or ""
        prompt_lower = query.lower()

        targets = []
        if any(w in prompt_lower for w in ["security", "credential", "password", "api key", "token", "secret", "vulnerability"]):
            targets.append("security_node")
        if any(w in prompt_lower for w in ["speed", "efficiency", "performance", "complexity", "nested loop", "radon"]):
            targets.append("performance_node")
        if any(w in prompt_lower for w in ["pep8", "style", "convention", "naming", "quality", "pylint"]):
            targets.append("quality_node")
        if any(w in prompt_lower for w in ["docstring", "comment", "readme", "test", "coverage", "documentation", "doc", "docs"]):
            targets.append("docs_node")

        # If no keywords matched, fall back to LLM router
        if not targets:
            messages = [
                SystemMessage(content=ROUTER_SYSTEM_PROMPT),
                HumanMessage(content=f"Short-Term History:\n{state.get('short_term_context') or ''}\n\nLong-Term Memory:\n{state.get('long_term_context') or ''}\n\nUser Query: {query}")
            ]
            try:
                res = self.router_llm.invoke(messages)
                choice = res.content.strip().upper()
                if "SECURITY" in choice:
                    targets.append("security_node")
                if "PERFORMANCE" in choice:
                    targets.append("performance_node")
                if "QUALITY" in choice:
                    targets.append("quality_node")
                if "DOCS" in choice:
                    targets.append("docs_node")
            except Exception:
                pass

        # Default to all agents if still empty (e.g. general "review my code" or FULL)
        if not targets:
            targets = ["security_node", "performance_node", "quality_node", "docs_node"]

        return {"routed_focus": targets}

    def _decide_next_nodes(self, state: AgentState) -> List[str]:
        return state.get("routed_focus") or ["security_node", "performance_node", "quality_node", "docs_node"]

    def _security_node(self, state: AgentState) -> Dict[str, Any]:
        context = f"Short-Term Context:\n{state.get('short_term_context') or ''}\n\nLong-Term Context:\n{state.get('long_term_context') or ''}"
        rep = self.security_agent.run(state["code"], state["filename"], context)
        return {"reports": [rep]}

    def _performance_node(self, state: AgentState) -> Dict[str, Any]:
        context = f"Short-Term Context:\n{state.get('short_term_context') or ''}\n\nLong-Term Context:\n{state.get('long_term_context') or ''}"
        rep = self.performance_agent.run(state["code"], state["filename"], context)
        return {"reports": [rep]}

    def _quality_node(self, state: AgentState) -> Dict[str, Any]:
        context = f"Short-Term Context:\n{state.get('short_term_context') or ''}\n\nLong-Term Context:\n{state.get('long_term_context') or ''}"
        rep = self.quality_agent.run(state["code"], state["filename"], context)
        return {"reports": [rep]}

    def _docs_node(self, state: AgentState) -> Dict[str, Any]:
        context = f"Short-Term Context:\n{state.get('short_term_context') or ''}\n\nLong-Term Context:\n{state.get('long_term_context') or ''}"
        rep = self.docs_agent.run(state["code"], state["filename"], context)
        return {"reports": [rep]}

    def run_review(
        self,
        code: str,
        filename: str = "",
        query: str = "",
        short_term_context: str = "",
        long_term_context: str = ""
    ) -> List[AgentReport]:
        initial_state: AgentState = {
            "code": code,
            "filename": filename,
            "query": query,
            "short_term_context": short_term_context,
            "long_term_context": long_term_context,
            "routed_focus": [],
            "reports": []
        }
        res = self.graph.invoke(initial_state)
        return res.get("reports", [])
