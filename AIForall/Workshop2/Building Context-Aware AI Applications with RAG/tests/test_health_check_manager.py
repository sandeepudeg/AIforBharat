"""Tests for Health Check Manager"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError

from src.health_check_manager import (
    HealthCheckManager,
    HealthCheckResult,
    SystemHealthStatus,
    ComponentStatus
)
from config.aws_config import AWSConfig


class TestHealthCheckResult:
    """Tests for HealthCheckResult class"""

    def test_health_check_result_creation(self):
        """Test creating a health check result"""
        result = HealthCheckResult(
            component_name="TestComponent",
            status=ComponentStatus.HEALTHY,
            message="Component is healthy",
            response_time_ms=100.5
        )

        assert result.component_name == "TestComponent"
        assert result.status == ComponentStatus.HEALTHY
        assert result.message == "Component is healthy"
        assert result.response_time_ms == 100.5
        assert result.timestamp is not None

    def test_health_check_result_is_healthy(self):
        """Test is_healthy method"""
        healthy_result = HealthCheckResult(
            component_name="Test",
            status=ComponentStatus.HEALTHY
        )
        degraded_result = HealthCheckResult(
            component_name="Test",
            status=ComponentStatus.DEGRADED
        )

        assert healthy_result.is_healthy() is True
        assert degraded_result.is_healthy() is False

    def test_health_check_result_is_degraded(self):
        """Test is_degraded method"""
        degraded_result = HealthCheckResult(
            component_name="Test",
            status=ComponentStatus.DEGRADED
        )
        healthy_result = HealthCheckResult(
            component_name="Test",
            status=ComponentStatus.HEALTHY
        )

        assert degraded_result.is_degraded() is True
        assert healthy_result.is_degraded() is False

    def test_health_check_result_is_unhealthy(self):
        """Test is_unhealthy method"""
        unhealthy_result = HealthCheckResult(
            component_name="Test",
            status=ComponentStatus.UNHEALTHY
        )
        healthy_result = HealthCheckResult(
            component_name="Test",
            status=ComponentStatus.HEALTHY
        )

        assert unhealthy_result.is_unhealthy() is True
        assert healthy_result.is_unhealthy() is False

    def test_health_check_result_to_dict(self):
        """Test converting health check result to dictionary"""
        result = HealthCheckResult(
            component_name="TestComponent",
            status=ComponentStatus.HEALTHY,
            message="All good",
            response_time_ms=50.0,
            details={"key": "value"}
        )

        result_dict = result.to_dict()

        assert result_dict["component_name"] == "TestComponent"
        assert result_dict["status"] == "HEALTHY"
        assert result_dict["message"] == "All good"
        assert result_dict["response_time_ms"] == 50.0
        assert result_dict["details"]["key"] == "value"
        assert "timestamp" in result_dict


class TestSystemHealthStatus:
    """Tests for SystemHealthStatus class"""

    def test_system_health_status_creation(self):
        """Test creating system health status"""
        status = SystemHealthStatus()

        assert len(status.component_results) == 0
        assert status.check_timestamp is None

    def test_system_health_status_add_result(self):
        """Test adding results to system health status"""
        status = SystemHealthStatus()
        result = HealthCheckResult(
            component_name="Component1",
            status=ComponentStatus.HEALTHY
        )

        status.add_result(result)

        assert len(status.component_results) == 1
        assert status.component_results[0].component_name == "Component1"

    def test_system_health_status_overall_status_all_healthy(self):
        """Test overall status when all components are healthy"""
        status = SystemHealthStatus()
        status.add_result(HealthCheckResult("C1", ComponentStatus.HEALTHY))
        status.add_result(HealthCheckResult("C2", ComponentStatus.HEALTHY))

        assert status.get_overall_status() == ComponentStatus.HEALTHY

    def test_system_health_status_overall_status_with_degraded(self):
        """Test overall status when one component is degraded"""
        status = SystemHealthStatus()
        status.add_result(HealthCheckResult("C1", ComponentStatus.HEALTHY))
        status.add_result(HealthCheckResult("C2", ComponentStatus.DEGRADED))

        assert status.get_overall_status() == ComponentStatus.DEGRADED

    def test_system_health_status_overall_status_with_unhealthy(self):
        """Test overall status when one component is unhealthy"""
        status = SystemHealthStatus()
        status.add_result(HealthCheckResult("C1", ComponentStatus.HEALTHY))
        status.add_result(HealthCheckResult("C2", ComponentStatus.UNHEALTHY))

        assert status.get_overall_status() == ComponentStatus.UNHEALTHY

    def test_system_health_status_overall_status_empty(self):
        """Test overall status with no components"""
        status = SystemHealthStatus()

        assert status.get_overall_status() == ComponentStatus.UNKNOWN

    def test_system_health_status_get_healthy_components(self):
        """Test getting healthy components"""
        status = SystemHealthStatus()
        status.add_result(HealthCheckResult("C1", ComponentStatus.HEALTHY))
        status.add_result(HealthCheckResult("C2", ComponentStatus.DEGRADED))
        status.add_result(HealthCheckResult("C3", ComponentStatus.HEALTHY))

        healthy = status.get_healthy_components()

        assert len(healthy) == 2
        assert all(r.is_healthy() for r in healthy)

    def test_system_health_status_get_degraded_components(self):
        """Test getting degraded components"""
        status = SystemHealthStatus()
        status.add_result(HealthCheckResult("C1", ComponentStatus.HEALTHY))
        status.add_result(HealthCheckResult("C2", ComponentStatus.DEGRADED))
        status.add_result(HealthCheckResult("C3", ComponentStatus.DEGRADED))

        degraded = status.get_degraded_components()

        assert len(degraded) == 2
        assert all(r.is_degraded() for r in degraded)

    def test_system_health_status_get_unhealthy_components(self):
        """Test getting unhealthy components"""
        status = SystemHealthStatus()
        status.add_result(HealthCheckResult("C1", ComponentStatus.HEALTHY))
        status.add_result(HealthCheckResult("C2", ComponentStatus.UNHEALTHY))
        status.add_result(HealthCheckResult("C3", ComponentStatus.UNHEALTHY))

        unhealthy = status.get_unhealthy_components()

        assert len(unhealthy) == 2
        assert all(r.is_unhealthy() for r in unhealthy)

    def test_system_health_status_to_dict(self):
        """Test converting system health status to dictionary"""
        status = SystemHealthStatus()
        status.check_timestamp = datetime(2024, 1, 1, 12, 0, 0)
        status.add_result(HealthCheckResult("C1", ComponentStatus.HEALTHY))
        status.add_result(HealthCheckResult("C2", ComponentStatus.DEGRADED))

        status_dict = status.to_dict()

        assert status_dict["overall_status"] == "DEGRADED"
        assert status_dict["total_components"] == 2
        assert status_dict["healthy_components"] == 1
        assert status_dict["degraded_components"] == 1
        assert status_dict["unhealthy_components"] == 0
        assert len(status_dict["components"]) == 2


class TestHealthCheckManager:
    """Tests for HealthCheckManager class"""

    @pytest.fixture
    def mock_aws_config(self):
        """Create mock AWS config"""
        config = MagicMock(spec=AWSConfig)
        config.get_region.return_value = "us-east-1"
        config.get_client.return_value = MagicMock()
        return config

    @pytest.fixture
    def health_check_manager(self, mock_aws_config):
        """Create health check manager with mocked AWS config"""
        return HealthCheckManager(mock_aws_config)

    def test_health_check_manager_creation(self, health_check_manager):
        """Test creating health check manager"""
        assert health_check_manager is not None
        assert health_check_manager.region == "us-east-1"

    def test_check_knowledge_base_availability_healthy(self, health_check_manager):
        """Test checking knowledge base availability when healthy"""
        health_check_manager.bedrock_agent_client.get_knowledge_base.return_value = {
            "knowledgeBase": {
                "id": "kb-123",
                "name": "test-kb",
                "status": "ACTIVE",
                "createdAt": "2024-01-01T00:00:00Z"
            }
        }

        result = health_check_manager.check_knowledge_base_availability("kb-123")

        assert result.is_healthy() is True
        assert result.component_name == "KnowledgeBase-kb-123"
        assert "active" in result.message.lower()

    def test_check_knowledge_base_availability_degraded(self, health_check_manager):
        """Test checking knowledge base availability when degraded"""
        health_check_manager.bedrock_agent_client.get_knowledge_base.return_value = {
            "knowledgeBase": {
                "id": "kb-123",
                "name": "test-kb",
                "status": "CREATING",
                "createdAt": "2024-01-01T00:00:00Z"
            }
        }

        result = health_check_manager.check_knowledge_base_availability("kb-123")

        assert result.is_degraded() is True
        assert result.component_name == "KnowledgeBase-kb-123"

    def test_check_knowledge_base_availability_unhealthy(self, health_check_manager):
        """Test checking knowledge base availability when unhealthy"""
        health_check_manager.bedrock_agent_client.get_knowledge_base.return_value = {
            "knowledgeBase": {
                "id": "kb-123",
                "name": "test-kb",
                "status": "FAILED",
                "failureReasons": ["Resource limit exceeded"]
            }
        }

        result = health_check_manager.check_knowledge_base_availability("kb-123")

        assert result.is_unhealthy() is True
        assert result.component_name == "KnowledgeBase-kb-123"

    def test_check_knowledge_base_availability_not_found(self, health_check_manager):
        """Test checking knowledge base availability when not found"""
        error = ClientError(
            {"Error": {"Code": "ResourceNotFoundException"}},
            "GetKnowledgeBase"
        )
        health_check_manager.bedrock_agent_client.get_knowledge_base.side_effect = error

        result = health_check_manager.check_knowledge_base_availability("kb-123")

        assert result.is_unhealthy() is True
        assert "not found" in result.message.lower()

    def test_check_knowledge_base_availability_service_unavailable(self, health_check_manager):
        """Test checking knowledge base availability when service is unavailable"""
        error = ClientError(
            {"Error": {"Code": "ServiceUnavailableException"}},
            "GetKnowledgeBase"
        )
        health_check_manager.bedrock_agent_client.get_knowledge_base.side_effect = error

        result = health_check_manager.check_knowledge_base_availability("kb-123")

        assert result.is_degraded() is True
        assert "unavailable" in result.message.lower()

    def test_check_knowledge_base_availability_invalid_id(self, health_check_manager):
        """Test checking knowledge base with invalid ID"""
        with pytest.raises(ValueError):
            health_check_manager.check_knowledge_base_availability("")

    def test_check_opensearch_connectivity_healthy(self, health_check_manager):
        """Test checking OpenSearch connectivity when healthy"""
        health_check_manager.opensearch_client.batch_get_collection.return_value = {
            "collectionSummaries": [
                {
                    "name": "test-collection",
                    "status": "ACTIVE",
                    "arn": "arn:aws:aoss:us-east-1:123456789012:collection/test-collection",
                    "createdAtUtc": "2024-01-01T00:00:00Z"
                }
            ]
        }

        result = health_check_manager.check_opensearch_connectivity("test-collection")

        assert result.is_healthy() is True
        assert result.component_name == "OpenSearchServerless-test-collection"
        assert "active" in result.message.lower()

    def test_check_opensearch_connectivity_degraded(self, health_check_manager):
        """Test checking OpenSearch connectivity when degraded"""
        health_check_manager.opensearch_client.batch_get_collection.return_value = {
            "collectionSummaries": [
                {
                    "name": "test-collection",
                    "status": "CREATING"
                }
            ]
        }

        result = health_check_manager.check_opensearch_connectivity("test-collection")

        assert result.is_degraded() is True

    def test_check_opensearch_connectivity_not_found(self, health_check_manager):
        """Test checking OpenSearch connectivity when collection not found"""
        health_check_manager.opensearch_client.batch_get_collection.return_value = {
            "collectionSummaries": []
        }

        result = health_check_manager.check_opensearch_connectivity("test-collection")

        assert result.is_unhealthy() is True
        assert "not found" in result.message.lower()

    def test_check_opensearch_connectivity_invalid_name(self, health_check_manager):
        """Test checking OpenSearch with invalid collection name"""
        with pytest.raises(ValueError):
            health_check_manager.check_opensearch_connectivity("")

    def test_check_s3_bucket_accessibility_healthy(self, health_check_manager):
        """Test checking S3 bucket accessibility when healthy"""
        health_check_manager.s3_client.head_bucket.return_value = {}

        result = health_check_manager.check_s3_bucket_accessibility("test-bucket")

        assert result.is_healthy() is True
        assert result.component_name == "S3Bucket-test-bucket"
        assert "accessible" in result.message.lower()

    def test_check_s3_bucket_accessibility_not_found(self, health_check_manager):
        """Test checking S3 bucket accessibility when not found"""
        error = ClientError(
            {"Error": {"Code": "404"}},
            "HeadBucket"
        )
        health_check_manager.s3_client.head_bucket.side_effect = error

        result = health_check_manager.check_s3_bucket_accessibility("test-bucket")

        assert result.is_unhealthy() is True
        assert "not found" in result.message.lower()

    def test_check_s3_bucket_accessibility_access_denied(self, health_check_manager):
        """Test checking S3 bucket accessibility when access denied"""
        error = ClientError(
            {"Error": {"Code": "403"}},
            "HeadBucket"
        )
        health_check_manager.s3_client.head_bucket.side_effect = error

        result = health_check_manager.check_s3_bucket_accessibility("test-bucket")

        assert result.is_unhealthy() is True
        assert "access denied" in result.message.lower()

    def test_check_s3_bucket_accessibility_service_unavailable(self, health_check_manager):
        """Test checking S3 bucket accessibility when service unavailable"""
        error = ClientError(
            {"Error": {"Code": "ServiceUnavailableException"}},
            "HeadBucket"
        )
        health_check_manager.s3_client.head_bucket.side_effect = error

        result = health_check_manager.check_s3_bucket_accessibility("test-bucket")

        assert result.is_degraded() is True
        assert "unavailable" in result.message.lower()

    def test_check_s3_bucket_accessibility_invalid_name(self, health_check_manager):
        """Test checking S3 bucket with invalid name"""
        with pytest.raises(ValueError):
            health_check_manager.check_s3_bucket_accessibility("")

    def test_perform_system_health_check_all_components(self, health_check_manager):
        """Test performing system health check with all components"""
        health_check_manager.bedrock_agent_client.get_knowledge_base.return_value = {
            "knowledgeBase": {"id": "kb-123", "status": "ACTIVE"}
        }
        health_check_manager.opensearch_client.batch_get_collection.return_value = {
            "collectionSummaries": [{"name": "test-collection", "status": "ACTIVE"}]
        }
        health_check_manager.s3_client.head_bucket.return_value = {}

        system_status = health_check_manager.perform_system_health_check(
            kb_id="kb-123",
            collection_name="test-collection",
            bucket_name="test-bucket"
        )

        assert system_status.check_timestamp is not None
        assert len(system_status.component_results) == 3
        assert system_status.get_overall_status() == ComponentStatus.HEALTHY

    def test_perform_system_health_check_partial_components(self, health_check_manager):
        """Test performing system health check with partial components"""
        health_check_manager.bedrock_agent_client.get_knowledge_base.return_value = {
            "knowledgeBase": {"id": "kb-123", "status": "ACTIVE"}
        }

        system_status = health_check_manager.perform_system_health_check(
            kb_id="kb-123"
        )

        assert len(system_status.component_results) == 1
        assert system_status.get_overall_status() == ComponentStatus.HEALTHY

    def test_perform_system_health_check_no_components(self, health_check_manager):
        """Test performing system health check with no components"""
        system_status = health_check_manager.perform_system_health_check()

        assert len(system_status.component_results) == 0
        assert system_status.get_overall_status() == ComponentStatus.UNKNOWN

    def test_perform_system_health_check_with_errors(self, health_check_manager):
        """Test performing system health check when checks raise errors"""
        health_check_manager.bedrock_agent_client.get_knowledge_base.side_effect = \
            ValueError("Invalid KB ID")

        system_status = health_check_manager.perform_system_health_check(
            kb_id="kb-123"
        )

        assert len(system_status.component_results) == 1
        assert system_status.component_results[0].status == ComponentStatus.UNKNOWN
