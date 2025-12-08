"""Tests for Knowledge Base management"""

import pytest
from unittest.mock import MagicMock, patch, call
from botocore.exceptions import ClientError
from src.knowledge_base_manager import BedrockKnowledgeBase
import os

# Disable hypothesis database to avoid Windows hanging issues
os.environ['HYPOTHESIS_DATABASE_DIRECTORY'] = 'none'


class TestKnowledgeBaseManagerInitialization:
    """Tests for Knowledge Base Manager initialization"""

    def test_init_with_aws_config(self, mock_bedrock_client):
        """Test Knowledge Base Manager initialization with AWS config"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    assert manager.aws_config is config
                    assert manager.account_id == '123456789012'
                    assert manager.region == 'us-east-1'


class TestCreateKnowledgeBase:
    """Tests for Knowledge Base creation"""

    def test_create_knowledge_base_success(self, mock_bedrock_client):
        """Test successful Knowledge Base creation"""
        from config.aws_config import AWSConfig

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

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    vector_store_config = {
                        "collectionArn": "arn:aws:aoss:us-east-1:123456789012:collection/test-collection",
                        "fieldMapping": {
                            "vectorField": "embedding",
                            "textField": "content",
                            "metadataField": "metadata"
                        }
                    }

                    result = manager.create_knowledge_base(
                        kb_name="test-kb",
                        kb_description="Test knowledge base",
                        role_arn="arn:aws:iam::123456789012:role/bedrock-kb-role",
                        vector_store_config=vector_store_config
                    )

                    assert result["kb_id"] == "kb-12345"
                    assert result["kb_name"] == "test-kb"
                    assert result["status"] == "CREATING"

    def test_create_knowledge_base_idempotence(self, mock_bedrock_client):
        """Test Knowledge Base creation idempotence (returns existing KB)"""
        from config.aws_config import AWSConfig

        # First call returns existing KB
        mock_bedrock_client.list_knowledge_bases.return_value = {
            "knowledgeBaseSummaries": [
                {
                    "knowledgeBaseId": "kb-12345",
                    "name": "test-kb",
                    "description": "Test knowledge base",
                    "status": "ACTIVE",
                    "createdAt": "2024-01-01T00:00:00Z"
                }
            ]
        }

        mock_bedrock_client.get_knowledge_base.return_value = {
            "knowledgeBase": {
                "id": "kb-12345",
                "name": "test-kb",
                "description": "Test knowledge base",
                "status": "ACTIVE",
                "roleArn": "arn:aws:iam::123456789012:role/bedrock-kb-role",
                "createdAt": "2024-01-01T00:00:00Z"
            }
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    vector_store_config = {
                        "collectionArn": "arn:aws:aoss:us-east-1:123456789012:collection/test-collection",
                        "fieldMapping": {
                            "vectorField": "embedding",
                            "textField": "content",
                            "metadataField": "metadata"
                        }
                    }

                    result = manager.create_knowledge_base(
                        kb_name="test-kb",
                        kb_description="Test knowledge base",
                        role_arn="arn:aws:iam::123456789012:role/bedrock-kb-role",
                        vector_store_config=vector_store_config
                    )

                    # Should return existing KB without calling create_knowledge_base
                    assert result["kb_id"] == "kb-12345"
                    assert result["kb_name"] == "test-kb"
                    mock_bedrock_client.create_knowledge_base.assert_not_called()

    def test_create_knowledge_base_empty_name(self, mock_bedrock_client):
        """Test KB creation with empty name"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    with pytest.raises(ValueError, match="Knowledge base name cannot be empty"):
                        manager.create_knowledge_base(
                            kb_name="",
                            kb_description="Test",
                            role_arn="arn:aws:iam::123456789012:role/bedrock-kb-role",
                            vector_store_config={}
                        )

    def test_create_knowledge_base_invalid_chunk_size(self, mock_bedrock_client):
        """Test KB creation with invalid chunk size"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    vector_store_config = {
                        "collectionArn": "arn:aws:aoss:us-east-1:123456789012:collection/test-collection",
                        "fieldMapping": {
                            "vectorField": "embedding",
                            "textField": "content",
                            "metadataField": "metadata"
                        }
                    }

                    with pytest.raises(ValueError, match="Chunk size must be greater than 0"):
                        manager.create_knowledge_base(
                            kb_name="test-kb",
                            kb_description="Test",
                            role_arn="arn:aws:iam::123456789012:role/bedrock-kb-role",
                            vector_store_config=vector_store_config,
                            chunk_size=-1
                        )

    def test_create_knowledge_base_invalid_chunk_overlap(self, mock_bedrock_client):
        """Test KB creation with invalid chunk overlap"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    vector_store_config = {
                        "collectionArn": "arn:aws:aoss:us-east-1:123456789012:collection/test-collection",
                        "fieldMapping": {
                            "vectorField": "embedding",
                            "textField": "content",
                            "metadataField": "metadata"
                        }
                    }

                    with pytest.raises(ValueError, match="Chunk overlap must be less than chunk size"):
                        manager.create_knowledge_base(
                            kb_name="test-kb",
                            kb_description="Test",
                            role_arn="arn:aws:iam::123456789012:role/bedrock-kb-role",
                            vector_store_config=vector_store_config,
                            chunk_size=1024,
                            chunk_overlap=1024
                        )

    def test_create_knowledge_base_failure(self, mock_bedrock_client):
        """Test KB creation failure"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.list_knowledge_bases.return_value = {"knowledgeBaseSummaries": []}
        error_response = {"Error": {"Code": "AccessDenied", "Message": "User is not authorized"}}
        mock_bedrock_client.create_knowledge_base.side_effect = ClientError(error_response, "CreateKnowledgeBase")

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    vector_store_config = {
                        "collectionArn": "arn:aws:aoss:us-east-1:123456789012:collection/test-collection",
                        "fieldMapping": {
                            "vectorField": "embedding",
                            "textField": "content",
                            "metadataField": "metadata"
                        }
                    }

                    with pytest.raises(ValueError, match="Failed to create knowledge base"):
                        manager.create_knowledge_base(
                            kb_name="test-kb",
                            kb_description="Test",
                            role_arn="arn:aws:iam::123456789012:role/bedrock-kb-role",
                            vector_store_config=vector_store_config
                        )


class TestGetKnowledgeBase:
    """Tests for retrieving Knowledge Base information"""

    def test_get_knowledge_base_success(self, mock_bedrock_client):
        """Test successful KB retrieval"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.get_knowledge_base.return_value = {
            "knowledgeBase": {
                "id": "kb-12345",
                "name": "test-kb",
                "description": "Test knowledge base",
                "status": "ACTIVE",
                "roleArn": "arn:aws:iam::123456789012:role/bedrock-kb-role",
                "createdAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-01-02T00:00:00Z"
            }
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    result = manager.get_knowledge_base("kb-12345")

                    assert result["kb_id"] == "kb-12345"
                    assert result["kb_name"] == "test-kb"
                    assert result["status"] == "ACTIVE"

    def test_get_knowledge_base_not_found(self, mock_bedrock_client):
        """Test KB retrieval when KB doesn't exist"""
        from config.aws_config import AWSConfig

        error_response = {"Error": {"Code": "ResourceNotFoundException", "Message": "KB not found"}}
        mock_bedrock_client.get_knowledge_base.side_effect = ClientError(error_response, "GetKnowledgeBase")

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    with pytest.raises(ValueError, match="not found"):
                        manager.get_knowledge_base("kb-nonexistent")


class TestGetKnowledgeBaseStatus:
    """Tests for retrieving Knowledge Base status"""

    def test_get_knowledge_base_status_active(self, mock_bedrock_client):
        """Test getting KB status when ACTIVE"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.get_knowledge_base.return_value = {
            "knowledgeBase": {
                "id": "kb-12345",
                "name": "test-kb",
                "status": "ACTIVE",
                "roleArn": "arn:aws:iam::123456789012:role/bedrock-kb-role",
                "createdAt": "2024-01-01T00:00:00Z"
            }
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    status = manager.get_knowledge_base_status("kb-12345")

                    assert status == "ACTIVE"


class TestListKnowledgeBases:
    """Tests for listing Knowledge Bases"""

    def test_list_knowledge_bases_success(self, mock_bedrock_client):
        """Test successful KB listing"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.list_knowledge_bases.return_value = {
            "knowledgeBaseSummaries": [
                {
                    "knowledgeBaseId": "kb-12345",
                    "name": "test-kb-1",
                    "description": "Test KB 1",
                    "status": "ACTIVE",
                    "createdAt": "2024-01-01T00:00:00Z"
                },
                {
                    "knowledgeBaseId": "kb-67890",
                    "name": "test-kb-2",
                    "description": "Test KB 2",
                    "status": "ACTIVE",
                    "createdAt": "2024-01-02T00:00:00Z"
                }
            ]
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    result = manager.list_knowledge_bases()

                    assert len(result) == 2
                    assert result[0]["kb_name"] == "test-kb-1"
                    assert result[1]["kb_name"] == "test-kb-2"

    def test_list_knowledge_bases_empty(self, mock_bedrock_client):
        """Test KB listing when no KBs exist"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.list_knowledge_bases.return_value = {"knowledgeBaseSummaries": []}

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    result = manager.list_knowledge_bases()

                    assert len(result) == 0


class TestDeleteKnowledgeBase:
    """Tests for deleting Knowledge Bases"""

    def test_delete_knowledge_base_success(self, mock_bedrock_client):
        """Test successful KB deletion"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.delete_knowledge_base.return_value = {}

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    result = manager.delete_knowledge_base("kb-12345")

                    assert result is True

    def test_delete_knowledge_base_not_found(self, mock_bedrock_client):
        """Test KB deletion when KB doesn't exist"""
        from config.aws_config import AWSConfig

        error_response = {"Error": {"Code": "ResourceNotFoundException", "Message": "KB not found"}}
        mock_bedrock_client.delete_knowledge_base.side_effect = ClientError(error_response, "DeleteKnowledgeBase")

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    # Should return True even if KB doesn't exist
                    result = manager.delete_knowledge_base("kb-nonexistent")

                    assert result is True


class TestCreateDataSource:
    """Tests for creating data sources"""

    def test_create_data_source_s3_success(self, mock_bedrock_client):
        """Test successful S3 data source creation"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.create_data_source.return_value = {
            "dataSource": {
                "id": "ds-12345",
                "name": "test-s3-source",
                "status": "AVAILABLE",
                "createdAt": "2024-01-01T00:00:00Z"
            }
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    s3_config = {
                        "bucketArn": "arn:aws:s3:::test-bucket",
                        "inclusionPrefixes": ["documents/"]
                    }

                    result = manager.create_data_source(
                        kb_id="kb-12345",
                        data_source_name="test-s3-source",
                        data_source_config=s3_config,
                        data_source_type="S3"
                    )

                    assert result["data_source_id"] == "ds-12345"
                    assert result["data_source_name"] == "test-s3-source"
                    assert result["data_source_type"] == "S3"

    def test_create_data_source_confluence_success(self, mock_bedrock_client):
        """Test successful Confluence data source creation"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.create_data_source.return_value = {
            "dataSource": {
                "id": "ds-67890",
                "name": "test-confluence-source",
                "status": "AVAILABLE",
                "createdAt": "2024-01-01T00:00:00Z"
            }
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    confluence_config = {
                        "sourceConfiguration": {
                            "authType": "OAUTH2",
                            "credentials": {
                                "secretArn": "arn:aws:secretsmanager:us-east-1:123456789012:secret:confluence-creds"
                            }
                        },
                        "hostUrl": "https://example.atlassian.net"
                    }

                    result = manager.create_data_source(
                        kb_id="kb-12345",
                        data_source_name="test-confluence-source",
                        data_source_config=confluence_config,
                        data_source_type="CONFLUENCE"
                    )

                    assert result["data_source_id"] == "ds-67890"
                    assert result["data_source_name"] == "test-confluence-source"
                    assert result["data_source_type"] == "CONFLUENCE"

    def test_create_data_source_sharepoint_success(self, mock_bedrock_client):
        """Test successful SharePoint data source creation"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.create_data_source.return_value = {
            "dataSource": {
                "id": "ds-11111",
                "name": "test-sharepoint-source",
                "status": "AVAILABLE",
                "createdAt": "2024-01-01T00:00:00Z"
            }
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    sharepoint_config = {
                        "sourceConfiguration": {
                            "authType": "OAUTH2",
                            "credentials": {
                                "secretArn": "arn:aws:secretsmanager:us-east-1:123456789012:secret:sharepoint-creds"
                            }
                        },
                        "siteUrls": ["https://example.sharepoint.com/sites/team"]
                    }

                    result = manager.create_data_source(
                        kb_id="kb-12345",
                        data_source_name="test-sharepoint-source",
                        data_source_config=sharepoint_config,
                        data_source_type="SHAREPOINT"
                    )

                    assert result["data_source_id"] == "ds-11111"
                    assert result["data_source_type"] == "SHAREPOINT"

    def test_create_data_source_salesforce_success(self, mock_bedrock_client):
        """Test successful Salesforce data source creation"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.create_data_source.return_value = {
            "dataSource": {
                "id": "ds-22222",
                "name": "test-salesforce-source",
                "status": "AVAILABLE",
                "createdAt": "2024-01-01T00:00:00Z"
            }
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    salesforce_config = {
                        "sourceConfiguration": {
                            "authType": "OAUTH2",
                            "credentials": {
                                "secretArn": "arn:aws:secretsmanager:us-east-1:123456789012:secret:salesforce-creds"
                            }
                        },
                        "instanceUrl": "https://example.salesforce.com"
                    }

                    result = manager.create_data_source(
                        kb_id="kb-12345",
                        data_source_name="test-salesforce-source",
                        data_source_config=salesforce_config,
                        data_source_type="SALESFORCE"
                    )

                    assert result["data_source_id"] == "ds-22222"
                    assert result["data_source_type"] == "SALESFORCE"

    def test_create_data_source_web_success(self, mock_bedrock_client):
        """Test successful Web data source creation"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.create_data_source.return_value = {
            "dataSource": {
                "id": "ds-33333",
                "name": "test-web-source",
                "status": "AVAILABLE",
                "createdAt": "2024-01-01T00:00:00Z"
            }
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    web_config = {
                        "sourceConfiguration": {
                            "urlConfiguration": {
                                "seedUrls": [
                                    {"url": "https://example.com"}
                                ]
                            }
                        }
                    }

                    result = manager.create_data_source(
                        kb_id="kb-12345",
                        data_source_name="test-web-source",
                        data_source_config=web_config,
                        data_source_type="WEB"
                    )

                    assert result["data_source_id"] == "ds-33333"
                    assert result["data_source_type"] == "WEB"

    def test_create_data_source_invalid_type(self, mock_bedrock_client):
        """Test data source creation with invalid type"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    s3_config = {
                        "bucketArn": "arn:aws:s3:::test-bucket",
                        "inclusionPrefixes": ["documents/"]
                    }

                    with pytest.raises(ValueError, match="Invalid data source type"):
                        manager.create_data_source(
                            kb_id="kb-12345",
                            data_source_name="test-source",
                            data_source_config=s3_config,
                            data_source_type="INVALID"
                        )

    def test_create_data_source_empty_name(self, mock_bedrock_client):
        """Test data source creation with empty name"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    with pytest.raises(ValueError, match="Data source name cannot be empty"):
                        manager.create_data_source(
                            kb_id="kb-12345",
                            data_source_name="",
                            data_source_config={},
                            data_source_type="S3"
                        )

    def test_create_data_source_failure(self, mock_bedrock_client):
        """Test data source creation failure"""
        from config.aws_config import AWSConfig

        error_response = {"Error": {"Code": "AccessDenied", "Message": "User is not authorized"}}
        mock_bedrock_client.create_data_source.side_effect = ClientError(error_response, "CreateDataSource")

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    s3_config = {
                        "bucketArn": "arn:aws:s3:::test-bucket",
                        "inclusionPrefixes": ["documents/"]
                    }

                    with pytest.raises(ValueError, match="Failed to create data source"):
                        manager.create_data_source(
                            kb_id="kb-12345",
                            data_source_name="test-source",
                            data_source_config=s3_config,
                            data_source_type="S3"
                        )


class TestGetDataSource:
    """Tests for retrieving data source information"""

    def test_get_data_source_success(self, mock_bedrock_client):
        """Test successful data source retrieval"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.get_data_source.return_value = {
            "dataSource": {
                "id": "ds-12345",
                "name": "test-source",
                "status": "AVAILABLE",
                "createdAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-01-02T00:00:00Z"
            }
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    result = manager.get_data_source("kb-12345", "ds-12345")

                    assert result["data_source_id"] == "ds-12345"
                    assert result["data_source_name"] == "test-source"
                    assert result["status"] == "AVAILABLE"

    def test_get_data_source_not_found(self, mock_bedrock_client):
        """Test data source retrieval when not found"""
        from config.aws_config import AWSConfig

        error_response = {"Error": {"Code": "ResourceNotFoundException", "Message": "DS not found"}}
        mock_bedrock_client.get_data_source.side_effect = ClientError(error_response, "GetDataSource")

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    with pytest.raises(ValueError, match="not found"):
                        manager.get_data_source("kb-12345", "ds-nonexistent")


class TestGetDataSourceStatus:
    """Tests for retrieving data source status"""

    def test_get_data_source_status_available(self, mock_bedrock_client):
        """Test getting data source status when AVAILABLE"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.get_data_source.return_value = {
            "dataSource": {
                "id": "ds-12345",
                "name": "test-source",
                "status": "AVAILABLE",
                "createdAt": "2024-01-01T00:00:00Z"
            }
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    status = manager.get_data_source_status("kb-12345", "ds-12345")

                    assert status == "AVAILABLE"

    def test_get_data_source_status_deleting(self, mock_bedrock_client):
        """Test getting data source status when DELETING"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.get_data_source.return_value = {
            "dataSource": {
                "id": "ds-12345",
                "name": "test-source",
                "status": "DELETING",
                "createdAt": "2024-01-01T00:00:00Z"
            }
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    status = manager.get_data_source_status("kb-12345", "ds-12345")

                    assert status == "DELETING"


class TestListDataSources:
    """Tests for listing data sources"""

    def test_list_data_sources_success(self, mock_bedrock_client):
        """Test successful data source listing"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.list_data_sources.return_value = {
            "dataSourceSummaries": [
                {
                    "dataSourceId": "ds-12345",
                    "name": "test-source-1",
                    "status": "AVAILABLE",
                    "createdAt": "2024-01-01T00:00:00Z"
                },
                {
                    "dataSourceId": "ds-67890",
                    "name": "test-source-2",
                    "status": "AVAILABLE",
                    "createdAt": "2024-01-02T00:00:00Z"
                }
            ]
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    result = manager.list_data_sources("kb-12345")

                    assert len(result) == 2
                    assert result[0]["data_source_name"] == "test-source-1"
                    assert result[1]["data_source_name"] == "test-source-2"

    def test_list_data_sources_empty(self, mock_bedrock_client):
        """Test data source listing when no sources exist"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.list_data_sources.return_value = {"dataSourceSummaries": []}

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    result = manager.list_data_sources("kb-12345")

                    assert len(result) == 0


class TestDeleteDataSource:
    """Tests for deleting data sources"""

    def test_delete_data_source_success(self, mock_bedrock_client):
        """Test successful data source deletion"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.delete_data_source.return_value = {}

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    result = manager.delete_data_source("kb-12345", "ds-12345")

                    assert result is True

    def test_delete_data_source_not_found(self, mock_bedrock_client):
        """Test data source deletion when not found"""
        from config.aws_config import AWSConfig

        error_response = {"Error": {"Code": "ResourceNotFoundException", "Message": "DS not found"}}
        mock_bedrock_client.delete_data_source.side_effect = ClientError(error_response, "DeleteDataSource")

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    # Should return True even if DS doesn't exist
                    result = manager.delete_data_source("kb-12345", "ds-nonexistent")

                    assert result is True


class TestStartIngestionJob:
    """Tests for starting ingestion jobs"""

    def test_start_ingestion_job_success(self, mock_bedrock_client):
        """Test successful ingestion job start"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.start_ingestion_job.return_value = {
            "ingestionJob": {
                "ingestionJobId": "job-12345",
                "knowledgeBaseId": "kb-12345",
                "dataSourceId": "ds-12345",
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
                    manager = BedrockKnowledgeBase(config)

                    result = manager.start_ingestion_job(
                        kb_id="kb-12345",
                        data_source_id="ds-12345"
                    )

                    assert result["ingestion_job_id"] == "job-12345"
                    assert result["status"] == "STARTING"


class TestGetIngestionJob:
    """Tests for retrieving ingestion job information"""

    def test_get_ingestion_job_success(self, mock_bedrock_client):
        """Test successful ingestion job retrieval"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.get_ingestion_job.return_value = {
            "ingestionJob": {
                "ingestionJobId": "job-12345",
                "knowledgeBaseId": "kb-12345",
                "dataSourceId": "ds-12345",
                "status": "COMPLETE",
                "startedAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-01-01T01:00:00Z",
                "statistics": {
                    "documentsProcessed": 100,
                    "documentsFailed": 0
                }
            }
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    result = manager.get_ingestion_job(
                        kb_id="kb-12345",
                        data_source_id="ds-12345",
                        ingestion_job_id="job-12345"
                    )

                    assert result["ingestion_job_id"] == "job-12345"
                    assert result["status"] == "COMPLETE"
                    assert result["statistics"]["documentsProcessed"] == 100


class TestModelArnConversion:
    """Tests for model ARN conversion"""

    def test_get_model_arn_with_model_id(self, mock_bedrock_client):
        """Test ARN conversion from model ID"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    arn = manager._get_model_arn("amazon.titan-embed-text-v2:0")

                    assert "arn:aws:bedrock:us-east-1::foundation-model/" in arn
                    assert "amazon.titan-embed-text-v2:0" in arn

    def test_get_model_arn_with_full_arn(self, mock_bedrock_client):
        """Test ARN conversion when already an ARN"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    full_arn = "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v2:0"
                    arn = manager._get_model_arn(full_arn)

                    assert arn == full_arn


class TestEmbeddingDimensions:
    """Tests for embedding dimension detection"""

    def test_get_embedding_dimensions_titan(self, mock_bedrock_client):
        """Test embedding dimensions for Titan model"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    dims = manager._get_embedding_dimensions("amazon.titan-embed-text-v2:0")

                    assert dims == 1536

    def test_get_embedding_dimensions_cohere(self, mock_bedrock_client):
        """Test embedding dimensions for Cohere model"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    dims = manager._get_embedding_dimensions("cohere.embed-english-v3")

                    assert dims == 1024


class TestCleanupKnowledgeBase:
    """Tests for Knowledge Base cleanup and deletion"""

    def test_cleanup_knowledge_base_success(self, mock_bedrock_client):
        """Test successful knowledge base cleanup"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.list_data_sources.return_value = {
            "dataSourceSummaries": [
                {
                    "dataSourceId": "ds-12345",
                    "name": "test-source-1",
                    "status": "AVAILABLE",
                    "createdAt": "2024-01-01T00:00:00Z"
                }
            ]
        }
        mock_bedrock_client.delete_data_source.return_value = {}
        mock_bedrock_client.delete_knowledge_base.return_value = {}

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    result = manager.cleanup_knowledge_base("kb-12345")

                    assert result["kb_deleted"] is True
                    assert result["data_sources_deleted"] == 1
                    assert len(result["errors"]) == 0

    def test_cleanup_knowledge_base_no_data_sources(self, mock_bedrock_client):
        """Test cleanup when no data sources exist"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.list_data_sources.return_value = {"dataSourceSummaries": []}
        mock_bedrock_client.delete_knowledge_base.return_value = {}

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    result = manager.cleanup_knowledge_base("kb-12345")

                    assert result["kb_deleted"] is True
                    assert result["data_sources_deleted"] == 0
                    assert len(result["errors"]) == 0

    def test_cleanup_knowledge_base_with_errors(self, mock_bedrock_client):
        """Test cleanup when data source deletion fails"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.list_data_sources.return_value = {
            "dataSourceSummaries": [
                {
                    "dataSourceId": "ds-12345",
                    "name": "test-source-1",
                    "status": "AVAILABLE",
                    "createdAt": "2024-01-01T00:00:00Z"
                }
            ]
        }
        error_response = {"Error": {"Code": "AccessDenied", "Message": "Access denied"}}
        mock_bedrock_client.delete_data_source.side_effect = ClientError(error_response, "DeleteDataSource")
        mock_bedrock_client.delete_knowledge_base.return_value = {}

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    result = manager.cleanup_knowledge_base("kb-12345")

                    assert result["kb_deleted"] is True
                    assert result["data_sources_deleted"] == 0
                    assert len(result["errors"]) > 0

    def test_cleanup_knowledge_base_empty_id(self, mock_bedrock_client):
        """Test cleanup with empty KB ID"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    with pytest.raises(ValueError, match="Knowledge base ID cannot be empty"):
                        manager.cleanup_knowledge_base("")

    def test_cleanup_all_resources_without_confirmation(self, mock_bedrock_client):
        """Test comprehensive cleanup without confirmation"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    with pytest.raises(ValueError, match="Cleanup confirmation required"):
                        manager.cleanup_all_resources("kb-12345", confirm=False)

    def test_cleanup_all_resources_with_confirmation(self, mock_bedrock_client):
        """Test comprehensive cleanup with confirmation"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.list_data_sources.return_value = {"dataSourceSummaries": []}
        mock_bedrock_client.delete_knowledge_base.return_value = {}

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    result = manager.cleanup_all_resources("kb-12345", confirm=True)

                    assert result["kb_cleanup"]["kb_deleted"] is True
                    assert len(result["total_errors"]) == 0


@pytest.mark.parametrize("kb_name,kb_description", [
    ("test-kb-1", "This is a test knowledge base"),
    ("my-kb", "Knowledge base for testing"),
    ("kb-prod", "Production knowledge base"),
    ("test-kb-2", "Another test knowledge base"),
    ("kb-dev", "Development knowledge base")
])
def test_kb_creation_idempotence_property(kb_name, kb_description):
    """
    **Feature: bedrock-rag-retrieval, Property 1: Knowledge Base Creation Idempotence**
    
    For any knowledge base configuration, creating the knowledge base multiple times 
    with the same parameters should result in the same knowledge base being retrieved 
    rather than creating duplicates.
    
    **Validates: Requirements 1.1, 1.2, 1.3**
    """
    from config.aws_config import AWSConfig

    with patch('boto3.client') as mock_boto_client:
        mock_bedrock_client = MagicMock()
        mock_boto_client.return_value = mock_bedrock_client

        # First creation - KB doesn't exist yet
        mock_bedrock_client.list_knowledge_bases.return_value = {"knowledgeBaseSummaries": []}
        mock_bedrock_client.create_knowledge_base.return_value = {
            "knowledgeBase": {
                "id": "kb-test-123",
                "name": kb_name,
                "description": kb_description,
                "status": "CREATING",
                "createdAt": "2024-01-01T00:00:00Z"
            }
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.side_effect = lambda service: mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = BedrockKnowledgeBase(config)

                    vector_store_config = {
                        "collectionArn": "arn:aws:aoss:us-east-1:123456789012:collection/test-collection",
                        "fieldMapping": {
                            "vectorField": "embedding",
                            "textField": "content",
                            "metadataField": "metadata"
                        }
                    }

                    # First creation
                    result1 = manager.create_knowledge_base(
                        kb_name=kb_name,
                        kb_description=kb_description,
                        role_arn="arn:aws:iam::123456789012:role/bedrock-kb-role",
                        vector_store_config=vector_store_config
                    )

                    # Second creation - KB now exists
                    mock_bedrock_client.list_knowledge_bases.return_value = {
                        "knowledgeBaseSummaries": [
                            {
                                "knowledgeBaseId": "kb-test-123",
                                "name": kb_name,
                                "description": kb_description,
                                "status": "ACTIVE",
                                "createdAt": "2024-01-01T00:00:00Z"
                            }
                        ]
                    }

                    mock_bedrock_client.get_knowledge_base.return_value = {
                        "knowledgeBase": {
                            "id": "kb-test-123",
                            "name": kb_name,
                            "description": kb_description,
                            "status": "ACTIVE",
                            "roleArn": "arn:aws:iam::123456789012:role/bedrock-kb-role",
                            "createdAt": "2024-01-01T00:00:00Z"
                        }
                    }

                    result2 = manager.create_knowledge_base(
                        kb_name=kb_name,
                        kb_description=kb_description,
                        role_arn="arn:aws:iam::123456789012:role/bedrock-kb-role",
                        vector_store_config=vector_store_config
                    )

                    # Both results should have the same KB ID (idempotence)
                    assert result1["kb_id"] == result2["kb_id"], \
                        "Creating KB with same parameters should return same KB ID"
                    
                    # Both should have the same name
                    assert result1["kb_name"] == result2["kb_name"], \
                        "KB name should be consistent across creations"
                    
                    # Both should have the same description
                    assert result1["kb_description"] == result2["kb_description"], \
                        "KB description should be consistent across creations"
                    
                    # create_knowledge_base should only be called once (for first creation)
                    assert mock_bedrock_client.create_knowledge_base.call_count == 1, \
                        "create_knowledge_base should only be called once due to idempotence"
