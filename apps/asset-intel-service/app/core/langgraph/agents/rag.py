from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

from app.core.langgraph.tools import rag_search
from app.schemas.graph import GraphState
from app.services.llm import llm_service

RAG_SYSTEM_PROMPT = """\
You are a retrieval-augmented generation assistant.

Your job is to answer the user's question using the application's
knowledge base.

Rules:

1. Use the rag_search tool to retrieve relevant information.
2. Base your answer primarily on the retrieved context.
3. Do not invent facts that are not supported by the retrieved context.
4. If the retrieved context is insufficient, say so clearly.
5. Synthesize the retrieved information instead of simply copying it.
6. Do not mention internal implementation details such as LlamaIndex,
   Qdrant, or LangGraph unless the user explicitly asks about them.
"""


async def rag_node(
    state: GraphState,
    _config: RunnableConfig,
) -> dict[str, object]:
    """Answer the user's question using the knowledge base."""

    user_message = state.messages[-1]

    query = str(user_message.content)

    search_results = await rag_search.ainvoke(query)

    prompt = f"""\
{RAG_SYSTEM_PROMPT}

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
