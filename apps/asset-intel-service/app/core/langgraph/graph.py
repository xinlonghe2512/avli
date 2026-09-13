"""LangGraph Agent/workflow and interactions with the LLM."""

import asyncio
from collections.abc import AsyncGenerator
from typing import Any, cast
from urllib.parse import quote_plus

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    convert_to_openai_messages,
)
from langchain_core.runnables.config import RunnableConfig
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.errors import GraphInterrupt
from langgraph.graph import (
    END,
    START,
    StateGraph,
)
from langgraph.graph.state import (
    Command,
    CompiledStateGraph,
)
from langgraph.types import (
    RetryPolicy,
    StateSnapshot,
)
from psycopg import (
    AsyncConnection,
    sql,
)
from psycopg.rows import (
    DictRow,
    dict_row,
)
from psycopg_pool import AsyncConnectionPool

from app.core.config import settings
from app.core.langgraph.agents.rag import rag_node
from app.core.langgraph.agents.research import research_node
from app.core.langgraph.agents.supervisor import supervisor_node
from app.core.logging import logger
from app.core.observability import langfuse_callback_handler
from app.schemas.chat import Message
from app.schemas.graph import GraphState
from app.services.llm import llm_service
from app.services.memory import memory_service
from app.utils import (
    convert_messages,
    extract_text_content,
)

PostgresConnPool = AsyncConnectionPool[AsyncConnection[DictRow]]


def route_from_supervisor(state: GraphState) -> str:
    """Route execution to the agent selected by the supervisor."""

    if state.next_agent is None:
        raise ValueError("Supervisor did not select an agent")

    return state.next_agent


class LangGraphWorkflow:
    """Manages the LangGraph workflow and interactions with the LLM.

    This class handles the creation and management of the LangGraph workflow,
    including LLM interactions, database connections, and response processing.
    """

    def __init__(self) -> None:
        """Initialize the LangGraph Agent with necessary components."""

        # Use the LLM service with tools bound
        self.llm_service = llm_service
        self._connection_pool: PostgresConnPool | None = None
        self._graph: CompiledStateGraph[GraphState] | None = None
        logger.info(
            "langgraph_agent_initialized",
            model=settings.LANGGRAPH_LLM_MODEL,
            environment=settings.ENVIRONMENT.value,
        )

    async def _get_connection_pool(self) -> PostgresConnPool:
        """Get a PostgreSQL connection pool using environment-specific settings.

        Returns:
            AsyncConnectionPool: The open connection pool.

        Raises:
            Exception: If the pool cannot be created, in every environment.
        """
        if self._connection_pool is None:
            try:
                # Configure pool size based on environment
                max_size = settings.POSTGRES_POOL_SIZE

                connection_url = (
                    "postgresql://"
                    f"{quote_plus(settings.POSTGRES_USER)}:{quote_plus(settings.POSTGRES_PASSWORD)}"
                    f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
                )

                self._connection_pool = AsyncConnectionPool(
                    connection_url,
                    open=False,
                    max_size=max_size,
                    kwargs={
                        "autocommit": True,
                        "connect_timeout": 5,
                        "prepare_threshold": None,
                        "row_factory": dict_row,
                    },
                )
                await self._connection_pool.open()
                logger.info(
                    "connection_pool_created",
                    max_size=max_size,
                    environment=settings.ENVIRONMENT.value,
                )
            except Exception as e:
                logger.exception(
                    "connection_pool_creation_failed",
                    error=str(e),
                    environment=settings.ENVIRONMENT.value,
                )
                # Never degrade silently: the checkpointer is the only store for
                # conversation history and HITL resume state. Serving without it
                # loses data rather than surfacing an outage.
                raise e
        return self._connection_pool

    async def create_graph(self) -> CompiledStateGraph[GraphState]:
        """Create and configure the multi-agent LangGraph.

        Returns:
            CompiledStateGraph: The configured LangGraph instance, always with a checkpointer.

        Raises:
            Exception: If the graph cannot be built, in every environment.
        """
        if self._graph is None:
            try:
                graph_builder = StateGraph(GraphState)

                graph_builder.add_node(
                    "supervisor",
                    supervisor_node,
                )

                graph_builder.add_node(
                    "rag", rag_node, retry_policy=RetryPolicy(max_attempts=3)
                )

                graph_builder.add_node(
                    "research", research_node, retry_policy=RetryPolicy(max_attempts=3)
                )

                # START -> supervisor
                graph_builder.add_edge(
                    START,
                    "supervisor",
                )

                # supervisor -> selected agent
                graph_builder.add_conditional_edges(
                    "supervisor",
                    route_from_supervisor,
                    {
                        "rag": "rag",
                        "research": "research",
                    },
                )

                # Specialists -> END
                graph_builder.add_edge(
                    "rag",
                    END,
                )

                graph_builder.add_edge(
                    "research",
                    END,
                )

                # Raises if the pool cannot be created — no checkpointer, no service.
                connection_pool = await self._get_connection_pool()
                checkpointer = AsyncPostgresSaver(connection_pool)
                await checkpointer.setup()

                self._graph = graph_builder.compile(
                    checkpointer=checkpointer,
                    name=f"{settings.PROJECT_NAME} Multi-Agent ({settings.ENVIRONMENT.value})",
                )

                logger.info(
                    "multi_agent_graph_created",
                    graph_name=f"{settings.PROJECT_NAME} Multi-Agent",
                    environment=settings.ENVIRONMENT.value,
                    has_checkpointer=checkpointer is not None,
                )
            except Exception as e:
                logger.exception(
                    "graph_creation_failed",
                    error=str(e),
                    environment=settings.ENVIRONMENT.value,
                )
                raise e

        return self._graph

    async def _get_graph(self) -> CompiledStateGraph[GraphState]:
        """Return the compiled graph, creating it on first access.

        Raises:
            Exception: Propagated from ``create_graph()`` when initialisation
                fails. Callers can rely on the return being non-``None``.
        """
        if self._graph is None:
            self._graph = await self.create_graph()
        return self._graph

    async def get_response(
        self,
        messages: list[Message],
        session_id: str,
        user_id: str | None = None,
        username: str | None = None,
    ) -> list[Message]:
        """Get a response from the LLM.

        Args:
            messages (list[Message]): The messages to send to the LLM.
            session_id (str): The session ID for the conversation.
            user_id (Optional[str]): The user ID for the conversation.
            username (Optional[str]): The display name of the user.

        Returns:
            list[Message]: The response from the LLM.
        """
        graph = await self._get_graph()

        callbacks: list[BaseCallbackHandler] = (
            [langfuse_callback_handler] if settings.LANGFUSE_TRACING_ENABLED else []
        )

        config: RunnableConfig = {
            "configurable": {"thread_id": session_id},
            "callbacks": callbacks,
            "metadata": {
                "user_id": user_id,
                "username": username,
                "session_id": session_id,
                "environment": settings.ENVIRONMENT.value,
                "debug": settings.DEBUG,
            },
        }

        try:
            # Convert API Message objects to LangChain messages before
            # passing them into the LangGraph state.
            langchain_messages = convert_messages(messages)

            # Run state check and memory search concurrently.
            state, relevant_memory = await asyncio.gather(
                graph.aget_state(config),
                memory_service.search(user_id, messages[-1].content),
            )

            if state.next:
                logger.info(
                    "resuming_interrupted_graph",
                    session_id=session_id,
                    next_nodes=state.next,
                )

                response = await graph.ainvoke(
                    Command(resume=messages[-1].content),
                    config=config,
                )
            else:
                relevant_memory = relevant_memory or "No relevant memory found."

                graph_input = cast(
                    GraphState,
                    {
                        "messages": langchain_messages,
                        "long_term_memory": relevant_memory,
                    },
                )

                response = await graph.ainvoke(
                    input=graph_input,
                    config=config,
                )

            # Check if the graph was interrupted during this invocation.
            state = await graph.aget_state(config)

            if state.next:
                interrupt_value = (
                    state.tasks[0].interrupts[0].value
                    if state.tasks
                    else "Waiting for input."
                )

                logger.info(
                    "graph_interrupted",
                    session_id=session_id,
                    interrupt_value=str(interrupt_value),
                )

                return [
                    Message(
                        role="assistant",
                        content=str(interrupt_value),
                    )
                ]

            openai_msgs = cast(
                list[dict[str, Any]],
                convert_to_openai_messages(response["messages"]),
            )

            asyncio.create_task(
                memory_service.add(
                    user_id,
                    openai_msgs,
                    config.get("metadata"),
                )
            )

            return self.__process_messages(response["messages"])

        except GraphInterrupt:
            state = await graph.aget_state(config)

            interrupt_value = (
                state.tasks[0].interrupts[0].value
                if state.tasks
                else "Waiting for input."
            )

            logger.info(
                "graph_interrupted",
                session_id=session_id,
                interrupt_value=str(interrupt_value),
            )

            return [
                Message(
                    role="assistant",
                    content=str(interrupt_value),
                )
            ]

        except Exception as e:
            logger.exception(
                "get_response_failed",
                error=str(e),
                session_id=session_id,
            )
            raise

    async def get_stream_response(
        self,
        messages: list[Message],
        session_id: str,
        user_id: str | None = None,
        username: str | None = None,
    ) -> AsyncGenerator[str]:
        """Get a stream response from the LLM.

        Args:
            messages (list[Message]): The messages to send to the LLM.
            session_id (str): The session ID for the conversation.
            user_id (Optional[str]): The user ID for the conversation.
            username (Optional[str]): The display name of the user.

        Yields:
            str: Tokens of the LLM response.
        """
        callbacks: list[BaseCallbackHandler] = (
            [langfuse_callback_handler] if settings.LANGFUSE_TRACING_ENABLED else []
        )
        config: RunnableConfig = {
            "configurable": {"thread_id": session_id},
            "callbacks": callbacks,
            "metadata": {
                "user_id": user_id,
                "username": username,
                "session_id": session_id,
                "environment": settings.ENVIRONMENT.value,
                "debug": settings.DEBUG,
            },
        }
        graph = await self._get_graph()

        langchain_messages = convert_messages(messages)

        try:
            # Run state check and memory search concurrently to save 200-500ms
            state, relevant_memory = await asyncio.gather(
                graph.aget_state(config),
                memory_service.search(user_id, messages[-1].content),
            )

            if state.next:
                async for token, _ in graph.astream(
                    Command(resume=messages[-1].content),
                    config,
                    stream_mode="messages",
                ):
                    if not isinstance(token, (AIMessage, AIMessageChunk)):
                        continue

                    text = extract_text_content(token.content)

                    if text:
                        yield text
            else:
                relevant_memory = relevant_memory or "No relevant memory found."

                graph_input = cast(
                    GraphState,
                    {
                        "messages": langchain_messages,
                        "long_term_memory": relevant_memory,
                    },
                )

                async for token, _ in graph.astream(
                    graph_input,
                    config,
                    stream_mode="messages",
                ):
                    if not isinstance(token, (AIMessage, AIMessageChunk)):
                        continue

                    text = extract_text_content(token.content)

                    if text:
                        yield text

            # After streaming completes, check for interrupt or update memory
            state = await graph.aget_state(config)
            if state.next:
                interrupt_value = (
                    state.tasks[0].interrupts[0].value
                    if state.tasks
                    else "Waiting for input."
                )
                logger.info(
                    "graph_interrupted_stream",
                    session_id=session_id,
                    interrupt_value=str(interrupt_value),
                )
                yield str(interrupt_value)
            elif state.values and "messages" in state.values:
                openai_msgs = cast(
                    list[dict[str, Any]],
                    convert_to_openai_messages(state.values["messages"]),
                )

                asyncio.create_task(
                    memory_service.add(user_id, openai_msgs, config.get("metadata"))
                )
        except GraphInterrupt:
            state = await graph.aget_state(config)
            interrupt_value = (
                state.tasks[0].interrupts[0].value
                if state.tasks
                else "Waiting for input."
            )
            logger.info(
                "graph_interrupted_stream",
                session_id=session_id,
                interrupt_value=str(interrupt_value),
            )
            yield str(interrupt_value)
        except Exception as stream_error:
            logger.exception(
                "stream_processing_failed",
                error=str(stream_error),
                session_id=session_id,
            )
            raise stream_error

    async def get_chat_history(self, session_id: str) -> list[Message]:
        """Get the chat history for a given thread ID.

        Args:
            session_id (str): The session ID for the conversation.

        Returns:
            list[Message]: The chat history.
        """
        graph = await self._get_graph()

        config: RunnableConfig = {"configurable": {"thread_id": session_id}}
        state: StateSnapshot = await graph.aget_state(config=config)
        return self.__process_messages(state.values["messages"]) if state.values else []

    def __process_messages(self, messages: list[BaseMessage]) -> list[Message]:
        openai_style_messages = convert_to_openai_messages(messages)
        # keep just assistant and user messages
        return [
            Message(role=message["role"], content=str(message["content"]))
            for message in openai_style_messages
            if message["role"] in ["assistant", "user"] and message["content"]
        ]

    async def clear_chat_history(self, session_id: str) -> None:
        """Clear all chat history for a given thread ID.

        Args:
            session_id: The ID of the session to clear history for.

        Raises:
            Exception: If there's an error clearing the chat history.
        """
        try:
            # Make sure the pool is initialized in the current event loop
            conn_pool = await self._get_connection_pool()
            if conn_pool is None:
                raise RuntimeError(
                    "connection pool unavailable; cannot clear chat history"
                )

            # Batch all DELETEs in a single pipeline round-trip
            async with conn_pool.connection() as conn:
                async with conn.pipeline():
                    for table in settings.CHECKPOINT_TABLES:
                        await conn.execute(
                            sql.SQL("DELETE FROM {} WHERE thread_id = %s").format(
                                sql.Identifier(table)
                            ),
                            (session_id,),
                        )
                logger.info(
                    "checkpoint_tables_cleared_for_session",
                    tables=settings.CHECKPOINT_TABLES,
                    session_id=session_id,
                )

        except Exception as e:
            logger.error(
                "clear_chat_history_operation_failed",
                session_id=session_id,
                error=str(e),
            )
            raise
