"""
agents/tools/__init__.py — Central Tools Registry
"""

from agents.tools.file_manager_tool import file_read_tool, file_list_tool
from agents.tools.bandit_scan_tool import bandit_scan_tool
from agents.tools.secret_pattern_tool import secret_pattern_scan_tool
from agents.tools.unsafe_function_tool import unsafe_function_tool
from agents.tools.radon_complexity_tool import cyclomatic_complexity_tool, maintainability_index_tool
from agents.tools.nested_loop_tool import nested_loop_detector_tool
from agents.tools.pylint_scan_tool import pylint_scan_tool
from agents.tools.naming_convention_tool import naming_convention_tool
from agents.tools.docstring_coverage_tool import docstring_coverage_tool
from agents.tools.test_presence_tool import test_presence_tool

ALL_TOOLS = [
    file_read_tool,
    file_list_tool,
    bandit_scan_tool,
    secret_pattern_scan_tool,
    unsafe_function_tool,
    cyclomatic_complexity_tool,
    maintainability_index_tool,
    nested_loop_detector_tool,
    pylint_scan_tool,
    naming_convention_tool,
    docstring_coverage_tool,
    test_presence_tool,
]
