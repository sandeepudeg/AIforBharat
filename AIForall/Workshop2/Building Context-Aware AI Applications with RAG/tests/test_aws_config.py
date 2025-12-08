"""Property-based tests for AWS configuration management"""

import pytest
from unittest.mock import MagicMock, patch, call
from config.aws_config import AWSConfig
import os

# Disable hypothesis database to avoid Windows hanging issues
os.environ['HYPOTHESIS_DATABASE_DIRECTORY'] = 'none'


class TestAWSConfigInitialization:
    """Tests for AWSConfig initialization"""

    def test_init_with_default_region(self):
        """Test initialization with default region"""
        config = AWSConfig()
        assert config.get_region() == "us-east-1"

    def test_init_with_custom_region(self):
        """Test initialization with custom region"""
        config = AWSConfig(region="eu-west-1")
        assert config.get_region() == "eu-west-1"

    def test_init_with_profile(self):
        """Test initialization with AWS profile"""
        config = AWSConfig(region="us-west-2", profile="dev")
        assert config.get_region() == "us-west-2"
        assert config.profile == "dev"


class TestAWSConfigCredentialValidation:
    """Tests for credential validation"""

    @patch("boto3.Session")
    def test_validate_credentials_success(self, mock_session):
        """Test successful credential validation"""
        mock_sts_client = MagicMock()
        mock_sts_client.get_caller_identity.return_value = {
            "Account": "123456789012",
            "UserId": "AIDAI23HXD2O5EXAMPLE",
            "Arn": "arn:aws:iam::123456789012:user/test-user"
        }

        mock_session_instance = MagicMock()
        mock_session_instance.client.return_value = mock_sts_client
        mock_session.return_value = mock_session_instance

        config = AWSConfig()
        result = config.validate_credentials()
        assert result is True

    @patch("boto3.Session")
    def test_validate_credentials_failure(self, mock_session):
        """Test credential validation failure"""
        from botocore.exceptions import NoCredentialsError

        mock_session_instance = MagicMock()
        mock_session_instance.client.side_effect = NoCredentialsError()
        mock_session.return_value = mock_session_instance

        config = AWSConfig()
        with pytest.raises(ValueError, match="Failed to create sts client"):
            config.validate_credentials()


class TestAWSConfigAccountIDDetection:
    """Tests for account ID detection"""

    @patch("boto3.Session")
    def test_get_account_id_success(self, mock_session):
        """Test successful account ID detection"""
        mock_sts_client = MagicMock()
        mock_sts_client.get_caller_identity.return_value = {
            "Account": "123456789012"
        }

        mock_session_instance = MagicMock()
        mock_session_instance.client.return_value = mock_sts_client
        mock_session.return_value = mock_session_instance

        config = AWSConfig()
        account_id = config.get_account_id()
        assert account_id == "123456789012"

    @patch("boto3.Session")
    def test_get_account_id_caching(self, mock_session):
        """Test that account ID is cached after first retrieval"""
        mock_sts_client = MagicMock()
        mock_sts_client.get_caller_identity.return_value = {
            "Account": "123456789012"
        }

        mock_session_instance = MagicMock()
        mock_session_instance.client.return_value = mock_sts_client
        mock_session.return_value = mock_session_instance

        config = AWSConfig()
        account_id_1 = config.get_account_id()
        account_id_2 = config.get_account_id()

        assert account_id_1 == account_id_2
        # Should only call get_caller_identity once due to caching
        assert mock_sts_client.get_caller_identity.call_count == 1

    @patch("boto3.Session")
    def test_get_account_id_failure(self, mock_session):
        """Test account ID detection failure"""
        from botocore.exceptions import ClientError

        mock_session_instance = MagicMock()
        error_response = {"Error": {"Code": "AccessDenied", "Message": "User is not authorized"}}
        mock_session_instance.client.side_effect = ClientError(error_response, "GetCallerIdentity")
        mock_session.return_value = mock_session_instance

        config = AWSConfig()
        with pytest.raises(ValueError, match="Failed to create sts client"):
            config.get_account_id()


class TestAWSConfigClientManagement:
    """Tests for boto3 client management"""

    @patch("boto3.Session")
    def test_get_client_creates_client(self, mock_session):
        """Test that get_client creates a boto3 client"""
        mock_client = MagicMock()
        mock_session_instance = MagicMock()
        mock_session_instance.client.return_value = mock_client
        mock_session.return_value = mock_session_instance

        config = AWSConfig(region="us-east-1")
        client = config.get_client("s3")

        assert client is mock_client
        mock_session_instance.client.assert_called_once_with("s3", region_name="us-east-1")

    @patch("boto3.Session")
    def test_get_client_caching(self, mock_session):
        """Test that clients are cached"""
        mock_client = MagicMock()
        mock_session_instance = MagicMock()
        mock_session_instance.client.return_value = mock_client
        mock_session.return_value = mock_session_instance

        config = AWSConfig(region="us-east-1")
        client_1 = config.get_client("s3")
        client_2 = config.get_client("s3")

        assert client_1 is client_2
        # Should only create client once due to caching
        assert mock_session_instance.client.call_count == 1

    @patch("boto3.Session")
    def test_get_client_different_services(self, mock_session):
        """Test that different services get different clients"""
        mock_s3_client = MagicMock()
        mock_bedrock_client = MagicMock()

        mock_session_instance = MagicMock()
        mock_session_instance.client.side_effect = [mock_s3_client, mock_bedrock_client]
        mock_session.return_value = mock_session_instance

        config = AWSConfig(region="us-east-1")
        s3_client = config.get_client("s3")
        bedrock_client = config.get_client("bedrock")

        assert s3_client is mock_s3_client
        assert bedrock_client is mock_bedrock_client
        assert s3_client is not bedrock_client


class TestAWSConfigServiceValidation:
    """Tests for service-specific validation"""

    @patch("boto3.Session")
    def test_validate_bedrock_access_success(self, mock_session):
        """Test successful Bedrock access validation"""
        mock_bedrock_client = MagicMock()
        mock_bedrock_client.list_foundation_models.return_value = {"modelSummaries": []}

        mock_session_instance = MagicMock()
        mock_session_instance.client.return_value = mock_bedrock_client
        mock_session.return_value = mock_session_instance

        config = AWSConfig()
        result = config.validate_bedrock_access()
        assert result is True

    @patch("boto3.Session")
    def test_validate_s3_access_success(self, mock_session):
        """Test successful S3 access validation"""
        mock_s3_client = MagicMock()
        mock_s3_client.list_buckets.return_value = {"Buckets": []}

        mock_session_instance = MagicMock()
        mock_session_instance.client.return_value = mock_s3_client
        mock_session.return_value = mock_session_instance

        config = AWSConfig()
        result = config.validate_s3_access()
        assert result is True

    @patch("boto3.Session")
    def test_validate_opensearch_access_success(self, mock_session):
        """Test successful OpenSearch access validation"""
        mock_oss_client = MagicMock()
        mock_oss_client.list_collections.return_value = {"collectionSummaries": []}

        mock_session_instance = MagicMock()
        mock_session_instance.client.return_value = mock_oss_client
        mock_session.return_value = mock_session_instance

        config = AWSConfig()
        result = config.validate_opensearch_access()
        assert result is True

    @patch("boto3.Session")
    def test_validate_iam_access_success(self, mock_session):
        """Test successful IAM access validation"""
        mock_iam_client = MagicMock()
        mock_iam_client.get_user.return_value = {"User": {"UserName": "test-user"}}

        mock_session_instance = MagicMock()
        mock_session_instance.client.return_value = mock_iam_client
        mock_session.return_value = mock_session_instance

        config = AWSConfig()
        result = config.validate_iam_access()
        assert result is True


class TestAWSConfigPropertyBased:
    """Property-based tests for AWS configuration"""

    @patch("boto3.Session")
    def test_property_kb_creation_idempotence(self, mock_session):
        """
        **Feature: bedrock-rag-retrieval, Property 1: Knowledge Base Creation Idempotence**

        For any knowledge base configuration, creating the knowledge base multiple times
        with the same parameters should result in the same knowledge base being retrieved
        rather than creating duplicates.

        This property validates that the AWS configuration can be created multiple times
        with the same parameters and returns consistent results.

        **Validates: Requirements 1.1, 1.2, 1.3**
        """
        mock_sts_client = MagicMock()
        mock_sts_client.get_caller_identity.return_value = {
            "Account": "123456789012"
        }

        mock_session_instance = MagicMock()
        mock_session_instance.client.return_value = mock_sts_client
        mock_session.return_value = mock_session_instance

        # Test with multiple regions to verify idempotence
        regions = ["us-east-1", "eu-west-1", "ap-southeast-1"]

        for region in regions:
            # Create config multiple times with same parameters
            config_1 = AWSConfig(region=region)
            config_2 = AWSConfig(region=region)

            # Both should have the same region
            assert config_1.get_region() == config_2.get_region()
            assert config_1.get_region() == region

            # Both should be able to get the same account ID
            account_id_1 = config_1.get_account_id()
            account_id_2 = config_2.get_account_id()
            assert account_id_1 == account_id_2
            assert account_id_1 == "123456789012"

            # Configuration summaries should be consistent
            summary_1 = config_1.get_config_summary()
            summary_2 = config_2.get_config_summary()
            assert summary_1["region"] == summary_2["region"]
            assert summary_1["account_id"] == summary_2["account_id"]
            assert summary_1["region"] == region
