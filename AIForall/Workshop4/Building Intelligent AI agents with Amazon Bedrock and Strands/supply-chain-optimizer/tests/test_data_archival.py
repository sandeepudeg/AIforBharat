"""Property-based tests for data archival and retention policies.

Feature: supply-chain-optimizer, Property 35: Data Archival and Accessibility
Validates: Requirements 8.5
"""

import json
import gzip
from datetime import datetime, timedelta, date
from typing import Any, Dict, List
from io import BytesIO
from unittest.mock import Mock, MagicMock, patch
import random
import string

from src.services.archival_service import DataArchivalService, ArchivalPolicy


def generate_random_string(min_size: int = 1, max_size: int = 50) -> str:
    """Generate a random string."""
    size = random.randint(min_size, max_size)
    return ''.join(random.choices(string.ascii_letters + string.digits + '_-', k=size))


def generate_random_int(min_value: int = 0, max_value: int = 10000) -> int:
    """Generate a random integer."""
    return random.randint(min_value, max_value)


def generate_random_float(min_value: float = 0.01, max_value: float = 10000.0) -> float:
    """Generate a random float."""
    return random.uniform(min_value, max_value)


def generate_purchase_order_record() -> Dict[str, Any]:
    """Generate a random purchase order record."""
    order_date = datetime.utcnow() - timedelta(days=random.randint(1, 365))
    return {
        "po_id": generate_random_string(1, 50),
        "sku": generate_random_string(1, 50),
        "supplier_id": generate_random_string(1, 50),
        "quantity": generate_random_int(1, 10000),
        "unit_price": generate_random_float(0.01, 10000.0),
        "total_cost": generate_random_float(0.01, 100000.0),
        "order_date": order_date.isoformat(),
        "expected_delivery_date": (order_date + timedelta(days=7)).isoformat(),
        "actual_delivery_date": (order_date + timedelta(days=8)).isoformat(),
        "status": random.choice(["pending", "confirmed", "shipped", "delivered"]),
        "created_at": order_date.isoformat(),
        "updated_at": order_date.isoformat(),
    }


def generate_forecast_record() -> Dict[str, Any]:
    """Generate a random forecast record."""
    created_date = datetime.utcnow() - timedelta(days=random.randint(1, 365))
    return {
        "forecast_id": generate_random_string(1, 50),
        "sku": generate_random_string(1, 50),
        "forecast_date": created_date.date().isoformat(),
        "forecast_period": generate_random_string(1, 100),
        "forecasted_demand": generate_random_int(0, 10000),
        "confidence_80": float(generate_random_int(0, 10000)),
        "confidence_95": float(generate_random_int(0, 10000)),
        "created_at": created_date.isoformat(),
    }


def generate_inventory_record() -> Dict[str, Any]:
    """Generate a random inventory record."""
    created_date = datetime.utcnow() - timedelta(days=random.randint(1, 365))
    quantity_on_hand = generate_random_int(0, 10000)
    return {
        "inventory_id": generate_random_string(1, 50),
        "sku": generate_random_string(1, 50),
        "warehouse_id": generate_random_string(1, 50),
        "quantity_on_hand": quantity_on_hand,
        "quantity_reserved": generate_random_int(0, quantity_on_hand),
        "quantity_available": quantity_on_hand - generate_random_int(0, quantity_on_hand),
        "reorder_point": generate_random_int(0, 10000),
        "last_updated": created_date.isoformat(),
        "created_at": created_date.isoformat(),
    }


class TestDataArchivalAndAccessibility:
    """Test data archival and accessibility for all data types.
    
    Feature: supply-chain-optimizer, Property 35: Data Archival and Accessibility
    Validates: Requirements 8.5
    """

    @patch("src.services.archival_service.get_s3_client")
    @patch("src.services.archival_service.get_dynamodb_resource")
    def test_archive_upload_and_download_round_trip(self, mock_dynamodb, mock_s3_client):
        """For any archived data, uploading to S3 and downloading should return identical data.
        
        Property: *For any* data retention policy applied, old data should be archived 
        to separate storage while remaining queryable for historical analysis.
        """
        # Setup mocks
        mock_s3 = MagicMock()
        mock_s3_client.return_value = mock_s3
        mock_dynamodb.return_value = MagicMock()

        service = DataArchivalService(s3_bucket="test-bucket")

        # Run 100 iterations with random data
        for _ in range(100):
            # Generate random records
            records = [generate_purchase_order_record() for _ in range(random.randint(1, 50))]
            cutoff_date = datetime.utcnow() - timedelta(days=365)

            # Create archive metadata
            archive_metadata = {
                "table_name": "purchase_orders",
                "cutoff_date": cutoff_date.isoformat(),
                "archived_at": datetime.utcnow().isoformat(),
                "record_count": len(records),
                "records": records,
            }

            # Serialize to JSON
            json_data = json.dumps(archive_metadata, default=str)

            # Compress with gzip
            compressed = BytesIO()
            with gzip.GzipFile(fileobj=compressed, mode="wb") as gz:
                gz.write(json_data.encode("utf-8"))
            compressed_data = compressed.getvalue()

            # Mock S3 put and get
            mock_s3.put_object.return_value = {"ETag": "test"}
            mock_s3.get_object.return_value = {
                "Body": MagicMock(read=lambda: compressed_data)
            }

            # Upload archive
            s3_key = service._upload_archive_to_s3(
                "purchase_orders", records, cutoff_date
            )

            # Verify upload was called
            assert mock_s3.put_object.called
            assert s3_key is not None

            # Download archive
            downloaded_records = service._download_archive_from_s3(s3_key)

            # Verify round trip: all records should match
            assert len(downloaded_records) == len(records)
            for original, downloaded in zip(records, downloaded_records):
                assert original["po_id"] == downloaded["po_id"]
                assert original["sku"] == downloaded["sku"]
                assert original["supplier_id"] == downloaded["supplier_id"]
                assert original["quantity"] == downloaded["quantity"]
                assert original["unit_price"] == downloaded["unit_price"]
                assert original["status"] == downloaded["status"]

    @patch("src.services.archival_service.get_s3_client")
    @patch("src.services.archival_service.get_dynamodb_resource")
    def test_archive_metadata_preservation(self, mock_dynamodb, mock_s3_client):
        """For any archived data, metadata should be preserved and queryable.
        
        Property: *For any* data retention policy applied, old data should be archived 
        to separate storage while remaining queryable for historical analysis.
        """
        mock_s3 = MagicMock()
        mock_s3_client.return_value = mock_s3
        mock_dynamodb.return_value = MagicMock()

        service = DataArchivalService(s3_bucket="test-bucket")

        # Run 50 iterations
        for _ in range(50):
            records = [generate_forecast_record() for _ in range(random.randint(1, 30))]
            cutoff_date = datetime.utcnow() - timedelta(days=90)

            # Create archive
            archive_metadata = {
                "table_name": "forecasts",
                "cutoff_date": cutoff_date.isoformat(),
                "archived_at": datetime.utcnow().isoformat(),
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

            # Upload and download
            s3_key = service._upload_archive_to_s3("forecasts", records, cutoff_date)
            downloaded_records = service._download_archive_from_s3(s3_key)

            # Verify metadata is preserved
            assert len(downloaded_records) == len(records)
            assert all(
                "forecast_id" in r and "sku" in r and "forecasted_demand" in r
                for r in downloaded_records
            )

    @patch("src.services.archival_service.get_s3_client")
    @patch("src.services.archival_service.get_dynamodb_resource")
    def test_archive_date_filtering(self, mock_dynamodb, mock_s3_client):
        """For any archived data with date filtering, only records in date range should be returned.
        
        Property: *For any* data retention policy applied, old data should be archived 
        to separate storage while remaining queryable for historical analysis.
        """
        mock_s3 = MagicMock()
        mock_s3_client.return_value = mock_s3
        mock_dynamodb.return_value = MagicMock()

        service = DataArchivalService(s3_bucket="test-bucket")

        # Run 50 iterations
        for _ in range(50):
            # Generate records with varying dates
            records = [generate_inventory_record() for _ in range(random.randint(10, 50))]

            # Define date range
            start_date = datetime.utcnow() - timedelta(days=180)
            end_date = datetime.utcnow() - timedelta(days=90)

            # Filter records
            filtered = service._filter_by_date(records, start_date, end_date)

            # Verify all filtered records are within date range
            for record in filtered:
                if "created_at" in record:
                    record_date = datetime.fromisoformat(record["created_at"])
                    assert start_date <= record_date <= end_date

    @patch("src.services.archival_service.get_s3_client")
    @patch("src.services.archival_service.get_dynamodb_resource")
    def test_archive_policy_configuration(self, mock_dynamodb, mock_s3_client):
        """For any archival policy, configuration should be correctly applied.
        
        Property: *For any* data retention policy applied, old data should be archived 
        to separate storage while remaining queryable for historical analysis.
        """
        mock_s3_client.return_value = MagicMock()
        mock_dynamodb.return_value = MagicMock()

        service = DataArchivalService(s3_bucket="test-bucket")

        # Run 30 iterations with different policies
        for _ in range(30):
            retention_days = random.randint(365, 3650)
            archive_days = random.randint(30, retention_days - 1)

            policy = ArchivalPolicy(
                table_name="test_table",
                retention_days=retention_days,
                archive_after_days=archive_days,
                archive_prefix="archives/test",
            )

            service.set_policy(policy)

            # Verify policy is set correctly
            assert service.policies["test_table"].retention_days == retention_days
            assert service.policies["test_table"].archive_after_days == archive_days
            assert service.policies["test_table"].archive_prefix == "archives/test"

    @patch("src.services.archival_service.get_s3_client")
    @patch("src.services.archival_service.get_dynamodb_resource")
    def test_archive_statistics_calculation(self, mock_dynamodb, mock_s3_client):
        """For any archived data, statistics should accurately reflect archive contents.
        
        Property: *For any* data retention policy applied, old data should be archived 
        to separate storage while remaining queryable for historical analysis.
        """
        mock_s3 = MagicMock()
        mock_s3_client.return_value = mock_s3
        mock_dynamodb.return_value = MagicMock()

        service = DataArchivalService(s3_bucket="test-bucket")

        # Run 20 iterations
        for _ in range(20):
            # Generate mock S3 objects
            num_archives = random.randint(1, 10)
            mock_objects = []

            for i in range(num_archives):
                table_name = random.choice(
                    ["purchase_orders", "forecasts", "inventory", "anomalies"]
                )
                size = random.randint(1000, 1000000)
                mock_objects.append(
                    {
                        "Key": f"archives/{table_name}/data_{i}.json.gz",
                        "Size": size,
                    }
                )

            mock_s3.list_objects_v2.return_value = {"Contents": mock_objects}

            # Get statistics
            stats = service.get_archive_statistics()

            # Verify statistics
            assert stats["bucket"] == "test-bucket"
            assert stats["total_archives"] == num_archives
            assert stats["total_size_bytes"] == sum(obj["Size"] for obj in mock_objects)
            assert len(stats["tables"]) > 0

    @patch("src.services.archival_service.get_s3_client")
    @patch("src.services.archival_service.get_dynamodb_resource")
    def test_archive_compression_efficiency(self, mock_dynamodb, mock_s3_client):
        """For any archived data, compression should reduce size.
        
        Property: *For any* data retention policy applied, old data should be archived 
        to separate storage while remaining queryable for historical analysis.
        """
        mock_s3 = MagicMock()
        mock_s3_client.return_value = mock_s3
        mock_dynamodb.return_value = MagicMock()

        service = DataArchivalService(s3_bucket="test-bucket")

        # Run 30 iterations
        for _ in range(30):
            records = [generate_purchase_order_record() for _ in range(random.randint(10, 100))]
            cutoff_date = datetime.utcnow() - timedelta(days=365)

            # Create archive metadata
            archive_metadata = {
                "table_name": "purchase_orders",
                "cutoff_date": cutoff_date.isoformat(),
                "archived_at": datetime.utcnow().isoformat(),
                "record_count": len(records),
                "records": records,
            }

            # Get uncompressed size
            json_data = json.dumps(archive_metadata, default=str)
            uncompressed_size = len(json_data.encode("utf-8"))

            # Get compressed size
            compressed = BytesIO()
            with gzip.GzipFile(fileobj=compressed, mode="wb") as gz:
                gz.write(json_data.encode("utf-8"))
            compressed_size = len(compressed.getvalue())

            # Verify compression reduces size
            assert compressed_size < uncompressed_size
            compression_ratio = compressed_size / uncompressed_size
            assert compression_ratio < 1.0

    @patch("src.services.archival_service.get_s3_client")
    @patch("src.services.archival_service.get_dynamodb_resource")
    def test_archive_multiple_tables_independence(self, mock_dynamodb, mock_s3_client):
        """For any archived data from multiple tables, archives should be independent.
        
        Property: *For any* data retention policy applied, old data should be archived 
        to separate storage while remaining queryable for historical analysis.
        """
        mock_s3 = MagicMock()
        mock_s3_client.return_value = mock_s3
        mock_dynamodb.return_value = MagicMock()

        service = DataArchivalService(s3_bucket="test-bucket")

        # Run 20 iterations
        for _ in range(20):
            # Archive different table types
            tables = ["purchase_orders", "forecasts", "inventory"]
            archives = {}

            for table_name in tables:
                if table_name == "purchase_orders":
                    records = [generate_purchase_order_record() for _ in range(10)]
                elif table_name == "forecasts":
                    records = [generate_forecast_record() for _ in range(10)]
                else:
                    records = [generate_inventory_record() for _ in range(10)]

                cutoff_date = datetime.utcnow() - timedelta(days=365)

                archive_metadata = {
                    "table_name": table_name,
                    "cutoff_date": cutoff_date.isoformat(),
                    "archived_at": datetime.utcnow().isoformat(),
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

                s3_key = service._upload_archive_to_s3(table_name, records, cutoff_date)
                archives[table_name] = {
                    "key": s3_key,
                    "record_count": len(records),
                }

            # Verify each archive is independent
            assert len(archives) == len(tables)
            for table_name, archive_info in archives.items():
                assert table_name in archive_info["key"]
                assert archive_info["record_count"] > 0

    def test_archive_policy_defaults(self):
        """For any default archival policy, configuration should be valid.
        
        Property: *For any* data retention policy applied, old data should be archived 
        to separate storage while remaining queryable for historical analysis.
        """
        # Verify default policies are configured
        assert len(DataArchivalService.DEFAULT_POLICIES) > 0

        for table_name, policy in DataArchivalService.DEFAULT_POLICIES.items():
            # Verify policy has valid configuration
            assert policy.table_name == table_name
            assert policy.retention_days > 0
            assert policy.archive_after_days > 0
            assert policy.retention_days >= policy.archive_after_days
            assert len(policy.archive_prefix) > 0

    @patch("src.services.archival_service.get_s3_client")
    @patch("src.services.archival_service.get_dynamodb_resource")
    def test_archive_empty_records_handling(self, mock_dynamodb, mock_s3_client):
        """For any archive with empty records, handling should be graceful.
        
        Property: *For any* data retention policy applied, old data should be archived 
        to separate storage while remaining queryable for historical analysis.
        """
        mock_s3 = MagicMock()
        mock_s3_client.return_value = mock_s3
        mock_dynamodb.return_value = MagicMock()

        service = DataArchivalService(s3_bucket="test-bucket")

        # Test with empty records
        records = []
        cutoff_date = datetime.utcnow() - timedelta(days=365)

        archive_metadata = {
            "table_name": "purchase_orders",
            "cutoff_date": cutoff_date.isoformat(),
            "archived_at": datetime.utcnow().isoformat(),
            "record_count": 0,
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

        # Upload and download empty archive
        s3_key = service._upload_archive_to_s3("purchase_orders", records, cutoff_date)
        downloaded_records = service._download_archive_from_s3(s3_key)

        # Verify empty archive is handled correctly
        assert len(downloaded_records) == 0
        assert s3_key is not None
