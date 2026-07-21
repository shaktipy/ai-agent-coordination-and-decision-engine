"""
DateTime Tool — AI Agent Coordination & Decision Engine
=======================================================
Tool 1 of the Custom Enterprise Toolkit (Milestone 2).

Provides agents with the ability to:
    - Get current date and time in various formats
    - Calculate the difference between two dates
    - Add/subtract days from a date

LangChain @tool decorator makes these functions directly usable
inside a ReAct AgentExecutor without any extra wiring.

Author: Infosys Springboard Virtual Internship 7.0
"""

from datetime import datetime, timedelta
from langchain_core.tools import tool


@tool
def datetime_tool(format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Get the REAL current date and time by calling the system clock.

    IMPORTANT: This tool fetches the LIVE system date and time.
    Do NOT assume or guess any date — always use this tool's output.

    Use this tool when the user asks about the current time, date, day of week,
    or any present-moment temporal information.

    Args:
        format_str: Python strftime format string.
                    Format codes:
                        '%Y-%m-%d'            → YYYY-MM-DD  (e.g. year-month-day)
                        '%d %B %Y'            → DD Month YYYY
                        '%Y-%m-%d %H:%M:%S'   → full datetime
                        '%A, %d %B %Y'        → Weekday, DD Month YYYY
                    Leave blank for full datetime: YYYY-MM-DD HH:MM:SS

    Returns:
        str: Formatted LIVE current date and time string from the system clock.
    """
    try:
        now = datetime.now()
        formatted = now.strftime(format_str)
        day_name = now.strftime("%A")
        return (
            f"Current date and time: {formatted}\n"
            f"Day of week: {day_name}\n"
            f"Timestamp: {now.isoformat()}"
        )
    except Exception as e:
        return f"[DateTimeTool Error] Could not format date: {str(e)}"


@tool
def date_calculator_tool(operation: str) -> str:
    """
    Perform date arithmetic — add/subtract days from TODAY's LIVE date, or find
    the difference between two dates.

    IMPORTANT: "today" in this tool always means the REAL system date (from the clock).
    Do NOT substitute any hardcoded or assumed date for "today".

    Use this tool when the user asks questions like:
        - "What date will it be 30 days from today?"
        - "How many days between two specific dates?"
        - "What was the date 100 days ago?"

    Args:
        operation: A string describing the date operation. Use one of these formats:
            - "today + N days"              → adds N days to today's real date
            - "today - N days"              → subtracts N days from today's real date
            - "diff YYYY-MM-DD YYYY-MM-DD"  → finds difference between two dates

    Returns:
        str: Result of the date calculation.
    """
    try:
        operation = operation.strip().lower()
        today = datetime.now().date()

        # ── Pattern: "today + N days" or "today - N days" ─────────────────────
        if operation.startswith("today"):
            parts = operation.split()
            # Parts: ["today", "+", "30", "days"] → 4 tokens
            if len(parts) >= 3 and parts[1] in ("+", "-"):
                # N can be at index 2 (e.g., "today + 30 days" or "today + 30")
                n_str = parts[2].rstrip("days").rstrip()
                n_str = parts[2]  # numeric part
                if n_str.isdigit():
                    n = int(n_str)
                    delta = timedelta(days=n)
                    if parts[1] == "+":
                        result_date = today + delta
                        return (
                            f"Today: {today.strftime('%d %B %Y')}\n"
                            f"After {n} days: {result_date.strftime('%d %B %Y')} "
                            f"({result_date.strftime('%A')})"
                        )
                    else:
                        result_date = today - delta
                        return (
                            f"Today: {today.strftime('%d %B %Y')}\n"
                            f"{n} days ago: {result_date.strftime('%d %B %Y')} "
                            f"({result_date.strftime('%A')})"
                        )

        # ── Pattern: "diff DATE1 DATE2" ────────────────────────────────────────
        elif operation.startswith("diff"):
            parts = operation.split()
            if len(parts) == 3:
                d1 = datetime.strptime(parts[1], "%Y-%m-%d").date()
                d2 = datetime.strptime(parts[2], "%Y-%m-%d").date()
                diff = abs((d2 - d1).days)
                return (
                    f"Date 1: {d1.strftime('%d %B %Y')}\n"
                    f"Date 2: {d2.strftime('%d %B %Y')}\n"
                    f"Difference: {diff} days"
                )

        return (
            "[DateCalculatorTool] Invalid format. Use:\n"
            "  'today + N days'  or  'today - N days'  or  'diff YYYY-MM-DD YYYY-MM-DD'"
        )

    except ValueError as e:
        return f"[DateCalculatorTool Error] Invalid date format: {str(e)}"
    except Exception as e:
        return f"[DateCalculatorTool Error] {str(e)}"
