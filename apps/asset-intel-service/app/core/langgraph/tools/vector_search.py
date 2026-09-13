"""RAG search tool for LangGraph.

A RAG search tool powered by ___ that can be used with LangGraph to perform RAG searches to Qdrant store.

It returns up to top 5 search results and handles errors gracefully.
"""

from langchain_core.tools import tool

from app.services.rag import rag_service

TOP_K = 5


@tool
async def vector_search(query: str) -> str:
    """Search the knowledge base for information relevant to the query."""

    try:
        retriever = rag_service.get_retriever(TOP_K)
        results = await retriever.aretrieve(query)

        if not results:
            return "No relevant documents were found."

        return "\n\n".join(str(result.node.get_content()) for result in results)

    except Exception:
        return "RAG search failed."
