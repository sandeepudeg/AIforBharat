"""End-to-end integration tests for Bedrock RAG Retrieval System

Tests complete workflows: KB creation → document ingestion → retrieval → generation
Tests with multiple data sources and error scenarios
"""

import pytest
import json
from unittest.mock import MagicMock, patch, call
from botocore.exceptions import ClientError
from config.aws_config import AWSConfig
from src.knowledge_base_manager import BedrockKnowledgeBase
from src.ingestion_manager import IngestionJobManager
from src.retrieval_api import RetrieveAPI, RetrievalConfig, RetrievalType
from src.retrieve_and_generate_api import RetrieveAndGenerateAPI, GenerationConfig
from src.data_source_connector import S3DataSourceConnector, DataSourceType
import os

# Disable hypothesis database to avoid Windows hanging issues
os.environ['HYPOTHESIS_DATABASE_DIRECTORY'] = 'none'


class TestEndToEndWorkflow:
    """Tests for complete end-to-end workflows"""

    def test_complete_workflow_kb_creation_to_retrieval(self, mock_bedrock_client):
        """Test complete workflow: KB creation → data source → ingestion → retrieval"""
        from config.aws_config import AWSConfig

        # Mock KB creation
        mock_bedrock_client.list_knowledge_bases.return_value = {"knowledgeBaseSummaries": []}
        mock_bedrock_client.create_knowledge_base.return_value = {
            "knowledgeBase": {
                "id": "kb-12345",
                "name": "test-kb",
                "description": "Test knowledge base",
                "status": "CREATING",
                "createdAt": "2024-01-01T00:00:00Z"
            }
        }

        # Mock KB status check
        mock_bedrock_client.get_knowledge_base.return_value = {
            "knowledgeBase": {
                "id": "kb-12345",
                "name": "test-kb",
                "status": "ACTIVE",
                "roleArn": "arn:aws:iam::123456789012:role/bedrock-kb-role",
                "createdAt": "2024-01-01T00:00:00Z"
            }
        }

        # Mock data source creation
        mock_bedrock_client.create_data_source.return_value = {
            "dataSource": {
                "id": "ds-12345",
                "name": "test-s3-source",
                "status": "AVAILABLE",
                "createdAt": "2024-01-01T00:00:00Z"
            }
        }

        # Mock ingestion job start
        mock_bedrock_client.start_ingestion_job.return_value = {
            "ingestionJob": {
                "ingestionJobId": "job-12345",
                "knowledgeBaseId": "kb-12345",
                "dataSourceId": "ds-12345",
                "status": "STARTING",
                "startedAt": "2024-01-01T00:00:00Z",
                "statistics": {
                    "numberOfDocumentsProcessed": 0,
                    "numberOfDocumentsFailed": 0,
                    "numberOfDocumentsSucceeded": 0,
                    "numberOfChunksCreated": 0
                }
            }
        }

        # Mock ingestion job completion
        mock_bedrock_client.get_ingestion_job.return_value = {
            "ingestionJob": {
                "ingestionJobId": "job-12345",
                "knowledgeBaseId": "kb-12345",
                "dataSourceId": "ds-12345",
                "status": "COMPLETE",
                "startedAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-01-01T00:10:00Z",
                "statistics": {
                    "numberOfDocumentsProcessed": 10,
                    "numberOfDocumentsFailed": 0,
                    "numberOfDocumentsSucceeded": 10,
                    "numberOfChunksCreated": 50
                },
                "failureReasons": []
            }
        }

        # Mock retrieval
        mock_bedrock_client.retrieve.return_value = {
            "retrievalResults": [
                {
                    "content": "Document content about AI",
                    "score": 0.95,
                    "retrievalResultMetadata": {
                        "location": {
                            "s3Location": {
                                "uri": "s3://bucket/doc.txt"
                            }
                        },
                        "document": {
                            "documentId": "doc-001"
                        }
                    }
                }
            ]
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()

                    # Step 1: Create Knowledge Base
                    kb_manager = BedrockKnowledgeBase(config)
                    vector_store_config = {
                        "collectionArn": "arn:aws:aoss:us-east-1:123456789012:collection/test",
                        "fieldMapping": {
                            "vectorField": "embedding",
                            "textField": "content",
                            "metadataField": "metadata"
                        }
                    }

                    kb_result = kb_manager.create_knowledge_base(
                        kb_name="test-kb",
                        kb_description="Test knowledge base",
                        role_arn="arn:aws:iam::123456789012:role/bedrock-kb-role",
                        vector_store_config=vector_store_config
                    )

                    assert kb_result["kb_id"] == "kb-12345"
                    assert kb_result["kb_name"] == "test-kb"

                    # Step 2: Create Data Source
                    s3_config = {
                        "bucketArn": "arn:aws:s3:::test-bucket",
                        "inclusionPrefixes": ["documents/"]
                    }

                    ds_result = kb_manager.create_data_source(
                        kb_id="kb-12345",
                        data_source_name="test-s3-source",
                        data_source_config=s3_config,
                        data_source_type="S3"
                    )

                    assert ds_result["data_source_id"] == "ds-12345"

                    # Step 3: Start Ingestion Job
                    ingestion_manager = IngestionJobManager(config)
                    job_result = ingestion_manager.start_ingestion_job(
                        kb_id="kb-12345",
                        data_source_id="ds-12345"
                    )

                    assert job_result["ingestion_job_id"] == "job-12345"
                    assert job_result["status"] == "STARTING"

                    # Step 4: Wait for Ingestion to Complete
                    job_info = ingestion_manager.get_ingestion_job(
                        kb_id="kb-12345",
                        data_source_id="ds-12345",
                        ingestion_job_id="job-12345"
                    )

                    assert job_info["status"] == "COMPLETE"
                    assert job_info["statistics"]["numberOfDocumentsSucceeded"] == 10

                    # Step 5: Retrieve Documents
                    retrieve_api = RetrieveAPI(config)
                    results = retrieve_api.retrieve(
                        knowledge_base_id="kb-12345",
                        query="What is AI?"
                    )

                    assert len(results) > 0
                    assert results[0].relevance_score == 0.95


class TestMultiSourceIngestion:
    """Tests for ingestion from multiple data sources"""

    def test_ingestion_from_s3_source(self, mock_bedrock_client):
        """Test ingestion from S3 data source"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.create_data_source.return_value = {
            "dataSource": {
                "id": "ds-s3-001",
                "name": "s3-source",
                "status": "AVAILABLE",
                "createdAt": "2024-01-01T00:00:00Z"
            }
        }

        mock_bedrock_client.start_ingestion_job.return_value = {
            "ingestionJob": {
                "ingestionJobId": "job-s3-001",
                "knowledgeBaseId": "kb-12345",
                "dataSourceId": "ds-s3-001",
                "status": "STARTING",
                "startedAt": "2024-01-01T00:00:00Z",
                "statistics": {}
            }
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    kb_manager = BedrockKnowledgeBase(config)

                    s3_config = {
                        "bucketArn": "arn:aws:s3:::test-bucket",
                        "inclusionPrefixes": ["documents/"]
                    }

                    ds_result = kb_manager.create_data_source(
                        kb_id="kb-12345",
                        data_source_name="s3-source",
                        data_source_config=s3_config,
                        data_source_type="S3"
                    )

                    assert ds_result["data_source_type"] == "S3"
                    assert ds_result["data_source_id"] == "ds-s3-001"

    def test_ingestion_from_confluence_source(self, mock_bedrock_client):
        """Test ingestion from Confluence data source"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.create_data_source.return_value = {
            "dataSource": {
                "id": "ds-confluence-001",
                "name": "confluence-source",
                "status": "AVAILABLE",
                "createdAt": "2024-01-01T00:00:00Z"
            }
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    kb_manager = BedrockKnowledgeBase(config)

                    confluence_config = {
                        "sourceConfiguration": {
                            "authType": "OAUTH2",
                            "credentials": {
                                "secretArn": "arn:aws:secretsmanager:us-east-1:123456789012:secret:confluence-creds"
                            }
                        },
                        "hostUrl": "https://example.atlassian.net"
                    }

                    ds_result = kb_manager.create_data_source(
                        kb_id="kb-12345",
                        data_source_name="confluence-source",
                        data_source_config=confluence_config,
                        data_source_type="CONFLUENCE"
                    )

                    assert ds_result["data_source_type"] == "CONFLUENCE"
                    assert ds_result["data_source_id"] == "ds-confluence-001"

    def test_ingestion_from_sharepoint_source(self, mock_bedrock_client):
        """Test ingestion from SharePoint data source"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.create_data_source.return_value = {
            "dataSource": {
                "id": "ds-sharepoint-001",
                "name": "sharepoint-source",
                "status": "AVAILABLE",
                "createdAt": "2024-01-01T00:00:00Z"
            }
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    kb_manager = BedrockKnowledgeBase(config)

                    sharepoint_config = {
                        "sourceConfiguration": {
                            "authType": "OAUTH2",
                            "credentials": {
                                "secretArn": "arn:aws:secretsmanager:us-east-1:123456789012:secret:sharepoint-creds"
                            }
                        },
                        "siteUrls": ["https://example.sharepoint.com/sites/team"]
                    }

                    ds_result = kb_manager.create_data_source(
                        kb_id="kb-12345",
                        data_source_name="sharepoint-source",
                        data_source_config=sharepoint_config,
                        data_source_type="SHAREPOINT"
                    )

                    assert ds_result["data_source_type"] == "SHAREPOINT"

    def test_ingestion_from_salesforce_source(self, mock_bedrock_client):
        """Test ingestion from Salesforce data source"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.create_data_source.return_value = {
            "dataSource": {
                "id": "ds-salesforce-001",
                "name": "salesforce-source",
                "status": "AVAILABLE",
                "createdAt": "2024-01-01T00:00:00Z"
            }
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    kb_manager = BedrockKnowledgeBase(config)

                    salesforce_config = {
                        "sourceConfiguration": {
                            "authType": "OAUTH2",
                            "credentials": {
                                "secretArn": "arn:aws:secretsmanager:us-east-1:123456789012:secret:salesforce-creds"
                            }
                        },
                        "instanceUrl": "https://example.salesforce.com"
                    }

                    ds_result = kb_manager.create_data_source(
                        kb_id="kb-12345",
                        data_source_name="salesforce-source",
                        data_source_config=salesforce_config,
                        data_source_type="SALESFORCE"
                    )

                    assert ds_result["data_source_type"] == "SALESFORCE"

    def test_ingestion_from_web_source(self, mock_bedrock_client):
        """Test ingestion from Web data source"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.create_data_source.return_value = {
            "dataSource": {
                "id": "ds-web-001",
                "name": "web-source",
                "status": "AVAILABLE",
                "createdAt": "2024-01-01T00:00:00Z"
            }
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    kb_manager = BedrockKnowledgeBase(config)

                    web_config = {
                        "sourceConfiguration": {
                            "urlConfiguration": {
                                "seedUrls": [
                                    {"url": "https://example.com"}
                                ]
                            }
                        }
                    }

                    ds_result = kb_manager.create_data_source(
                        kb_id="kb-12345",
                        data_source_name="web-source",
                        data_source_config=web_config,
                        data_source_type="WEB"
                    )

                    assert ds_result["data_source_type"] == "WEB"

    def test_multiple_data_sources_in_single_kb(self, mock_bedrock_client):
        """Test creating multiple data sources in a single knowledge base"""
        from config.aws_config import AWSConfig

        # Mock responses for multiple data sources
        mock_bedrock_client.create_data_source.side_effect = [
            {
                "dataSource": {
                    "id": "ds-s3-001",
                    "name": "s3-source",
                    "status": "AVAILABLE",
                    "createdAt": "2024-01-01T00:00:00Z"
                }
            },
            {
                "dataSource": {
                    "id": "ds-confluence-001",
                    "name": "confluence-source",
                    "status": "AVAILABLE",
                    "createdAt": "2024-01-01T00:00:00Z"
                }
            },
            {
                "dataSource": {
                    "id": "ds-web-001",
                    "name": "web-source",
                    "status": "AVAILABLE",
                    "createdAt": "2024-01-01T00:00:00Z"
                }
            }
        ]

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    kb_manager = BedrockKnowledgeBase(config)

                    # Create S3 data source
                    s3_config = {
                        "bucketArn": "arn:aws:s3:::test-bucket",
                        "inclusionPrefixes": ["documents/"]
                    }
                    ds1 = kb_manager.create_data_source(
                        kb_id="kb-12345",
                        data_source_name="s3-source",
                        data_source_config=s3_config,
                        data_source_type="S3"
                    )

                    # Create Confluence data source
                    confluence_config = {
                        "sourceConfiguration": {
                            "authType": "OAUTH2",
                            "credentials": {
                                "secretArn": "arn:aws:secretsmanager:us-east-1:123456789012:secret:confluence-creds"
                            }
                        },
                        "hostUrl": "https://example.atlassian.net"
                    }
                    ds2 = kb_manager.create_data_source(
                        kb_id="kb-12345",
                        data_source_name="confluence-source",
                        data_source_config=confluence_config,
                        data_source_type="CONFLUENCE"
                    )

                    # Create Web data source
                    web_config = {
                        "sourceConfiguration": {
                            "urlConfiguration": {
                                "seedUrls": [
                                    {"url": "https://example.com"}
                                ]
                            }
                        }
                    }
                    ds3 = kb_manager.create_data_source(
                        kb_id="kb-12345",
                        data_source_name="web-source",
                        data_source_config=web_config,
                        data_source_type="WEB"
                    )

                    # Verify all data sources were created
                    assert ds1["data_source_id"] == "ds-s3-001"
                    assert ds2["data_source_id"] == "ds-confluence-001"
                    assert ds3["data_source_id"] == "ds-web-001"
                    assert ds1["data_source_type"] == "S3"
                    assert ds2["data_source_type"] == "CONFLUENCE"
                    assert ds3["data_source_type"] == "WEB"


class TestRetrievalWorkflows:
    """Tests for retrieval workflows"""

    def test_retrieve_api_with_various_queries(self, mock_bedrock_client):
        """Test Retrieve API with various query types"""
        from config.aws_config import AWSConfig

        # Mock retrieval responses for different queries
        mock_bedrock_client.retrieve.side_effect = [
            {
                "retrievalResults": [
                    {
                        "content": "Artificial Intelligence is transformative",
                        "score": 0.95,
                        "retrievalResultMetadata": {
                            "location": {"s3Location": {"uri": "s3://bucket/ai.txt"}},
                            "document": {"documentId": "doc-001"}
                        }
                    }
                ]
            },
            {
                "retrievalResults": [
                    {
                        "content": "Machine learning enables computers to learn",
                        "score": 0.92,
                        "retrievalResultMetadata": {
                            "location": {"s3Location": {"uri": "s3://bucket/ml.txt"}},
                            "document": {"documentId": "doc-002"}
                        }
                    }
                ]
            },
            {
                "retrievalResults": [
                    {
                        "content": "Deep learning uses neural networks",
                        "score": 0.88,
                        "retrievalResultMetadata": {
                            "location": {"s3Location": {"uri": "s3://bucket/dl.txt"}},
                            "document": {"documentId": "doc-003"}
                        }
                    }
                ]
            }
        ]

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    retrieve_api = RetrieveAPI(config)

                    # Query 1: AI
                    results1 = retrieve_api.retrieve(
                        knowledge_base_id="kb-12345",
                        query="What is AI?"
                    )
                    assert len(results1) > 0
                    assert results1[0].relevance_score == 0.95

                    # Query 2: Machine Learning
                    results2 = retrieve_api.retrieve(
                        knowledge_base_id="kb-12345",
                        query="What is machine learning?"
                    )
                    assert len(results2) > 0
                    assert results2[0].relevance_score == 0.92

                    # Query 3: Deep Learning
                    results3 = retrieve_api.retrieve(
                        knowledge_base_id="kb-12345",
                        query="What is deep learning?"
                    )
                    assert len(results3) > 0
                    assert results3[0].relevance_score == 0.88

    def test_retrieve_and_generate_api(self, mock_bedrock_client):
        """Test Retrieve and Generate API"""
        from config.aws_config import AWSConfig

        # Mock retrieve response
        mock_bedrock_client.retrieve.return_value = {
            "retrievalResults": [
                {
                    "content": "AI is transformative technology",
                    "score": 0.95,
                    "retrievalResultMetadata": {
                        "location": {"s3Location": {"uri": "s3://bucket/doc.txt"}},
                        "document": {"documentId": "doc-001"}
                    }
                }
            ]
        }

        # Mock generation response
        mock_bedrock_client.invoke_model.return_value = {
            "body": MagicMock(read=lambda: json.dumps({
                "content": [{"text": "AI is a transformative technology that enables computers to learn and make decisions."}]
            }).encode())
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    rag_api = RetrieveAndGenerateAPI(config)

                    response = rag_api.retrieve_and_generate(
                        knowledge_base_id="kb-12345",
                        query="What is AI?"
                    )

                    assert response.generated_text is not None
                    assert response.query == "What is AI?"

    def test_retrieve_with_result_filtering(self, mock_bedrock_client):
        """Test retrieval with result filtering and ranking"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.retrieve.return_value = {
            "retrievalResults": [
                {
                    "content": "Highly relevant document",
                    "score": 0.95,
                    "retrievalResultMetadata": {
                        "location": {"s3Location": {"uri": "s3://bucket/doc1.txt"}},
                        "document": {"documentId": "doc-001"}
                    }
                },
                {
                    "content": "Moderately relevant document",
                    "score": 0.75,
                    "retrievalResultMetadata": {
                        "location": {"s3Location": {"uri": "s3://bucket/doc2.txt"}},
                        "document": {"documentId": "doc-002"}
                    }
                },
                {
                    "content": "Slightly relevant document",
                    "score": 0.55,
                    "retrievalResultMetadata": {
                        "location": {"s3Location": {"uri": "s3://bucket/doc3.txt"}},
                        "document": {"documentId": "doc-003"}
                    }
                }
            ]
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    retrieve_api = RetrieveAPI(config)

                    # Retrieve with minimum relevance score filter
                    config_with_filter = RetrievalConfig(
                        max_results=5,
                        min_relevance_score=0.7
                    )

                    results = retrieve_api.retrieve(
                        knowledge_base_id="kb-12345",
                        query="Test query",
                        config=config_with_filter
                    )

                    # Should only return results with score >= 0.7
                    assert len(results) == 2
                    assert all(r.relevance_score >= 0.7 for r in results)
                    # Results should be sorted by relevance score descending
                    assert results[0].relevance_score >= results[1].relevance_score

    def test_retrieve_with_max_results_limit(self, mock_bedrock_client):
        """Test retrieval with maximum results limit"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.retrieve.return_value = {
            "retrievalResults": [
                {
                    "content": f"Document {i}",
                    "score": 0.95 - (i * 0.05),
                    "retrievalResultMetadata": {
                        "location": {"s3Location": {"uri": f"s3://bucket/doc{i}.txt"}},
                        "document": {"documentId": f"doc-{i:03d}"}
                    }
                }
                for i in range(10)
            ]
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    retrieve_api = RetrieveAPI(config)

                    # Retrieve with max_results = 3
                    config_with_limit = RetrievalConfig(max_results=3)

                    results = retrieve_api.retrieve(
                        knowledge_base_id="kb-12345",
                        query="Test query",
                        config=config_with_limit
                    )

                    assert len(results) == 3

    def test_retrieve_and_generate_with_custom_config(self, mock_bedrock_client):
        """Test Retrieve and Generate with custom generation configuration"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.retrieve.return_value = {
            "retrievalResults": [
                {
                    "content": "Test content",
                    "score": 0.95,
                    "retrievalResultMetadata": {
                        "location": {"s3Location": {"uri": "s3://bucket/doc.txt"}},
                        "document": {"documentId": "doc-001"}
                    }
                }
            ]
        }

        mock_bedrock_client.invoke_model.return_value = {
            "body": MagicMock(read=lambda: json.dumps({
                "content": [{"text": "Generated response"}]
            }).encode())
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    rag_api = RetrieveAndGenerateAPI(config)

                    gen_config = GenerationConfig(
                        max_tokens=2048,
                        temperature=0.5
                    )

                    response = rag_api.retrieve_and_generate(
                        knowledge_base_id="kb-12345",
                        query="Test query",
                        generation_config=gen_config
                    )

                    assert response.generated_text is not None

    def test_retrieve_with_metadata_filtering(self, mock_bedrock_client):
        """Test retrieval with metadata filtering"""
        from config.aws_config import AWSConfig

        # Mock retrieval with metadata in results
        mock_bedrock_client.retrieve.return_value = {
            "retrievalResults": [
                {
                    "content": "Document from Q1 2024",
                    "score": 0.95,
                    "retrievalResultMetadata": {
                        "location": {"s3Location": {"uri": "s3://bucket/q1-2024.txt"}},
                        "document": {
                            "documentId": "doc-001",
                            "title": "Q1 Report",
                            "createdAt": "2024-01-15"
                        }
                    }
                },
                {
                    "content": "Document from Q2 2024",
                    "score": 0.85,
                    "retrievalResultMetadata": {
                        "location": {"s3Location": {"uri": "s3://bucket/q2-2024.txt"}},
                        "document": {
                            "documentId": "doc-002",
                            "title": "Q2 Report",
                            "createdAt": "2024-04-15"
                        }
                    }
                },
                {
                    "content": "Document from Q3 2024",
                    "score": 0.75,
                    "retrievalResultMetadata": {
                        "location": {"s3Location": {"uri": "s3://bucket/q3-2024.txt"}},
                        "document": {
                            "documentId": "doc-003",
                            "title": "Q3 Report",
                            "createdAt": "2024-07-15"
                        }
                    }
                }
            ]
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    retrieve_api = RetrieveAPI(config)

                    # Retrieve with metadata filter
                    results = retrieve_api.retrieve(
                        knowledge_base_id="kb-12345",
                        query="quarterly reports"
                    )

                    # Verify all results include metadata
                    assert len(results) == 3
                    for result in results:
                        assert result.metadata is not None
                        # Metadata can be nested under 'document' key
                        assert "document" in result.metadata or "location" in result.metadata

    def test_retrieve_with_source_document_tracking(self, mock_bedrock_client):
        """Test that retrieval results track source documents correctly"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.retrieve.return_value = {
            "retrievalResults": [
                {
                    "content": "Content from document A",
                    "score": 0.95,
                    "retrievalResultMetadata": {
                        "location": {"s3Location": {"uri": "s3://bucket/doc-a.txt"}},
                        "document": {"documentId": "doc-a"}
                    }
                },
                {
                    "content": "Another chunk from document A",
                    "score": 0.90,
                    "retrievalResultMetadata": {
                        "location": {"s3Location": {"uri": "s3://bucket/doc-a.txt"}},
                        "document": {"documentId": "doc-a"}
                    }
                },
                {
                    "content": "Content from document B",
                    "score": 0.85,
                    "retrievalResultMetadata": {
                        "location": {"s3Location": {"uri": "s3://bucket/doc-b.txt"}},
                        "document": {"documentId": "doc-b"}
                    }
                }
            ]
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    retrieve_api = RetrieveAPI(config)

                    results = retrieve_api.retrieve(
                        knowledge_base_id="kb-12345",
                        query="test query"
                    )

                    # Verify source document tracking
                    assert len(results) == 3
                    assert results[0].source_document == "doc-a"
                    assert results[1].source_document == "doc-a"
                    assert results[2].source_document == "doc-b"

                    # Verify location tracking
                    assert results[0].location == "s3://bucket/doc-a.txt"
                    assert results[1].location == "s3://bucket/doc-a.txt"
                    assert results[2].location == "s3://bucket/doc-b.txt"

    def test_retrieve_and_generate_with_citations(self, mock_bedrock_client):
        """Test that Retrieve and Generate includes proper citations"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.retrieve.return_value = {
            "retrievalResults": [
                {
                    "content": "Machine learning is a subset of artificial intelligence",
                    "score": 0.95,
                    "retrievalResultMetadata": {
                        "location": {"s3Location": {"uri": "s3://bucket/ai-basics.txt"}},
                        "document": {"documentId": "doc-ai-basics"}
                    }
                },
                {
                    "content": "Deep learning uses neural networks with multiple layers",
                    "score": 0.85,
                    "retrievalResultMetadata": {
                        "location": {"s3Location": {"uri": "s3://bucket/deep-learning.txt"}},
                        "document": {"documentId": "doc-deep-learning"}
                    }
                }
            ]
        }

        mock_bedrock_client.invoke_model.return_value = {
            "body": MagicMock(read=lambda: json.dumps({
                "content": [{"text": "Machine learning is a subset of AI that enables systems to learn from data. Deep learning, a specialized form of machine learning, uses neural networks with multiple layers to process complex patterns."}]
            }).encode())
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    rag_api = RetrieveAndGenerateAPI(config)

                    response = rag_api.retrieve_and_generate(
                        knowledge_base_id="kb-12345",
                        query="What is machine learning and deep learning?"
                    )

                    # Verify response includes generated text
                    assert response.generated_text is not None
                    assert "machine learning" in response.generated_text.lower()

                    # Verify source documents are tracked
                    assert response.source_documents is not None
                    assert len(response.source_documents) > 0

    def test_retrieve_with_hybrid_search_configuration(self, mock_bedrock_client):
        """Test retrieval with hybrid search configuration"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.retrieve.return_value = {
            "retrievalResults": [
                {
                    "content": "Hybrid search combines vector and keyword search",
                    "score": 0.92,
                    "retrievalResultMetadata": {
                        "location": {"s3Location": {"uri": "s3://bucket/hybrid.txt"}},
                        "document": {"documentId": "doc-001"}
                    }
                }
            ]
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    retrieve_api = RetrieveAPI(config)

                    # Configure hybrid search
                    hybrid_config = RetrievalConfig(
                        max_results=5,
                        retrieval_type=RetrievalType.HYBRID,
                        vector_weight=0.6,
                        text_weight=0.4
                    )

                    results = retrieve_api.retrieve(
                        knowledge_base_id="kb-12345",
                        query="hybrid search",
                        config=hybrid_config
                    )

                    assert len(results) > 0
                    assert results[0].relevance_score == 0.92


class TestErrorScenarios:
    """Tests for error scenarios in end-to-end workflows"""

    def test_kb_creation_failure_handling(self, mock_bedrock_client):
        """Test handling of KB creation failure"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.list_knowledge_bases.return_value = {"knowledgeBaseSummaries": []}
        error_response = {"Error": {"Code": "AccessDenied", "Message": "User is not authorized"}}
        mock_bedrock_client.create_knowledge_base.side_effect = ClientError(error_response, "CreateKnowledgeBase")

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    kb_manager = BedrockKnowledgeBase(config)

                    vector_store_config = {
                        "collectionArn": "arn:aws:aoss:us-east-1:123456789012:collection/test",
                        "fieldMapping": {
                            "vectorField": "embedding",
                            "textField": "content",
                            "metadataField": "metadata"
                        }
                    }

                    with pytest.raises(ValueError, match="Failed to create knowledge base"):
                        kb_manager.create_knowledge_base(
                            kb_name="test-kb",
                            kb_description="Test",
                            role_arn="arn:aws:iam::123456789012:role/bedrock-kb-role",
                            vector_store_config=vector_store_config
                        )

    def test_data_source_creation_failure_handling(self, mock_bedrock_client):
        """Test handling of data source creation failure"""
        from config.aws_config import AWSConfig

        error_response = {"Error": {"Code": "ValidationException", "Message": "Invalid configuration"}}
        mock_bedrock_client.create_data_source.side_effect = ClientError(error_response, "CreateDataSource")

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    kb_manager = BedrockKnowledgeBase(config)

                    s3_config = {
                        "bucketArn": "arn:aws:s3:::test-bucket",
                        "inclusionPrefixes": ["documents/"]
                    }

                    with pytest.raises(ValueError, match="Failed to create data source"):
                        kb_manager.create_data_source(
                            kb_id="kb-12345",
                            data_source_name="test-source",
                            data_source_config=s3_config,
                            data_source_type="S3"
                        )

    def test_ingestion_job_failure_handling(self, mock_bedrock_client):
        """Test handling of ingestion job failure"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.get_ingestion_job.return_value = {
            "ingestionJob": {
                "ingestionJobId": "job-12345",
                "knowledgeBaseId": "kb-12345",
                "dataSourceId": "ds-12345",
                "status": "FAILED",
                "startedAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-01-01T00:10:00Z",
                "statistics": {},
                "failureReasons": ["Document parsing failed"]
            }
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    ingestion_manager = IngestionJobManager(config)

                    with pytest.raises(ValueError, match="Ingestion job failed"):
                        ingestion_manager.wait_for_ingestion_job_complete(
                            kb_id="kb-12345",
                            data_source_id="ds-12345",
                            ingestion_job_id="job-12345"
                        )

    def test_retrieval_with_no_results(self, mock_bedrock_client):
        """Test retrieval when no results are found"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.retrieve.return_value = {
            "retrievalResults": []
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    retrieve_api = RetrieveAPI(config)

                    results = retrieve_api.retrieve(
                        knowledge_base_id="kb-12345",
                        query="Nonexistent query"
                    )

                    assert len(results) == 0

    def test_retrieve_and_generate_with_empty_retrieval(self, mock_bedrock_client):
        """Test Retrieve and Generate when retrieval returns no results"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.retrieve.return_value = {
            "retrievalResults": []
        }

        mock_bedrock_client.invoke_model.return_value = {
            "body": MagicMock(read=lambda: json.dumps({
                "content": [{"text": "I could not find relevant information to answer your question."}]
            }).encode())
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    rag_api = RetrieveAndGenerateAPI(config)

                    response = rag_api.retrieve_and_generate(
                        knowledge_base_id="kb-12345",
                        query="Nonexistent query"
                    )

                    assert response.generated_text is not None

    def test_invalid_retrieval_configuration(self, mock_bedrock_client):
        """Test retrieval with invalid configuration"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    retrieve_api = RetrieveAPI(config)

                    # Invalid max_results
                    invalid_config = RetrievalConfig(max_results=0)

                    with pytest.raises(ValueError, match="max_results must be greater than 0"):
                        retrieve_api.retrieve(
                            knowledge_base_id="kb-12345",
                            query="Test",
                            config=invalid_config
                        )

    def test_invalid_generation_configuration(self, mock_bedrock_client):
        """Test generation with invalid configuration"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    rag_api = RetrieveAndGenerateAPI(config)

                    # Invalid temperature
                    invalid_config = GenerationConfig(temperature=1.5)

                    with pytest.raises(ValueError, match="temperature must be between"):
                        rag_api.retrieve_and_generate(
                            knowledge_base_id="kb-12345",
                            query="Test",
                            generation_config=invalid_config
                        )

    def test_workflow_with_partial_failures(self, mock_bedrock_client):
        """Test workflow handling when some documents fail to ingest"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.get_ingestion_job.return_value = {
            "ingestionJob": {
                "ingestionJobId": "job-12345",
                "knowledgeBaseId": "kb-12345",
                "dataSourceId": "ds-12345",
                "status": "COMPLETE",
                "startedAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-01-01T00:10:00Z",
                "statistics": {
                    "numberOfDocumentsProcessed": 100,
                    "numberOfDocumentsFailed": 10,
                    "numberOfDocumentsSucceeded": 90,
                    "numberOfChunksCreated": 450
                },
                "failureReasons": ["Some documents could not be parsed"]
            }
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    ingestion_manager = IngestionJobManager(config)

                    job_info = ingestion_manager.get_ingestion_job(
                        kb_id="kb-12345",
                        data_source_id="ds-12345",
                        ingestion_job_id="job-12345"
                    )

                    # Verify that job completed despite some failures
                    assert job_info["status"] == "COMPLETE"
                    assert job_info["statistics"]["numberOfDocumentsFailed"] == 10
                    assert job_info["statistics"]["numberOfDocumentsSucceeded"] == 90
