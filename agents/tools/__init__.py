"""
Tools Package — AI Agent Coordination & Decision Engine
=======================================================
Milestone 2: Custom Enterprise Tools

This package contains all LangChain-compatible tool definitions.
Each tool is decorated with @tool and can be passed directly to
a LangChain ReAct AgentExecutor.

Available Tools:
    - datetime_tool      : Get current date/time and do date calculations
    - calculator_tool    : Evaluate mathematical expressions safely
    - file_manager_tool  : Read, write, and list files on the filesystem
    - web_search_tool    : Search the web using DuckDuckGo (free, no API key)
    - api_connector_tool : Make GET/POST requests to any REST API endpoint

Author: Infosys Springboard Virtual Internship 7.0
Project: AI Agent Coordination & Decision Engine
"""

from agents.tools.datetime_tool import datetime_tool, date_calculator_tool
from agents.tools.calculator_tool import calculator_tool
from agents.tools.file_manager_tool import (
    file_read_tool,
    file_write_tool,
    file_list_tool,
)
from agents.tools.web_search_tool import web_search_tool
from agents.tools.api_connector_tool import api_get_tool, api_post_tool

# ── All tools in a single list — pass this to AgentExecutor ───────────────────
ALL_TOOLS = [
    datetime_tool,
    date_calculator_tool,
    calculator_tool,
    file_read_tool,
    file_write_tool,
    file_list_tool,
    web_search_tool,
    api_get_tool,
    api_post_tool,
]

__all__ = [
    "datetime_tool",
    "date_calculator_tool",
    "calculator_tool",
    "file_read_tool",
    "file_write_tool",
    "file_list_tool",
    "web_search_tool",
    "api_get_tool",
    "api_post_tool",
    "ALL_TOOLS",
]
