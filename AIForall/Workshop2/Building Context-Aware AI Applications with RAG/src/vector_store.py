"""Vector store management for Bedrock RAG Retrieval System using OpenSearch Serverless"""

import json
from typing import Optional, Dict, Any, List
from botocore.exceptions import ClientError
from config.aws_config import AWSConfig


class VectorIndexManager:
    """Manages vector indices in OpenSearch Serverless for semantic search"""

    def __init__(self, aws_config: AWSConfig):
        """
        Initialize Vector Index Manager.

        Args:
            aws_config: AWSConfig instance for AWS client management
        """
        self.aws_config = aws_config
        self.oss_client = aws_config.get_client("opensearchserverless")
        self.account_id = aws_config.get_account_id()
        self.region = aws_config.get_region()

    def create_vector_index(
        self,
        collection_name: str,
        index_name: str,
        vector_field_name: str = "embedding",
        vector_dimension: int = 1536,
        similarity_metric: str = "cosine",
        description: str = "Vector index for semantic search"
    ) -> Dict[str, Any]:
        """
        Create a vector index in OpenSearch Serverless collection.

        Args:
            collection_name: Name of the OpenSearch Serverless collection
            index_name: Name of the vector index to create
            vector_field_name: Name of the vector field in documents (default: "embedding")
            vector_dimension: Dimension of the vector embeddings (default: 1536 for Titan)
            similarity_metric: Similarity metric for vector search ("cosine", "euclidean", "innerproduct")
            description: Description of the index

        Returns:
            Dictionary containing index creation information

        Raises:
            ValueError: If index creation fails
        """
        if vector_dimension not in [384, 768, 1024, 1536, 3072]:
            raise ValueError(
                f"Invalid vector dimension {vector_dimension}. "
                "Supported dimensions: 384, 768, 1024, 1536, 3072"
            )

        if similarity_metric not in ["cosine", "euclidean", "innerproduct"]:
            raise ValueError(
                f"Invalid similarity metric {similarity_metric}. "
                "Supported metrics: cosine, euclidean, innerproduct"
            )

        # Build index settings for semantic search
        index_settings = {
            "index": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "knn": True,
                "knn.algo_param.ef_construction": 256
            }
        }

        # Build index mappings with vector field
        index_mappings = {
            "properties": {
                vector_field_name: {
                    "type": "knn_vector",
                    "dimension": vector_dimension,
                    "method": {
                        "name": "hnsw",
                        "space_type": similarity_metric,
                        "engine": "nmslib",
                        "parameters": {
                            "ef_construction": 256,
                            "m": 16
                        }
                    }
                },
                "content": {
                    "type": "text"
                },
                "metadata": {
                    "type": "object",
                    "enabled": True
                },
                "document_id": {
                    "type": "keyword"
                },
                "chunk_index": {
                    "type": "integer"
                }
            }
        }

        index_body = {
            "settings": index_settings,
            "mappings": index_mappings
        }

        try:
            # Get collection endpoint
            collection_endpoint = self._get_collection_endpoint(collection_name)

            # Create index using OpenSearch API
            response = self.oss_client.create_index(
                collectionName=collection_name,
                indexName=index_name,
                indexBody=json.dumps(index_body)
            )

            return {
                "index_name": index_name,
                "collection_name": collection_name,
                "vector_field_name": vector_field_name,
                "vector_dimension": vector_dimension,
                "similarity_metric": similarity_metric,
                "status": "created",
                "description": description
            }
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceAlreadyExistsException":
                # Index already exists, return its info
                return {
                    "index_name": index_name,
                    "collection_name": collection_name,
                    "vector_field_name": vector_field_name,
                    "vector_dimension": vector_dimension,
                    "similarity_metric": similarity_metric,
                    "status": "already_exists",
                    "description": description
                }
            else:
                raise ValueError(f"Failed to create vector index: {str(e)}")

    def get_index_info(
        self,
        collection_name: str,
        index_name: str
    ) -> Dict[str, Any]:
        """
        Get information about a vector index.

        Args:
            collection_name: Name of the OpenSearch Serverless collection
            index_name: Name of the vector index

        Returns:
            Dictionary containing index information

        Raises:
            ValueError: If index cannot be retrieved
        """
        try:
            response = self.oss_client.get_index(
                collectionName=collection_name,
                indexName=index_name
            )

            index_body = json.loads(response.get("indexBody", "{}"))
            settings = index_body.get("settings", {})
            mappings = index_body.get("mappings", {})

            # Extract vector field information
            vector_field_info = {}
            for field_name, field_config in mappings.get("properties", {}).items():
                if field_config.get("type") == "knn_vector":
                    vector_field_info = {
                        "field_name": field_name,
                        "dimension": field_config.get("dimension"),
                        "method": field_config.get("method", {})
                    }
                    break

            return {
                "index_name": index_name,
                "collection_name": collection_name,
                "settings": settings,
                "mappings": mappings,
                "vector_field_info": vector_field_info,
                "status": "active"
            }
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                raise ValueError(f"Index '{index_name}' not found in collection '{collection_name}'")
            else:
                raise ValueError(f"Failed to get index information: {str(e)}")

    def update_index_settings(
        self,
        collection_name: str,
        index_name: str,
        settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update settings for a vector index.

        Args:
            collection_name: Name of the OpenSearch Serverless collection
            index_name: Name of the vector index
            settings: Dictionary of settings to update

        Returns:
            Dictionary containing updated index information

        Raises:
            ValueError: If update fails
        """
        try:
            response = self.oss_client.update_index(
                collectionName=collection_name,
                indexName=index_name,
                indexBody=json.dumps({"settings": settings})
            )

            return {
                "index_name": index_name,
                "collection_name": collection_name,
                "settings_updated": settings,
                "status": "updated"
            }
        except ClientError as e:
            raise ValueError(f"Failed to update index settings: {str(e)}")

    def delete_index(
        self,
        collection_name: str,
        index_name: str
    ) -> bool:
        """
        Delete a vector index from OpenSearch Serverless collection.

        Args:
            collection_name: Name of the OpenSearch Serverless collection
            index_name: Name of the vector index to delete

        Returns:
            True if index was deleted successfully

        Raises:
            ValueError: If deletion fails
        """
        try:
            self.oss_client.delete_index(
                collectionName=collection_name,
                indexName=index_name
            )
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                # Index doesn't exist, which is fine
                return True
            else:
                raise ValueError(f"Failed to delete vector index: {str(e)}")

    def list_indices(self, collection_name: str) -> List[Dict[str, Any]]:
        """
        List all indices in a collection.

        Args:
            collection_name: Name of the OpenSearch Serverless collection

        Returns:
            List of index information dictionaries

        Raises:
            ValueError: If listing fails
        """
        try:
            response = self.oss_client.list_indices(
                collectionName=collection_name
            )

            indices = []
            for index_summary in response.get("indexSummaries", []):
                indices.append({
                    "index_name": index_summary.get("name"),
                    "status": index_summary.get("status"),
                    "created_date": index_summary.get("createdDate")
                })

            return indices
        except ClientError as e:
            raise ValueError(f"Failed to list indices: {str(e)}")

    def validate_index_configuration(
        self,
        collection_name: str,
        index_name: str,
        expected_vector_dimension: int,
        expected_similarity_metric: str = "cosine"
    ) -> Dict[str, bool]:
        """
        Validate that an index is properly configured for semantic search.

        Args:
            collection_name: Name of the OpenSearch Serverless collection
            index_name: Name of the vector index
            expected_vector_dimension: Expected dimension of vector embeddings
            expected_similarity_metric: Expected similarity metric

        Returns:
            Dictionary with validation results

        Raises:
            ValueError: If validation fails
        """
        try:
            index_info = self.get_index_info(collection_name, index_name)
            vector_field_info = index_info.get("vector_field_info", {})

            results = {
                "index_exists": True,
                "has_vector_field": len(vector_field_info) > 0,
                "vector_dimension_correct": vector_field_info.get("dimension") == expected_vector_dimension,
                "similarity_metric_correct": vector_field_info.get("method", {}).get("space_type") == expected_similarity_metric,
                "knn_enabled": index_info.get("settings", {}).get("index", {}).get("knn", False)
            }

            return results
        except ValueError:
            return {
                "index_exists": False,
                "has_vector_field": False,
                "vector_dimension_correct": False,
                "similarity_metric_correct": False,
                "knn_enabled": False
            }

    def _get_collection_endpoint(self, collection_name: str) -> str:
        """
        Get the endpoint URL for an OpenSearch Serverless collection.

        Args:
            collection_name: Name of the collection

        Returns:
            Collection endpoint URL

        Raises:
            ValueError: If collection cannot be found
        """
        try:
            response = self.oss_client.batch_get_collection(
                names=[collection_name]
            )

            if response.get("collectionDetails"):
                collection = response["collectionDetails"][0]
                return collection.get("collectionEndpoint", "")
            else:
                raise ValueError(f"Collection '{collection_name}' not found")
        except ClientError as e:
            raise ValueError(f"Failed to get collection endpoint: {str(e)}")

    def configure_index_for_semantic_search(
        self,
        collection_name: str,
        index_name: str,
        vector_field_name: str = "embedding",
        vector_dimension: int = 1536,
        similarity_metric: str = "cosine"
    ) -> Dict[str, Any]:
        """
        Configure an index with optimal settings for semantic search.

        This is a convenience method that creates an index with recommended
        settings for semantic search using vector embeddings.

        Args:
            collection_name: Name of the OpenSearch Serverless collection
            index_name: Name of the vector index
            vector_field_name: Name of the vector field
            vector_dimension: Dimension of vector embeddings
            similarity_metric: Similarity metric for search

        Returns:
            Dictionary containing configuration information

        Raises:
            ValueError: If configuration fails
        """
        return self.create_vector_index(
            collection_name=collection_name,
            index_name=index_name,
            vector_field_name=vector_field_name,
            vector_dimension=vector_dimension,
            similarity_metric=similarity_metric,
            description="Configured for semantic search with vector embeddings"
        )

    def get_index_statistics(
        self,
        collection_name: str,
        index_name: str
    ) -> Dict[str, Any]:
        """
        Get statistics about a vector index.

        Args:
            collection_name: Name of the OpenSearch Serverless collection
            index_name: Name of the vector index

        Returns:
            Dictionary containing index statistics

        Raises:
            ValueError: If statistics cannot be retrieved
        """
        try:
            response = self.oss_client.get_index_stats(
                collectionName=collection_name,
                indexName=index_name
            )

            stats = response.get("stats", {})
            return {
                "index_name": index_name,
                "collection_name": collection_name,
                "document_count": stats.get("documentCount", 0),
                "storage_size_bytes": stats.get("storageSizeBytes", 0),
                "status": "active"
            }
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                # Index doesn't exist yet, return zero stats
                return {
                    "index_name": index_name,
                    "collection_name": collection_name,
                    "document_count": 0,
                    "storage_size_bytes": 0,
                    "status": "not_found"
                }
            else:
                raise ValueError(f"Failed to get index statistics: {str(e)}")

    def search_by_vector(
        self,
        collection_name: str,
        index_name: str,
        query_vector: List[float],
        vector_field_name: str = "embedding",
        k: int = 5,
        metadata_filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for documents by vector similarity.

        Args:
            collection_name: Name of the OpenSearch Serverless collection
            index_name: Name of the vector index
            query_vector: Query vector for similarity search
            vector_field_name: Name of the vector field in documents
            k: Number of results to return (default: 5)
            metadata_filters: Optional metadata filters to apply

        Returns:
            List of search results ranked by relevance score

        Raises:
            ValueError: If search fails
        """
        if k <= 0:
            raise ValueError("k must be greater than 0")

        if not query_vector or len(query_vector) == 0:
            raise ValueError("query_vector cannot be empty")

        # Build the KNN query
        query_body = {
            "size": k,
            "query": {
                "knn": {
                    vector_field_name: {
                        "vector": query_vector,
                        "k": k
                    }
                }
            }
        }

        # Add metadata filters if provided
        if metadata_filters:
            query_body["query"] = {
                "bool": {
                    "must": [
                        {
                            "knn": {
                                vector_field_name: {
                                    "vector": query_vector,
                                    "k": k
                                }
                            }
                        }
                    ],
                    "filter": self._build_filter_clause(metadata_filters)
                }
            }

        try:
            response = self.oss_client.search(
                collectionName=collection_name,
                indexName=index_name,
                body=json.dumps(query_body)
            )

            results = []
            hits = response.get("hits", {}).get("hits", [])

            for hit in hits:
                result = {
                    "id": hit.get("_id"),
                    "score": hit.get("_score", 0.0),
                    "content": hit.get("_source", {}).get("content", ""),
                    "metadata": hit.get("_source", {}).get("metadata", {}),
                    "document_id": hit.get("_source", {}).get("document_id", ""),
                    "chunk_index": hit.get("_source", {}).get("chunk_index")
                }
                results.append(result)

            # Sort by score in descending order
            results.sort(key=lambda x: x["score"], reverse=True)

            return results
        except ClientError as e:
            raise ValueError(f"Vector search failed: {str(e)}")

    def search_by_text(
        self,
        collection_name: str,
        index_name: str,
        query_text: str,
        k: int = 5,
        metadata_filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for documents by text similarity (keyword search).

        Args:
            collection_name: Name of the OpenSearch Serverless collection
            index_name: Name of the vector index
            query_text: Query text for keyword search
            k: Number of results to return (default: 5)
            metadata_filters: Optional metadata filters to apply

        Returns:
            List of search results ranked by relevance score

        Raises:
            ValueError: If search fails
        """
        if k <= 0:
            raise ValueError("k must be greater than 0")

        if not query_text or len(query_text.strip()) == 0:
            raise ValueError("query_text cannot be empty")

        # Build the text query
        query_body = {
            "size": k,
            "query": {
                "match": {
                    "content": {
                        "query": query_text,
                        "fuzziness": "AUTO"
                    }
                }
            }
        }

        # Add metadata filters if provided
        if metadata_filters:
            query_body["query"] = {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "content": {
                                    "query": query_text,
                                    "fuzziness": "AUTO"
                                }
                            }
                        }
                    ],
                    "filter": self._build_filter_clause(metadata_filters)
                }
            }

        try:
            response = self.oss_client.search(
                collectionName=collection_name,
                indexName=index_name,
                body=json.dumps(query_body)
            )

            results = []
            hits = response.get("hits", {}).get("hits", [])

            for hit in hits:
                result = {
                    "id": hit.get("_id"),
                    "score": hit.get("_score", 0.0),
                    "content": hit.get("_source", {}).get("content", ""),
                    "metadata": hit.get("_source", {}).get("metadata", {}),
                    "document_id": hit.get("_source", {}).get("document_id", ""),
                    "chunk_index": hit.get("_source", {}).get("chunk_index")
                }
                results.append(result)

            # Sort by score in descending order
            results.sort(key=lambda x: x["score"], reverse=True)

            return results
        except ClientError as e:
            raise ValueError(f"Text search failed: {str(e)}")

    def hybrid_search(
        self,
        collection_name: str,
        index_name: str,
        query_vector: List[float],
        query_text: str,
        vector_field_name: str = "embedding",
        k: int = 5,
        vector_weight: float = 0.5,
        text_weight: float = 0.5,
        metadata_filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining vector and text similarity.

        Args:
            collection_name: Name of the OpenSearch Serverless collection
            index_name: Name of the vector index
            query_vector: Query vector for similarity search
            query_text: Query text for keyword search
            vector_field_name: Name of the vector field in documents
            k: Number of results to return (default: 5)
            vector_weight: Weight for vector search results (0.0-1.0)
            text_weight: Weight for text search results (0.0-1.0)
            metadata_filters: Optional metadata filters to apply

        Returns:
            List of search results ranked by combined relevance score

        Raises:
            ValueError: If search fails
        """
        if k <= 0:
            raise ValueError("k must be greater than 0")

        if not query_vector or len(query_vector) == 0:
            raise ValueError("query_vector cannot be empty")

        if not query_text or len(query_text.strip()) == 0:
            raise ValueError("query_text cannot be empty")

        if vector_weight < 0.0 or vector_weight > 1.0:
            raise ValueError("vector_weight must be between 0.0 and 1.0")

        if text_weight < 0.0 or text_weight > 1.0:
            raise ValueError("text_weight must be between 0.0 and 1.0")

        # Normalize weights
        total_weight = vector_weight + text_weight
        if total_weight == 0:
            raise ValueError("At least one weight must be greater than 0")

        vector_weight = vector_weight / total_weight
        text_weight = text_weight / total_weight

        # Perform both searches
        vector_results = self.search_by_vector(
            collection_name=collection_name,
            index_name=index_name,
            query_vector=query_vector,
            vector_field_name=vector_field_name,
            k=k,
            metadata_filters=metadata_filters
        )

        text_results = self.search_by_text(
            collection_name=collection_name,
            index_name=index_name,
            query_text=query_text,
            k=k,
            metadata_filters=metadata_filters
        )

        # Combine results with weighted scores
        combined_results = {}

        for result in vector_results:
            doc_id = result["id"]
            combined_results[doc_id] = result.copy()
            combined_results[doc_id]["combined_score"] = result["score"] * vector_weight

        for result in text_results:
            doc_id = result["id"]
            if doc_id in combined_results:
                combined_results[doc_id]["combined_score"] += result["score"] * text_weight
            else:
                combined_results[doc_id] = result.copy()
                combined_results[doc_id]["combined_score"] = result["score"] * text_weight

        # Sort by combined score and return top k
        sorted_results = sorted(
            combined_results.values(),
            key=lambda x: x["combined_score"],
            reverse=True
        )[:k]

        return sorted_results

    def _build_filter_clause(self, metadata_filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Build OpenSearch filter clause from metadata filters.

        Args:
            metadata_filters: Dictionary of metadata filters

        Returns:
            List of filter clauses for OpenSearch query

        Raises:
            ValueError: If filter construction fails
        """
        filters = []

        for key, value in metadata_filters.items():
            if value is None:
                continue

            if isinstance(value, list):
                # For list values, use terms query
                filters.append({
                    "terms": {
                        f"metadata.{key}": value
                    }
                })
            elif isinstance(value, str):
                # For string values, use term query
                filters.append({
                    "term": {
                        f"metadata.{key}": value
                    }
                })
            elif isinstance(value, (int, float)):
                # For numeric values, use term query
                filters.append({
                    "term": {
                        f"metadata.{key}": value
                    }
                })
            elif isinstance(value, bool):
                # For boolean values, use term query
                filters.append({
                    "term": {
                        f"metadata.{key}": value
                    }
                })

        return filters
