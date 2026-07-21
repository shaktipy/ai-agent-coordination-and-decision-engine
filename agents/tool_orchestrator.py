"""
Tool Orchestrator — AI Agent Coordination & Decision Engine
===========================================================
Milestone 2: Central Tool Manager

The ToolOrchestrator is the backbone of Milestone 2's tool system.
It provides:
    - Central registry of all available tools
    - Tool lookup by name
    - Direct tool invocation with logging
    - Exception recovery — graceful error messages if a tool fails
    - Tool invocation history with timestamps

This class is used INTERNALLY by the ToolAgent.
You can also use it standalone to test or invoke specific tools directly.

Usage:
    orchestrator = ToolOrchestrator()
    result = orchestrator.invoke("calculator_tool", "15 * 24 + 100")
    print(result)

Author: Infosys Springboard Virtual Internship 7.0
"""

import time
from datetime import datetime
from typing import Optional
from agents.tools import ALL_TOOLS


class ToolOrchestrator:
    """
    Central manager for all enterprise tools.

    Registers all available tools, provides lookup by name,
    handles direct invocation with full error recovery and logging.

    Attributes:
        _tools_map     : Dict mapping tool name → tool function
        invocation_log : List of all tool invocations with timestamps
    """

    def __init__(self):
        """
        Initialize the orchestrator and register all tools.
        """
        # Build name → tool mapping for O(1) lookup
        self._tools_map: dict = {tool.name: tool for tool in ALL_TOOLS}
        self.invocation_log: list = []

        print(f"[ToolOrchestrator] Initialized with {len(self._tools_map)} tools:")
        for name in self._tools_map:
            print(f"  ✅ {name}")

    # ── Public Properties ──────────────────────────────────────────────────────

    @property
    def tools(self) -> list:
        """Return all registered tools as a list (for AgentExecutor)."""
        return ALL_TOOLS

    @property
    def tool_names(self) -> list[str]:
        """Return list of all registered tool names."""
        return list(self._tools_map.keys())

    # ── Tool Lookup ────────────────────────────────────────────────────────────

    def get_tool(self, name: str):
        """
        Retrieve a tool by name.

        Args:
            name: The tool's name (e.g., "calculator_tool", "web_search_tool")

        Returns:
            The tool function or None if not found.
        """
        return self._tools_map.get(name)

    def has_tool(self, name: str) -> bool:
        """Check if a tool with the given name is registered."""
        return name in self._tools_map

    # ── Direct Tool Invocation ─────────────────────────────────────────────────

    def invoke(self, tool_name: str, tool_input) -> str:
        """
        Directly invoke a tool by name with the given input.

        Handles all exceptions gracefully — never raises, always returns a string.
        Logs every invocation with timestamp and duration.

        Args:
            tool_name  : Name of the tool to invoke (e.g., "calculator_tool")
            tool_input : Input to pass to the tool (string or dict)

        Returns:
            str: Tool output or an error message.
        """
        # Check if tool exists
        if not self.has_tool(tool_name):
            error_msg = (
                f"[ToolOrchestrator] Unknown tool: '{tool_name}'\n"
                f"Available tools: {', '.join(self.tool_names)}"
            )
            self._log_invocation(tool_name, tool_input, error_msg, success=False)
            return error_msg

        tool = self._tools_map[tool_name]
        start_time = time.time()

        try:
            # Invoke the tool
            result = tool.invoke(tool_input)
            duration_ms = (time.time() - start_time) * 1000

            self._log_invocation(tool_name, tool_input, result, success=True, duration_ms=duration_ms)
            return result

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            error_msg = (
                f"[ToolOrchestrator] Tool '{tool_name}' raised an exception:\n"
                f"Error: {type(e).__name__}: {str(e)}\n"
                f"Input was: {tool_input}"
            )
            self._log_invocation(tool_name, tool_input, error_msg, success=False, duration_ms=duration_ms)
            return error_msg

    # ── Invocation Logging ─────────────────────────────────────────────────────

    def _log_invocation(
        self,
        tool_name: str,
        tool_input,
        result: str,
        success: bool,
        duration_ms: float = 0.0,
    ):
        """
        Record a tool invocation in the internal log.

        Args:
            tool_name  : Name of the invoked tool
            tool_input : Input passed to the tool
            result     : Output from the tool
            success    : Whether the invocation succeeded
            duration_ms: Time taken in milliseconds
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "input": str(tool_input)[:200],      # truncate for log
            "output_preview": str(result)[:200],  # truncate for log
            "success": success,
            "duration_ms": round(duration_ms, 2),
        }
        self.invocation_log.append(entry)

        status = "✅" if success else "❌"
        print(
            f"[ToolOrchestrator] {status} {tool_name} "
            f"({duration_ms:.0f}ms)"
        )

    def get_log_summary(self) -> str:
        """
        Return a human-readable summary of all tool invocations this session.

        Returns:
            str: Formatted invocation log.
        """
        if not self.invocation_log:
            return "No tool invocations recorded yet."

        lines = [f"📋 Tool Invocation Log ({len(self.invocation_log)} entries)", "─" * 60]
        for i, entry in enumerate(self.invocation_log, 1):
            status = "✅" if entry["success"] else "❌"
            lines.append(
                f"{i:2}. {status} [{entry['timestamp'][11:19]}] "  # show HH:MM:SS
                f"{entry['tool_name']} "
                f"({entry['duration_ms']}ms)\n"
                f"    Input  : {entry['input'][:80]}\n"
                f"    Output : {entry['output_preview'][:80]}"
            )
        lines.append("─" * 60)

        successes = sum(1 for e in self.invocation_log if e["success"])
        failures  = len(self.invocation_log) - successes
        lines.append(f"Summary: {successes} succeeded, {failures} failed")

        return "\n".join(lines)

    def list_tools(self) -> str:
        """
        Return a formatted list of all available tools with descriptions.

        Returns:
            str: Tool names and their descriptions.
        """
        lines = ["🛠️  Available Enterprise Tools", "─" * 60]
        for i, tool in enumerate(ALL_TOOLS, 1):
            # First line of the docstring = short description
            desc = (tool.description or "No description").split("\n")[0].strip()
            lines.append(f"  {i:2}. {tool.name}\n      {desc}")
        lines.append("─" * 60)
        return "\n".join(lines)
