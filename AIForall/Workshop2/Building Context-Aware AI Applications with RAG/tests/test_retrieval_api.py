"""Tests for Retrieve API"""

import pytest
from unittest.mock import MagicMock, patch
from src.retrieval_api import RetrieveAPI, RetrievalConfig, RetrievalType, RetrievalResult
from config.aws_config import AWSConfig
import os

# Disable hypothesis database to avoid Windows hanging issues
os.environ['HYPOTHESIS_DATABASE_DIRECTORY'] = 'none'


class TestRetrievalConfig:
    """Tests for RetrievalConfig"""

    def test_default_config(self):
        """Test default retrieval configuration"""
        config = RetrievalConfig()
        assert config.max_results == 5
        assert config.retrieval_type == RetrievalType.SEMANTIC
        assert config.vector_weight == 0.5
        assert config.text_weight == 0.5
        assert config.min_relevance_score == 0.0

    def test_custom_config(self):
        """Test custom retrieval configuration"""
        config = RetrievalConfig(
            max_results=10,
            retrieval_type=RetrievalType.HYBRID,
            vector_weight=0.6,
            text_weight=0.4,
            min_relevance_score=0.5
        )
        assert config.max_results == 10
        assert config.retrieval_type == RetrievalType.HYBRID
        assert config.vector_weight == 0.6
        assert config.text_weight == 0.4
        assert config.min_relevance_score == 0.5

    def test_config_validation_invalid_max_results(self):
        """Test config validation with invalid max_results"""
        config = RetrievalConfig(max_results=0)
        with pytest.raises(ValueError, match="max_results must be greater than 0"):
            config.validate()

    def test_config_validation_invalid_vector_weight(self):
        """Test config validation with invalid vector_weight"""
        config = RetrievalConfig(vector_weight=1.5)
        with pytest.raises(ValueError, match="vector_weight must be between 0.0 and 1.0"):
            config.validate()

    def test_config_validation_invalid_text_weight(self):
        """Test config validation with invalid text_weight"""
        config = RetrievalConfig(text_weight=-0.1)
        with pytest.raises(ValueError, match="text_weight must be between 0.0 and 1.0"):
            config.validate()

    def test_config_validation_invalid_min_relevance_score(self):
        """Test config validation with invalid min_relevance_score"""
        config = RetrievalConfig(min_relevance_score=1.5)
        with pytest.raises(ValueError, match="min_relevance_score must be between 0.0 and 1.0"):
            config.validate()

    def test_config_validation_success(self):
        """Test successful config validation"""
        config = RetrievalConfig()
        assert config.validate() is True


class TestRetrievalResult:
    """Tests for RetrievalResult"""

    def test_result_creation(self):
        """Test creating a retrieval result"""
        result = RetrievalResult(
            chunk_id="chunk-001",
            content="Sample content",
            relevance_score=0.95,
            location="s3://bucket/doc.txt",
            metadata={"source": "s3"},
            source_document="doc-001"
        )
        assert result.chunk_id == "chunk-001"
        assert result.content == "Sample content"
        assert result.relevance_score == 0.95

    def test_result_to_dict(self):
        """Test converting result to dictionary"""
        result = RetrievalResult(
            chunk_id="chunk-001",
            content="Sample content",
            relevance_score=0.95,
            location="s3://bucket/doc.txt",
            metadata={"source": "s3"},
            source_document="doc-001"
        )
        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert result_dict["chunk_id"] == "chunk-001"
        assert result_dict["relevance_score"] == 0.95


class TestRetrieveAPI:
    """Tests for Retrieve API"""

    def test_init_with_aws_config(self, mock_bedrock_client):
        """Test Retrieve API initialization"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    api = RetrieveAPI(config)

                    assert api.aws_config is config
                    assert api.vector_store is not None
                    assert api.bedrock_client is not None

    @pytest.mark.parametrize("max_results,retrieval_type", [
        (5, RetrievalType.SEMANTIC),
        (10, RetrievalType.KEYWORD),
        (3, RetrievalType.HYBRID)
    ])
    def test_retrieve_with_bedrock_api(self, max_results, retrieval_type, mock_bedrock_client):
        """Test retrieve using Bedrock API"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.retrieve.return_value = {
            "retrievalResults": [
                {
                    "content": "Document 1 content",
                    "score": 0.95,
                    "retrievalResultMetadata": {
                        "location": {
                            "s3Location": {
                                "uri": "s3://bucket/doc1.txt"
                            }
                        },
                        "document": {
                            "documentId": "doc-001"
                        }
                    }
                },
                {
                    "content": "Document 2 content",
                    "score": 0.85,
                    "retrievalResultMetadata": {
                        "location": {
                            "s3Location": {
                                "uri": "s3://bucket/doc2.txt"
                            }
                        },
                        "document": {
                            "documentId": "doc-002"
                        }
                    }
                }
            ]
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    api = RetrieveAPI(config)

                    config = RetrievalConfig(
                        max_results=max_results,
                        retrieval_type=retrieval_type
                    )

                    results = api.retrieve(
                        knowledge_base_id="kb-12345",
                        query="test query",
                        config=config
                    )

                    assert len(results) <= max_results
                    assert all(isinstance(r, RetrievalResult) for r in results)
                    assert results[0].relevance_score >= results[-1].relevance_score

    def test_retrieve_with_vector_search(self, mock_opensearch_client):
        """Test retrieve using vector search"""
        from config.aws_config import AWSConfig

        mock_opensearch_client.search.return_value = {
            "hits": {
                "hits": [
                    {
                        "_id": "chunk-001",
                        "_score": 0.95,
                        "_source": {
                            "content": "Vector search result 1",
                            "metadata": {"source": "s3://bucket/doc1.txt"},
                            "document_id": "doc-001",
                            "chunk_index": 0
                        }
                    },
                    {
                        "_id": "chunk-002",
                        "_score": 0.85,
                        "_source": {
                            "content": "Vector search result 2",
                            "metadata": {"source": "s3://bucket/doc2.txt"},
                            "document_id": "doc-002",
                            "chunk_index": 0
                        }
                    }
                ]
            }
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_opensearch_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    api = RetrieveAPI(config)

                    query_vector = [0.1] * 1536
                    results = api.retrieve_with_vector(
                        collection_name="test-collection",
                        index_name="test-index",
                        query_vector=query_vector
                    )

                    assert len(results) > 0
                    assert all(isinstance(r, RetrievalResult) for r in results)
                    assert results[0].relevance_score >= results[-1].relevance_score

    def test_retrieve_with_text_search(self, mock_opensearch_client):
        """Test retrieve using text search"""
        from config.aws_config import AWSConfig

        mock_opensearch_client.search.return_value = {
            "hits": {
                "hits": [
                    {
                        "_id": "chunk-001",
                        "_score": 0.90,
                        "_source": {
                            "content": "Text search result 1",
                            "metadata": {"source": "s3://bucket/doc1.txt"},
                            "document_id": "doc-001",
                            "chunk_index": 0
                        }
                    }
                ]
            }
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_opensearch_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    api = RetrieveAPI(config)

                    results = api.retrieve_with_text(
                        collection_name="test-collection",
                        index_name="test-index",
                        query_text="test query"
                    )

                    assert len(results) > 0
                    assert all(isinstance(r, RetrievalResult) for r in results)

    @pytest.mark.parametrize("max_results", [1, 5, 10])
    def test_retrieve_respects_max_results(self, max_results, mock_opensearch_client):
        """Test that retrieve respects max_results parameter"""
        from config.aws_config import AWSConfig

        # Create mock results
        mock_hits = []
        for i in range(20):
            mock_hits.append({
                "_id": f"chunk-{i:03d}",
                "_score": 1.0 - (i * 0.05),
                "_source": {
                    "content": f"Result {i}",
                    "metadata": {"source": f"s3://bucket/doc{i}.txt"},
                    "document_id": f"doc-{i:03d}",
                    "chunk_index": 0
                }
            })

        mock_opensearch_client.search.return_value = {
            "hits": {"hits": mock_hits}
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_opensearch_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    api = RetrieveAPI(config)

                    config = RetrievalConfig(max_results=max_results)
                    results = api.retrieve_with_vector(
                        collection_name="test-collection",
                        index_name="test-index",
                        query_vector=[0.1] * 1536,
                        config=config
                    )

                    assert len(results) <= max_results

    def test_retrieve_filters_by_min_relevance_score(self, mock_opensearch_client):
        """Test that retrieve filters by minimum relevance score"""
        from config.aws_config import AWSConfig

        mock_opensearch_client.search.return_value = {
            "hits": {
                "hits": [
                    {
                        "_id": "chunk-001",
                        "_score": 0.95,
                        "_source": {
                            "content": "High relevance result",
                            "metadata": {"source": "s3://bucket/doc1.txt"},
                            "document_id": "doc-001",
                            "chunk_index": 0
                        }
                    },
                    {
                        "_id": "chunk-002",
                        "_score": 0.3,
                        "_source": {
                            "content": "Low relevance result",
                            "metadata": {"source": "s3://bucket/doc2.txt"},
                            "document_id": "doc-002",
                            "chunk_index": 0
                        }
                    }
                ]
            }
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_opensearch_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    api = RetrieveAPI(config)

                    config = RetrievalConfig(min_relevance_score=0.5)
                    results = api.retrieve_with_vector(
                        collection_name="test-collection",
                        index_name="test-index",
                        query_vector=[0.1] * 1536,
                        config=config
                    )

                    # Only high relevance result should be returned
                    assert len(results) == 1
                    assert results[0].relevance_score >= 0.5

    def test_retrieve_results_sorted_by_relevance(self, mock_opensearch_client):
        """Test that retrieve results are sorted by relevance score"""
        from config.aws_config import AWSConfig

        mock_opensearch_client.search.return_value = {
            "hits": {
                "hits": [
                    {
                        "_id": "chunk-001",
                        "_score": 0.95,
                        "_source": {
                            "content": "Result 1",
                            "metadata": {"source": "s3://bucket/doc1.txt"},
                            "document_id": "doc-001",
                            "chunk_index": 0
                        }
                    },
                    {
                        "_id": "chunk-002",
                        "_score": 0.85,
                        "_source": {
                            "content": "Result 2",
                            "metadata": {"source": "s3://bucket/doc2.txt"},
                            "document_id": "doc-002",
                            "chunk_index": 0
                        }
                    },
                    {
                        "_id": "chunk-003",
                        "_score": 0.75,
                        "_source": {
                            "content": "Result 3",
                            "metadata": {"source": "s3://bucket/doc3.txt"},
                            "document_id": "doc-003",
                            "chunk_index": 0
                        }
                    }
                ]
            }
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_opensearch_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    api = RetrieveAPI(config)

                    results = api.retrieve_with_vector(
                        collection_name="test-collection",
                        index_name="test-index",
                        query_vector=[0.1] * 1536
                    )

                    # Verify results are sorted in descending order by relevance
                    for i in range(len(results) - 1):
                        assert results[i].relevance_score >= results[i + 1].relevance_score
