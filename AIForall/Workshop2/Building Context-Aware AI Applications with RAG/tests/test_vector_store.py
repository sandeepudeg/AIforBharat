"""Tests for vector store and index management"""

import pytest
import json
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError
from src.vector_store import VectorIndexManager


class TestVectorIndexManagerInitialization:
    """Tests for Vector Index Manager initialization"""

    def test_init_with_aws_config(self, mock_opensearch_client):
        """Test Vector Index Manager initialization with AWS config"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = VectorIndexManager(config)

                    assert manager.aws_config is config
                    assert manager.oss_client is mock_opensearch_client
                    assert manager.account_id == '123456789012'
                    assert manager.region == 'us-east-1'


class TestCreateVectorIndex:
    """Tests for vector index creation"""

    def test_create_vector_index_success(self, mock_opensearch_client):
        """Test successful creation of vector index"""
        from config.aws_config import AWSConfig

        mock_opensearch_client.create_index.return_value = {
            "indexStatus": "CREATING"
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = VectorIndexManager(config)
                    result = manager.create_vector_index(
                        collection_name="test-collection",
                        index_name="test-index",
                        vector_dimension=1536
                    )

                    assert result["index_name"] == "test-index"
                    assert result["collection_name"] == "test-collection"
                    assert result["vector_dimension"] == 1536
                    assert result["status"] == "created"

    def test_create_vector_index_with_custom_settings(self, mock_opensearch_client):
        """Test vector index creation with custom settings"""
        from config.aws_config import AWSConfig

        mock_opensearch_client.create_index.return_value = {
            "indexStatus": "CREATING"
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = VectorIndexManager(config)
                    result = manager.create_vector_index(
                        collection_name="test-collection",
                        index_name="test-index",
                        vector_field_name="embeddings",
                        vector_dimension=768,
                        similarity_metric="euclidean"
                    )

                    assert result["vector_field_name"] == "embeddings"
                    assert result["vector_dimension"] == 768
                    assert result["similarity_metric"] == "euclidean"

    def test_create_vector_index_invalid_dimension(self, mock_opensearch_client):
        """Test vector index creation with invalid dimension"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = VectorIndexManager(config)

                    with pytest.raises(ValueError, match="Invalid vector dimension"):
                        manager.create_vector_index(
                            collection_name="test-collection",
                            index_name="test-index",
                            vector_dimension=512  # Invalid dimension
                        )

    def test_create_vector_index_invalid_similarity_metric(self, mock_opensearch_client):
        """Test vector index creation with invalid similarity metric"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = VectorIndexManager(config)

                    with pytest.raises(ValueError, match="Invalid similarity metric"):
                        manager.create_vector_index(
                            collection_name="test-collection",
                            index_name="test-index",
                            similarity_metric="invalid_metric"
                        )

    def test_create_vector_index_already_exists(self, mock_opensearch_client):
        """Test creation when vector index already exists"""
        from config.aws_config import AWSConfig

        error_response = {"Error": {"Code": "ResourceAlreadyExistsException", "Message": "Index already exists"}}
        mock_opensearch_client.create_index.side_effect = ClientError(error_response, "CreateIndex")

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = VectorIndexManager(config)
                    result = manager.create_vector_index(
                        collection_name="test-collection",
                        index_name="test-index"
                    )

                    assert result["status"] == "already_exists"

    def test_create_vector_index_failure(self, mock_opensearch_client):
        """Test vector index creation failure"""
        from config.aws_config import AWSConfig

        error_response = {"Error": {"Code": "AccessDenied", "Message": "User is not authorized"}}
        mock_opensearch_client.create_index.side_effect = ClientError(error_response, "CreateIndex")

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = VectorIndexManager(config)

                    with pytest.raises(ValueError, match="Failed to create vector index"):
                        manager.create_vector_index(
                            collection_name="test-collection",
                            index_name="test-index"
                        )


class TestGetIndexInfo:
    """Tests for retrieving index information"""

    def test_get_index_info_success(self, mock_opensearch_client):
        """Test successful retrieval of index information"""
        from config.aws_config import AWSConfig

        index_body = {
            "settings": {
                "index": {
                    "number_of_shards": 1,
                    "knn": True
                }
            },
            "mappings": {
                "properties": {
                    "embedding": {
                        "type": "knn_vector",
                        "dimension": 1536,
                        "method": {
                            "name": "hnsw",
                            "space_type": "cosine"
                        }
                    }
                }
            }
        }

        mock_opensearch_client.get_index.return_value = {
            "indexBody": json.dumps(index_body)
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = VectorIndexManager(config)
                    result = manager.get_index_info(
                        collection_name="test-collection",
                        index_name="test-index"
                    )

                    assert result["index_name"] == "test-index"
                    assert result["collection_name"] == "test-collection"
                    assert result["status"] == "active"
                    assert result["vector_field_info"]["field_name"] == "embedding"
                    assert result["vector_field_info"]["dimension"] == 1536

    def test_get_index_info_not_found(self, mock_opensearch_client):
        """Test retrieval of non-existent index"""
        from config.aws_config import AWSConfig

        error_response = {"Error": {"Code": "ResourceNotFoundException", "Message": "Index not found"}}
        mock_opensearch_client.get_index.side_effect = ClientError(error_response, "GetIndex")

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = VectorIndexManager(config)

                    with pytest.raises(ValueError, match="not found"):
                        manager.get_index_info(
                            collection_name="test-collection",
                            index_name="test-index"
                        )


class TestUpdateIndexSettings:
    """Tests for updating index settings"""

    def test_update_index_settings_success(self, mock_opensearch_client):
        """Test successful update of index settings"""
        from config.aws_config import AWSConfig

        mock_opensearch_client.update_index.return_value = {}

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = VectorIndexManager(config)
                    settings = {
                        "index": {
                            "number_of_replicas": 1
                        }
                    }
                    result = manager.update_index_settings(
                        collection_name="test-collection",
                        index_name="test-index",
                        settings=settings
                    )

                    assert result["status"] == "updated"
                    assert result["settings_updated"] == settings

    def test_update_index_settings_failure(self, mock_opensearch_client):
        """Test index settings update failure"""
        from config.aws_config import AWSConfig

        error_response = {"Error": {"Code": "AccessDenied", "Message": "User is not authorized"}}
        mock_opensearch_client.update_index.side_effect = ClientError(error_response, "UpdateIndex")

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = VectorIndexManager(config)

                    with pytest.raises(ValueError, match="Failed to update index settings"):
                        manager.update_index_settings(
                            collection_name="test-collection",
                            index_name="test-index",
                            settings={}
                        )


class TestDeleteIndex:
    """Tests for index deletion"""

    def test_delete_index_success(self, mock_opensearch_client):
        """Test successful deletion of vector index"""
        from config.aws_config import AWSConfig

        mock_opensearch_client.delete_index.return_value = {}

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = VectorIndexManager(config)
                    result = manager.delete_index(
                        collection_name="test-collection",
                        index_name="test-index"
                    )

                    assert result is True
                    mock_opensearch_client.delete_index.assert_called_once()

    def test_delete_index_not_found(self, mock_opensearch_client):
        """Test deletion of non-existent index"""
        from config.aws_config import AWSConfig

        error_response = {"Error": {"Code": "ResourceNotFoundException", "Message": "Index not found"}}
        mock_opensearch_client.delete_index.side_effect = ClientError(error_response, "DeleteIndex")

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = VectorIndexManager(config)
                    result = manager.delete_index(
                        collection_name="test-collection",
                        index_name="test-index"
                    )

                    # Should return True even if index doesn't exist
                    assert result is True

    def test_delete_index_failure(self, mock_opensearch_client):
        """Test index deletion failure"""
        from config.aws_config import AWSConfig

        error_response = {"Error": {"Code": "AccessDenied", "Message": "User is not authorized"}}
        mock_opensearch_client.delete_index.side_effect = ClientError(error_response, "DeleteIndex")

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = VectorIndexManager(config)

                    with pytest.raises(ValueError, match="Failed to delete vector index"):
                        manager.delete_index(
                            collection_name="test-collection",
                            index_name="test-index"
                        )


class TestListIndices:
    """Tests for listing indices"""

    def test_list_indices_success(self, mock_opensearch_client):
        """Test successful listing of indices"""
        from config.aws_config import AWSConfig

        mock_opensearch_client.list_indices.return_value = {
            "indexSummaries": [
                {
                    "name": "test-index-1",
                    "status": "ACTIVE",
                    "createdDate": 1234567890
                },
                {
                    "name": "test-index-2",
                    "status": "ACTIVE",
                    "createdDate": 1234567891
                }
            ]
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = VectorIndexManager(config)
                    result = manager.list_indices(collection_name="test-collection")

                    assert len(result) == 2
                    assert result[0]["index_name"] == "test-index-1"
                    assert result[1]["index_name"] == "test-index-2"

    def test_list_indices_empty(self, mock_opensearch_client):
        """Test listing indices when none exist"""
        from config.aws_config import AWSConfig

        mock_opensearch_client.list_indices.return_value = {
            "indexSummaries": []
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = VectorIndexManager(config)
                    result = manager.list_indices(collection_name="test-collection")

                    assert len(result) == 0

    def test_list_indices_failure(self, mock_opensearch_client):
        """Test listing indices failure"""
        from config.aws_config import AWSConfig

        error_response = {"Error": {"Code": "AccessDenied", "Message": "User is not authorized"}}
        mock_opensearch_client.list_indices.side_effect = ClientError(error_response, "ListIndices")

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = VectorIndexManager(config)

                    with pytest.raises(ValueError, match="Failed to list indices"):
                        manager.list_indices(collection_name="test-collection")


class TestValidateIndexConfiguration:
    """Tests for index configuration validation"""

    def test_validate_index_configuration_valid(self, mock_opensearch_client):
        """Test validation of properly configured index"""
        from config.aws_config import AWSConfig

        index_body = {
            "settings": {
                "index": {
                    "knn": True
                }
            },
            "mappings": {
                "properties": {
                    "embedding": {
                        "type": "knn_vector",
                        "dimension": 1536,
                        "method": {
                            "space_type": "cosine"
                        }
                    }
                }
            }
        }

        mock_opensearch_client.get_index.return_value = {
            "indexBody": json.dumps(index_body)
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = VectorIndexManager(config)
                    result = manager.validate_index_configuration(
                        collection_name="test-collection",
                        index_name="test-index",
                        expected_vector_dimension=1536,
                        expected_similarity_metric="cosine"
                    )

                    assert result["index_exists"] is True
                    assert result["has_vector_field"] is True
                    assert result["vector_dimension_correct"] is True
                    assert result["similarity_metric_correct"] is True
                    assert result["knn_enabled"] is True

    def test_validate_index_configuration_not_found(self, mock_opensearch_client):
        """Test validation of non-existent index"""
        from config.aws_config import AWSConfig

        error_response = {"Error": {"Code": "ResourceNotFoundException", "Message": "Index not found"}}
        mock_opensearch_client.get_index.side_effect = ClientError(error_response, "GetIndex")

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = VectorIndexManager(config)
                    result = manager.validate_index_configuration(
                        collection_name="test-collection",
                        index_name="test-index",
                        expected_vector_dimension=1536
                    )

                    assert result["index_exists"] is False
                    assert result["has_vector_field"] is False


class TestConfigureIndexForSemanticSearch:
    """Tests for semantic search configuration"""

    def test_configure_index_for_semantic_search_success(self, mock_opensearch_client):
        """Test successful configuration for semantic search"""
        from config.aws_config import AWSConfig

        mock_opensearch_client.create_index.return_value = {
            "indexStatus": "CREATING"
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = VectorIndexManager(config)
                    result = manager.configure_index_for_semantic_search(
                        collection_name="test-collection",
                        index_name="test-index"
                    )

                    assert result["status"] == "created"
                    assert "semantic search" in result["description"].lower()


class TestGetIndexStatistics:
    """Tests for index statistics retrieval"""

    def test_get_index_statistics_success(self, mock_opensearch_client):
        """Test successful retrieval of index statistics"""
        from config.aws_config import AWSConfig

        mock_opensearch_client.get_index_stats.return_value = {
            "stats": {
                "documentCount": 1000,
                "storageSizeBytes": 5242880
            }
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = VectorIndexManager(config)
                    result = manager.get_index_statistics(
                        collection_name="test-collection",
                        index_name="test-index"
                    )

                    assert result["document_count"] == 1000
                    assert result["storage_size_bytes"] == 5242880
                    assert result["status"] == "active"

    def test_get_index_statistics_not_found(self, mock_opensearch_client):
        """Test statistics retrieval for non-existent index"""
        from config.aws_config import AWSConfig

        error_response = {"Error": {"Code": "ResourceNotFoundException", "Message": "Index not found"}}
        mock_opensearch_client.get_index_stats.side_effect = ClientError(error_response, "GetIndexStats")

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = VectorIndexManager(config)
                    result = manager.get_index_statistics(
                        collection_name="test-collection",
                        index_name="test-index"
                    )

                    assert result["document_count"] == 0
                    assert result["storage_size_bytes"] == 0
                    assert result["status"] == "not_found"

    def test_get_index_statistics_failure(self, mock_opensearch_client):
        """Test statistics retrieval failure"""
        from config.aws_config import AWSConfig

        error_response = {"Error": {"Code": "AccessDenied", "Message": "User is not authorized"}}
        mock_opensearch_client.get_index_stats.side_effect = ClientError(error_response, "GetIndexStats")

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = VectorIndexManager(config)

                    with pytest.raises(ValueError, match="Failed to get index statistics"):
                        manager.get_index_statistics(
                            collection_name="test-collection",
                            index_name="test-index"
                        )


class TestVectorSearch:
    """Tests for vector similarity search"""

    def test_search_by_vector_success(self, mock_opensearch_client):
        """Test successful vector search"""
        from config.aws_config import AWSConfig

        mock_opensearch_client.search.return_value = {
            "hits": {
                "hits": [
                    {
                        "_id": "doc-1",
                        "_score": 0.95,
                        "_source": {
                            "content": "Document 1 content",
                            "metadata": {"source": "s3://bucket/doc1.txt"},
                            "document_id": "doc-1",
                            "chunk_index": 0
                        }
                    },
                    {
                        "_id": "doc-2",
                        "_score": 0.85,
                        "_source": {
                            "content": "Document 2 content",
                            "metadata": {"source": "s3://bucket/doc2.txt"},
                            "document_id": "doc-2",
                            "chunk_index": 0
                        }
                    }
                ]
            }
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = VectorIndexManager(config)
                    query_vector = [0.1] * 1536
                    results = manager.search_by_vector(
                        collection_name="test-collection",
                        index_name="test-index",
                        query_vector=query_vector,
                        k=5
                    )

                    assert len(results) == 2
                    assert results[0]["score"] == 0.95
                    assert results[1]["score"] == 0.85
                    assert results[0]["score"] >= results[1]["score"]

    def test_search_by_vector_with_metadata_filters(self, mock_opensearch_client):
        """Test vector search with metadata filters"""
        from config.aws_config import AWSConfig

        mock_opensearch_client.search.return_value = {
            "hits": {
                "hits": [
                    {
                        "_id": "doc-1",
                        "_score": 0.95,
                        "_source": {
                            "content": "Document 1 content",
                            "metadata": {"source": "s3://bucket/doc1.txt", "source_type": "S3"},
                            "document_id": "doc-1",
                            "chunk_index": 0
                        }
                    }
                ]
            }
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = VectorIndexManager(config)
                    query_vector = [0.1] * 1536
                    results = manager.search_by_vector(
                        collection_name="test-collection",
                        index_name="test-index",
                        query_vector=query_vector,
                        k=5,
                        metadata_filters={"source_type": "S3"}
                    )

                    assert len(results) == 1
                    assert results[0]["metadata"]["source_type"] == "S3"

    def test_search_by_vector_invalid_k(self, mock_opensearch_client):
        """Test vector search with invalid k"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = VectorIndexManager(config)
                    query_vector = [0.1] * 1536

                    with pytest.raises(ValueError, match="k must be greater than 0"):
                        manager.search_by_vector(
                            collection_name="test-collection",
                            index_name="test-index",
                            query_vector=query_vector,
                            k=0
                        )

    def test_search_by_vector_empty_query_vector(self, mock_opensearch_client):
        """Test vector search with empty query vector"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = VectorIndexManager(config)

                    with pytest.raises(ValueError, match="query_vector cannot be empty"):
                        manager.search_by_vector(
                            collection_name="test-collection",
                            index_name="test-index",
                            query_vector=[],
                            k=5
                        )

    def test_search_by_vector_failure(self, mock_opensearch_client):
        """Test vector search failure"""
        from config.aws_config import AWSConfig

        error_response = {"Error": {"Code": "AccessDenied", "Message": "User is not authorized"}}
        mock_opensearch_client.search.side_effect = ClientError(error_response, "Search")

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = VectorIndexManager(config)
                    query_vector = [0.1] * 1536

                    with pytest.raises(ValueError, match="Vector search failed"):
                        manager.search_by_vector(
                            collection_name="test-collection",
                            index_name="test-index",
                            query_vector=query_vector,
                            k=5
                        )


class TestTextSearch:
    """Tests for text similarity search"""

    def test_search_by_text_success(self, mock_opensearch_client):
        """Test successful text search"""
        from config.aws_config import AWSConfig

        mock_opensearch_client.search.return_value = {
            "hits": {
                "hits": [
                    {
                        "_id": "doc-1",
                        "_score": 0.95,
                        "_source": {
                            "content": "Document about machine learning",
                            "metadata": {"source": "s3://bucket/doc1.txt"},
                            "document_id": "doc-1",
                            "chunk_index": 0
                        }
                    },
                    {
                        "_id": "doc-2",
                        "_score": 0.85,
                        "_source": {
                            "content": "Document about deep learning",
                            "metadata": {"source": "s3://bucket/doc2.txt"},
                            "document_id": "doc-2",
                            "chunk_index": 0
                        }
                    }
                ]
            }
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = VectorIndexManager(config)
                    results = manager.search_by_text(
                        collection_name="test-collection",
                        index_name="test-index",
                        query_text="machine learning",
                        k=5
                    )

                    assert len(results) == 2
                    assert results[0]["score"] == 0.95
                    assert results[1]["score"] == 0.85

    def test_search_by_text_empty_query(self, mock_opensearch_client):
        """Test text search with empty query"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = VectorIndexManager(config)

                    with pytest.raises(ValueError, match="query_text cannot be empty"):
                        manager.search_by_text(
                            collection_name="test-collection",
                            index_name="test-index",
                            query_text="",
                            k=5
                        )

    def test_search_by_text_failure(self, mock_opensearch_client):
        """Test text search failure"""
        from config.aws_config import AWSConfig

        error_response = {"Error": {"Code": "AccessDenied", "Message": "User is not authorized"}}
        mock_opensearch_client.search.side_effect = ClientError(error_response, "Search")

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = VectorIndexManager(config)

                    with pytest.raises(ValueError, match="Text search failed"):
                        manager.search_by_text(
                            collection_name="test-collection",
                            index_name="test-index",
                            query_text="test query",
                            k=5
                        )


class TestHybridSearch:
    """Tests for hybrid search combining vector and text"""

    def test_hybrid_search_success(self, mock_opensearch_client):
        """Test successful hybrid search"""
        from config.aws_config import AWSConfig

        mock_opensearch_client.search.return_value = {
            "hits": {
                "hits": [
                    {
                        "_id": "doc-1",
                        "_score": 0.95,
                        "_source": {
                            "content": "Document about machine learning",
                            "metadata": {"source": "s3://bucket/doc1.txt"},
                            "document_id": "doc-1",
                            "chunk_index": 0
                        }
                    }
                ]
            }
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = VectorIndexManager(config)
                    query_vector = [0.1] * 1536
                    results = manager.hybrid_search(
                        collection_name="test-collection",
                        index_name="test-index",
                        query_vector=query_vector,
                        query_text="machine learning",
                        k=5
                    )

                    assert len(results) >= 1
                    assert "combined_score" in results[0]

    def test_hybrid_search_invalid_weights(self, mock_opensearch_client):
        """Test hybrid search with invalid weights"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = VectorIndexManager(config)
                    query_vector = [0.1] * 1536

                    with pytest.raises(ValueError, match="vector_weight must be between"):
                        manager.hybrid_search(
                            collection_name="test-collection",
                            index_name="test-index",
                            query_vector=query_vector,
                            query_text="test",
                            vector_weight=1.5
                        )

    def test_hybrid_search_zero_weights(self, mock_opensearch_client):
        """Test hybrid search with zero weights"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = VectorIndexManager(config)
                    query_vector = [0.1] * 1536

                    with pytest.raises(ValueError, match="At least one weight must be greater than 0"):
                        manager.hybrid_search(
                            collection_name="test-collection",
                            index_name="test-index",
                            query_vector=query_vector,
                            query_text="test",
                            vector_weight=0.0,
                            text_weight=0.0
                        )
