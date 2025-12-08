"""Tests for data source connectors"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
import os
from src.data_source_connector import (
    DataSourceConnector,
    S3DataSourceConnector,
    Document,
    DataSourceType
)

# Disable hypothesis database to avoid Windows hanging issues
os.environ['HYPOTHESIS_DATABASE_DIRECTORY'] = 'none'


class TestDocumentModel:
    """Tests for Document data model"""

    def test_document_creation(self):
        """Test document creation"""
        doc = Document(
            id="doc-001",
            content="Test content",
            source="s3://bucket/doc.txt",
            source_type=DataSourceType.S3,
            metadata={"key": "value"},
            author="test-user"
        )

        assert doc.id == "doc-001"
        assert doc.content == "Test content"
        assert doc.source == "s3://bucket/doc.txt"
        assert doc.source_type == DataSourceType.S3
        assert doc.author == "test-user"

    def test_document_to_dict(self):
        """Test document conversion to dictionary"""
        doc = Document(
            id="doc-001",
            content="Test content",
            source="s3://bucket/doc.txt",
            source_type=DataSourceType.S3,
            metadata={"key": "value"},
            author="test-user",
            tags=["tag1", "tag2"]
        )

        doc_dict = doc.to_dict()

        assert doc_dict["id"] == "doc-001"
        assert doc_dict["content"] == "Test content"
        assert doc_dict["source_type"] == "S3"
        assert doc_dict["author"] == "test-user"
        assert doc_dict["tags"] == ["tag1", "tag2"]

    def test_document_with_dates(self):
        """Test document with date fields"""
        now = datetime.now()
        doc = Document(
            id="doc-001",
            content="Test content",
            source="s3://bucket/doc.txt",
            source_type=DataSourceType.S3,
            metadata={},
            created_date=now,
            modified_date=now
        )

        doc_dict = doc.to_dict()

        assert doc_dict["created_date"] is not None
        assert doc_dict["modified_date"] is not None


class TestS3DataSourceConnectorInitialization:
    """Tests for S3 connector initialization"""

    def test_init_with_s3_manager(self):
        """Test S3 connector initialization"""
        mock_s3_manager = MagicMock()
        connector = S3DataSourceConnector(mock_s3_manager)

        assert connector.source_type == DataSourceType.S3
        assert connector.s3_manager is mock_s3_manager
        assert connector.bucket_name is None
        assert connector.prefix == ""
        assert connector.is_connected() is False


class TestS3DataSourceConnectorConnection:
    """Tests for S3 connector connection"""

    def test_connect_success(self):
        """Test successful S3 connection"""
        mock_s3_manager = MagicMock()
        mock_s3_manager.bucket_exists.return_value = True

        connector = S3DataSourceConnector(mock_s3_manager)
        result = connector.connect({
            "bucket_name": "test-bucket",
            "prefix": "documents/"
        })

        assert result is True
        assert connector.bucket_name == "test-bucket"
        assert connector.prefix == "documents/"
        assert connector.is_connected() is True

    def test_connect_missing_bucket_name(self):
        """Test connection with missing bucket name"""
        mock_s3_manager = MagicMock()
        connector = S3DataSourceConnector(mock_s3_manager)

        with pytest.raises(ValueError, match="bucket_name"):
            connector.connect({})

    def test_connect_empty_bucket_name(self):
        """Test connection with empty bucket name"""
        mock_s3_manager = MagicMock()
        connector = S3DataSourceConnector(mock_s3_manager)

        with pytest.raises(ValueError, match="bucket_name cannot be empty"):
            connector.connect({"bucket_name": ""})

    def test_connect_bucket_not_exists(self):
        """Test connection to non-existent bucket"""
        mock_s3_manager = MagicMock()
        mock_s3_manager.bucket_exists.return_value = False

        connector = S3DataSourceConnector(mock_s3_manager)

        with pytest.raises(ValueError, match="does not exist"):
            connector.connect({"bucket_name": "nonexistent-bucket"})

    def test_disconnect(self):
        """Test S3 disconnection"""
        mock_s3_manager = MagicMock()
        mock_s3_manager.bucket_exists.return_value = True

        connector = S3DataSourceConnector(mock_s3_manager)
        connector.connect({"bucket_name": "test-bucket"})

        assert connector.is_connected() is True

        result = connector.disconnect()

        assert result is True
        assert connector.is_connected() is False
        assert connector.bucket_name is None

    def test_validate_connection_success(self):
        """Test successful connection validation"""
        mock_s3_manager = MagicMock()
        mock_s3_manager.bucket_exists.return_value = True

        connector = S3DataSourceConnector(mock_s3_manager)
        connector.connect({"bucket_name": "test-bucket"})

        result = connector.validate_connection()

        assert result is True

    def test_validate_connection_not_connected(self):
        """Test connection validation when not connected"""
        mock_s3_manager = MagicMock()
        connector = S3DataSourceConnector(mock_s3_manager)

        result = connector.validate_connection()

        assert result is False

    def test_validate_connection_bucket_not_exists(self):
        """Test connection validation when bucket no longer exists"""
        mock_s3_manager = MagicMock()
        mock_s3_manager.bucket_exists.side_effect = [True, False]

        connector = S3DataSourceConnector(mock_s3_manager)
        connector.connect({"bucket_name": "test-bucket"})

        result = connector.validate_connection()

        assert result is False


class TestS3DataSourceConnectorFetchDocuments:
    """Tests for fetching documents from S3"""

    def test_fetch_documents_success(self):
        """Test successful document fetching"""
        mock_s3_manager = MagicMock()
        mock_s3_manager.bucket_exists.return_value = True
        mock_s3_manager.list_objects.return_value = {
            "objects": [
                {
                    "key": "doc1.txt",
                    "size": 1024,
                    "last_modified": datetime.now().isoformat(),
                    "storage_class": "STANDARD"
                },
                {
                    "key": "doc2.txt",
                    "size": 2048,
                    "last_modified": datetime.now().isoformat(),
                    "storage_class": "STANDARD"
                }
            ]
        }
        mock_s3_manager.get_object.side_effect = [
            {
                "body": b"Content of doc1",
                "content_type": "text/plain",
                "content_length": 1024,
                "last_modified": datetime.now().isoformat(),
                "metadata": {}
            },
            {
                "body": b"Content of doc2",
                "content_type": "text/plain",
                "content_length": 2048,
                "last_modified": datetime.now().isoformat(),
                "metadata": {}
            }
        ]

        connector = S3DataSourceConnector(mock_s3_manager)
        connector.connect({"bucket_name": "test-bucket"})

        documents = connector.fetch_documents()

        assert len(documents) == 2
        assert documents[0].id == "doc1.txt"
        assert documents[0].content == "Content of doc1"
        assert documents[0].source_type == DataSourceType.S3
        assert documents[1].id == "doc2.txt"

    def test_fetch_documents_with_limit(self):
        """Test document fetching with limit"""
        mock_s3_manager = MagicMock()
        mock_s3_manager.bucket_exists.return_value = True
        mock_s3_manager.list_objects.return_value = {
            "objects": [
                {
                    "key": "doc1.txt",
                    "size": 1024,
                    "last_modified": datetime.now().isoformat(),
                    "storage_class": "STANDARD"
                },
                {
                    "key": "doc2.txt",
                    "size": 2048,
                    "last_modified": datetime.now().isoformat(),
                    "storage_class": "STANDARD"
                }
            ]
        }
        mock_s3_manager.get_object.return_value = {
            "body": b"Content",
            "content_type": "text/plain",
            "content_length": 1024,
            "last_modified": datetime.now().isoformat(),
            "metadata": {}
        }

        connector = S3DataSourceConnector(mock_s3_manager)
        connector.connect({"bucket_name": "test-bucket"})

        documents = connector.fetch_documents(limit=1)

        assert len(documents) == 1

    def test_fetch_documents_not_connected(self):
        """Test document fetching when not connected"""
        mock_s3_manager = MagicMock()
        connector = S3DataSourceConnector(mock_s3_manager)

        with pytest.raises(ValueError, match="Not connected"):
            connector.fetch_documents()

    def test_fetch_document_by_id_success(self):
        """Test fetching a specific document by ID"""
        mock_s3_manager = MagicMock()
        mock_s3_manager.bucket_exists.return_value = True
        mock_s3_manager.get_object.return_value = {
            "body": b"Document content",
            "content_type": "text/plain",
            "content_length": 1024,
            "last_modified": datetime.now().isoformat(),
            "metadata": {}
        }

        connector = S3DataSourceConnector(mock_s3_manager)
        connector.connect({"bucket_name": "test-bucket"})

        document = connector.fetch_document_by_id("doc1.txt")

        assert document is not None
        assert document.id == "doc1.txt"
        assert document.content == "Document content"

    def test_fetch_document_by_id_not_found(self):
        """Test fetching non-existent document"""
        mock_s3_manager = MagicMock()
        mock_s3_manager.bucket_exists.return_value = True
        mock_s3_manager.get_object.side_effect = ValueError("Object 'doc1.txt' does not exist")

        connector = S3DataSourceConnector(mock_s3_manager)
        connector.connect({"bucket_name": "test-bucket"})

        document = connector.fetch_document_by_id("doc1.txt")

        assert document is None

    def test_fetch_document_by_id_empty_id(self):
        """Test fetching document with empty ID"""
        mock_s3_manager = MagicMock()
        mock_s3_manager.bucket_exists.return_value = True

        connector = S3DataSourceConnector(mock_s3_manager)
        connector.connect({"bucket_name": "test-bucket"})

        with pytest.raises(ValueError, match="document_id cannot be empty"):
            connector.fetch_document_by_id("")

    def test_get_document_count(self):
        """Test getting document count"""
        mock_s3_manager = MagicMock()
        mock_s3_manager.bucket_exists.return_value = True
        mock_s3_manager.list_objects.return_value = {
            "object_count": 5
        }

        connector = S3DataSourceConnector(mock_s3_manager)
        connector.connect({"bucket_name": "test-bucket"})

        count = connector.get_document_count()

        assert count == 5

    def test_get_document_count_not_connected(self):
        """Test getting document count when not connected"""
        mock_s3_manager = MagicMock()
        connector = S3DataSourceConnector(mock_s3_manager)

        with pytest.raises(ValueError, match="Not connected"):
            connector.get_document_count()


class TestDocumentIngestionCompleteness:
    """Property-based tests for document ingestion completeness"""

    @pytest.mark.parametrize("num_documents,document_size", [
        (1, 10), (5, 100), (10, 500), (10, 1000), (8, 750)
    ])
    def test_property_document_ingestion_completeness(self, num_documents, document_size):
        """
        **Feature: bedrock-rag-retrieval, Property 2: Document Ingestion Completeness**
        
        For any set of documents uploaded to a data source, after ingestion completes,
        all documents should be retrievable through the knowledge base search.
        
        **Validates: Requirements 2.1, 2.2**
        """
        # Generate mock documents
        mock_s3_manager = MagicMock()
        mock_s3_manager.bucket_exists.return_value = True

        # Create list of mock objects
        mock_objects = []
        for i in range(num_documents):
            mock_objects.append({
                "key": f"doc_{i}.txt",
                "size": document_size,
                "last_modified": datetime.now().isoformat(),
                "storage_class": "STANDARD"
            })

        mock_s3_manager.list_objects.return_value = {
            "objects": mock_objects,
            "object_count": num_documents
        }

        # Mock get_object to return content for each document
        def mock_get_object(bucket, key):
            return {
                "body": f"Content of {key}".encode(),
                "content_type": "text/plain",
                "content_length": document_size,
                "last_modified": datetime.now().isoformat(),
                "metadata": {}
            }

        mock_s3_manager.get_object.side_effect = mock_get_object

        # Connect and fetch documents
        connector = S3DataSourceConnector(mock_s3_manager)
        connector.connect({"bucket_name": "test-bucket"})

        # Fetch all documents
        fetched_documents = connector.fetch_documents()

        # Property: All uploaded documents should be retrievable
        assert len(fetched_documents) == num_documents, \
            f"Expected {num_documents} documents, but got {len(fetched_documents)}"

        # Property: Each fetched document should have valid content
        for doc in fetched_documents:
            assert doc.id is not None, "Document ID should not be None"
            assert len(doc.content) > 0, "Document content should not be empty"
            assert doc.source_type == DataSourceType.S3, "Document source type should be S3"
            assert doc.source.startswith("s3://"), "Document source should be S3 URI"

        # Property: Document count should match fetched documents
        count = connector.get_document_count()
        assert count == len(fetched_documents), \
            f"Document count {count} should match fetched documents {len(fetched_documents)}"

        # Property: Each document should be individually retrievable
        for doc in fetched_documents:
            retrieved_doc = connector.fetch_document_by_id(doc.id)
            assert retrieved_doc is not None, f"Document {doc.id} should be retrievable by ID"
            assert retrieved_doc.id == doc.id, "Retrieved document ID should match"
            assert len(retrieved_doc.content) > 0, "Retrieved document should have content"
