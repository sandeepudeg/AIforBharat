"""Pytest configuration and fixtures for Bedrock RAG Retrieval System"""

import pytest
from unittest.mock import MagicMock, patch
import json
from datetime import datetime
import sys
import os

# Disable hypothesis database to avoid Windows hanging issues
os.environ['HYPOTHESIS_DATABASE_DIRECTORY'] = 'none'


# ============================================================================
# AWS Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_bedrock_client():
    """Mock Bedrock client for testing"""
    with patch('boto3.client') as mock_client:
        client = MagicMock()
        mock_client.return_value = client
        yield client


@pytest.fixture
def mock_s3_client():
    """Mock S3 client for testing"""
    with patch('boto3.client') as mock_client:
        client = MagicMock()
        mock_client.return_value = client
        yield client


@pytest.fixture
def mock_opensearch_client():
    """Mock OpenSearch client for testing"""
    with patch('boto3.client') as mock_client:
        client = MagicMock()
        mock_client.return_value = client
        yield client


@pytest.fixture
def mock_iam_client():
    """Mock IAM client for testing"""
    with patch('boto3.client') as mock_client:
        client = MagicMock()
        mock_client.return_value = client
        yield client


@pytest.fixture
def mock_secrets_manager_client():
    """Mock Secrets Manager client for testing"""
    with patch('boto3.client') as mock_client:
        client = MagicMock()
        mock_client.return_value = client
        yield client


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture
def sample_document():
    """Sample document for testing"""
    return {
        "id": "doc-001",
        "content": "This is a sample document for testing the RAG system.",
        "metadata": {
            "source": "s3://test-bucket/doc.txt",
            "source_type": "S3",
            "created_date": datetime.now().isoformat(),
            "modified_date": datetime.now().isoformat(),
            "author": "test-user",
            "tags": ["test", "sample"]
        }
    }


@pytest.fixture
def sample_chunk():
    """Sample chunk for testing"""
    return {
        "id": "chunk-001",
        "document_id": "doc-001",
        "content": "This is a sample chunk of text.",
        "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
        "metadata": {
            "chunk_index": 0,
            "chunk_size": 1024,
            "overlap": 20
        }
    }


@pytest.fixture
def sample_retrieval_result():
    """Sample retrieval result for testing"""
    return {
        "chunk_id": "chunk-001",
        "content": "This is a sample chunk of text.",
        "relevance_score": 0.95,
        "location": "s3://test-bucket/doc.txt",
        "metadata": {
            "source": "s3://test-bucket/doc.txt",
            "source_type": "S3"
        },
        "source_document": "doc-001"
    }


@pytest.fixture
def sample_generation_response():
    """Sample generation response for testing"""
    return {
        "generated_text": "This is a generated response based on the retrieved documents.",
        "source_documents": [
            {
                "chunk_id": "chunk-001",
                "content": "This is a sample chunk of text.",
                "relevance_score": 0.95,
                "location": "s3://test-bucket/doc.txt",
                "metadata": {"source": "s3://test-bucket/doc.txt"},
                "source_document": "doc-001"
            }
        ],
        "citations": [
            {
                "text": "sample chunk",
                "source_id": "chunk-001",
                "source_location": "s3://test-bucket/doc.txt",
                "relevance_score": 0.95
            }
        ],
        "model_used": "anthropic.claude-3-sonnet-20240229-v1:0",
        "generation_time_ms": 1500
    }


# ============================================================================
# Utility Fixtures
# ============================================================================

@pytest.fixture
def aws_credentials():
    """Mock AWS credentials for testing"""
    return {
        "region": "us-east-1",
        "account_id": "123456789012",
        "access_key_id": "AKIAIOSFODNN7EXAMPLE",
        "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    }


@pytest.fixture
def s3_bucket_config():
    """S3 bucket configuration for testing"""
    return {
        "bucket_name": "test-bedrock-rag-bucket",
        "region": "us-east-1",
        "prefix": "documents/"
    }


@pytest.fixture
def opensearch_config():
    """OpenSearch configuration for testing"""
    return {
        "collection_name": "test-bedrock-rag-collection",
        "index_name": "test-bedrock-rag-index",
        "vector_dimension": 1536,
        "region": "us-east-1"
    }
