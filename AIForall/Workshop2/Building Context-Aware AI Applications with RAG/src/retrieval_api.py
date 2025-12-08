"""Retrieve API for Bedrock RAG Retrieval System"""

from typing import Optional, Dict, Any, List
from enum import Enum
from dataclasses import dataclass
from botocore.exceptions import ClientError
from config.aws_config import AWSConfig
from src.vector_store import VectorIndexManager


class RetrievalType(Enum):
    """Enumeration of retrieval types"""
    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    HYBRID = "hybrid"


@dataclass
class RetrievalConfig:
    """Configuration for retrieval operations"""
    max_results: int = 5
    retrieval_type: RetrievalType = RetrievalType.SEMANTIC
    vector_weight: float = 0.5
    text_weight: float = 0.5
    metadata_filters: Optional[Dict[str, Any]] = None
    vector_field_name: str = "embedding"
    min_relevance_score: float = 0.0

    def validate(self) -> bool:
        """
        Validate retrieval configuration.

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        if self.max_results <= 0:
            raise ValueError("max_results must be greater than 0")

        if self.vector_weight < 0.0 or self.vector_weight > 1.0:
            raise ValueError("vector_weight must be between 0.0 and 1.0")

        if self.text_weight < 0.0 or self.text_weight > 1.0:
            raise ValueError("text_weight must be between 0.0 and 1.0")

        if self.min_relevance_score < 0.0 or self.min_relevance_score > 1.0:
            raise ValueError("min_relevance_score must be between 0.0 and 1.0")

        return True


@dataclass
class RetrievalResult:
    """Result from a retrieval operation"""
    chunk_id: str
    content: str
    relevance_score: float
    location: str
    metadata: Dict[str, Any]
    source_document: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            "chunk_id": self.chunk_id,
            "content": self.content,
            "relevance_score": self.relevance_score,
            "location": self.location,
            "metadata": self.metadata,
            "source_document": self.source_document
        }


class RetrieveAPI:
    """
    Retrieve API for semantic search and document retrieval.

    Provides methods for retrieving relevant documents from a knowledge base
    using vector similarity, keyword search, or hybrid approaches.
    """

    def __init__(self, aws_config: AWSConfig):
        """
        Initialize Retrieve API.

        Args:
            aws_config: AWSConfig instance for AWS client management
        """
        self.aws_config = aws_config
        self.vector_store = VectorIndexManager(aws_config)
        self.bedrock_client = aws_config.get_client("bedrock-runtime")

    def retrieve(
        self,
        knowledge_base_id: str,
        query: str,
        config: Optional[RetrievalConfig] = None
    ) -> List[RetrievalResult]:
        """
        Retrieve relevant documents from the knowledge base.

        Args:
            knowledge_base_id: ID of the knowledge base
            query: Query string or vector for retrieval
            config: RetrievalConfig instance (uses defaults if not provided)

        Returns:
            List of RetrievalResult objects ranked by relevance

        Raises:
            ValueError: If retrieval fails
        """
        if not config:
            config = RetrievalConfig()

        config.validate()

        try:
            # Use Bedrock Retrieve API
            response = self.bedrock_client.retrieve(
                knowledgeBaseId=knowledge_base_id,
                retrievalConfiguration={
                    "vectorSearchConfiguration": {
                        "numberOfResults": config.max_results,
                        "overrideSearchType": config.retrieval_type.value
                    }
                },
                text=query
            )

            results = []
            for result in response.get("retrievalResults", []):
                # Filter by minimum relevance score
                score = result.get("score", 0.0)
                if score >= config.min_relevance_score:
                    retrieval_result = RetrievalResult(
                        chunk_id=result.get("retrievalResultMetadata", {}).get("location", {}).get("s3Location", {}).get("uri", ""),
                        content=result.get("content", ""),
                        relevance_score=score,
                        location=result.get("retrievalResultMetadata", {}).get("location", {}).get("s3Location", {}).get("uri", ""),
                        metadata=result.get("retrievalResultMetadata", {}),
                        source_document=result.get("retrievalResultMetadata", {}).get("document", {}).get("documentId", "")
                    )
                    results.append(retrieval_result)

            # Sort by relevance score in descending order
            results.sort(key=lambda x: x.relevance_score, reverse=True)

            return results[:config.max_results]

        except ClientError as e:
            raise ValueError(f"Retrieve API call failed: {str(e)}")

    def retrieve_with_vector(
        self,
        collection_name: str,
        index_name: str,
        query_vector: List[float],
        config: Optional[RetrievalConfig] = None
    ) -> List[RetrievalResult]:
        """
        Retrieve documents using vector similarity search.

        Args:
            collection_name: Name of the OpenSearch Serverless collection
            index_name: Name of the vector index
            query_vector: Query vector for similarity search
            config: RetrievalConfig instance (uses defaults if not provided)

        Returns:
            List of RetrievalResult objects ranked by relevance

        Raises:
            ValueError: If retrieval fails
        """
        if not config:
            config = RetrievalConfig()

        config.validate()

        try:
            results = self.vector_store.search_by_vector(
                collection_name=collection_name,
                index_name=index_name,
                query_vector=query_vector,
                vector_field_name=config.vector_field_name,
                k=config.max_results,
                metadata_filters=config.metadata_filters
            )

            retrieval_results = []
            for result in results:
                # Filter by minimum relevance score
                if result["score"] >= config.min_relevance_score:
                    retrieval_result = RetrievalResult(
                        chunk_id=result.get("id", ""),
                        content=result.get("content", ""),
                        relevance_score=result.get("score", 0.0),
                        location=f"s3://{result.get('metadata', {}).get('source', '')}",
                        metadata=result.get("metadata", {}),
                        source_document=result.get("document_id", "")
                    )
                    retrieval_results.append(retrieval_result)

            return retrieval_results[:config.max_results]

        except ValueError as e:
            raise ValueError(f"Vector retrieval failed: {str(e)}")

    def retrieve_with_text(
        self,
        collection_name: str,
        index_name: str,
        query_text: str,
        config: Optional[RetrievalConfig] = None
    ) -> List[RetrievalResult]:
        """
        Retrieve documents using keyword/text search.

        Args:
            collection_name: Name of the OpenSearch Serverless collection
            index_name: Name of the vector index
            query_text: Query text for keyword search
            config: RetrievalConfig instance (uses defaults if not provided)

        Returns:
            List of RetrievalResult objects ranked by relevance

        Raises:
            ValueError: If retrieval fails
        """
        if not config:
            config = RetrievalConfig()

        config.validate()

        try:
            results = self.vector_store.search_by_text(
                collection_name=collection_name,
                index_name=index_name,
                query_text=query_text,
                k=config.max_results,
                metadata_filters=config.metadata_filters
            )

            retrieval_results = []
            for result in results:
                # Filter by minimum relevance score
                if result["score"] >= config.min_relevance_score:
                    retrieval_result = RetrievalResult(
                        chunk_id=result.get("id", ""),
                        content=result.get("content", ""),
                        relevance_score=result.get("score", 0.0),
                        location=f"s3://{result.get('metadata', {}).get('source', '')}",
                        metadata=result.get("metadata", {}),
                        source_document=result.get("document_id", "")
                    )
                    retrieval_results.append(retrieval_result)

            return retrieval_results[:config.max_results]

        except ValueError as e:
            raise ValueError(f"Text retrieval failed: {str(e)}")

    def retrieve_hybrid(
        self,
        collection_name: str,
        index_name: str,
        query_vector: List[float],
        query_text: str,
        config: Optional[RetrievalConfig] = None
    ) -> List[RetrievalResult]:
        """
        Retrieve documents using hybrid search (vector + text).

        Args:
            collection_name: Name of the OpenSearch Serverless collection
            index_name: Name of the vector index
            query_vector: Query vector for similarity search
            query_text: Query text for keyword search
            config: RetrievalConfig instance (uses defaults if not provided)

        Returns:
            List of RetrievalResult objects ranked by combined relevance

        Raises:
            ValueError: If retrieval fails
        """
        if not config:
            config = RetrievalConfig()

        config.validate()

        try:
            results = self.vector_store.hybrid_search(
                collection_name=collection_name,
                index_name=index_name,
                query_vector=query_vector,
                query_text=query_text,
                vector_field_name=config.vector_field_name,
                k=config.max_results,
                vector_weight=config.vector_weight,
                text_weight=config.text_weight,
                metadata_filters=config.metadata_filters
            )

            retrieval_results = []
            for result in results:
                # Filter by minimum relevance score
                combined_score = result.get("combined_score", 0.0)
                if combined_score >= config.min_relevance_score:
                    retrieval_result = RetrievalResult(
                        chunk_id=result.get("id", ""),
                        content=result.get("content", ""),
                        relevance_score=combined_score,
                        location=f"s3://{result.get('metadata', {}).get('source', '')}",
                        metadata=result.get("metadata", {}),
                        source_document=result.get("document_id", "")
                    )
                    retrieval_results.append(retrieval_result)

            return retrieval_results[:config.max_results]

        except ValueError as e:
            raise ValueError(f"Hybrid retrieval failed: {str(e)}")

    def validate_retrieval_configuration(
        self,
        collection_name: str,
        index_name: str,
        expected_vector_dimension: int = 1536
    ) -> Dict[str, bool]:
        """
        Validate that the retrieval system is properly configured.

        Args:
            collection_name: Name of the OpenSearch Serverless collection
            index_name: Name of the vector index
            expected_vector_dimension: Expected dimension of vector embeddings

        Returns:
            Dictionary with validation results

        Raises:
            ValueError: If validation fails
        """
        try:
            validation_results = self.vector_store.validate_index_configuration(
                collection_name=collection_name,
                index_name=index_name,
                expected_vector_dimension=expected_vector_dimension
            )

            return validation_results
        except ValueError as e:
            raise ValueError(f"Retrieval configuration validation failed: {str(e)}")

    def get_retrieval_statistics(
        self,
        collection_name: str,
        index_name: str
    ) -> Dict[str, Any]:
        """
        Get statistics about the retrieval index.

        Args:
            collection_name: Name of the OpenSearch Serverless collection
            index_name: Name of the vector index

        Returns:
            Dictionary containing index statistics

        Raises:
            ValueError: If statistics cannot be retrieved
        """
        try:
            stats = self.vector_store.get_index_statistics(
                collection_name=collection_name,
                index_name=index_name
            )

            return stats
        except ValueError as e:
            raise ValueError(f"Failed to get retrieval statistics: {str(e)}")
