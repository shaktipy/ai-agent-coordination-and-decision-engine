"""
File Manager Tool — AI Agent Coordination & Decision Engine
===========================================================
Tool 3 of the Custom Enterprise Toolkit (Milestone 2).

Provides agents with filesystem access to:
    - Read file contents
    - Write content to a file
    - List files in a directory

Security: Operations are restricted to the workspace directory.
Absolute paths outside the workspace are blocked.

Author: Infosys Springboard Virtual Internship 7.0
"""

import os
from pathlib import Path
from langchain_core.tools import tool

# ── Workspace root (relative operations are relative to this) ──────────────────
_WORKSPACE_ROOT = Path(os.getcwd()).resolve()


def _safe_path(file_path: str) -> Path:
    """
    Resolve and validate that a path stays within workspace root.

    Args:
        file_path: User-supplied file path (relative or absolute)

    Returns:
        Resolved Path object

    Raises:
        PermissionError: If path escapes workspace root
    """
    resolved = (_WORKSPACE_ROOT / file_path).resolve()
    if not str(resolved).startswith(str(_WORKSPACE_ROOT)):
        raise PermissionError(
            f"Access denied: Path '{file_path}' is outside the workspace."
        )
    return resolved


@tool
def file_read_tool(file_path: str) -> str:
    """
    Read the contents of a file and return it as text.

    Use this tool when the user wants to read, view, or inspect the contents
    of a file. The file must be within the project workspace.

    Args:
        file_path: Relative path to the file from the project root.
                   Examples: "README.md", "agents/tool_agent.py", "data/output.txt"

    Returns:
        str: The file contents, or an error message if file not found/unreadable.
    """
    try:
        path = _safe_path(file_path)

        if not path.exists():
            return f"[FileReadTool] File not found: '{file_path}'"
        if not path.is_file():
            return f"[FileReadTool] '{file_path}' is a directory, not a file. Use file_list_tool to list directories."

        # Read with size limit (100KB) to avoid memory issues
        max_bytes = 100_000
        size = path.stat().st_size
        if size > max_bytes:
            return (
                f"[FileReadTool] File is too large ({size:,} bytes). "
                f"Max allowed: {max_bytes:,} bytes."
            )

        content = path.read_text(encoding="utf-8", errors="replace")
        lines = content.count("\n") + 1

        return (
            f"File: {file_path}\n"
            f"Size: {size:,} bytes | Lines: {lines}\n"
            f"{'─' * 50}\n"
            f"{content}"
        )

    except PermissionError as e:
        return f"[FileReadTool] Permission denied: {str(e)}"
    except Exception as e:
        return f"[FileReadTool Error] {str(e)}"


@tool
def file_write_tool(file_path: str, content: str) -> str:
    """
    Write text content to a file. Creates the file if it doesn't exist.
    Overwrites existing content.

    Use this tool when the user wants to save, create, or update a file
    within the project workspace.

    Args:
        file_path: Relative path to the target file from the project root.
                   Example: "output/result.txt", "data/report.md"
        content  : The text content to write into the file.

    Returns:
        str: Success message with file details, or an error message.
    """
    try:
        path = _safe_path(file_path)

        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(content, encoding="utf-8")
        size = path.stat().st_size
        lines = content.count("\n") + 1

        return (
            f"[FileWriteTool] ✅ Successfully wrote to '{file_path}'\n"
            f"Size: {size:,} bytes | Lines: {lines}"
        )

    except PermissionError as e:
        return f"[FileWriteTool] Permission denied: {str(e)}"
    except Exception as e:
        return f"[FileWriteTool Error] {str(e)}"


@tool
def file_list_tool(directory_path: str = ".") -> str:
    """
    List all files and subdirectories in a given directory.

    Use this tool when the user wants to explore the project structure,
    see what files exist in a folder, or browse the workspace.

    Args:
        directory_path: Relative path to the directory to list.
                        Use "." for the project root (default).
                        Examples: ".", "agents", "agents/tools", "tests"

    Returns:
        str: A formatted directory listing, or an error message.
    """
    try:
        path = _safe_path(directory_path)

        if not path.exists():
            return f"[FileListTool] Directory not found: '{directory_path}'"
        if not path.is_dir():
            return f"[FileListTool] '{directory_path}' is a file, not a directory."

        items = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name))
        if not items:
            return f"[FileListTool] Directory '{directory_path}' is empty."

        lines = [f"📁 Directory: {directory_path}", "─" * 40]
        dirs_count = 0
        files_count = 0

        for item in items:
            # Skip hidden files/dirs (e.g., .git, __pycache__)
            if item.name.startswith(".") or item.name == "__pycache__":
                continue
            if item.is_dir():
                lines.append(f"  📂 {item.name}/")
                dirs_count += 1
            else:
                size = item.stat().st_size
                size_str = f"{size:,} B" if size < 1024 else f"{size/1024:.1f} KB"
                lines.append(f"  📄 {item.name}  ({size_str})")
                files_count += 1

        lines.append("─" * 40)
        lines.append(f"Total: {dirs_count} folder(s), {files_count} file(s)")

        return "\n".join(lines)

    except PermissionError as e:
        return f"[FileListTool] Permission denied: {str(e)}"
    except Exception as e:
        return f"[FileListTool Error] {str(e)}"
