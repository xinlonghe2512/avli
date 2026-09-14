"""LlamaIndex knowledge base backed by Qdrant."""

from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.base.base_retriever import BaseRetriever
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from app.core.config import settings


class RAGService:
    """Service for managing knowledge base using LlamaIndex and Qdrant."""

    def __init__(self) -> None:
        self._client = self._create_qdrant_client()
        self._embed_model = self._create_embedding_model()
        self._index = self._create_index()

    def _create_qdrant_client(self) -> QdrantClient:
        """Create the Qdrant client."""

        return QdrantClient(
            url=settings.KNOWLEDGE_BASE_URL,
            api_key=settings.KNOWLEDGE_BASE_API_KEY,
        )

    def _create_embedding_model(self) -> OpenAIEmbedding:
        """Create the embedding model."""

        return OpenAIEmbedding(
            model=settings.KNOWLEDGE_BASE_EMBEDDING_MODEL,
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

    def get_retriever(self, top_k: int) -> BaseRetriever:
        """Return a retriever for the knowledge base."""

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero")

        return self._index.as_retriever(
            similarity_top_k=top_k,
        )


rag_service = RAGService()
