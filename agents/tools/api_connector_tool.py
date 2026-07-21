"""
API Connector Tool — AI Agent Coordination & Decision Engine
============================================================
Tool 5 of the Custom Enterprise Toolkit (Milestone 2).

Provides agents with the ability to:
    - Make GET requests to any public REST API
    - Make POST requests with JSON payload to any REST API

Supports common enterprise integrations:
    - Weather APIs (e.g., Open-Meteo — free, no key)
    - News APIs
    - Any other public REST endpoint

Timeout: 10 seconds per request to prevent hanging.

Author: Infosys Springboard Virtual Internship 7.0
"""

import json
import requests
from langchain_core.tools import tool

# ── Request timeout in seconds ─────────────────────────────────────────────────
_TIMEOUT = 10

# ── Default headers ────────────────────────────────────────────────────────────
_DEFAULT_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "User-Agent": "AI-Agent-CoordinationEngine/1.0",
}


def _format_response(response: requests.Response, url: str) -> str:
    """
    Format an HTTP response into a readable string for the agent.

    Args:
        response: The requests.Response object
        url     : The URL that was called

    Returns:
        str: Formatted response string
    """
    status = response.status_code
    content_type = response.headers.get("Content-Type", "")

    header_lines = [
        f"🌐 API Response",
        f"URL        : {url}",
        f"Status     : {status} ({requests.status_codes._codes[status][0].upper()})",
        "─" * 60,
    ]

    # Try to parse JSON response
    if "application/json" in content_type:
        try:
            data = response.json()
            body = json.dumps(data, indent=2, ensure_ascii=False)
            # Truncate very large responses
            if len(body) > 3000:
                body = body[:2997] + "\n... [truncated — response too large]"
        except Exception:
            body = response.text[:3000]
    else:
        body = response.text[:3000]
        if len(response.text) > 3000:
            body += "\n... [truncated]"

    return "\n".join(header_lines) + "\n" + body


@tool
def api_get_tool(url: str, params: str = "") -> str:
    """
    Make an HTTP GET request to a REST API endpoint and return the response.

    Use this tool when the user wants to fetch data from an external API,
    check an API status, retrieve weather data, get public information, etc.

    Common free APIs you can use:
        - Weather     : https://api.open-meteo.com/v1/forecast?latitude=28.6&longitude=77.2&current_weather=true
        - IP Info     : https://ipapi.co/json/
        - Random fact : https://uselessfacts.jsph.pl/random.json?language=en
        - UUID gen    : https://www.uuidgenerator.net/api/version4
        - Exchange    : https://api.exchangerate-api.com/v4/latest/USD

    Args:
        url   : The full URL of the API endpoint to call.
                Example: "https://api.open-meteo.com/v1/forecast?latitude=28.6&longitude=77.2&current_weather=true"
        params: Optional additional query parameters as a JSON string.
                Example: '{"key": "value", "limit": "10"}'
                Leave blank if URL already has all parameters.

    Returns:
        str: Formatted API response with status code and body.
    """
    try:
        # Parse optional params
        query_params = {}
        if params.strip():
            try:
                query_params = json.loads(params)
            except json.JSONDecodeError:
                return (
                    "[APIGetTool] Invalid params format. "
                    "Use JSON string like '{\"key\": \"value\"}'"
                )

        response = requests.get(
            url,
            params=query_params,
            headers=_DEFAULT_HEADERS,
            timeout=_TIMEOUT,
        )

        return _format_response(response, url)

    except requests.exceptions.ConnectionError:
        return (
            f"[APIGetTool Error] Could not connect to: {url}\n"
            f"Check if the URL is correct and internet is available."
        )
    except requests.exceptions.Timeout:
        return (
            f"[APIGetTool Error] Request timed out after {_TIMEOUT}s: {url}\n"
            f"The server may be slow or unavailable."
        )
    except requests.exceptions.InvalidURL:
        return f"[APIGetTool Error] Invalid URL format: '{url}'"
    except Exception as e:
        return f"[APIGetTool Error] Unexpected error: {str(e)}"


@tool
def api_post_tool(url: str, body: str = "{}") -> str:
    """
    Make an HTTP POST request to a REST API endpoint with a JSON body.

    Use this tool when the user wants to send data to an API, submit a form,
    create a resource, or trigger an action on an external service.

    Args:
        url : The full URL of the API endpoint to POST to.
              Example: "https://httpbin.org/post"
        body: JSON string of the request body payload.
              Example: '{"name": "test", "value": 42}'
              Leave as '{}' for an empty body.

    Returns:
        str: Formatted API response with status code and body.
    """
    try:
        # Validate and parse JSON body
        try:
            payload = json.loads(body) if body.strip() else {}
        except json.JSONDecodeError as e:
            return (
                f"[APIPostTool Error] Invalid JSON body: {str(e)}\n"
                f"Make sure the body is valid JSON. Example: '{{\"key\": \"value\"}}'"
            )

        response = requests.post(
            url,
            json=payload,
            headers=_DEFAULT_HEADERS,
            timeout=_TIMEOUT,
        )

        return _format_response(response, url)

    except requests.exceptions.ConnectionError:
        return (
            f"[APIPostTool Error] Could not connect to: {url}\n"
            f"Check if the URL is correct and internet is available."
        )
    except requests.exceptions.Timeout:
        return (
            f"[APIPostTool Error] Request timed out after {_TIMEOUT}s: {url}"
        )
    except requests.exceptions.InvalidURL:
        return f"[APIPostTool Error] Invalid URL format: '{url}'"
    except Exception as e:
        return f"[APIPostTool Error] Unexpected error: {str(e)}"
