"""Tests for Secrets Manager credential storage and retrieval"""

import pytest
import json
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError
from src.secrets_manager import SecretsManager


class TestSecretsManagerInitialization:
    """Tests for Secrets Manager initialization"""

    def test_init_with_aws_config(self, mock_secrets_manager_client):
        """Test Secrets Manager initialization with AWS config"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client', return_value=mock_secrets_manager_client):
            config = AWSConfig()
            manager = SecretsManager(config)

            assert manager.aws_config is config
            assert manager.secrets_client is mock_secrets_manager_client


class TestStoreCredential:
    """Tests for storing credentials"""

    def test_store_credential_success(self, mock_secrets_manager_client):
        """Test successful credential storage"""
        from config.aws_config import AWSConfig

        credential_data = {
            "username": "test_user",
            "password": "test_password",
            "api_key": "test_api_key"
        }

        mock_secrets_manager_client.create_secret.return_value = {
            "Name": "bedrock-rag/confluence-credentials",
            "ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:bedrock-rag/confluence-credentials-XXXXX",
            "VersionId": "version-123"
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_secrets_manager_client):
            config = AWSConfig()
            manager = SecretsManager(config)
            result = manager.store_credential(
                "bedrock-rag/confluence-credentials",
                credential_data,
                description="Confluence credentials for RAG"
            )

            assert result["secret_name"] == "bedrock-rag/confluence-credentials"
            assert "arn:aws:secretsmanager:us-east-1:123456789012:secret" in result["secret_arn"]
            assert result["version_id"] == "version-123"

    def test_store_credential_with_tags(self, mock_secrets_manager_client):
        """Test credential storage with tags"""
        from config.aws_config import AWSConfig

        credential_data = {
            "username": "test_user",
            "password": "test_password"
        }

        tags = {
            "Environment": "test",
            "Application": "bedrock-rag"
        }

        mock_secrets_manager_client.create_secret.return_value = {
            "Name": "bedrock-rag/s3-credentials",
            "ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:bedrock-rag/s3-credentials-XXXXX",
            "VersionId": "version-123"
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_secrets_manager_client):
            config = AWSConfig()
            manager = SecretsManager(config)
            result = manager.store_credential(
                "bedrock-rag/s3-credentials",
                credential_data,
                tags=tags
            )

            assert result["secret_name"] == "bedrock-rag/s3-credentials"
            # Verify tags were passed to create_secret
            call_args = mock_secrets_manager_client.create_secret.call_args
            assert "Tags" in call_args[1]

    def test_store_credential_already_exists(self, mock_secrets_manager_client):
        """Test credential storage when secret already exists"""
        from config.aws_config import AWSConfig

        credential_data = {
            "username": "test_user",
            "password": "test_password"
        }

        error_response = {"Error": {"Code": "ResourceExistsException", "Message": "Secret already exists"}}
        mock_secrets_manager_client.create_secret.side_effect = ClientError(error_response, "CreateSecret")
        mock_secrets_manager_client.update_secret.return_value = {
            "Name": "bedrock-rag/existing-credentials",
            "ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:bedrock-rag/existing-credentials-XXXXX",
            "VersionId": "version-124"
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_secrets_manager_client):
            config = AWSConfig()
            manager = SecretsManager(config)
            result = manager.store_credential(
                "bedrock-rag/existing-credentials",
                credential_data
            )

            assert result["secret_name"] == "bedrock-rag/existing-credentials"
            mock_secrets_manager_client.update_secret.assert_called_once()

    def test_store_credential_failure(self, mock_secrets_manager_client):
        """Test credential storage failure"""
        from config.aws_config import AWSConfig

        credential_data = {
            "username": "test_user",
            "password": "test_password"
        }

        error_response = {"Error": {"Code": "AccessDenied", "Message": "User is not authorized"}}
        mock_secrets_manager_client.create_secret.side_effect = ClientError(error_response, "CreateSecret")

        with patch.object(AWSConfig, 'get_client', return_value=mock_secrets_manager_client):
            config = AWSConfig()
            manager = SecretsManager(config)

            with pytest.raises(ValueError, match="Failed to store credential"):
                manager.store_credential(
                    "bedrock-rag/credentials",
                    credential_data
                )


class TestRetrieveCredential:
    """Tests for retrieving credentials"""

    def test_retrieve_credential_success(self, mock_secrets_manager_client):
        """Test successful credential retrieval"""
        from config.aws_config import AWSConfig

        credential_data = {
            "username": "test_user",
            "password": "test_password",
            "api_key": "test_api_key"
        }

        mock_secrets_manager_client.get_secret_value.return_value = {
            "Name": "bedrock-rag/confluence-credentials",
            "ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:bedrock-rag/confluence-credentials-XXXXX",
            "VersionId": "version-123",
            "SecretString": json.dumps(credential_data)
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_secrets_manager_client):
            config = AWSConfig()
            manager = SecretsManager(config)
            result = manager.retrieve_credential("bedrock-rag/confluence-credentials")

            assert result["secret_name"] == "bedrock-rag/confluence-credentials"
            assert result["credential_data"] == credential_data
            assert result["version_id"] == "version-123"

    def test_retrieve_credential_with_version_id(self, mock_secrets_manager_client):
        """Test credential retrieval with specific version ID"""
        from config.aws_config import AWSConfig

        credential_data = {
            "username": "test_user",
            "password": "old_password"
        }

        mock_secrets_manager_client.get_secret_value.return_value = {
            "Name": "bedrock-rag/credentials",
            "ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:bedrock-rag/credentials-XXXXX",
            "VersionId": "version-100",
            "SecretString": json.dumps(credential_data)
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_secrets_manager_client):
            config = AWSConfig()
            manager = SecretsManager(config)
            result = manager.retrieve_credential("bedrock-rag/credentials", version_id="version-100")

            assert result["credential_data"] == credential_data
            # Verify version_id was passed to get_secret_value
            call_args = mock_secrets_manager_client.get_secret_value.call_args
            assert call_args[1]["VersionId"] == "version-100"

    def test_retrieve_credential_not_found(self, mock_secrets_manager_client):
        """Test credential retrieval when secret not found"""
        from config.aws_config import AWSConfig

        error_response = {"Error": {"Code": "ResourceNotFoundException", "Message": "Secret not found"}}
        mock_secrets_manager_client.get_secret_value.side_effect = ClientError(error_response, "GetSecretValue")

        with patch.object(AWSConfig, 'get_client', return_value=mock_secrets_manager_client):
            config = AWSConfig()
            manager = SecretsManager(config)

            with pytest.raises(ValueError, match="not found"):
                manager.retrieve_credential("bedrock-rag/nonexistent-credentials")

    def test_retrieve_credential_invalid_request(self, mock_secrets_manager_client):
        """Test credential retrieval with invalid request"""
        from config.aws_config import AWSConfig

        error_response = {"Error": {"Code": "InvalidRequestException", "Message": "Invalid request"}}
        mock_secrets_manager_client.get_secret_value.side_effect = ClientError(error_response, "GetSecretValue")

        with patch.object(AWSConfig, 'get_client', return_value=mock_secrets_manager_client):
            config = AWSConfig()
            manager = SecretsManager(config)

            with pytest.raises(ValueError, match="Invalid request"):
                manager.retrieve_credential("bedrock-rag/credentials")


class TestValidateCredential:
    """Tests for validating credentials"""

    def test_validate_credential_success(self, mock_secrets_manager_client):
        """Test successful credential validation"""
        from config.aws_config import AWSConfig

        credential_data = {
            "username": "test_user",
            "password": "test_password",
            "api_key": "test_api_key"
        }

        mock_secrets_manager_client.get_secret_value.return_value = {
            "Name": "bedrock-rag/credentials",
            "ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:bedrock-rag/credentials-XXXXX",
            "VersionId": "version-123",
            "SecretString": json.dumps(credential_data)
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_secrets_manager_client):
            config = AWSConfig()
            manager = SecretsManager(config)
            result = manager.validate_credential(
                "bedrock-rag/credentials",
                required_fields=["username", "password"]
            )

            assert result is True

    def test_validate_credential_missing_required_fields(self, mock_secrets_manager_client):
        """Test credential validation with missing required fields"""
        from config.aws_config import AWSConfig

        credential_data = {
            "username": "test_user"
        }

        mock_secrets_manager_client.get_secret_value.return_value = {
            "Name": "bedrock-rag/credentials",
            "ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:bedrock-rag/credentials-XXXXX",
            "VersionId": "version-123",
            "SecretString": json.dumps(credential_data)
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_secrets_manager_client):
            config = AWSConfig()
            manager = SecretsManager(config)

            with pytest.raises(ValueError, match="missing required fields"):
                manager.validate_credential(
                    "bedrock-rag/credentials",
                    required_fields=["username", "password", "api_key"]
                )

    def test_validate_credential_not_found(self, mock_secrets_manager_client):
        """Test credential validation when secret not found"""
        from config.aws_config import AWSConfig

        error_response = {"Error": {"Code": "ResourceNotFoundException", "Message": "Secret not found"}}
        mock_secrets_manager_client.get_secret_value.side_effect = ClientError(error_response, "GetSecretValue")

        with patch.object(AWSConfig, 'get_client', return_value=mock_secrets_manager_client):
            config = AWSConfig()
            manager = SecretsManager(config)

            with pytest.raises(ValueError):
                manager.validate_credential("bedrock-rag/nonexistent-credentials")

    def test_validate_credential_invalid_data_type(self, mock_secrets_manager_client):
        """Test credential validation with invalid data type"""
        from config.aws_config import AWSConfig

        mock_secrets_manager_client.get_secret_value.return_value = {
            "Name": "bedrock-rag/credentials",
            "ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:bedrock-rag/credentials-XXXXX",
            "VersionId": "version-123",
            "SecretString": json.dumps("not a dictionary")
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_secrets_manager_client):
            config = AWSConfig()
            manager = SecretsManager(config)

            with pytest.raises(ValueError, match="not a dictionary"):
                manager.validate_credential("bedrock-rag/credentials")


class TestDeleteCredential:
    """Tests for deleting credentials"""

    def test_delete_credential_success(self, mock_secrets_manager_client):
        """Test successful credential deletion"""
        from config.aws_config import AWSConfig
        from datetime import datetime

        mock_secrets_manager_client.delete_secret.return_value = {
            "Name": "bedrock-rag/credentials",
            "ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:bedrock-rag/credentials-XXXXX",
            "DeletionDate": datetime.now()
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_secrets_manager_client):
            config = AWSConfig()
            manager = SecretsManager(config)
            result = manager.delete_credential("bedrock-rag/credentials")

            assert result["secret_name"] == "bedrock-rag/credentials"
            assert "arn:aws:secretsmanager:us-east-1:123456789012:secret" in result["secret_arn"]

    def test_delete_credential_force_delete(self, mock_secrets_manager_client):
        """Test credential deletion with force delete"""
        from config.aws_config import AWSConfig
        from datetime import datetime

        mock_secrets_manager_client.delete_secret.return_value = {
            "Name": "bedrock-rag/credentials",
            "ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:bedrock-rag/credentials-XXXXX",
            "DeletionDate": datetime.now()
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_secrets_manager_client):
            config = AWSConfig()
            manager = SecretsManager(config)
            result = manager.delete_credential("bedrock-rag/credentials", force_delete=True)

            # Verify force_delete was passed
            call_args = mock_secrets_manager_client.delete_secret.call_args
            assert call_args[1]["ForceDeleteWithoutRecovery"] is True

    def test_delete_credential_not_found(self, mock_secrets_manager_client):
        """Test credential deletion when secret not found"""
        from config.aws_config import AWSConfig

        error_response = {"Error": {"Code": "ResourceNotFoundException", "Message": "Secret not found"}}
        mock_secrets_manager_client.delete_secret.side_effect = ClientError(error_response, "DeleteSecret")

        with patch.object(AWSConfig, 'get_client', return_value=mock_secrets_manager_client):
            config = AWSConfig()
            manager = SecretsManager(config)

            with pytest.raises(ValueError, match="not found"):
                manager.delete_credential("bedrock-rag/nonexistent-credentials")


class TestListCredentials:
    """Tests for listing credentials"""

    def test_list_credentials_success(self, mock_secrets_manager_client):
        """Test successful credential listing"""
        from config.aws_config import AWSConfig
        from datetime import datetime

        mock_secrets_manager_client.list_secrets.return_value = {
            "SecretList": [
                {
                    "Name": "bedrock-rag/confluence-credentials",
                    "ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:bedrock-rag/confluence-credentials-XXXXX",
                    "Description": "Confluence credentials",
                    "CreatedDate": datetime.now(),
                    "LastChangedDate": datetime.now(),
                    "Tags": [{"Key": "Application", "Value": "bedrock-rag"}]
                },
                {
                    "Name": "bedrock-rag/s3-credentials",
                    "ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:bedrock-rag/s3-credentials-XXXXX",
                    "Description": "S3 credentials",
                    "CreatedDate": datetime.now(),
                    "LastChangedDate": datetime.now(),
                    "Tags": []
                }
            ]
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_secrets_manager_client):
            config = AWSConfig()
            manager = SecretsManager(config)
            results = manager.list_credentials()

            assert len(results) == 2
            assert results[0]["secret_name"] == "bedrock-rag/confluence-credentials"
            assert results[1]["secret_name"] == "bedrock-rag/s3-credentials"

    def test_list_credentials_with_filters(self, mock_secrets_manager_client):
        """Test credential listing with filters"""
        from config.aws_config import AWSConfig
        from datetime import datetime

        mock_secrets_manager_client.list_secrets.return_value = {
            "SecretList": [
                {
                    "Name": "bedrock-rag/confluence-credentials",
                    "ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:bedrock-rag/confluence-credentials-XXXXX",
                    "Description": "Confluence credentials",
                    "CreatedDate": datetime.now(),
                    "LastChangedDate": datetime.now(),
                    "Tags": [{"Key": "Application", "Value": "bedrock-rag"}]
                }
            ]
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_secrets_manager_client):
            config = AWSConfig()
            manager = SecretsManager(config)
            results = manager.list_credentials(filters={"Application": "bedrock-rag"})

            assert len(results) == 1
            # Verify filters were passed
            call_args = mock_secrets_manager_client.list_secrets.call_args
            assert "Filters" in call_args[1]

    def test_list_credentials_empty(self, mock_secrets_manager_client):
        """Test credential listing when no credentials exist"""
        from config.aws_config import AWSConfig

        mock_secrets_manager_client.list_secrets.return_value = {
            "SecretList": []
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_secrets_manager_client):
            config = AWSConfig()
            manager = SecretsManager(config)
            results = manager.list_credentials()

            assert len(results) == 0


class TestGetCredentialMetadata:
    """Tests for getting credential metadata"""

    def test_get_credential_metadata_success(self, mock_secrets_manager_client):
        """Test successful credential metadata retrieval"""
        from config.aws_config import AWSConfig
        from datetime import datetime

        mock_secrets_manager_client.describe_secret.return_value = {
            "Name": "bedrock-rag/credentials",
            "ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:bedrock-rag/credentials-XXXXX",
            "Description": "Test credentials",
            "CreatedDate": datetime.now(),
            "LastChangedDate": datetime.now(),
            "LastAccessedDate": datetime.now(),
            "Tags": [{"Key": "Application", "Value": "bedrock-rag"}],
            "RotationEnabled": False,
            "VersionIdsToStages": {"version-123": ["AWSCURRENT"]}
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_secrets_manager_client):
            config = AWSConfig()
            manager = SecretsManager(config)
            result = manager.get_credential_metadata("bedrock-rag/credentials")

            assert result["secret_name"] == "bedrock-rag/credentials"
            assert result["rotation_enabled"] is False
            assert "version-123" in result["versions"]

    def test_get_credential_metadata_not_found(self, mock_secrets_manager_client):
        """Test credential metadata retrieval when secret not found"""
        from config.aws_config import AWSConfig

        error_response = {"Error": {"Code": "ResourceNotFoundException", "Message": "Secret not found"}}
        mock_secrets_manager_client.describe_secret.side_effect = ClientError(error_response, "DescribeSecret")

        with patch.object(AWSConfig, 'get_client', return_value=mock_secrets_manager_client):
            config = AWSConfig()
            manager = SecretsManager(config)

            with pytest.raises(ValueError, match="not found"):
                manager.get_credential_metadata("bedrock-rag/nonexistent-credentials")


class TestRotateCredential:
    """Tests for rotating credentials"""

    def test_rotate_credential_success(self, mock_secrets_manager_client):
        """Test successful credential rotation"""
        from config.aws_config import AWSConfig

        new_credential_data = {
            "username": "test_user",
            "password": "new_password"
        }

        mock_secrets_manager_client.update_secret.return_value = {
            "Name": "bedrock-rag/credentials",
            "ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:bedrock-rag/credentials-XXXXX",
            "VersionId": "version-124"
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_secrets_manager_client):
            config = AWSConfig()
            manager = SecretsManager(config)
            result = manager.rotate_credential("bedrock-rag/credentials", new_credential_data)

            assert result["secret_name"] == "bedrock-rag/credentials"
            assert result["version_id"] == "version-124"

    def test_rotate_credential_not_found(self, mock_secrets_manager_client):
        """Test credential rotation when secret not found"""
        from config.aws_config import AWSConfig

        new_credential_data = {
            "username": "test_user",
            "password": "new_password"
        }

        error_response = {"Error": {"Code": "ResourceNotFoundException", "Message": "Secret not found"}}
        mock_secrets_manager_client.update_secret.side_effect = ClientError(error_response, "UpdateSecret")

        with patch.object(AWSConfig, 'get_client', return_value=mock_secrets_manager_client):
            config = AWSConfig()
            manager = SecretsManager(config)

            with pytest.raises(ValueError, match="not found"):
                manager.rotate_credential("bedrock-rag/nonexistent-credentials", new_credential_data)


class TestTagCredential:
    """Tests for tagging credentials"""

    def test_tag_credential_success(self, mock_secrets_manager_client):
        """Test successful credential tagging"""
        from config.aws_config import AWSConfig

        tags = {
            "Environment": "production",
            "Application": "bedrock-rag"
        }

        mock_secrets_manager_client.tag_resource.return_value = {}

        with patch.object(AWSConfig, 'get_client', return_value=mock_secrets_manager_client):
            config = AWSConfig()
            manager = SecretsManager(config)
            result = manager.tag_credential("bedrock-rag/credentials", tags)

            assert result is True
            mock_secrets_manager_client.tag_resource.assert_called_once()

    def test_tag_credential_not_found(self, mock_secrets_manager_client):
        """Test credential tagging when secret not found"""
        from config.aws_config import AWSConfig

        tags = {"Environment": "production"}

        error_response = {"Error": {"Code": "ResourceNotFoundException", "Message": "Secret not found"}}
        mock_secrets_manager_client.tag_resource.side_effect = ClientError(error_response, "TagResource")

        with patch.object(AWSConfig, 'get_client', return_value=mock_secrets_manager_client):
            config = AWSConfig()
            manager = SecretsManager(config)

            with pytest.raises(ValueError, match="not found"):
                manager.tag_credential("bedrock-rag/nonexistent-credentials", tags)


class TestUntagCredential:
    """Tests for untagging credentials"""

    def test_untag_credential_success(self, mock_secrets_manager_client):
        """Test successful credential untagging"""
        from config.aws_config import AWSConfig

        mock_secrets_manager_client.untag_resource.return_value = {}

        with patch.object(AWSConfig, 'get_client', return_value=mock_secrets_manager_client):
            config = AWSConfig()
            manager = SecretsManager(config)
            result = manager.untag_credential("bedrock-rag/credentials", ["Environment"])

            assert result is True
            mock_secrets_manager_client.untag_resource.assert_called_once()

    def test_untag_credential_not_found(self, mock_secrets_manager_client):
        """Test credential untagging when secret not found"""
        from config.aws_config import AWSConfig

        error_response = {"Error": {"Code": "ResourceNotFoundException", "Message": "Secret not found"}}
        mock_secrets_manager_client.untag_resource.side_effect = ClientError(error_response, "UntagResource")

        with patch.object(AWSConfig, 'get_client', return_value=mock_secrets_manager_client):
            config = AWSConfig()
            manager = SecretsManager(config)

            with pytest.raises(ValueError, match="not found"):
                manager.untag_credential("bedrock-rag/nonexistent-credentials", ["Environment"])
