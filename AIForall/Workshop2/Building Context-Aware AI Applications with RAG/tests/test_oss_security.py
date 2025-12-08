"""Tests for OpenSearch Serverless security policy management"""

import pytest
import json
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError
from src.oss_security import OSSSecurityManager


class TestOSSSecurityManagerInitialization:
    """Tests for OSS Security Manager initialization"""

    def test_init_with_aws_config(self, mock_opensearch_client):
        """Test OSS Security Manager initialization with AWS config"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = OSSSecurityManager(config)

                    assert manager.aws_config is config
                    assert manager.oss_client is mock_opensearch_client
                    assert manager.account_id == '123456789012'
                    assert manager.region == 'us-east-1'


class TestEncryptionPolicy:
    """Tests for encryption policy creation"""

    def test_create_encryption_policy_success(self, mock_opensearch_client):
        """Test successful creation of encryption policy"""
        from config.aws_config import AWSConfig

        mock_opensearch_client.create_security_policy.return_value = {
            "securityPolicyDetail": {
                "name": "bedrock-encryption-policy",
                "version": "1",
                "createdDate": 1234567890,
                "type": "encryption"
            }
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = OSSSecurityManager(config)
                    result = manager.create_encryption_policy("bedrock-encryption-policy")

                    assert result["policy_name"] == "bedrock-encryption-policy"
                    assert result["policy_version"] == "1"
                    assert result["policy_type"] == "encryption"

    def test_create_encryption_policy_already_exists(self, mock_opensearch_client):
        """Test creation when encryption policy already exists"""
        from config.aws_config import AWSConfig

        error_response = {"Error": {"Code": "ConflictException", "Message": "Policy already exists"}}
        mock_opensearch_client.create_security_policy.side_effect = ClientError(error_response, "CreateSecurityPolicy")
        mock_opensearch_client.get_security_policy.return_value = {
            "securityPolicyDetail": {
                "name": "bedrock-encryption-policy",
                "version": "1",
                "createdDate": 1234567890,
                "type": "encryption"
            }
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = OSSSecurityManager(config)
                    result = manager.create_encryption_policy("bedrock-encryption-policy")

                    assert result["policy_name"] == "bedrock-encryption-policy"
                    assert result["policy_type"] == "encryption"

    def test_create_encryption_policy_failure(self, mock_opensearch_client):
        """Test encryption policy creation failure"""
        from config.aws_config import AWSConfig

        error_response = {"Error": {"Code": "AccessDenied", "Message": "User is not authorized"}}
        mock_opensearch_client.create_security_policy.side_effect = ClientError(error_response, "CreateSecurityPolicy")

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = OSSSecurityManager(config)

                    with pytest.raises(ValueError, match="Failed to create encryption policy"):
                        manager.create_encryption_policy("bedrock-encryption-policy")


class TestNetworkPolicy:
    """Tests for network policy creation"""

    def test_create_network_policy_private_success(self, mock_opensearch_client):
        """Test successful creation of private network policy"""
        from config.aws_config import AWSConfig

        mock_opensearch_client.create_security_policy.return_value = {
            "securityPolicyDetail": {
                "name": "bedrock-network-policy",
                "version": "1",
                "createdDate": 1234567890,
                "type": "network"
            }
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = OSSSecurityManager(config)
                    result = manager.create_network_policy(
                        "bedrock-network-policy",
                        ["test-collection"],
                        allow_public_access=False
                    )

                    assert result["policy_name"] == "bedrock-network-policy"
                    assert result["policy_type"] == "network"
                    assert result["public_access_enabled"] is False

    def test_create_network_policy_public_success(self, mock_opensearch_client):
        """Test successful creation of public network policy"""
        from config.aws_config import AWSConfig

        mock_opensearch_client.create_security_policy.return_value = {
            "securityPolicyDetail": {
                "name": "bedrock-network-policy",
                "version": "1",
                "createdDate": 1234567890,
                "type": "network"
            }
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = OSSSecurityManager(config)
                    result = manager.create_network_policy(
                        "bedrock-network-policy",
                        ["test-collection"],
                        allow_public_access=True
                    )

                    assert result["policy_name"] == "bedrock-network-policy"
                    assert result["public_access_enabled"] is True

    def test_create_network_policy_multiple_collections(self, mock_opensearch_client):
        """Test network policy with multiple collections"""
        from config.aws_config import AWSConfig

        mock_opensearch_client.create_security_policy.return_value = {
            "securityPolicyDetail": {
                "name": "bedrock-network-policy",
                "version": "1",
                "createdDate": 1234567890,
                "type": "network"
            }
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = OSSSecurityManager(config)
                    result = manager.create_network_policy(
                        "bedrock-network-policy",
                        ["collection-1", "collection-2", "collection-3"]
                    )

                    assert result["policy_name"] == "bedrock-network-policy"
                    # Verify the policy document includes all collections
                    call_args = mock_opensearch_client.create_security_policy.call_args
                    policy_doc = json.loads(call_args[1]["policy"])
                    assert len(policy_doc["Rules"]) == 3


class TestDataAccessPolicy:
    """Tests for data access policy creation"""

    def test_create_data_access_policy_success(self, mock_opensearch_client):
        """Test successful creation of data access policy"""
        from config.aws_config import AWSConfig

        mock_opensearch_client.create_access_policy.return_value = {
            "accessPolicyDetail": {
                "name": "bedrock-data-access-policy",
                "version": "1",
                "createdDate": 1234567890,
                "type": "data"
            }
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = OSSSecurityManager(config)
                    result = manager.create_data_access_policy(
                        "bedrock-data-access-policy",
                        ["test-collection"],
                        ["arn:aws:iam::123456789012:role/bedrock-kb-execution-role"]
                    )

                    assert result["policy_name"] == "bedrock-data-access-policy"
                    assert result["policy_type"] == "data"
                    assert result["principals_count"] == 1

    def test_create_data_access_policy_multiple_principals(self, mock_opensearch_client):
        """Test data access policy with multiple principals"""
        from config.aws_config import AWSConfig

        mock_opensearch_client.create_access_policy.return_value = {
            "accessPolicyDetail": {
                "name": "bedrock-data-access-policy",
                "version": "1",
                "createdDate": 1234567890,
                "type": "data"
            }
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = OSSSecurityManager(config)
                    principals = [
                        "arn:aws:iam::123456789012:role/bedrock-kb-execution-role",
                        "arn:aws:iam::123456789012:role/bedrock-retrieval-role"
                    ]
                    result = manager.create_data_access_policy(
                        "bedrock-data-access-policy",
                        ["test-collection"],
                        principals
                    )

                    assert result["principals_count"] == 2

    def test_create_data_access_policy_already_exists(self, mock_opensearch_client):
        """Test creation when data access policy already exists"""
        from config.aws_config import AWSConfig

        error_response = {"Error": {"Code": "ConflictException", "Message": "Policy already exists"}}
        mock_opensearch_client.create_access_policy.side_effect = ClientError(error_response, "CreateAccessPolicy")
        mock_opensearch_client.get_access_policy.return_value = {
            "accessPolicyDetail": {
                "name": "bedrock-data-access-policy",
                "version": "1",
                "createdDate": 1234567890,
                "type": "data"
            }
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = OSSSecurityManager(config)
                    result = manager.create_data_access_policy(
                        "bedrock-data-access-policy",
                        ["test-collection"],
                        ["arn:aws:iam::123456789012:role/bedrock-kb-execution-role"]
                    )

                    assert result["policy_name"] == "bedrock-data-access-policy"


class TestPolicyRetrieval:
    """Tests for retrieving policy information"""

    def test_get_encryption_policy_success(self, mock_opensearch_client):
        """Test successful retrieval of encryption policy"""
        from config.aws_config import AWSConfig

        policy_doc = {"Rules": [{"Resource": ["collection/*"], "ResourceType": "collection"}]}
        mock_opensearch_client.get_security_policy.return_value = {
            "securityPolicyDetail": {
                "name": "bedrock-encryption-policy",
                "version": "1",
                "createdDate": 1234567890,
                "type": "encryption",
                "policy": json.dumps(policy_doc)
            }
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = OSSSecurityManager(config)
                    result = manager.get_encryption_policy("bedrock-encryption-policy")

                    assert result["policy_name"] == "bedrock-encryption-policy"
                    assert result["policy_type"] == "encryption"
                    assert result["policy"] == policy_doc

    def test_get_network_policy_success(self, mock_opensearch_client):
        """Test successful retrieval of network policy"""
        from config.aws_config import AWSConfig

        policy_doc = {"Rules": [{"Resource": ["collection/test"], "ResourceType": "collection"}]}
        mock_opensearch_client.get_security_policy.return_value = {
            "securityPolicyDetail": {
                "name": "bedrock-network-policy",
                "version": "1",
                "createdDate": 1234567890,
                "type": "network",
                "policy": json.dumps(policy_doc)
            }
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = OSSSecurityManager(config)
                    result = manager.get_network_policy("bedrock-network-policy")

                    assert result["policy_name"] == "bedrock-network-policy"
                    assert result["policy_type"] == "network"

    def test_get_data_access_policy_success(self, mock_opensearch_client):
        """Test successful retrieval of data access policy"""
        from config.aws_config import AWSConfig

        policy_doc = {"Rules": []}
        mock_opensearch_client.get_access_policy.return_value = {
            "accessPolicyDetail": {
                "name": "bedrock-data-access-policy",
                "version": "1",
                "createdDate": 1234567890,
                "type": "data",
                "policy": json.dumps(policy_doc)
            }
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = OSSSecurityManager(config)
                    result = manager.get_data_access_policy("bedrock-data-access-policy")

                    assert result["policy_name"] == "bedrock-data-access-policy"
                    assert result["policy_type"] == "data"


class TestPolicyDeletion:
    """Tests for policy deletion"""

    def test_delete_encryption_policy_success(self, mock_opensearch_client):
        """Test successful deletion of encryption policy"""
        from config.aws_config import AWSConfig

        mock_opensearch_client.delete_security_policy.return_value = {}

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = OSSSecurityManager(config)
                    result = manager.delete_encryption_policy("bedrock-encryption-policy")

                    assert result is True
                    mock_opensearch_client.delete_security_policy.assert_called_once()

    def test_delete_network_policy_success(self, mock_opensearch_client):
        """Test successful deletion of network policy"""
        from config.aws_config import AWSConfig

        mock_opensearch_client.delete_security_policy.return_value = {}

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = OSSSecurityManager(config)
                    result = manager.delete_network_policy("bedrock-network-policy")

                    assert result is True

    def test_delete_data_access_policy_success(self, mock_opensearch_client):
        """Test successful deletion of data access policy"""
        from config.aws_config import AWSConfig

        mock_opensearch_client.delete_access_policy.return_value = {}

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = OSSSecurityManager(config)
                    result = manager.delete_data_access_policy("bedrock-data-access-policy")

                    assert result is True

    def test_delete_policy_not_found(self, mock_opensearch_client):
        """Test deletion of non-existent policy"""
        from config.aws_config import AWSConfig

        error_response = {"Error": {"Code": "ResourceNotFoundException", "Message": "Policy not found"}}
        mock_opensearch_client.delete_security_policy.side_effect = ClientError(error_response, "DeleteSecurityPolicy")

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = OSSSecurityManager(config)
                    result = manager.delete_encryption_policy("bedrock-encryption-policy")

                    # Should return True even if policy doesn't exist
                    assert result is True


class TestPolicyValidation:
    """Tests for policy validation"""

    def test_validate_policy_consistency_all_valid(self, mock_opensearch_client):
        """Test validation when all policies are valid"""
        from config.aws_config import AWSConfig

        policy_doc = {"Rules": []}
        mock_opensearch_client.get_security_policy.return_value = {
            "securityPolicyDetail": {
                "name": "test-policy",
                "version": "1",
                "createdDate": 1234567890,
                "type": "encryption",
                "policy": json.dumps(policy_doc)
            }
        }
        mock_opensearch_client.get_access_policy.return_value = {
            "accessPolicyDetail": {
                "name": "test-policy",
                "version": "1",
                "createdDate": 1234567890,
                "type": "data",
                "policy": json.dumps(policy_doc)
            }
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = OSSSecurityManager(config)
                    result = manager.validate_policy_consistency(
                        "bedrock-encryption-policy",
                        "bedrock-network-policy",
                        "bedrock-data-access-policy"
                    )

                    assert result["encryption_policy_valid"] is True
                    assert result["network_policy_valid"] is True
                    assert result["data_access_policy_valid"] is True

    def test_validate_policy_consistency_some_invalid(self, mock_opensearch_client):
        """Test validation when some policies are invalid"""
        from config.aws_config import AWSConfig

        policy_doc = {"Rules": []}
        mock_opensearch_client.get_security_policy.side_effect = ClientError(
            {"Error": {"Code": "ResourceNotFoundException"}},
            "GetSecurityPolicy"
        )
        mock_opensearch_client.get_access_policy.return_value = {
            "accessPolicyDetail": {
                "name": "test-policy",
                "version": "1",
                "createdDate": 1234567890,
                "type": "data",
                "policy": json.dumps(policy_doc)
            }
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_opensearch_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = OSSSecurityManager(config)
                    result = manager.validate_policy_consistency(
                        "bedrock-encryption-policy",
                        "bedrock-network-policy",
                        "bedrock-data-access-policy"
                    )

                    assert result["encryption_policy_valid"] is False
                    assert result["data_access_policy_valid"] is True
