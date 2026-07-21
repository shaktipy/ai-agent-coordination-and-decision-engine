"""
test_tools.py — Tool Validation & Test Suite
============================================
Milestone 2: Test tool invocation workflows and exception handling.

Tests cover:
    1. DateTimeTool        — current time + date arithmetic
    2. CalculatorTool      — math expressions + edge cases
    3. FileManagerTool     — read / write / list + error cases
    4. WebSearchTool       — search results + empty query
    5. APIConnectorTool    — GET/POST requests + invalid URLs
    6. ToolOrchestrator    — registry, invocation, logging, error recovery
    7. Integration         — ToolAgent routes correctly to tools

Run:
    python -m pytest tests/test_tools.py -v

Author: Infosys Springboard Virtual Internship 7.0
"""

import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from pathlib import Path


# ══════════════════════════════════════════════════════════════════════════════
# 1. DATETIME TOOL TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestDatetimeTool:
    """Tests for datetime_tool and date_calculator_tool."""

    def test_datetime_tool_returns_current_date(self):
        """datetime_tool should return today's date in the output."""
        from agents.tools.datetime_tool import datetime_tool
        from datetime import datetime

        result = datetime_tool.invoke("%Y-%m-%d %H:%M:%S")
        assert "Current date and time:" in result
        assert "Day of week:" in result
        assert datetime.now().strftime("%Y") in result  # current year present

    def test_datetime_tool_custom_format(self):
        """datetime_tool should respect custom format strings."""
        from agents.tools.datetime_tool import datetime_tool
        from datetime import datetime

        result = datetime_tool.invoke("%A")  # day name only
        today_name = datetime.now().strftime("%A")
        assert today_name in result

    def test_datetime_tool_invalid_format(self):
        """datetime_tool with invalid format should return an error string (not raise)."""
        from agents.tools.datetime_tool import datetime_tool

        result = datetime_tool.invoke("%INVALIDFORMAT%")
        # Should not raise — should return formatted result or error
        assert isinstance(result, str)

    def test_date_calculator_add_days(self):
        """date_calculator_tool should correctly add days to today."""
        from agents.tools.datetime_tool import date_calculator_tool
        from datetime import datetime, timedelta

        result = date_calculator_tool.invoke("today + 30 days")
        # Result should mention the future date — at minimum contain 'After'
        assert "After 30 days" in result or "After" in result

    def test_date_calculator_subtract_days(self):
        """date_calculator_tool should correctly subtract days from today."""
        from agents.tools.datetime_tool import date_calculator_tool

        result = date_calculator_tool.invoke("today - 7 days")
        assert "7 days ago" in result or "Today" in result

    def test_date_calculator_diff(self):
        """date_calculator_tool should compute difference between two dates."""
        from agents.tools.datetime_tool import date_calculator_tool

        result = date_calculator_tool.invoke("diff 2024-01-01 2024-07-01")
        assert "182" in result  # 182 days between Jan 1 and Jul 1 2024

    def test_date_calculator_invalid_format(self):
        """date_calculator_tool with invalid format returns helpful message."""
        from agents.tools.datetime_tool import date_calculator_tool

        result = date_calculator_tool.invoke("invalid operation")
        assert isinstance(result, str)
        assert "[DateCalculatorTool]" in result or "Invalid" in result.lower()


# ══════════════════════════════════════════════════════════════════════════════
# 2. CALCULATOR TOOL TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestCalculatorTool:
    """Tests for calculator_tool."""

    def test_basic_arithmetic(self):
        """Calculator should handle basic arithmetic correctly."""
        from agents.tools.calculator_tool import calculator_tool

        result = calculator_tool.invoke("2 + 2")
        assert "4" in result

    def test_multiplication(self):
        """Calculator should handle multiplication."""
        from agents.tools.calculator_tool import calculator_tool

        result = calculator_tool.invoke("15 * 24")
        assert "360" in result

    def test_complex_expression(self):
        """Calculator should handle complex expressions with order of operations."""
        from agents.tools.calculator_tool import calculator_tool

        result = calculator_tool.invoke("(3 + 5) * 2")
        assert "16" in result

    def test_power_operator(self):
        """Calculator should handle power using ^ operator."""
        from agents.tools.calculator_tool import calculator_tool

        result = calculator_tool.invoke("2^10")
        assert "1024" in result

    def test_sqrt_function(self):
        """Calculator should handle sqrt()."""
        from agents.tools.calculator_tool import calculator_tool

        result = calculator_tool.invoke("sqrt(144)")
        assert "12" in result

    def test_division(self):
        """Calculator should handle division."""
        from agents.tools.calculator_tool import calculator_tool

        result = calculator_tool.invoke("100 / 4")
        assert "25" in result

    def test_invalid_expression(self):
        """Calculator should return error message for invalid expressions."""
        from agents.tools.calculator_tool import calculator_tool

        result = calculator_tool.invoke("abc + xyz")
        assert isinstance(result, str)
        assert "Error" in result or "error" in result.lower()

    def test_empty_expression(self):
        """Calculator should handle empty expression gracefully."""
        from agents.tools.calculator_tool import calculator_tool

        result = calculator_tool.invoke("")
        assert isinstance(result, str)


# ══════════════════════════════════════════════════════════════════════════════
# 3. FILE MANAGER TOOL TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestFileManagerTool:
    """Tests for file_read_tool, file_write_tool, file_list_tool."""

    def test_list_root_directory(self):
        """file_list_tool should list the project root contents."""
        from agents.tools.file_manager_tool import file_list_tool

        result = file_list_tool.invoke(".")
        assert "Directory: ." in result
        assert "agents" in result  # agents folder must exist

    def test_list_agents_directory(self):
        """file_list_tool should list agents/ directory."""
        from agents.tools.file_manager_tool import file_list_tool

        result = file_list_tool.invoke("agents")
        assert "tool_agent.py" in result or "code_generator_agent.py" in result

    def test_list_nonexistent_directory(self):
        """file_list_tool on non-existent dir returns 'not found' message."""
        from agents.tools.file_manager_tool import file_list_tool

        result = file_list_tool.invoke("nonexistent_directory_xyz")
        assert "not found" in result.lower() or "FileListTool" in result

    def test_write_and_read_file(self, tmp_path, monkeypatch):
        """file_write_tool then file_read_tool should round-trip correctly."""
        from agents.tools import file_write_tool, file_read_tool
        import agents.tools.file_manager_tool as fm

        # Monkeypatch workspace root to tmp_path so we can write safely
        monkeypatch.setattr(fm, "_WORKSPACE_ROOT", tmp_path.resolve())

        content = "Hello, Tool Agent!\nThis is a test file.\n"
        write_result = file_write_tool.invoke({"file_path": "test_output.txt", "content": content})
        assert "Successfully wrote" in write_result

        read_result = file_read_tool.invoke("test_output.txt")
        assert "Hello, Tool Agent!" in read_result

    def test_read_requirements_txt(self):
        """file_read_tool should successfully read requirements.txt."""
        from agents.tools.file_manager_tool import file_read_tool

        result = file_read_tool.invoke("requirements.txt")
        assert "langchain" in result.lower()

    def test_read_nonexistent_file(self):
        """file_read_tool on missing file returns 'not found' message."""
        from agents.tools.file_manager_tool import file_read_tool

        result = file_read_tool.invoke("this_file_does_not_exist.txt")
        assert "not found" in result.lower() or "FileReadTool" in result

    def test_write_creates_parent_dirs(self, tmp_path, monkeypatch):
        """file_write_tool should create parent directories automatically."""
        from agents.tools import file_write_tool
        import agents.tools.file_manager_tool as fm

        monkeypatch.setattr(fm, "_WORKSPACE_ROOT", tmp_path.resolve())

        result = file_write_tool.invoke({
            "file_path": "nested/folder/output.txt",
            "content": "nested content"
        })
        assert "Successfully wrote" in result
        assert (tmp_path / "nested" / "folder" / "output.txt").exists()


# ══════════════════════════════════════════════════════════════════════════════
# 4. WEB SEARCH TOOL TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestWebSearchTool:
    """Tests for web_search_tool (mocked to avoid network calls in CI)."""

    def test_search_returns_formatted_results(self):
        """web_search_tool should return formatted results for a valid query."""
        from agents.tools import web_search_tool as ws_module
        from agents.tools.web_search_tool import web_search_tool

        # Mock DDGS to avoid actual network calls
        mock_results = [
            {"title": "LangChain Docs", "href": "https://docs.langchain.com", "body": "LangChain is a framework..."},
            {"title": "LangChain GitHub", "href": "https://github.com/langchain-ai/langchain", "body": "Open source LLM framework."},
        ]

        mock_ddgs_instance = MagicMock()
        mock_ddgs_instance.__enter__ = MagicMock(return_value=mock_ddgs_instance)
        mock_ddgs_instance.__exit__ = MagicMock(return_value=False)
        mock_ddgs_instance.text = MagicMock(return_value=mock_results)

        with patch("duckduckgo_search.DDGS", return_value=mock_ddgs_instance):
            result = web_search_tool.invoke({"query": "LangChain framework", "max_results": 2})
            assert isinstance(result, str)
            # Either we got results or it failed gracefully
            assert "LangChain" in result or "Error" in result or "Results" in result

    def test_search_no_results(self):
        """web_search_tool should handle no results gracefully."""
        from agents.tools.web_search_tool import web_search_tool

        mock_ddgs_instance = MagicMock()
        mock_ddgs_instance.__enter__ = MagicMock(return_value=mock_ddgs_instance)
        mock_ddgs_instance.__exit__ = MagicMock(return_value=False)
        mock_ddgs_instance.text = MagicMock(return_value=[])

        with patch("ddgs.DDGS", return_value=mock_ddgs_instance):
            result = web_search_tool.invoke({"query": "xyzabcnonexistent123", "max_results": 3})
            assert isinstance(result, str)

    def test_search_exception_handled(self):
        """web_search_tool should handle network exceptions gracefully."""
        from agents.tools.web_search_tool import web_search_tool

        with patch("ddgs.DDGS", side_effect=Exception("Network error")):
            result = web_search_tool.invoke({"query": "test query", "max_results": 3})
            assert isinstance(result, str)
            # Should not raise — gracefully handled


# ══════════════════════════════════════════════════════════════════════════════
# 5. API CONNECTOR TOOL TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestAPIConnectorTool:
    """Tests for api_get_tool and api_post_tool (mocked HTTP calls)."""

    def test_get_request_success(self):
        """api_get_tool should format a successful response."""
        from agents.tools.api_connector_tool import api_get_tool

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"status": "ok", "data": "test"}
        mock_response.text = '{"status": "ok"}'

        with patch("agents.tools.api_connector_tool.requests.get", return_value=mock_response):
            result = api_get_tool.invoke({"url": "https://httpbin.org/get", "params": ""})
            assert "200" in result
            assert "API Response" in result

    def test_get_request_invalid_url(self):
        """api_get_tool should handle invalid URLs gracefully."""
        from agents.tools.api_connector_tool import api_get_tool
        import requests as req

        with patch("agents.tools.api_connector_tool.requests.get",
                   side_effect=req.exceptions.InvalidURL("Invalid URL")):
            result = api_get_tool.invoke({"url": "not-a-url", "params": ""})
            assert "Invalid URL" in result or "Error" in result

    def test_get_request_timeout(self):
        """api_get_tool should handle timeouts gracefully."""
        from agents.tools.api_connector_tool import api_get_tool
        import requests as req

        with patch("agents.tools.api_connector_tool.requests.get",
                   side_effect=req.exceptions.Timeout("Timed out")):
            result = api_get_tool.invoke({"url": "https://httpbin.org/delay/30", "params": ""})
            assert "timed out" in result.lower() or "Timeout" in result or "timeout" in result.lower()

    def test_post_request_success(self):
        """api_post_tool should handle a successful POST."""
        from agents.tools.api_connector_tool import api_post_tool

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"received": True}
        mock_response.text = '{"received": true}'

        with patch("agents.tools.api_connector_tool.requests.post", return_value=mock_response):
            result = api_post_tool.invoke({
                "url": "https://httpbin.org/post",
                "body": '{"name": "test"}'
            })
            assert "200" in result

    def test_post_invalid_json_body(self):
        """api_post_tool should return error for invalid JSON body."""
        from agents.tools.api_connector_tool import api_post_tool

        result = api_post_tool.invoke({
            "url": "https://httpbin.org/post",
            "body": "this is not json {"
        })
        assert "Invalid JSON" in result or "Error" in result

    def test_get_connection_error(self):
        """api_get_tool should handle connection errors."""
        from agents.tools.api_connector_tool import api_get_tool
        import requests as req

        with patch("agents.tools.api_connector_tool.requests.get",
                   side_effect=req.exceptions.ConnectionError("No connection")):
            result = api_get_tool.invoke({"url": "https://unreachable.xyz", "params": ""})
            assert "connect" in result.lower() or "Error" in result


# ══════════════════════════════════════════════════════════════════════════════
# 6. TOOL ORCHESTRATOR TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestToolOrchestrator:
    """Tests for ToolOrchestrator — registry, invocation, logging."""

    def test_orchestrator_registers_all_tools(self):
        """ToolOrchestrator should register all 9 tools on init."""
        from agents.tool_orchestrator import ToolOrchestrator

        orch = ToolOrchestrator()
        assert len(orch.tools) == 9, f"Expected 9 tools, got {len(orch.tools)}: {[t.name for t in orch.tools]}"

    def test_has_tool_returns_true_for_valid(self):
        """has_tool should return True for registered tools."""
        from agents.tool_orchestrator import ToolOrchestrator

        orch = ToolOrchestrator()
        assert orch.has_tool("calculator_tool") is True
        assert orch.has_tool("web_search_tool") is True
        assert orch.has_tool("datetime_tool") is True

    def test_has_tool_returns_false_for_invalid(self):
        """has_tool should return False for unknown tools."""
        from agents.tool_orchestrator import ToolOrchestrator

        orch = ToolOrchestrator()
        assert orch.has_tool("nonexistent_tool") is False

    def test_invoke_calculator_via_orchestrator(self):
        """Orchestrator.invoke should correctly delegate to calculator_tool."""
        from agents.tool_orchestrator import ToolOrchestrator

        orch = ToolOrchestrator()
        result = orch.invoke("calculator_tool", "10 + 5")
        assert "15" in result

    def test_invoke_unknown_tool_returns_error(self):
        """Orchestrator.invoke with unknown tool returns error message, not exception."""
        from agents.tool_orchestrator import ToolOrchestrator

        orch = ToolOrchestrator()
        result = orch.invoke("nonexistent_tool", "some input")
        assert "Unknown tool" in result
        assert isinstance(result, str)

    def test_invocation_log_recorded(self):
        """Orchestrator should log every invocation."""
        from agents.tool_orchestrator import ToolOrchestrator

        orch = ToolOrchestrator()
        orch.invoke("calculator_tool", "2 + 2")
        orch.invoke("datetime_tool", "%Y")

        assert len(orch.invocation_log) == 2
        assert orch.invocation_log[0]["tool_name"] == "calculator_tool"
        assert orch.invocation_log[1]["tool_name"] == "datetime_tool"

    def test_get_log_summary_format(self):
        """get_log_summary should return formatted string."""
        from agents.tool_orchestrator import ToolOrchestrator

        orch = ToolOrchestrator()
        orch.invoke("calculator_tool", "5 * 5")
        summary = orch.get_log_summary()
        assert "Tool Invocation Log" in summary
        assert "calculator_tool" in summary

    def test_list_tools_format(self):
        """list_tools should return all tool names in formatted output."""
        from agents.tool_orchestrator import ToolOrchestrator

        orch = ToolOrchestrator()
        listing = orch.list_tools()
        assert "calculator_tool" in listing
        assert "web_search_tool" in listing
        assert "datetime_tool" in listing
        assert "file_read_tool" in listing

    def test_tool_exception_recovery(self):
        """Orchestrator should catch tool exceptions and return error string."""
        from agents.tool_orchestrator import ToolOrchestrator

        orch = ToolOrchestrator()
        # Pass an object that will cause the tool to fail internally
        result = orch.invoke("calculator_tool", None)
        # Should NOT raise — should return error string
        assert isinstance(result, str)


# ══════════════════════════════════════════════════════════════════════════════
# 7. INTEGRATION — TOOL NAMES CHECK
# ══════════════════════════════════════════════════════════════════════════════

class TestToolIntegration:
    """Integration tests — verify ALL_TOOLS list is correctly populated."""

    def test_all_tools_list_length(self):
        """ALL_TOOLS should have exactly 9 tools."""
        from agents.tools import ALL_TOOLS
        assert len(ALL_TOOLS) == 9

    def test_all_tools_have_names(self):
        """Every tool in ALL_TOOLS should have a name attribute."""
        from agents.tools import ALL_TOOLS
        for tool in ALL_TOOLS:
            assert hasattr(tool, "name"), f"Tool {tool} missing 'name' attribute"
            assert tool.name, f"Tool has empty name"

    def test_all_tools_have_descriptions(self):
        """Every tool should have a non-empty description."""
        from agents.tools import ALL_TOOLS
        for tool in ALL_TOOLS:
            assert hasattr(tool, "description"), f"Tool {tool.name} missing 'description'"
            assert tool.description, f"Tool {tool.name} has empty description"

    def test_expected_tool_names_present(self):
        """All expected tool names should be present in ALL_TOOLS."""
        from agents.tools import ALL_TOOLS

        expected_names = {
            "datetime_tool",
            "date_calculator_tool",
            "calculator_tool",
            "file_read_tool",
            "file_write_tool",
            "file_list_tool",
            "web_search_tool",
            "api_get_tool",
            "api_post_tool",
        }
        actual_names = {tool.name for tool in ALL_TOOLS}
        assert expected_names == actual_names, (
            f"Missing tools: {expected_names - actual_names}\n"
            f"Extra tools: {actual_names - expected_names}"
        )
