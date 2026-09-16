"""LlamaIndex knowledge base backed by Qdrant."""

from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.base.base_retriever import BaseRetriever
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from src.core.config import settings
from src.core.logging import logger


class RAGService:
    """Service for managing knowledge base using LlamaIndex and Qdrant."""

    def __init__(self) -> None:
        self._client: QdrantClient | None = None
        self._embed_model: OpenAIEmbedding | None = None
        self._index: VectorStoreIndex | None = None

        try:
            self._client = self._create_qdrant_client()
            self._embed_model = self._create_embedding_model()
            self._index = self._create_index()

        except Exception as exc:
            logger.warning(
                "Knowledge base unavailable: %s",
                exc,
            )

            self._client = None
            self._index = None

    def _create_qdrant_client(self) -> QdrantClient:
        """Create the Qdrant client."""

        return QdrantClient(
            host=settings.KNOWLEDGE_BASE_HOST, port=settings.KNOWLEDGE_BASE_PORT
        )

        # return QdrantClient(
        #     url=settings.KNOWLEDGE_BASE_CLOUD_URL,
        #     api_key=settings.KNOWLEDGE_BASE_CLOUD_API_KEY,
        # )

    def _create_embedding_model(self) -> OpenAIEmbedding:
        """Create the embedding model."""

        return OpenAIEmbedding(
            model_name=settings.KNOWLEDGE_BASE_EMBEDDING_MODEL,
            api_key=settings.MODEL_PROVIDER_API_KEY,
            api_base=settings.MODEL_PROVIDER_API_BASE,
        )

    def _create_index(self) -> VectorStoreIndex:
        """Create the LlamaIndex backed by Qdrant."""

        vector_store = QdrantVectorStore(
            client=self._client,
            collection_name=settings.KNOWLEDGE_BASE_COLLECTION_NAME,
        )

        storage_context = StorageContext.from_defaults(
            vector_store=vector_store,
        )

        return VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            storage_context=storage_context,
            embed_model=self._embed_model,
        )

    @property
    def available(self) -> bool:
        """Return whether the knowledge base is available."""
        return self._index is not None

    def get_retriever(self, top_k: int) -> BaseRetriever | None:
        """Return a retriever for the knowledge base."""
        if top_k <= 0:
            raise ValueError("top_k must be greater than zero")

        if self._index is None:
            logger.warning("Knowledge base is unavailable; skipping retrieval")
            return None

        return self._index.as_retriever(
            similarity_top_k=top_k,
        )


rag_service = RAGService()
