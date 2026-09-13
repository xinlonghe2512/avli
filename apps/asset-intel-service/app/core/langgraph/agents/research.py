""" """

from langchain_core.messages import AIMessage, SystemMessage

from app.core.langgraph.tools import web_search
from app.schemas.graph import GraphState
from app.services.llm import llm_service

RESEARCH_SYSTEM_PROMPT = """\
You are a research assistant.

Answer the user's question using the web search results provided below.

Rules:

1. Prefer information supported by the search results.
2. Do not fabricate sources or facts.
3. If the search results are insufficient or conflicting, say so.
4. Clearly distinguish known information from uncertainty.
5. Provide a concise synthesis rather than simply copying search results.
"""


async def research_node(
    state: GraphState,
) -> dict[str, object]:
    """Research the user's question using web search."""

    user_message = state.messages[-1]

    query = str(user_message.content)

    search_results = await web_search.ainvoke(query)

    prompt = f"""\
{RESEARCH_SYSTEM_PROMPT}

Web search results:

<search_results>
{search_results}
</search_results>
"""

    messages = [
        SystemMessage(content=prompt),
        *state.messages,
    ]

    response = await llm_service.call(messages)

    return {
        "messages": [
            AIMessage(
                content=str(response.content),
                name="research",
            )
        ],
    }
