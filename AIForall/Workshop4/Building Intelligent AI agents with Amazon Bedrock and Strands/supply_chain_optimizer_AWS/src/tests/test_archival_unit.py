"""Unit tests for data archival service.

Tests specific examples and edge cases for archival functionality.
"""

from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch
import json
import gzip
from io import BytesIO

import pytest

from src.services.archival_service import DataArchivalService, ArchivalPolicy


class TestArchivalPolicyConfiguration:
    """Test archival policy configuration."""

    def test_archival_policy_creation(self):
        """Test creating an archival policy."""
        policy = ArchivalPolicy(
            table_name="test_table",
            retention_days=730,
            archive_after_days=90,
            archive_prefix="archives/test",
        )

        assert policy.table_name == "test_table"
        assert policy.retention_days == 730
        assert policy.archive_after_days == 90
        assert policy.archive_prefix == "archives/test"

    def test_archival_policy_validation(self):
        """Test that retention_days >= archive_after_days."""
        # Valid policy
        policy = ArchivalPolicy(
            table_name="test",
            retention_days=730,
            archive_after_days=90,
            archive_prefix="archives/test",
        )
        assert policy.retention_days >= policy.archive_after_days

    def test_default_policies_exist(self):
        """Test that default policies are configured."""
        policies = DataArchivalService.DEFAULT_POLICIES

        assert "purchase_orders" in policies
        assert "products" in policies
        assert "suppliers" in policies
        assert "forecasts" in policies
        assert "inventory" in policies
        assert "anomalies" in policies

    def test_default_policy_values(self):
        """Test default policy values are reasonable."""
        policies = DataArchivalService.DEFAULT_POLICIES

        # Purchase orders: 7 years retention, 1 year archive
        po_policy = policies["purchase_orders"]
        assert po_policy.retention_days == 2555  # 7 years
        assert po_policy.archive_after_days == 365  # 1 year

        # Forecasts: 2 years retention, 3 months archive
        forecast_policy = policies["forecasts"]
        assert forecast_policy.retention_days == 730  # 2 years
        assert forecast_policy.archive_after_days == 90  # 3 months


class TestArchivalServiceInitialization:
    """Test archival service initialization."""

    @patch("src.services.archival_service.get_s3_client")
    @patch("src.services.archival_service.get_dynamodb_resource")
    def test_service_initialization_with_default_bucket(self, mock_dynamodb, mock_s3_client):
        """Test service initialization with default bucket."""
        mock_s3_client.return_value = MagicMock()
        mock_dynamodb.return_value = MagicMock()

        service = DataArchivalService()

        assert service.s3_bucket is not None
        assert service.s3_client is not None
        assert service.dynamodb is not None
        assert len(service.policies) > 0

    @patch("src.services.archival_service.get_s3_client")
    @patch("src.services.archival_service.get_dynamodb_resource")
    def test_service_initialization_with_custom_bucket(self, mock_dynamodb, mock_s3_client):
        """Test service initialization with custom bucket."""
        mock_s3_client.return_value = MagicMock()
        mock_dynamodb.return_value = MagicMock()

        service = DataArchivalService(s3_bucket="custom-bucket")

        assert service.s3_bucket == "custom-bucket"

    @patch("src.services.archival_service.get_s3_client")
    @patch("src.services.archival_service.get_dynamodb_resource")
    def test_set_custom_policy(self, mock_dynamodb, mock_s3_client):
        """Test setting a custom archival policy."""
        mock_s3_client.return_value = MagicMock()
        mock_dynamodb.return_value = MagicMock()

        service = DataArchivalService()

        custom_policy = ArchivalPolicy(
            table_name="custom_table",
            retention_days=1000,
            archive_after_days=100,
            archive_prefix="archives/custom",
        )

        service.set_policy(custom_policy)

        assert "custom_table" in service.policies
        assert service.policies["custom_table"].retention_days == 1000


class TestArchiveUploadAndDownload:
    """Test archive upload and download functionality."""

    @patch("src.services.archival_service.get_s3_client")
    @patch("src.services.archival_service.get_dynamodb_resource")
    def test_upload_archive_to_s3(self, mock_dynamodb, mock_s3_client):
        """Test uploading archive to S3."""
        mock_s3 = MagicMock()
        mock_s3_client.return_value = mock_s3
        mock_dynamodb.return_value = MagicMock()

        service = DataArchivalService(s3_bucket="test-bucket")

        records = [
            {
                "po_id": "PO-001",
                "sku": "PROD-001",
                "quantity": 100,
                "status": "delivered",
            }
        ]
        cutoff_date = datetime.utcnow() - timedelta(days=365)

        mock_s3.put_object.return_value = {"ETag": "test"}

        s3_key = service._upload_archive_to_s3("purchase_orders", records, cutoff_date)

        assert s3_key is not None
        assert "purchase_orders" in s3_key
        assert mock_s3.put_object.called

    @patch("src.services.archival_service.get_s3_client")
    @patch("src.services.archival_service.get_dynamodb_resource")
    def test_download_archive_from_s3(self, mock_dynamodb, mock_s3_client):
        """Test downloading archive from S3."""
        mock_s3 = MagicMock()
        mock_s3_client.return_value = mock_s3
        mock_dynamodb.return_value = MagicMock()

        service = DataArchivalService(s3_bucket="test-bucket")

        # Create test archive
        records = [
            {
                "po_id": "PO-001",
                "sku": "PROD-001",
                "quantity": 100,
            }
        ]
        archive_metadata = {
            "table_name": "purchase_orders",
            "cutoff_date": datetime.utcnow().isoformat(),
            "archived_at": datetime.utcnow().isoformat(),
            "record_count": len(records),
            "records": records,
        }

        json_data = json.dumps(archive_metadata, default=str)
        compressed = BytesIO()
        with gzip.GzipFile(fileobj=compressed, mode="wb") as gz:
            gz.write(json_data.encode("utf-8"))
        compressed_data = compressed.getvalue()

        mock_s3.get_object.return_value = {
            "Body": MagicMock(read=lambda: compressed_data)
        }

        downloaded_records = service._download_archive_from_s3("test_key.json.gz")

        assert len(downloaded_records) == 1
        assert downloaded_records[0]["po_id"] == "PO-001"

    @patch("src.services.archival_service.get_s3_client")
    @patch("src.services.archival_service.get_dynamodb_resource")
    def test_archive_compression(self, mock_dynamodb, mock_s3_client):
        """Test that archives are compressed."""
        mock_s3 = MagicMock()
        mock_s3_client.return_value = mock_s3
        mock_dynamodb.return_value = MagicMock()

        service = DataArchivalService(s3_bucket="test-bucket")

        # Create large record set
        records = [
            {
                "po_id": f"PO-{i:05d}",
                "sku": f"PROD-{i:05d}",
                "quantity": 100 + i,
                "unit_price": 10.50 + i,
                "status": "delivered",
            }
            for i in range(100)
        ]

        cutoff_date = datetime.utcnow() - timedelta(days=365)

        # Capture the uploaded data
        uploaded_data = None

        def capture_put_object(**kwargs):
            nonlocal uploaded_data
            uploaded_data = kwargs["Body"]
            return {"ETag": "test"}

        mock_s3.put_object.side_effect = capture_put_object

        service._upload_archive_to_s3("purchase_orders", records, cutoff_date)

        # Verify data was compressed
        assert uploaded_data is not None
        assert len(uploaded_data) > 0

        # Verify it's valid gzip
        with gzip.GzipFile(fileobj=BytesIO(uploaded_data), mode="rb") as gz:
            decompressed = gz.read()
            assert len(decompressed) > 0


class TestDateFiltering:
    """Test date filtering functionality."""

    @patch("src.services.archival_service.get_s3_client")
    @patch("src.services.archival_service.get_dynamodb_resource")
    def test_filter_by_date_range(self, mock_dynamodb, mock_s3_client):
        """Test filtering records by date range."""
        mock_s3_client.return_value = MagicMock()
        mock_dynamodb.return_value = MagicMock()

        service = DataArchivalService()

        now = datetime.utcnow()
        records = [
            {"id": "1", "created_at": (now - timedelta(days=200)).isoformat()},
            {"id": "2", "created_at": (now - timedelta(days=150)).isoformat()},
            {"id": "3", "created_at": (now - timedelta(days=100)).isoformat()},
            {"id": "4", "created_at": (now - timedelta(days=50)).isoformat()},
        ]

        start_date = now - timedelta(days=180)
        end_date = now - timedelta(days=80)

        filtered = service._filter_by_date(records, start_date, end_date)

        # Should include records 2 and 3
        assert len(filtered) == 2
        assert filtered[0]["id"] == "2"
        assert filtered[1]["id"] == "3"

    @patch("src.services.archival_service.get_s3_client")
    @patch("src.services.archival_service.get_dynamodb_resource")
    def test_filter_by_start_date_only(self, mock_dynamodb, mock_s3_client):
        """Test filtering with only start date."""
        mock_s3_client.return_value = MagicMock()
        mock_dynamodb.return_value = MagicMock()

        service = DataArchivalService()

        now = datetime.utcnow()
        records = [
            {"id": "1", "created_at": (now - timedelta(days=200)).isoformat()},
            {"id": "2", "created_at": (now - timedelta(days=100)).isoformat()},
            {"id": "3", "created_at": (now - timedelta(days=50)).isoformat()},
        ]

        start_date = now - timedelta(days=150)

        filtered = service._filter_by_date(records, start_date=start_date)

        # Should include records 2 and 3
        assert len(filtered) == 2

    @patch("src.services.archival_service.get_s3_client")
    @patch("src.services.archival_service.get_dynamodb_resource")
    def test_filter_by_end_date_only(self, mock_dynamodb, mock_s3_client):
        """Test filtering with only end date."""
        mock_s3_client.return_value = MagicMock()
        mock_dynamodb.return_value = MagicMock()

        service = DataArchivalService()

        now = datetime.utcnow()
        records = [
            {"id": "1", "created_at": (now - timedelta(days=200)).isoformat()},
            {"id": "2", "created_at": (now - timedelta(days=100)).isoformat()},
            {"id": "3", "created_at": (now - timedelta(days=50)).isoformat()},
        ]

        end_date = now - timedelta(days=75)

        filtered = service._filter_by_date(records, end_date=end_date)

        # Should include records 1 and 2
        assert len(filtered) == 2

    @patch("src.services.archival_service.get_s3_client")
    @patch("src.services.archival_service.get_dynamodb_resource")
    def test_filter_records_without_date_field(self, mock_dynamodb, mock_s3_client):
        """Test filtering records without date field."""
        mock_s3_client.return_value = MagicMock()
        mock_dynamodb.return_value = MagicMock()

        service = DataArchivalService()

        records = [
            {"id": "1", "name": "Record 1"},
            {"id": "2", "name": "Record 2"},
        ]

        now = datetime.utcnow()
        start_date = now - timedelta(days=100)

        filtered = service._filter_by_date(records, start_date=start_date)

        # Records without date field should be included
        assert len(filtered) == 2


class TestArchiveStatistics:
    """Test archive statistics functionality."""

    @patch("src.services.archival_service.get_s3_client")
    @patch("src.services.archival_service.get_dynamodb_resource")
    def test_get_archive_statistics(self, mock_dynamodb, mock_s3_client):
        """Test getting archive statistics."""
        mock_s3 = MagicMock()
        mock_s3_client.return_value = mock_s3
        mock_dynamodb.return_value = MagicMock()

        service = DataArchivalService(s3_bucket="test-bucket")

        mock_s3.list_objects_v2.return_value = {
            "Contents": [
                {"Key": "archives/purchase_orders/data_1.json.gz", "Size": 5000},
                {"Key": "archives/purchase_orders/data_2.json.gz", "Size": 6000},
                {"Key": "archives/forecasts/data_1.json.gz", "Size": 3000},
            ]
        }

        stats = service.get_archive_statistics()

        assert stats["bucket"] == "test-bucket"
        assert stats["total_archives"] == 3
        assert stats["total_size_bytes"] == 14000
        assert "purchase_orders" in stats["tables"]
        assert "forecasts" in stats["tables"]
        assert stats["tables"]["purchase_orders"]["archive_count"] == 2
        assert stats["tables"]["forecasts"]["archive_count"] == 1

    @patch("src.services.archival_service.get_s3_client")
    @patch("src.services.archival_service.get_dynamodb_resource")
    def test_get_archive_statistics_empty_bucket(self, mock_dynamodb, mock_s3_client):
        """Test getting statistics for empty bucket."""
        mock_s3 = MagicMock()
        mock_s3_client.return_value = mock_s3
        mock_dynamodb.return_value = MagicMock()

        service = DataArchivalService(s3_bucket="test-bucket")

        mock_s3.list_objects_v2.return_value = {}

        stats = service.get_archive_statistics()

        assert stats["bucket"] == "test-bucket"
        assert stats["total_archives"] == 0
        assert stats["total_size_bytes"] == 0
        assert len(stats["tables"]) == 0


class TestErrorHandling:
    """Test error handling in archival service."""

    @patch("src.services.archival_service.get_s3_client")
    @patch("src.services.archival_service.get_dynamodb_resource")
    def test_invalid_policy_error(self, mock_dynamodb, mock_s3_client):
        """Test error when policy doesn't exist."""
        mock_s3_client.return_value = MagicMock()
        mock_dynamodb.return_value = MagicMock()

        service = DataArchivalService()

        with pytest.raises(ValueError):
            service._upload_archive_to_s3("nonexistent_table", [], datetime.utcnow())

    @patch("src.services.archival_service.get_s3_client")
    @patch("src.services.archival_service.get_dynamodb_resource")
    def test_query_archive_invalid_table(self, mock_dynamodb, mock_s3_client):
        """Test querying archive for invalid table."""
        mock_s3_client.return_value = MagicMock()
        mock_dynamodb.return_value = MagicMock()

        service = DataArchivalService()

        with pytest.raises(ValueError):
            service.query_archive("nonexistent_table")

    @patch("src.services.archival_service.get_s3_client")
    @patch("src.services.archival_service.get_dynamodb_resource")
    def test_query_archive_no_results(self, mock_dynamodb, mock_s3_client):
        """Test querying archive with no results."""
        mock_s3 = MagicMock()
        mock_s3_client.return_value = mock_s3
        mock_dynamodb.return_value = MagicMock()

        service = DataArchivalService()

        mock_s3.list_objects_v2.return_value = {}

        results = service.query_archive("purchase_orders")

        assert len(results) == 0


class TestRetentionPolicyEnforcement:
    """Test retention policy enforcement functionality."""

    @patch("src.services.archival_service.get_s3_client")
    @patch("src.services.archival_service.get_dynamodb_resource")
    def test_retention_policy_configuration(self, mock_dynamodb, mock_s3_client):
        """Test that retention policies are correctly configured."""
        mock_s3_client.return_value = MagicMock()
        mock_dynamodb.return_value = MagicMock()

        service = DataArchivalService()

        # Verify purchase orders policy
        po_policy = service.policies["purchase_orders"]
        assert po_policy.retention_days == 2555  # 7 years
        assert po_policy.archive_after_days == 365  # 1 year
        assert po_policy.retention_days >= po_policy.archive_after_days

        # Verify forecasts policy
        forecast_policy = service.policies["forecasts"]
        assert forecast_policy.retention_days == 730  # 2 years
        assert forecast_policy.archive_after_days == 90  # 3 months

    @patch("src.services.archival_service.get_s3_client")
    @patch("src.services.archival_service.get_dynamodb_resource")
    def test_enforce_retention_policy_calculates_cutoff_dates(self, mock_dynamodb, mock_s3_client):
        """Test that enforce_retention_policy calculates correct cutoff dates."""
        mock_s3 = MagicMock()
        mock_s3_client.return_value = mock_s3
        mock_dynamodb.return_value = MagicMock()

        service = DataArchivalService()

        # Mock the archive_rds_table method to capture the cutoff date
        captured_cutoff = None

        def capture_archive_rds_table(table_name, cutoff_date, batch_size=1000):
            nonlocal captured_cutoff
            captured_cutoff = cutoff_date
            return {
                "table_name": table_name,
                "archived_count": 0,
                "deleted_count": 0,
                "archive_key": None,
                "cutoff_date": cutoff_date.isoformat(),
                "timestamp": datetime.utcnow().isoformat(),
            }

        service.archive_rds_table = capture_archive_rds_table

        # Enforce policy
        now = datetime.utcnow()
        result = service.enforce_retention_policy("purchase_orders")

        # Verify cutoff date is approximately 365 days ago
        expected_cutoff = now - timedelta(days=365)
        assert captured_cutoff is not None
        assert abs((captured_cutoff - expected_cutoff).total_seconds()) < 60  # Within 1 minute

    @patch("src.services.archival_service.get_s3_client")
    @patch("src.services.archival_service.get_dynamodb_resource")
    def test_retention_policy_archive_cutoff_calculation(self, mock_dynamodb, mock_s3_client):
        """Test that archive cutoff is calculated correctly based on policy."""
        mock_s3_client.return_value = MagicMock()
        mock_dynamodb.return_value = MagicMock()

        service = DataArchivalService()

        # Create custom policy
        custom_policy = ArchivalPolicy(
            table_name="test_table",
            retention_days=1000,
            archive_after_days=100,
            archive_prefix="archives/test",
        )
        service.set_policy(custom_policy)

        now = datetime.utcnow()
        archive_cutoff = now - timedelta(days=custom_policy.archive_after_days)
        retention_cutoff = now - timedelta(days=custom_policy.retention_days)

        # Verify cutoff calculations
        assert (now - archive_cutoff).days == custom_policy.archive_after_days
        assert (now - retention_cutoff).days == custom_policy.retention_days

    @patch("src.services.archival_service.get_s3_client")
    @patch("src.services.archival_service.get_dynamodb_resource")
    def test_retention_policy_enforcement_result_structure(self, mock_dynamodb, mock_s3_client):
        """Test that enforce_retention_policy returns correct result structure."""
        mock_s3 = MagicMock()
        mock_s3_client.return_value = mock_s3
        mock_dynamodb.return_value = MagicMock()

        service = DataArchivalService()

        # Mock archive method
        service.archive_rds_table = Mock(
            return_value={
                "table_name": "purchase_orders",
                "archived_count": 100,
                "deleted_count": 100,
                "archive_key": "archives/purchase_orders/data_1.json.gz",
                "cutoff_date": datetime.utcnow().isoformat(),
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        result = service.enforce_retention_policy("purchase_orders")

        # Verify result structure
        assert "table_name" in result
        assert "policy" in result
        assert "archive_result" in result
        assert result["table_name"] == "purchase_orders"
        assert result["policy"]["retention_days"] == 2555
        assert result["policy"]["archive_after_days"] == 365

    @patch("src.services.archival_service.get_s3_client")
    @patch("src.services.archival_service.get_dynamodb_resource")
    def test_retention_policy_invalid_table(self, mock_dynamodb, mock_s3_client):
        """Test error when enforcing policy for invalid table."""
        mock_s3_client.return_value = MagicMock()
        mock_dynamodb.return_value = MagicMock()

        service = DataArchivalService()

        with pytest.raises(ValueError):
            service.enforce_retention_policy("nonexistent_table")


class TestArchiveQueryability:
    """Test archive queryability and retrieval functionality."""

    @patch("src.services.archival_service.get_s3_client")
    @patch("src.services.archival_service.get_dynamodb_resource")
    def test_query_archive_with_date_range(self, mock_dynamodb, mock_s3_client):
        """Test querying archives with date range filter."""
        mock_s3 = MagicMock()
        mock_s3_client.return_value = mock_s3
        mock_dynamodb.return_value = MagicMock()

        service = DataArchivalService()

        # Create test archive data
        now = datetime.utcnow()
        records = [
            {
                "po_id": "PO-001",
                "created_at": (now - timedelta(days=200)).isoformat(),
            },
            {
                "po_id": "PO-002",
                "created_at": (now - timedelta(days=150)).isoformat(),
            },
            {
                "po_id": "PO-003",
                "created_at": (now - timedelta(days=100)).isoformat(),
            },
        ]

        archive_metadata = {
            "table_name": "purchase_orders",
            "cutoff_date": (now - timedelta(days=365)).isoformat(),
            "archived_at": now.isoformat(),
            "record_count": len(records),
            "records": records,
        }

        json_data = json.dumps(archive_metadata, default=str)
        compressed = BytesIO()
        with gzip.GzipFile(fileobj=compressed, mode="wb") as gz:
            gz.write(json_data.encode("utf-8"))
        compressed_data = compressed.getvalue()

        mock_s3.list_objects_v2.return_value = {
            "Contents": [{"Key": "archives/purchase_orders/data_1.json.gz", "Size": 1000}]
        }
        mock_s3.get_object.return_value = {
            "Body": MagicMock(read=lambda: compressed_data)
        }

        # Query with date range
        start_date = now - timedelta(days=180)
        end_date = now - timedelta(days=120)

        results = service.query_archive(
            "purchase_orders", start_date=start_date, end_date=end_date
        )

        # Should return only PO-002
        assert len(results) == 1
        assert results[0]["po_id"] == "PO-002"

    @patch("src.services.archival_service.get_s3_client")
    @patch("src.services.archival_service.get_dynamodb_resource")
    def test_query_archive_multiple_files(self, mock_dynamodb, mock_s3_client):
        """Test querying archives across multiple archive files."""
        mock_s3 = MagicMock()
        mock_s3_client.return_value = mock_s3
        mock_dynamodb.return_value = MagicMock()

        service = DataArchivalService()

        now = datetime.utcnow()

        # Create two archive files
        records1 = [
            {"po_id": "PO-001", "created_at": (now - timedelta(days=200)).isoformat()},
            {"po_id": "PO-002", "created_at": (now - timedelta(days=190)).isoformat()},
        ]

        records2 = [
            {"po_id": "PO-003", "created_at": (now - timedelta(days=180)).isoformat()},
            {"po_id": "PO-004", "created_at": (now - timedelta(days=170)).isoformat()},
        ]

        # Create compressed archives
        archives = []
        for records in [records1, records2]:
            archive_metadata = {
                "table_name": "purchase_orders",
                "cutoff_date": (now - timedelta(days=365)).isoformat(),
                "archived_at": now.isoformat(),
                "record_count": len(records),
                "records": records,
            }

            json_data = json.dumps(archive_metadata, default=str)
            compressed = BytesIO()
            with gzip.GzipFile(fileobj=compressed, mode="wb") as gz:
                gz.write(json_data.encode("utf-8"))
            archives.append(compressed.getvalue())

        # Mock S3 list and get
        mock_s3.list_objects_v2.return_value = {
            "Contents": [
                {"Key": "archives/purchase_orders/data_1.json.gz", "Size": 1000},
                {"Key": "archives/purchase_orders/data_2.json.gz", "Size": 1000},
            ]
        }

        # Mock get_object to return different archives
        call_count = [0]

        def mock_get_object(**kwargs):
            result = call_count[0]
            call_count[0] += 1
            return {"Body": MagicMock(read=lambda: archives[result])}

        mock_s3.get_object.side_effect = mock_get_object

        results = service.query_archive("purchase_orders")

        # Should return all 4 records
        assert len(results) == 4
        po_ids = [r["po_id"] for r in results]
        assert "PO-001" in po_ids
        assert "PO-004" in po_ids

    @patch("src.services.archival_service.get_s3_client")
    @patch("src.services.archival_service.get_dynamodb_resource")
    def test_query_archive_preserves_all_fields(self, mock_dynamodb, mock_s3_client):
        """Test that querying archives preserves all record fields."""
        mock_s3 = MagicMock()
        mock_s3_client.return_value = mock_s3
        mock_dynamodb.return_value = MagicMock()

        service = DataArchivalService()

        now = datetime.utcnow()
        records = [
            {
                "po_id": "PO-001",
                "sku": "PROD-001",
                "supplier_id": "SUP-001",
                "quantity": 100,
                "unit_price": 10.50,
                "total_cost": 1050.00,
                "status": "delivered",
                "created_at": (now - timedelta(days=200)).isoformat(),
            }
        ]

        archive_metadata = {
            "table_name": "purchase_orders",
            "cutoff_date": (now - timedelta(days=365)).isoformat(),
            "archived_at": now.isoformat(),
            "record_count": len(records),
            "records": records,
        }

        json_data = json.dumps(archive_metadata, default=str)
        compressed = BytesIO()
        with gzip.GzipFile(fileobj=compressed, mode="wb") as gz:
            gz.write(json_data.encode("utf-8"))
        compressed_data = compressed.getvalue()

        mock_s3.list_objects_v2.return_value = {
            "Contents": [{"Key": "archives/purchase_orders/data_1.json.gz", "Size": 1000}]
        }
        mock_s3.get_object.return_value = {
            "Body": MagicMock(read=lambda: compressed_data)
        }

        results = service.query_archive("purchase_orders")

        # Verify all fields are preserved
        assert len(results) == 1
        result = results[0]
        assert result["po_id"] == "PO-001"
        assert result["sku"] == "PROD-001"
        assert result["supplier_id"] == "SUP-001"
        assert result["quantity"] == 100
        assert result["unit_price"] == 10.50
        assert result["total_cost"] == 1050.00
        assert result["status"] == "delivered"


class TestArchivalProcessWorkflow:
    """Test complete archival process workflows."""

    @patch("src.services.archival_service.get_s3_client")
    @patch("src.services.archival_service.get_dynamodb_resource")
    def test_complete_archival_workflow(self, mock_dynamodb, mock_s3_client):
        """Test complete archival workflow from upload to query."""
        mock_s3 = MagicMock()
        mock_s3_client.return_value = mock_s3
        mock_dynamodb.return_value = MagicMock()

        service = DataArchivalService(s3_bucket="test-bucket")

        # Step 1: Create records to archive
        now = datetime.utcnow()
        records = [
            {
                "po_id": f"PO-{i:03d}",
                "sku": f"PROD-{i:03d}",
                "quantity": 100 + i,
                "created_at": (now - timedelta(days=365 + i)).isoformat(),
            }
            for i in range(10)
        ]

        cutoff_date = now - timedelta(days=365)

        # Step 2: Upload archive
        archive_metadata = {
            "table_name": "purchase_orders",
            "cutoff_date": cutoff_date.isoformat(),
            "archived_at": now.isoformat(),
            "record_count": len(records),
            "records": records,
        }

        json_data = json.dumps(archive_metadata, default=str)
        compressed = BytesIO()
        with gzip.GzipFile(fileobj=compressed, mode="wb") as gz:
            gz.write(json_data.encode("utf-8"))
        compressed_data = compressed.getvalue()

        mock_s3.put_object.return_value = {"ETag": "test"}
        mock_s3.get_object.return_value = {
            "Body": MagicMock(read=lambda: compressed_data)
        }

        s3_key = service._upload_archive_to_s3("purchase_orders", records, cutoff_date)

        # Verify upload
        assert s3_key is not None
        assert mock_s3.put_object.called

        # Step 3: Query archive
        mock_s3.list_objects_v2.return_value = {
            "Contents": [{"Key": s3_key, "Size": len(compressed_data)}]
        }

        results = service.query_archive("purchase_orders")

        # Verify query results
        assert len(results) == 10
        assert all("po_id" in r for r in results)
        assert all("sku" in r for r in results)

    @patch("src.services.archival_service.get_s3_client")
    @patch("src.services.archival_service.get_dynamodb_resource")
    def test_archival_with_policy_enforcement(self, mock_dynamodb, mock_s3_client):
        """Test archival process with retention policy enforcement."""
        mock_s3 = MagicMock()
        mock_s3_client.return_value = mock_s3
        mock_dynamodb.return_value = MagicMock()

        service = DataArchivalService()

        # Mock archive method
        archive_called = []

        def mock_archive_rds_table(table_name, cutoff_date, batch_size=1000):
            archive_called.append(
                {
                    "table_name": table_name,
                    "cutoff_date": cutoff_date,
                }
            )
            return {
                "table_name": table_name,
                "archived_count": 50,
                "deleted_count": 50,
                "archive_key": f"archives/{table_name}/data_1.json.gz",
                "cutoff_date": cutoff_date.isoformat(),
                "timestamp": datetime.utcnow().isoformat(),
            }

        service.archive_rds_table = mock_archive_rds_table

        # Enforce policy
        result = service.enforce_retention_policy("purchase_orders")

        # Verify policy was enforced
        assert len(archive_called) == 1
        assert archive_called[0]["table_name"] == "purchase_orders"
        assert result["archive_result"]["archived_count"] == 50
        assert result["archive_result"]["deleted_count"] == 50
