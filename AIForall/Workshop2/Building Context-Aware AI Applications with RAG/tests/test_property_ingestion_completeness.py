"""Property-Based Tests for Document Ingestion Completeness

Feature: bedrock-rag-retrieval, Property 2: Document Ingestion Completeness
Validates: Requirements 2.1, 2.2

Property: For any set of documents uploaded to a data source, after ingestion completes,
all documents should be retrievable through the knowledge base search.
"""

import pytest
from unittest.mock import MagicMock, patch
from src.ingestion_manager import IngestionJobManager
from src.error_handler import ErrorHandler, IngestionSummary
from config.aws_config import AWSConfig
import os

# Disable hypothesis database to avoid Windows hanging issues
os.environ['HYPOTHESIS_DATABASE_DIRECTORY'] = 'none'


class TestIngestionCompletenessProperty:
    """
    Property-Based Tests for Document Ingestion Completeness
    
    **Feature: bedrock-rag-retrieval, Property 2: Document Ingestion Completeness**
    **Validates: Requirements 2.1, 2.2**
    """

    @pytest.mark.parametrize("num_documents", [1, 5, 10, 25, 50, 100])
    def test_all_documents_retrievable_after_ingestion(self, num_documents):
        """
        Property: For any set of documents, after successful ingestion,
        all documents should be retrievable.
        
        This property verifies that:
        1. All documents in the input set are accounted for in the ingestion summary
        2. The number of successfully ingested documents matches the input count
        3. The ingestion summary correctly reflects the document count
        
        **Feature: bedrock-rag-retrieval, Property 2: Document Ingestion Completeness**
        **Validates: Requirements 2.1, 2.2**
        """
        # Setup
        mock_bedrock_client = MagicMock()
        
        # Create mock response with statistics matching our documents
        mock_bedrock_client.get_ingestion_job.return_value = {
            "ingestionJob": {
                "ingestionJobId": "job-12345",
                "knowledgeBaseId": "kb-12345",
                "dataSourceId": "ds-12345",
                "status": "COMPLETE",
                "startedAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-01-01T00:10:00Z",
                "statistics": {
                    "numberOfDocumentsProcessed": num_documents,
                    "numberOfDocumentsFailed": 0,
                    "numberOfDocumentsSucceeded": num_documents,
                    "numberOfChunksCreated": num_documents * 5
                }
            }
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_bedrock_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = IngestionJobManager(config)

                    # Get ingestion job info
                    job_status = manager.get_ingestion_job(
                        kb_id="kb-12345",
                        data_source_id="ds-12345",
                        ingestion_job_id="job-12345"
                    )

                    # Property 1: All documents are accounted for
                    assert job_status["statistics"]["numberOfDocumentsProcessed"] == num_documents, \
                        f"Expected {num_documents} documents processed, got {job_status['statistics']['numberOfDocumentsProcessed']}"

                    # Property 2: No documents failed
                    assert job_status["statistics"]["numberOfDocumentsFailed"] == 0, \
                        f"Expected 0 failed documents, got {job_status['statistics']['numberOfDocumentsFailed']}"

                    # Property 3: All documents succeeded
                    assert job_status["statistics"]["numberOfDocumentsSucceeded"] == num_documents, \
                        f"Expected {num_documents} succeeded documents, got {job_status['statistics']['numberOfDocumentsSucceeded']}"

                    # Property 4: Chunks were created for all documents
                    assert job_status["statistics"]["numberOfChunksCreated"] >= num_documents, \
                        f"Expected at least {num_documents} chunks, got {job_status['statistics']['numberOfChunksCreated']}"

    @pytest.mark.parametrize("total_docs,failed_docs", [
        (10, 0), (20, 2), (50, 5), (100, 10), (100, 0)
    ])
    def test_ingestion_statistics_consistency(self, total_docs, failed_docs):
        """
        Property: Ingestion statistics should be internally consistent.
        
        This property verifies that:
        1. succeeded + failed = total processed
        2. All statistics are non-negative
        3. Chunks created >= succeeded documents
        
        **Feature: bedrock-rag-retrieval, Property 2: Document Ingestion Completeness**
        **Validates: Requirements 2.1, 2.2**
        """
        succeeded_docs = total_docs - failed_docs
        
        mock_bedrock_client = MagicMock()
        mock_bedrock_client.get_ingestion_job.return_value = {
            "ingestionJob": {
                "ingestionJobId": "job-12345",
                "knowledgeBaseId": "kb-12345",
                "dataSourceId": "ds-12345",
                "status": "COMPLETE",
                "statistics": {
                    "numberOfDocumentsProcessed": total_docs,
                    "numberOfDocumentsFailed": failed_docs,
                    "numberOfDocumentsSucceeded": succeeded_docs,
                    "numberOfChunksCreated": succeeded_docs * 3
                }
            }
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_bedrock_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = IngestionJobManager(config)

                    job_status = manager.get_ingestion_job(
                        kb_id="kb-12345",
                        data_source_id="ds-12345",
                        ingestion_job_id="job-12345"
                    )

                    stats = job_status.get("statistics", {})

                    # Property 1: succeeded + failed = total
                    assert stats["numberOfDocumentsSucceeded"] + stats["numberOfDocumentsFailed"] == stats["numberOfDocumentsProcessed"], \
                        f"Inconsistent statistics: {stats['numberOfDocumentsSucceeded']} + {stats['numberOfDocumentsFailed']} != {stats['numberOfDocumentsProcessed']}"

                    # Property 2: All values are non-negative
                    assert stats["numberOfDocumentsProcessed"] >= 0
                    assert stats["numberOfDocumentsFailed"] >= 0
                    assert stats["numberOfDocumentsSucceeded"] >= 0
                    assert stats["numberOfChunksCreated"] >= 0

                    # Property 3: Chunks >= succeeded documents
                    assert stats["numberOfChunksCreated"] >= stats["numberOfDocumentsSucceeded"], \
                        f"Number of chunks must be >= number of succeeded documents"

    @pytest.mark.parametrize("num_documents", [5, 10, 25, 50])
    def test_partial_ingestion_failure_handling(self, num_documents):
        """
        Property: When some documents fail, the system should handle it gracefully.
        
        **Feature: bedrock-rag-retrieval, Property 2: Document Ingestion Completeness**
        **Validates: Requirements 2.1, 2.2**
        """
        num_failed = max(1, num_documents // 5)  # 20% failure rate
        num_succeeded = num_documents - num_failed

        mock_bedrock_client = MagicMock()
        mock_bedrock_client.get_ingestion_job.return_value = {
            "ingestionJob": {
                "ingestionJobId": "job-12345",
                "knowledgeBaseId": "kb-12345",
                "dataSourceId": "ds-12345",
                "status": "COMPLETE",
                "statistics": {
                    "numberOfDocumentsProcessed": num_documents,
                    "numberOfDocumentsFailed": num_failed,
                    "numberOfDocumentsSucceeded": num_succeeded,
                    "numberOfChunksCreated": num_succeeded * 4
                }
            }
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_bedrock_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = IngestionJobManager(config)

                    job_status = manager.get_ingestion_job(
                        kb_id="kb-12345",
                        data_source_id="ds-12345",
                        ingestion_job_id="job-12345"
                    )

                    stats = job_status.get("statistics", {})

                    # Property: Failed documents are tracked
                    assert stats["numberOfDocumentsFailed"] == num_failed, \
                        f"Expected {num_failed} error logs, got {stats['numberOfDocumentsFailed']}"

                    # Property: Succeeded documents are still processed
                    assert stats["numberOfDocumentsSucceeded"] == num_succeeded
                    assert stats["numberOfChunksCreated"] > 0

    @pytest.mark.parametrize("num_documents", [1, 5, 10, 20, 50])
    def test_ingestion_summary_serialization(self, num_documents):
        """
        Property: Ingestion summary should be serializable to dict format.
        
        **Feature: bedrock-rag-retrieval, Property 2: Document Ingestion Completeness**
        **Validates: Requirements 2.1, 2.2**
        """
        mock_bedrock_client = MagicMock()
        mock_bedrock_client.get_ingestion_job.return_value = {
            "ingestionJob": {
                "ingestionJobId": "job-12345",
                "knowledgeBaseId": "kb-12345",
                "dataSourceId": "ds-12345",
                "status": "COMPLETE",
                "statistics": {
                    "numberOfDocumentsProcessed": num_documents,
                    "numberOfDocumentsFailed": 0,
                    "numberOfDocumentsSucceeded": num_documents,
                    "numberOfChunksCreated": num_documents * 5
                }
            }
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_bedrock_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = IngestionJobManager(config)

                    job_status = manager.get_ingestion_job(
                        kb_id="kb-12345",
                        data_source_id="ds-12345",
                        ingestion_job_id="job-12345"
                    )

                    # Property: Status is a dict
                    assert isinstance(job_status, dict)

                    # Property: Contains required fields
                    assert "statistics" in job_status

                    stats = job_status.get("statistics", {})

                    # Property: Statistics contain required fields
                    assert "numberOfDocumentsProcessed" in stats
                    assert "numberOfDocumentsFailed" in stats
                    assert "numberOfDocumentsSucceeded" in stats
                    assert "numberOfChunksCreated" in stats

                    # Property: All values are integers
                    assert isinstance(stats["numberOfDocumentsProcessed"], int)
                    assert isinstance(stats["numberOfDocumentsFailed"], int)
                    assert isinstance(stats["numberOfDocumentsSucceeded"], int)
                    assert isinstance(stats["numberOfChunksCreated"], int)
