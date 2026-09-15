"""LangGraph tools for enhanced language model capabilities.

Custom tools that can be used with LangGraph to extend the capabilities of language models.

Currently includes tools for web search and other external integrations.
"""

from langchain_core.tools import BaseTool

from .ask_human import ask_human
from .vector_search import vector_search
from .web_search import web_search

tools: list[BaseTool] = [
    ask_human,
    web_search,
    vector_search,
]
