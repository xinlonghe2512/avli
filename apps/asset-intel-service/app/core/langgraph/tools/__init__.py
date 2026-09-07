"""LangGraph tools for enhanced language model capabilities.

Custom tools that can be used with LangGraph to extend the capabilities of language models.

Currently includes tools for web search and other external integrations.
"""

from langchain_core.tools import BaseTool

from .ask_human import ask_human
from .duckduckgo_search import duckduckgo_search as ddgs_tool

tools: list[BaseTool] = [ddgs_tool, ask_human]
