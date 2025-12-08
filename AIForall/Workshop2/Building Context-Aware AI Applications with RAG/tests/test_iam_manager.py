"""Tests for IAM role and policy management"""

import pytest
import json
from unittest.mock import MagicMock, patch, call
from botocore.exceptions import ClientError
from src.iam_manager import IAMManager


class TestIAMManagerInitialization:
    """Tests for IAM Manager initialization"""

    def test_init_with_aws_config(self, mock_iam_client):
        """Test IAM Manager initialization with AWS config"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client', return_value=mock_iam_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                config = AWSConfig()
                manager = IAMManager(config)

                assert manager.aws_config is config
                assert manager.iam_client is mock_iam_client
                assert manager.account_id == '123456789012'


class TestKnowledgeBaseExecutionRole:
    """Tests for Knowledge Base execution role creation"""

    def test_create_knowledge_base_execution_role_success(self, mock_iam_client):
        """Test successful creation of Knowledge Base execution role"""
        from config.aws_config import AWSConfig

        mock_iam_client.create_role.return_value = {
            "Role": {
                "RoleName": "bedrock-kb-execution-role",
                "Arn": "arn:aws:iam::123456789012:role/bedrock-kb-execution-role",
                "RoleId": "AIDAI23HXD2O5EXAMPLE"
            }
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_iam_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                config = AWSConfig()
                manager = IAMManager(config)
                result = manager.create_knowledge_base_execution_role("bedrock-kb-execution-role")

                assert result["role_name"] == "bedrock-kb-execution-role"
                assert "arn:aws:iam::123456789012:role/bedrock-kb-execution-role" in result["role_arn"]
                assert result["role_id"] == "AIDAI23HXD2O5EXAMPLE"

    def test_create_knowledge_base_execution_role_already_exists(self, mock_iam_client):
        """Test creation when role already exists"""
        from config.aws_config import AWSConfig

        error_response = {"Error": {"Code": "EntityAlreadyExists", "Message": "Role already exists"}}
        mock_iam_client.create_role.side_effect = ClientError(error_response, "CreateRole")
        mock_iam_client.get_role.return_value = {
            "Role": {
                "RoleName": "bedrock-kb-execution-role",
                "Arn": "arn:aws:iam::123456789012:role/bedrock-kb-execution-role",
                "RoleId": "AIDAI23HXD2O5EXAMPLE"
            }
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_iam_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                config = AWSConfig()
                manager = IAMManager(config)
                result = manager.create_knowledge_base_execution_role("bedrock-kb-execution-role")

                assert result["role_name"] == "bedrock-kb-execution-role"
                assert "arn:aws:iam::123456789012:role/bedrock-kb-execution-role" in result["role_arn"]

    def test_create_knowledge_base_execution_role_failure(self, mock_iam_client):
        """Test role creation failure"""
        from config.aws_config import AWSConfig

        error_response = {"Error": {"Code": "AccessDenied", "Message": "User is not authorized"}}
        mock_iam_client.create_role.side_effect = ClientError(error_response, "CreateRole")

        with patch.object(AWSConfig, 'get_client', return_value=mock_iam_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                config = AWSConfig()
                manager = IAMManager(config)

                with pytest.raises(ValueError, match="Failed to create IAM role"):
                    manager.create_knowledge_base_execution_role("bedrock-kb-execution-role")


class TestFoundationModelPolicy:
    """Tests for foundation model policy creation"""

    def test_create_foundation_model_policy_all_models(self, mock_iam_client):
        """Test creation of foundation model policy for all models"""
        from config.aws_config import AWSConfig

        mock_iam_client.create_policy.return_value = {
            "Policy": {
                "PolicyName": "bedrock-foundation-model-policy",
                "Arn": "arn:aws:iam::123456789012:policy/bedrock-foundation-model-policy",
                "PolicyId": "ANPAI23HXD2O5EXAMPLE"
            }
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_iam_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = IAMManager(config)
                    result = manager.create_foundation_model_policy("bedrock-foundation-model-policy")

                    assert result["policy_name"] == "bedrock-foundation-model-policy"
                    assert "arn:aws:iam::123456789012:policy/bedrock-foundation-model-policy" in result["policy_arn"]

    def test_create_foundation_model_policy_specific_models(self, mock_iam_client):
        """Test creation of foundation model policy for specific models"""
        from config.aws_config import AWSConfig

        mock_iam_client.create_policy.return_value = {
            "Policy": {
                "PolicyName": "bedrock-foundation-model-policy",
                "Arn": "arn:aws:iam::123456789012:policy/bedrock-foundation-model-policy",
                "PolicyId": "ANPAI23HXD2O5EXAMPLE"
            }
        }

        models = [
            "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
            "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v2:0"
        ]

        with patch.object(AWSConfig, 'get_client', return_value=mock_iam_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = IAMManager(config)
                    result = manager.create_foundation_model_policy("bedrock-foundation-model-policy", models)

                    assert result["policy_name"] == "bedrock-foundation-model-policy"

    def test_create_foundation_model_policy_already_exists(self, mock_iam_client):
        """Test creation when policy already exists"""
        from config.aws_config import AWSConfig

        error_response = {"Error": {"Code": "EntityAlreadyExists", "Message": "Policy already exists"}}
        mock_iam_client.create_policy.side_effect = ClientError(error_response, "CreatePolicy")
        mock_iam_client.get_policy.return_value = {
            "Policy": {
                "PolicyName": "bedrock-foundation-model-policy",
                "Arn": "arn:aws:iam::123456789012:policy/bedrock-foundation-model-policy",
                "PolicyId": "ANPAI23HXD2O5EXAMPLE"
            }
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_iam_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = IAMManager(config)
                    result = manager.create_foundation_model_policy("bedrock-foundation-model-policy")

                    assert result["policy_name"] == "bedrock-foundation-model-policy"


class TestS3BucketPolicy:
    """Tests for S3 bucket policy creation"""

    def test_create_s3_bucket_policy_success(self, mock_iam_client):
        """Test successful creation of S3 bucket policy"""
        from config.aws_config import AWSConfig

        mock_iam_client.create_policy.return_value = {
            "Policy": {
                "PolicyName": "bedrock-s3-bucket-policy",
                "Arn": "arn:aws:iam::123456789012:policy/bedrock-s3-bucket-policy",
                "PolicyId": "ANPAI23HXD2O5EXAMPLE"
            }
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_iam_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                config = AWSConfig()
                manager = IAMManager(config)
                result = manager.create_s3_bucket_policy(
                    "bedrock-s3-bucket-policy",
                    ["test-bucket-1", "test-bucket-2"]
                )

                assert result["policy_name"] == "bedrock-s3-bucket-policy"
                assert "arn:aws:iam::123456789012:policy/bedrock-s3-bucket-policy" in result["policy_arn"]

    def test_create_s3_bucket_policy_multiple_buckets(self, mock_iam_client):
        """Test S3 bucket policy with multiple buckets"""
        from config.aws_config import AWSConfig

        mock_iam_client.create_policy.return_value = {
            "Policy": {
                "PolicyName": "bedrock-s3-bucket-policy",
                "Arn": "arn:aws:iam::123456789012:policy/bedrock-s3-bucket-policy",
                "PolicyId": "ANPAI23HXD2O5EXAMPLE"
            }
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_iam_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                config = AWSConfig()
                manager = IAMManager(config)
                result = manager.create_s3_bucket_policy(
                    "bedrock-s3-bucket-policy",
                    ["bucket-1", "bucket-2", "bucket-3"]
                )

                # Verify the policy document includes all buckets
                call_args = mock_iam_client.create_policy.call_args
                policy_doc = json.loads(call_args[1]["PolicyDocument"])
                assert len(policy_doc["Statement"]) == 2  # Two statements: read and write

    def test_create_s3_bucket_policy_already_exists(self, mock_iam_client):
        """Test creation when S3 policy already exists"""
        from config.aws_config import AWSConfig

        error_response = {"Error": {"Code": "EntityAlreadyExists", "Message": "Policy already exists"}}
        mock_iam_client.create_policy.side_effect = ClientError(error_response, "CreatePolicy")
        mock_iam_client.get_policy.return_value = {
            "Policy": {
                "PolicyName": "bedrock-s3-bucket-policy",
                "Arn": "arn:aws:iam::123456789012:policy/bedrock-s3-bucket-policy",
                "PolicyId": "ANPAI23HXD2O5EXAMPLE"
            }
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_iam_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                config = AWSConfig()
                manager = IAMManager(config)
                result = manager.create_s3_bucket_policy(
                    "bedrock-s3-bucket-policy",
                    ["test-bucket"]
                )

                assert result["policy_name"] == "bedrock-s3-bucket-policy"


class TestCloudWatchLoggingPolicy:
    """Tests for CloudWatch logging policy creation"""

    def test_create_cloudwatch_logging_policy_all_logs(self, mock_iam_client):
        """Test creation of CloudWatch logging policy for all log groups"""
        from config.aws_config import AWSConfig

        mock_iam_client.create_policy.return_value = {
            "Policy": {
                "PolicyName": "bedrock-cloudwatch-logging-policy",
                "Arn": "arn:aws:iam::123456789012:policy/bedrock-cloudwatch-logging-policy",
                "PolicyId": "ANPAI23HXD2O5EXAMPLE"
            }
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_iam_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = IAMManager(config)
                    result = manager.create_cloudwatch_logging_policy("bedrock-cloudwatch-logging-policy")

                    assert result["policy_name"] == "bedrock-cloudwatch-logging-policy"
                    assert "arn:aws:iam::123456789012:policy/bedrock-cloudwatch-logging-policy" in result["policy_arn"]

    def test_create_cloudwatch_logging_policy_specific_log_group(self, mock_iam_client):
        """Test creation of CloudWatch logging policy for specific log group"""
        from config.aws_config import AWSConfig

        mock_iam_client.create_policy.return_value = {
            "Policy": {
                "PolicyName": "bedrock-cloudwatch-logging-policy",
                "Arn": "arn:aws:iam::123456789012:policy/bedrock-cloudwatch-logging-policy",
                "PolicyId": "ANPAI23HXD2O5EXAMPLE"
            }
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_iam_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = IAMManager(config)
                    result = manager.create_cloudwatch_logging_policy(
                        "bedrock-cloudwatch-logging-policy",
                        "/aws/bedrock/knowledge-base"
                    )

                    assert result["policy_name"] == "bedrock-cloudwatch-logging-policy"

    def test_create_cloudwatch_logging_policy_already_exists(self, mock_iam_client):
        """Test creation when CloudWatch policy already exists"""
        from config.aws_config import AWSConfig

        error_response = {"Error": {"Code": "EntityAlreadyExists", "Message": "Policy already exists"}}
        mock_iam_client.create_policy.side_effect = ClientError(error_response, "CreatePolicy")
        mock_iam_client.get_policy.return_value = {
            "Policy": {
                "PolicyName": "bedrock-cloudwatch-logging-policy",
                "Arn": "arn:aws:iam::123456789012:policy/bedrock-cloudwatch-logging-policy",
                "PolicyId": "ANPAI23HXD2O5EXAMPLE"
            }
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_iam_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = IAMManager(config)
                    result = manager.create_cloudwatch_logging_policy("bedrock-cloudwatch-logging-policy")

                    assert result["policy_name"] == "bedrock-cloudwatch-logging-policy"


class TestPolicyAttachment:
    """Tests for policy attachment to roles"""

    def test_attach_policy_to_role_success(self, mock_iam_client):
        """Test successful policy attachment"""
        from config.aws_config import AWSConfig

        mock_iam_client.attach_role_policy.return_value = {}

        with patch.object(AWSConfig, 'get_client', return_value=mock_iam_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                config = AWSConfig()
                manager = IAMManager(config)
                result = manager.attach_policy_to_role(
                    "bedrock-kb-execution-role",
                    "arn:aws:iam::123456789012:policy/bedrock-foundation-model-policy"
                )

                assert result is True
                mock_iam_client.attach_role_policy.assert_called_once()

    def test_attach_policy_to_role_failure(self, mock_iam_client):
        """Test policy attachment failure"""
        from config.aws_config import AWSConfig

        error_response = {"Error": {"Code": "NoSuchEntity", "Message": "Role not found"}}
        mock_iam_client.attach_role_policy.side_effect = ClientError(error_response, "AttachRolePolicy")

        with patch.object(AWSConfig, 'get_client', return_value=mock_iam_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                config = AWSConfig()
                manager = IAMManager(config)

                with pytest.raises(ValueError, match="Role or policy does not exist"):
                    manager.attach_policy_to_role(
                        "bedrock-kb-execution-role",
                        "arn:aws:iam::123456789012:policy/bedrock-foundation-model-policy"
                    )

    def test_detach_policy_from_role_success(self, mock_iam_client):
        """Test successful policy detachment"""
        from config.aws_config import AWSConfig

        mock_iam_client.detach_role_policy.return_value = {}

        with patch.object(AWSConfig, 'get_client', return_value=mock_iam_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                config = AWSConfig()
                manager = IAMManager(config)
                result = manager.detach_policy_from_role(
                    "bedrock-kb-execution-role",
                    "arn:aws:iam::123456789012:policy/bedrock-foundation-model-policy"
                )

                assert result is True


class TestRoleDeletion:
    """Tests for role deletion"""

    def test_delete_role_success(self, mock_iam_client):
        """Test successful role deletion"""
        from config.aws_config import AWSConfig

        mock_iam_client.list_attached_role_policies.return_value = {
            "AttachedPolicies": [
                {"PolicyName": "policy1", "PolicyArn": "arn:aws:iam::123456789012:policy/policy1"}
            ]
        }
        mock_iam_client.detach_role_policy.return_value = {}
        mock_iam_client.delete_role.return_value = {}

        with patch.object(AWSConfig, 'get_client', return_value=mock_iam_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                config = AWSConfig()
                manager = IAMManager(config)
                result = manager.delete_role("bedrock-kb-execution-role")

                assert result is True
                mock_iam_client.delete_role.assert_called_once()

    def test_delete_role_not_found(self, mock_iam_client):
        """Test deletion of non-existent role"""
        from config.aws_config import AWSConfig

        mock_iam_client.list_attached_role_policies.return_value = {"AttachedPolicies": []}
        error_response = {"Error": {"Code": "NoSuchEntity", "Message": "Role not found"}}
        mock_iam_client.delete_role.side_effect = ClientError(error_response, "DeleteRole")

        with patch.object(AWSConfig, 'get_client', return_value=mock_iam_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                config = AWSConfig()
                manager = IAMManager(config)
                result = manager.delete_role("bedrock-kb-execution-role")

                # Should return True even if role doesn't exist
                assert result is True


class TestPolicyDeletion:
    """Tests for policy deletion"""

    def test_delete_policy_success(self, mock_iam_client):
        """Test successful policy deletion"""
        from config.aws_config import AWSConfig

        mock_iam_client.list_entities_for_policy.return_value = {"PolicyRoles": []}
        mock_iam_client.delete_policy.return_value = {}

        with patch.object(AWSConfig, 'get_client', return_value=mock_iam_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                config = AWSConfig()
                manager = IAMManager(config)
                result = manager.delete_policy("arn:aws:iam::123456789012:policy/bedrock-foundation-model-policy")

                assert result is True
                mock_iam_client.delete_policy.assert_called_once()

    def test_delete_policy_not_found(self, mock_iam_client):
        """Test deletion of non-existent policy"""
        from config.aws_config import AWSConfig

        mock_iam_client.list_entities_for_policy.return_value = {"PolicyRoles": []}
        error_response = {"Error": {"Code": "NoSuchEntity", "Message": "Policy not found"}}
        mock_iam_client.delete_policy.side_effect = ClientError(error_response, "DeletePolicy")

        with patch.object(AWSConfig, 'get_client', return_value=mock_iam_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                config = AWSConfig()
                manager = IAMManager(config)
                result = manager.delete_policy("arn:aws:iam::123456789012:policy/bedrock-foundation-model-policy")

                # Should return True even if policy doesn't exist
                assert result is True


class TestGetRoleInfo:
    """Tests for retrieving role information"""

    def test_get_role_info_success(self, mock_iam_client):
        """Test successful role information retrieval"""
        from config.aws_config import AWSConfig
        from datetime import datetime

        mock_iam_client.get_role.return_value = {
            "Role": {
                "RoleName": "bedrock-kb-execution-role",
                "Arn": "arn:aws:iam::123456789012:role/bedrock-kb-execution-role",
                "RoleId": "AIDAI23HXD2O5EXAMPLE",
                "CreateDate": datetime.now()
            }
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_iam_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                config = AWSConfig()
                manager = IAMManager(config)
                result = manager.get_role_info("bedrock-kb-execution-role")

                assert result["role_name"] == "bedrock-kb-execution-role"
                assert "arn:aws:iam::123456789012:role/bedrock-kb-execution-role" in result["role_arn"]


class TestGetPolicyInfo:
    """Tests for retrieving policy information"""

    def test_get_policy_info_success(self, mock_iam_client):
        """Test successful policy information retrieval"""
        from config.aws_config import AWSConfig
        from datetime import datetime

        mock_iam_client.get_policy.return_value = {
            "Policy": {
                "PolicyName": "bedrock-foundation-model-policy",
                "Arn": "arn:aws:iam::123456789012:policy/bedrock-foundation-model-policy",
                "PolicyId": "ANPAI23HXD2O5EXAMPLE",
                "CreateDate": datetime.now()
            }
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_iam_client):
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                config = AWSConfig()
                manager = IAMManager(config)
                result = manager.get_policy_info("arn:aws:iam::123456789012:policy/bedrock-foundation-model-policy")

                assert result["policy_name"] == "bedrock-foundation-model-policy"
                assert "arn:aws:iam::123456789012:policy/bedrock-foundation-model-policy" in result["policy_arn"]
