"""
Tool Agent — AI Agent Coordination & Decision Engine
====================================================
Agent 2 of the Multi-Agent System (Milestone 2).

This is a LangChain Tool-Calling Agent that can intelligently:
    1. Understand what the user is asking
    2. Decide WHICH tool(s) to use (via LLM tool-calling)
    3. Invoke those tools to gather information
    4. Reason about the tool results
    5. Provide a final, grounded answer

Built using the modern LangChain 1.x `create_agent` API (LangGraph-based)
which replaces the legacy `AgentExecutor` / `create_react_agent` pattern.

Supported Tools (via ToolOrchestrator):
    ├── datetime_tool        → Current date/time
    ├── date_calculator_tool → Date arithmetic
    ├── calculator_tool      → Math expressions
    ├── file_read_tool       → Read files
    ├── file_write_tool      → Write files
    ├── file_list_tool       → List directories
    ├── web_search_tool      → DuckDuckGo web search
    ├── api_get_tool         → HTTP GET requests
    └── api_post_tool        → HTTP POST requests

Architecture (Tool-Calling Loop):
    User Input
         ↓
    LLM decides which tool(s) to call
         ↓
    Tools are invoked
         ↓
    Results returned to LLM
         ↓
    LLM generates final answer

Author: Infosys Springboard Virtual Internship 7.0
Project: AI Agent Coordination & Decision Engine
"""

import os
from dotenv import load_dotenv

# ── LangChain modern imports ───────────────────────────────────────────────────
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# ── Internal imports ───────────────────────────────────────────────────────────
from agents.tool_orchestrator import ToolOrchestrator

load_dotenv()

# ── API Keys ───────────────────────────────────────────────────────────────────
GROQ_API_KEY   = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ── System Prompt ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an intelligent AI Tool Agent, part of the
AI Agent Coordination & Decision Engine.

Your role is to help users by intelligently selecting and using the right tool(s)
to answer their questions and complete their tasks accurately.

Guidelines:
- Always think carefully about WHICH tool is best suited for the task.
- Use calculator_tool for math, datetime_tool for time questions, web_search_tool for current info.
- Use file_read_tool / file_list_tool for file operations.
- Use api_get_tool for fetching data from REST APIs.
- If a task needs multiple tools, chain them — use one, analyze the result, then use another.
- Be concise in your final answer; the user cares about results, not your reasoning steps.
- If no tool is needed (general knowledge question), answer directly from your knowledge."""


def _build_llm(provider: str, model: str, temperature: float):
    """
    Factory — returns LangChain LLM based on provider.

    Args:
        provider   : "groq" or "gemini"
        model      : model name string
        temperature: 0.0 to 1.0

    Returns:
        LangChain chat model instance
    """
    if provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=model,
            groq_api_key=GROQ_API_KEY,
            temperature=temperature,
        )
    elif provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=model,
            google_api_key=GEMINI_API_KEY,
            temperature=temperature,
        )
    else:
        raise ValueError(f"Unknown provider '{provider}'. Use 'groq' or 'gemini'.")


class ToolAgent:
    """
    LangChain Tool-Calling Agent with access to the full enterprise tool suite.

    Uses the modern LangChain 1.x `create_agent` API (LangGraph-based).
    The agent autonomously decides which tools to use based on the user's
    input via LLM tool-calling (function calling).

    Attributes:
        provider        : LLM provider ("groq" or "gemini")
        orchestrator    : ToolOrchestrator managing all registered tools
        llm             : LangChain LLM instance
        agent           : Compiled LangGraph agent
        session_history : List of session query records
    """

    def __init__(
        self,
        provider: str = "groq",
        model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.0,
        verbose: bool = False,
    ):
        """
        Initialize the Tool Agent.

        Args:
            provider   : "groq" (default) or "gemini"
            model      : Model name. Groq supports tool-calling on llama-3.3-70b-versatile
            temperature: 0.0 = deterministic. Best for tool use.
            verbose    : If True, enables debug logging on the agent graph
        """
        self.provider = provider
        self.session_history: list = []

        # ── Step 1: Initialize Tool Orchestrator ───────────────────────────────
        self.orchestrator = ToolOrchestrator()

        # ── Step 2: Build LLM ──────────────────────────────────────────────────
        self.llm = _build_llm(provider, model, temperature)

        # ── Step 3: Create modern LangChain agent ─────────────────────────────
        # create_agent uses LangGraph under the hood:
        #   - LLM node: calls the model with messages
        #   - Tools node: executes tool calls from LLM response
        #   - Loop: repeats until no more tool calls
        self.agent = create_agent(
            model=self.llm,
            tools=self.orchestrator.tools,
            system_prompt=SYSTEM_PROMPT,
            debug=verbose,
        )

        print(f"\n[ToolAgent Init] ✅ Tool Agent ready (Modern LangChain create_agent)")
        print(f"[ToolAgent Init] Provider: {provider.upper()} | Model: {model} | Temp: {temperature}")
        print(f"[ToolAgent Init] Tools available: {len(self.orchestrator.tools)}")

    def run(self, user_input: str) -> str:
        """
        Run the tool-calling agent on the given user input.

        The agent will:
        1. Send the message to the LLM
        2. LLM decides which tools to call (if any)
        3. Tools are executed automatically
        4. Results are fed back to the LLM
        5. Final answer is returned

        Args:
            user_input: The user's question or task

        Returns:
            str: The agent's final answer
        """
        if not user_input.strip():
            return "Error: Please provide a question or task."

        print(f"\n[ToolAgent] 🚀 Running: {user_input[:70]}{'...' if len(user_input) > 70 else ''}")

        try:
            # Invoke the agent with a messages list
            result = self.agent.invoke({
                "messages": [HumanMessage(content=user_input)]
            })

            # Extract final answer from the last AI message
            messages = result.get("messages", [])
            final_answer = "No answer generated."

            # Find the last AIMessage that is not a tool call
            for msg in reversed(messages):
                if isinstance(msg, AIMessage):
                    # Check it's a final answer (no pending tool calls)
                    if not getattr(msg, "tool_calls", None):
                        final_answer = msg.content
                        break
                    # If it has content but also tool calls, use content if non-empty
                    elif msg.content:
                        final_answer = msg.content
                        break

            # Extract tools used from messages
            tools_used = []
            for msg in messages:
                if isinstance(msg, AIMessage) and getattr(msg, "tool_calls", None):
                    for tc in msg.tool_calls:
                        if isinstance(tc, dict):
                            tools_used.append(tc.get("name", "unknown"))
                        elif hasattr(tc, "name"):
                            tools_used.append(tc.name)

            # Deduplicate while preserving order
            seen = set()
            tools_used_unique = []
            for t in tools_used:
                if t not in seen:
                    seen.add(t)
                    tools_used_unique.append(t)

            # Log to session history
            self.session_history.append({
                "input": user_input,
                "output": final_answer,
                "tools_used": tools_used_unique,
            })

            if tools_used_unique:
                print(f"[ToolAgent] Tools used: {', '.join(tools_used_unique)}")

            return final_answer

        except Exception as e:
            error_msg = (
                f"[ToolAgent Error] An error occurred while processing your request:\n"
                f"{type(e).__name__}: {str(e)}\n"
                f"Please try rephrasing your query."
            )
            self.session_history.append({
                "input": user_input,
                "output": error_msg,
                "tools_used": [],
            })
            return error_msg

    def get_session_summary(self) -> str:
        """
        Return a readable summary of this session's queries and tools used.

        Returns:
            str: Formatted session summary
        """
        if not self.session_history:
            return "No queries processed yet in this session."

        lines = [f"📊 ToolAgent Session Summary ({len(self.session_history)} query/queries)", "─" * 60]
        for i, entry in enumerate(self.session_history, 1):
            tools_str = ", ".join(entry["tools_used"]) if entry["tools_used"] else "None (direct answer)"
            preview = entry["input"][:70] + ("..." if len(entry["input"]) > 70 else "")
            answer_preview = str(entry["output"])[:100]
            lines.append(
                f"\n{i}. Query  : {preview}\n"
                f"   Tools  : {tools_str}\n"
                f"   Answer : {answer_preview}..."
            )
        lines.append("─" * 60)
        return "\n".join(lines)

    def list_tools(self) -> str:
        """Return a formatted list of all available tools."""
        return self.orchestrator.list_tools()

    def get_tool_log(self) -> str:
        """Return the orchestrator's invocation log."""
        return self.orchestrator.get_log_summary()


# ── Standalone test ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 65)
    print("  TOOL AGENT — Standalone Test")
    print("  Provider: Groq | Modern create_agent with Enterprise Tools")
    print("=" * 65)

    if not GROQ_API_KEY:
        print("\n[ERROR] Please set GROQ_API_KEY in .env file!")
        exit(1)

    agent = ToolAgent(provider="groq", verbose=False)

    print("\n--- Test 1: DateTime Tool ---")
    print(agent.run("What is today's date and what day of the week is it?"))

    print("\n--- Test 2: Calculator Tool ---")
    print(agent.run("Calculate 15 * 24 + 100"))

    print("\n--- Test 3: Web Search ---")
    print(agent.run("Search for the latest news about LangChain AI framework"))

    print("\n--- Test 4: File List ---")
    print(agent.run("List all files in the agents directory of this project"))

    print("\n--- Session Summary ---")
    print(agent.get_session_summary())
