"""DuckDuckGo search tool for LangGraph.

A DuckDuckGo search tool that can be used with LangGraph
to perform web searches. It returns up to 10 search results and handles errors
gracefully.
"""

from typing import Any

from ddgs import DDGS
from langchain_core.tools import tool


@tool
def duckduckgo_search(query: str, max_results: int = 10) -> list[dict[str, Any]]:
    """Search the web using DuckDuckGo and return search results."""
    try:
        with DDGS() as ddgs:
            return list(
                ddgs.text(
                    query,
                    max_results=max_results,
                )
            )
    except Exception as exc:
        return [{"error": f"DuckDuckGo search failed: {exc}"}]
