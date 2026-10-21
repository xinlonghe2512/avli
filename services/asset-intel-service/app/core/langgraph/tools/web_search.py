"""Web search tool for LangGraph.

A web search tool powered by DuckDuckGo API that can be used with LangGraph to perform web searches.

It returns up to 10 search results and handles errors gracefully.
"""

from ddgs import DDGS
from langchain_core.tools import tool


@tool
def web_search(query: str, max_results: int = 10) -> list[dict[str, str]]:
    """Search the web and return search results."""
    try:
        with DDGS() as ddgs:
            return list(
                ddgs.text(
                    query,
                    max_results=max_results,
                )
            )
    except Exception as exc:
        return [{"error": f"Web search failed: {exc}"}]
