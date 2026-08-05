"""
agents/tools/file_manager_tool.py — Read-only File Tools
"""

import os
from pathlib import Path
from langchain_core.tools import tool

_WORKSPACE_ROOT = Path(os.getcwd()).resolve()

def _safe_path(file_path: str) -> Path:
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
    """
    try:
        path = _safe_path(file_path)

        if not path.exists():
            return f"[FileReadTool] File not found: '{file_path}'"
        if not path.is_file():
            return f"[FileReadTool] '{file_path}' is a directory, not a file."

        max_bytes = 200_000
        size = path.stat().st_size
        if size > max_bytes:
            return f"[FileReadTool] File is too large. Max: {max_bytes} bytes."

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
def file_list_tool(directory_path: str = ".") -> str:
    """
    List all files and subdirectories in a given directory.
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
    except Exception as e:
        return f"[FileListTool Error] {str(e)}"
