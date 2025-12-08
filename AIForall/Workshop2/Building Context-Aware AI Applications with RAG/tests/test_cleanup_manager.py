"""Tests for Resource Cleanup Manager"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from src.cleanup_manager import ResourceCleanupManager


class TestResourceCleanupManager:
    """Tests for ResourceCleanupManager class"""

    @pytest.fixture
    def mock_aws_config(self):
        """Create mock AWS config"""
        config = Mock()
        config.get_account_id.return_value = "123456789012"
        config.get_region.return_value = "us-east-1"
        return config

    @pytest.fixture
    def cleanup_manager(self, mock_aws_config):
        """Create cleanup manager instance"""
        return ResourceCleanupManager(mock_aws_config)

    def test_cleanup_manager_initialization(self, cleanup_manager, mock_aws_config):
        """Test cleanup manager initialization"""
        assert cleanup_manager.aws_config == mock_aws_config
        assert cleanup_manager.account_id == "123456789012"
        assert cleanup_manager.region == "us-east-1"

    def test_cleanup_knowledge_base_resources_without_confirmation(self, cleanup_manager):
        """Test cleanup without confirmation raises error"""
        with pytest.raises(ValueError, match="Cleanup confirmation required"):
            cleanup_manager.cleanup_knowledge_base_resources(
                kb_id="kb-12345",
                confirm=False
            )

    def test_cleanup_knowledge_base_resources_empty_kb_id(self, cleanup_manager):
        """Test cleanup with empty KB ID raises error"""
        with pytest.raises(ValueError, match="Knowledge base ID cannot be empty"):
            cleanup_manager.cleanup_knowledge_base_resources(
                kb_id="",
                confirm=True
            )

    def test_cleanup_knowledge_base_resources_success(self, cleanup_manager):
        """Test successful knowledge base cleanup"""
        mock_kb_manager = Mock()
        mock_kb_manager.cleanup_knowledge_base.return_value = {
            "kb_deleted": True,
            "data_sources_deleted": 2,
            "errors": []
        }

        result = cleanup_manager.cleanup_knowledge_base_resources(
            kb_id="kb-12345",
            kb_manager=mock_kb_manager,
            confirm=True
        )

        assert result["kb_cleanup"]["kb_deleted"] is True
        assert result["kb_cleanup"]["data_sources_deleted"] == 2
        assert result["total_resources_deleted"] == 3  # 1 KB + 2 data sources
        assert len(result["errors"]) == 0

    def test_cleanup_knowledge_base_resources_with_errors(self, cleanup_manager):
        """Test knowledge base cleanup with errors"""
        mock_kb_manager = Mock()
        mock_kb_manager.cleanup_knowledge_base.return_value = {
            "kb_deleted": True,
            "data_sources_deleted": 1,
            "errors": ["Failed to delete data source ds-123"]
        }

        result = cleanup_manager.cleanup_knowledge_base_resources(
            kb_id="kb-12345",
            kb_manager=mock_kb_manager,
            confirm=True
        )

        assert result["kb_cleanup"]["kb_deleted"] is True
        assert len(result["errors"]) == 1
        assert "Failed to delete data source" in result["errors"][0]

    def test_cleanup_test_resources_without_confirmation(self, cleanup_manager):
        """Test test resource cleanup without confirmation raises error"""
        with pytest.raises(ValueError, match="Test resource cleanup confirmation required"):
            cleanup_manager.cleanup_test_resources(
                confirm=False
            )

    def test_cleanup_test_resources_success(self, cleanup_manager):
        """Test successful test resource cleanup"""
        mock_kb_manager = Mock()
        mock_kb_manager.list_knowledge_bases.return_value = [
            {"kb_id": "kb-test-1", "kb_name": "test-kb-1"},
            {"kb_id": "kb-prod-1", "kb_name": "prod-kb-1"},
            {"kb_id": "kb-test-2", "kb_name": "test-kb-2"}
        ]
        mock_kb_manager.delete_knowledge_base.return_value = True

        result = cleanup_manager.cleanup_test_resources(
            test_prefix="test-",
            kb_manager=mock_kb_manager,
            confirm=True
        )

        assert result["knowledge_bases_deleted"] == 2
        assert len(result["errors"]) == 0

    def test_cleanup_test_resources_with_deletion_errors(self, cleanup_manager):
        """Test test resource cleanup with deletion errors"""
        mock_kb_manager = Mock()
        mock_kb_manager.list_knowledge_bases.return_value = [
            {"kb_id": "kb-test-1", "kb_name": "test-kb-1"},
            {"kb_id": "kb-test-2", "kb_name": "test-kb-2"}
        ]
        mock_kb_manager.delete_knowledge_base.side_effect = [
            True,
            Exception("Failed to delete KB")
        ]

        result = cleanup_manager.cleanup_test_resources(
            test_prefix="test-",
            kb_manager=mock_kb_manager,
            confirm=True
        )

        assert result["knowledge_bases_deleted"] == 1
        assert len(result["errors"]) == 1

    def test_cleanup_orphaned_resources_without_confirmation(self, cleanup_manager):
        """Test orphaned resource cleanup without confirmation raises error"""
        with pytest.raises(ValueError, match="Orphaned resource cleanup confirmation required"):
            cleanup_manager.cleanup_orphaned_resources(
                confirm=False
            )

    def test_cleanup_orphaned_resources_success(self, cleanup_manager):
        """Test successful orphaned resource cleanup"""
        mock_kb_manager = Mock()
        mock_kb_manager.list_knowledge_bases.return_value = [
            {"kb_id": "kb-1", "kb_name": "kb-1"},
            {"kb_id": "kb-2", "kb_name": "kb-2"}
        ]
        mock_kb_manager.get_knowledge_base.side_effect = [
            {"status": "FAILED"},
            {"status": "ACTIVE"}
        ]
        mock_kb_manager.delete_knowledge_base.return_value = True

        result = cleanup_manager.cleanup_orphaned_resources(
            kb_manager=mock_kb_manager,
            confirm=True
        )

        assert result["orphaned_kbs_deleted"] == 1
        assert len(result["errors"]) == 0

    def test_generate_cleanup_report_with_all_resources(self, cleanup_manager):
        """Test cleanup report generation with all resources"""
        cleanup_results = {
            "kb_cleanup": {
                "kb_deleted": True,
                "data_sources_deleted": 2
            },
            "vector_store_cleanup": {
                "collections_deleted": 1
            },
            "s3_cleanup": {
                "buckets_deleted": 1
            },
            "iam_cleanup": {
                "roles_deleted": 1,
                "policies_deleted": 3
            },
            "total_resources_deleted": 9,
            "errors": []
        }

        report = cleanup_manager.generate_cleanup_report(cleanup_results)

        assert "RESOURCE CLEANUP REPORT" in report
        assert "KB Deleted: True" in report
        assert "Data Sources Deleted: 2" in report
        assert "Collections Deleted: 1" in report
        assert "Buckets Deleted: 1" in report
        assert "Roles Deleted: 1" in report
        assert "Policies Deleted: 3" in report
        assert "Total Resources Deleted: 9" in report
        assert "No errors encountered" in report

    def test_generate_cleanup_report_with_errors(self, cleanup_manager):
        """Test cleanup report generation with errors"""
        cleanup_results = {
            "kb_cleanup": {},
            "vector_store_cleanup": {},
            "s3_cleanup": {},
            "iam_cleanup": {},
            "total_resources_deleted": 0,
            "errors": [
                "Failed to delete KB",
                "Failed to delete S3 bucket"
            ]
        }

        report = cleanup_manager.generate_cleanup_report(cleanup_results)

        assert "RESOURCE CLEANUP REPORT" in report
        assert "Errors Encountered: 2" in report
        assert "Failed to delete KB" in report
        assert "Failed to delete S3 bucket" in report

    def test_cleanup_knowledge_base_resources_with_all_managers(self, cleanup_manager):
        """Test cleanup with all manager types"""
        mock_kb_manager = Mock()
        mock_kb_manager.cleanup_knowledge_base.return_value = {
            "kb_deleted": True,
            "data_sources_deleted": 1,
            "errors": []
        }

        mock_vector_store_manager = Mock()
        mock_s3_manager = Mock()
        mock_iam_manager = Mock()

        result = cleanup_manager.cleanup_knowledge_base_resources(
            kb_id="kb-12345",
            kb_manager=mock_kb_manager,
            vector_store_manager=mock_vector_store_manager,
            s3_manager=mock_s3_manager,
            iam_manager=mock_iam_manager,
            delete_s3_buckets=True,
            delete_iam_roles=True,
            confirm=True
        )

        assert result["kb_cleanup"]["kb_deleted"] is True
        assert "vector_store_cleanup" in result
        assert "s3_cleanup" in result
        assert "iam_cleanup" in result

    def test_cleanup_knowledge_base_resources_partial_failure(self, cleanup_manager):
        """Test cleanup with partial failure"""
        mock_kb_manager = Mock()
        mock_kb_manager.cleanup_knowledge_base.side_effect = Exception("KB cleanup failed")

        result = cleanup_manager.cleanup_knowledge_base_resources(
            kb_id="kb-12345",
            kb_manager=mock_kb_manager,
            confirm=True
        )

        assert len(result["errors"]) > 0
        assert "KB cleanup failed" in str(result["errors"])

    def test_cleanup_test_resources_no_test_kbs(self, cleanup_manager):
        """Test test resource cleanup when no test KBs exist"""
        mock_kb_manager = Mock()
        mock_kb_manager.list_knowledge_bases.return_value = [
            {"kb_id": "kb-prod-1", "kb_name": "prod-kb-1"},
            {"kb_id": "kb-prod-2", "kb_name": "prod-kb-2"}
        ]

        result = cleanup_manager.cleanup_test_resources(
            test_prefix="test-",
            kb_manager=mock_kb_manager,
            confirm=True
        )

        assert result["knowledge_bases_deleted"] == 0
        assert len(result["errors"]) == 0

    def test_cleanup_orphaned_resources_no_failed_kbs(self, cleanup_manager):
        """Test orphaned resource cleanup when no failed KBs exist"""
        mock_kb_manager = Mock()
        mock_kb_manager.list_knowledge_bases.return_value = [
            {"kb_id": "kb-1", "kb_name": "kb-1"},
            {"kb_id": "kb-2", "kb_name": "kb-2"}
        ]
        mock_kb_manager.get_knowledge_base.side_effect = [
            {"status": "ACTIVE"},
            {"status": "ACTIVE"}
        ]

        result = cleanup_manager.cleanup_orphaned_resources(
            kb_manager=mock_kb_manager,
            confirm=True
        )

        assert result["orphaned_kbs_deleted"] == 0
        assert len(result["errors"]) == 0


class TestCleanupManagerIntegration:
    """Integration tests for cleanup manager"""

    @pytest.fixture
    def mock_aws_config(self):
        """Create mock AWS config"""
        config = Mock()
        config.get_account_id.return_value = "123456789012"
        config.get_region.return_value = "us-east-1"
        return config

    @pytest.fixture
    def cleanup_manager(self, mock_aws_config):
        """Create cleanup manager instance"""
        return ResourceCleanupManager(mock_aws_config)

    def test_full_cleanup_workflow(self, cleanup_manager):
        """Test full cleanup workflow"""
        # Create mock managers
        mock_kb_manager = Mock()
        mock_kb_manager.cleanup_knowledge_base.return_value = {
            "kb_deleted": True,
            "data_sources_deleted": 2,
            "errors": []
        }

        # Perform cleanup
        result = cleanup_manager.cleanup_knowledge_base_resources(
            kb_id="kb-12345",
            kb_manager=mock_kb_manager,
            confirm=True
        )

        # Verify results
        assert result["kb_cleanup"]["kb_deleted"] is True
        assert result["total_resources_deleted"] == 3
        assert len(result["errors"]) == 0

        # Generate report
        report = cleanup_manager.generate_cleanup_report(result)
        assert "RESOURCE CLEANUP REPORT" in report
        assert "Total Resources Deleted: 3" in report
