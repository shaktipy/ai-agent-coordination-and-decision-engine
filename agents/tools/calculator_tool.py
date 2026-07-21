"""
Calculator Tool — AI Agent Coordination & Decision Engine
=========================================================
Tool 2 of the Custom Enterprise Toolkit (Milestone 2).

Provides agents with the ability to:
    - Evaluate arithmetic and algebraic expressions safely
    - Handle basic math (add, subtract, multiply, divide, power, roots)
    - Solve symbolic math expressions using sympy

Safety: Uses sympy for parsing instead of raw eval() to prevent
code injection attacks.

Author: Infosys Springboard Virtual Internship 7.0
"""

from langchain_core.tools import tool


@tool
def calculator_tool(expression: str) -> str:
    """
    Evaluate a mathematical expression and return the result.

    Use this tool when the user asks to calculate, compute, or solve any
    mathematical expression, including arithmetic, algebra, powers, and roots.

    IMPORTANT: Do NOT use Python syntax like ** for power — write expressions
    in plain math form. The tool understands: +, -, *, /, ^, sqrt(), pi, e, etc.

    Args:
        expression: A mathematical expression string.
                    Examples:
                        "15 * 24 + 100"
                        "sqrt(144)"
                        "2^10"
                        "(3 + 5) * (2 - 1) / 4"
                        "pi * 5^2"
                        "log(100, 10)"

    Returns:
        str: The computed result or an error message.
    """
    try:
        import sympy
        from sympy.parsing.sympy_parser import (
            parse_expr,
            standard_transformations,
            implicit_multiplication_application,
            convert_xor,
        )

        # Transformations: allow implicit mult (2x = 2*x), ^ = power
        transformations = (
            standard_transformations
            + (implicit_multiplication_application, convert_xor)
        )

        # Clean up the expression
        expr_cleaned = expression.strip()

        # Parse with sympy — safe, no exec/eval of arbitrary code
        parsed = parse_expr(expr_cleaned, transformations=transformations)

        # Evaluate numerically
        result = parsed.evalf()

        # Format output — show integer if no decimal part
        if result == int(result):
            result_str = str(int(result))
        else:
            result_str = f"{float(result):.6g}"  # up to 6 significant figures

        return (
            f"Expression : {expression}\n"
            f"Result     : {result_str}"
        )

    except ImportError:
        # Fallback to safe eval if sympy not installed
        return _safe_eval_fallback(expression)
    except Exception as e:
        return (
            f"[CalculatorTool Error] Could not evaluate '{expression}'.\n"
            f"Reason: {str(e)}\n"
            f"Tip: Use standard math notation. Example: '15 * 24 + 100', 'sqrt(16)', '2^8'"
        )


def _safe_eval_fallback(expression: str) -> str:
    """
    Minimal fallback calculator using restricted eval.
    Only allows safe math operations — no imports, no builtins.

    Args:
        expression: math expression string

    Returns:
        str: Result or error message
    """
    import math
    allowed_names = {
        k: v for k, v in math.__dict__.items() if not k.startswith("_")
    }
    allowed_names["abs"] = abs

    try:
        result = eval(expression, {"__builtins__": {}}, allowed_names)  # noqa: S307
        return f"Expression: {expression}\nResult: {result}"
    except Exception as e:
        return f"[CalculatorTool Error] {str(e)}"
