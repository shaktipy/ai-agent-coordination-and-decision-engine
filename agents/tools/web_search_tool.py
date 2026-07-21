"""
Web Search Tool — AI Agent Coordination & Decision Engine
=========================================================
Tool 4 of the Custom Enterprise Toolkit (Milestone 2).

Provides agents with real-time web search capability using DuckDuckGo.
No API key required — completely free and India-friendly.

Dependencies: ddgs (pip install ddgs)

Author: Infosys Springboard Virtual Internship 7.0
"""

from langchain_core.tools import tool


@tool
def web_search_tool(query: str, max_results: str = "5") -> str:
    """
    Search the web using DuckDuckGo and return the top results.

    Use this tool when the user asks about current events, real-world facts,
    news, information about people, places, products, or anything that requires
    up-to-date information from the internet.

    Args:
        query      : The search query string.
                     Examples:
                        "latest Python 3.13 features"
                        "Infosys Q4 2024 results"
                        "how does LangChain ReAct agent work"
        max_results: Number of results to return as a string (default: "5", max recommended: "10")

    Returns:
        str: Formatted search results with title, URL, and snippet for each result.
             Returns an error message if search fails.
    """
    try:
        from ddgs import DDGS

        # Cast to int and clamp to reasonable range
        try:
            max_results_int = int(max_results)
        except ValueError:
            max_results_int = 5
        max_results_int = max(1, min(max_results_int, 10))

        results = []
        with DDGS() as ddgs_client:
            search_results = list(ddgs_client.text(query, max_results=max_results_int))

        if not search_results:
            return (
                f"[WebSearchTool] No results found for query: '{query}'\n"
                f"Try rephrasing your search query."
            )

        output_lines = [
            f"🔍 Web Search Results for: '{query}'",
            f"Found {len(search_results)} result(s)",
            "─" * 60,
        ]

        for i, result in enumerate(search_results, start=1):
            title   = result.get("title", "No title")
            url     = result.get("href", "No URL")
            snippet = result.get("body", "No description available.")

            # Truncate long snippets for readability
            if len(snippet) > 300:
                snippet = snippet[:297] + "..."

            output_lines.append(
                f"\n[{i}] {title}\n"
                f"    URL: {url}\n"
                f"    {snippet}"
            )

        output_lines.append("\n" + "─" * 60)
        return "\n".join(output_lines)

    except ImportError:
        return (
            "[WebSearchTool Error] 'ddgs' package not installed.\n"
            "Fix: pip install ddgs"
        )
    except Exception as e:
        return (
            f"[WebSearchTool Error] Search failed for query: '{query}'\n"
            f"Reason: {str(e)}\n"
            f"This may be a temporary network issue. Please try again."
        )
