""" """

from langchain_core.messages import AIMessage, SystemMessage

from app.core.langgraph.tools import rag_search
from app.schemas.graph import GraphState
from app.services.llm import llm_service

RAG_SYSTEM_MESSAGE = """\
# Role
You are a retrieval-augmented generation assistant.

# Job
Your job is to answer the user's question using the application's
knowledge base.

# Instructions
- Use the rag_search tool to retrieve relevant information.
- Base your answer primarily on the retrieved context.
- Do not invent facts that are not supported by the retrieved context.
- If the retrieved context is insufficient, say so clearly.
- Synthesize the retrieved information instead of simply copying it.
- Do not mention internal implementation details such as LlamaIndex,
   Qdrant, or LangGraph unless the user explicitly asks about them.
"""


async def rag_node(
    state: GraphState,
) -> dict[str, object]:
    """Answer the user's question using the knowledge base."""

    user_message = state.messages[-1]

    query = str(user_message.content)

    search_results = await rag_search.ainvoke(query)

    prompt = f"""\
{RAG_SYSTEM_MESSAGE}

Retrieved context:

<retrieved_context>
{search_results}
</retrieved_context>
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
                name="rag",
            )
        ],
    }
