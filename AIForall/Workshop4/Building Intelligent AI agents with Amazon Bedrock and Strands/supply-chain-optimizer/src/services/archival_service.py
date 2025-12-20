"""Data archival and retention policy service.

This module handles archiving old records to S3 and enforcing retention policies.
"""

import json
import gzip
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from io import BytesIO

from src.config import config, logger
from src.aws.clients import get_s3_client, get_dynamodb_resource
from src.database.connection import get_rds_session
from src.database.schema import PurchaseOrderTable, ProductTable, SupplierTable


class ArchivalPolicy:
    """Configuration for data archival policies."""

    def __init__(
        self,
        table_name: str,
        retention_days: int,
        archive_after_days: int,
        archive_prefix: str,
    ):
        """Initialize archival policy.
        
        Args:
            table_name: Name of the table to archive
            retention_days: Days to keep data before deletion
            archive_after_days: Days before archiving to S3
            archive_prefix: S3 prefix for archived data
        """
        self.table_name = table_name
        self.retention_days = retention_days
        self.archive_after_days = archive_after_days
        self.archive_prefix = archive_prefix


class DataArchivalService:
    """Service for archiving and managing data retention policies."""

    # Default archival policies
    DEFAULT_POLICIES = {
        "purchase_orders": ArchivalPolicy(
            table_name="purchase_orders",
            retention_days=2555,  # 7 years
            archive_after_days=365,  # 1 year
            archive_prefix="archives/purchase_orders",
        ),
        "products": ArchivalPolicy(
            table_name="products",
            retention_days=3650,  # 10 years
            archive_after_days=1825,  # 5 years
            archive_prefix="archives/products",
        ),
        "suppliers": ArchivalPolicy(
            table_name="suppliers",
            retention_days=3650,  # 10 years
            archive_after_days=1825,  # 5 years
            archive_prefix="archives/suppliers",
        ),
        "forecasts": ArchivalPolicy(
            table_name="forecasts",
            retention_days=730,  # 2 years
            archive_after_days=90,  # 3 months
            archive_prefix="archives/forecasts",
        ),
        "inventory": ArchivalPolicy(
            table_name="inventory",
            retention_days=730,  # 2 years
            archive_after_days=90,  # 3 months
            archive_prefix="archives/inventory",
        ),
        "anomalies": ArchivalPolicy(
            table_name="anomalies",
            retention_days=1095,  # 3 years
            archive_after_days=180,  # 6 months
            archive_prefix="archives/anomalies",
        ),
    }

    def __init__(self, s3_bucket: Optional[str] = None):
        """Initialize archival service.
        
        Args:
            s3_bucket: S3 bucket name for archives (uses config if not provided)
        """
        self.s3_bucket = s3_bucket or config.s3.bucket_name
        self.s3_client = get_s3_client()
        self.dynamodb = get_dynamodb_resource()
        self.policies = self.DEFAULT_POLICIES.copy()

    def set_policy(self, policy: ArchivalPolicy) -> None:
        """Set or override an archival policy.
        
        Args:
            policy: ArchivalPolicy instance
        """
        self.policies[policy.table_name] = policy
        logger.info(f"Archival policy set for {policy.table_name}")

    def archive_rds_table(
        self,
        table_name: str,
        cutoff_date: datetime,
        batch_size: int = 1000,
    ) -> Dict[str, Any]:
        """Archive old records from RDS table to S3.
        
        Args:
            table_name: Name of RDS table to archive
            cutoff_date: Archive records older than this date
            batch_size: Number of records to process per batch
            
        Returns:
            Dictionary with archival statistics
        """
        try:
            session = get_rds_session()
            archived_count = 0
            deleted_count = 0
            archive_key = None

            if table_name == "purchase_orders":
                # Query old purchase orders
                old_records = (
                    session.query(PurchaseOrderTable)
                    .filter(PurchaseOrderTable.created_at < cutoff_date)
                    .all()
                )

                if old_records:
                    # Convert to JSON-serializable format
                    records_data = [
                        {
                            "po_id": r.po_id,
                            "sku": r.sku,
                            "supplier_id": r.supplier_id,
                            "quantity": r.quantity,
                            "unit_price": r.unit_price,
                            "total_cost": r.total_cost,
                            "order_date": r.order_date.isoformat() if r.order_date else None,
                            "expected_delivery_date": r.expected_delivery_date.isoformat()
                            if r.expected_delivery_date
                            else None,
                            "actual_delivery_date": r.actual_delivery_date.isoformat()
                            if r.actual_delivery_date
                            else None,
                            "status": r.status,
                            "created_at": r.created_at.isoformat() if r.created_at else None,
                            "updated_at": r.updated_at.isoformat() if r.updated_at else None,
                        }
                        for r in old_records
                    ]

                    # Upload to S3
                    archive_key = self._upload_archive_to_s3(
                        table_name, records_data, cutoff_date
                    )
                    archived_count = len(records_data)

                    # Delete archived records from RDS
                    for record in old_records:
                        session.delete(record)
                    session.commit()
                    deleted_count = len(old_records)

            elif table_name == "products":
                old_records = (
                    session.query(ProductTable)
                    .filter(ProductTable.created_at < cutoff_date)
                    .all()
                )

                if old_records:
                    records_data = [
                        {
                            "sku": r.sku,
                            "name": r.name,
                            "category": r.category,
                            "unit_cost": r.unit_cost,
                            "holding_cost_per_unit": r.holding_cost_per_unit,
                            "ordering_cost": r.ordering_cost,
                            "lead_time_days": r.lead_time_days,
                            "supplier_id": r.supplier_id,
                            "reorder_point": r.reorder_point,
                            "safety_stock": r.safety_stock,
                            "economic_order_quantity": r.economic_order_quantity,
                            "created_at": r.created_at.isoformat() if r.created_at else None,
                            "updated_at": r.updated_at.isoformat() if r.updated_at else None,
                        }
                        for r in old_records
                    ]

                    archive_key = self._upload_archive_to_s3(
                        table_name, records_data, cutoff_date
                    )
                    archived_count = len(records_data)

                    for record in old_records:
                        session.delete(record)
                    session.commit()
                    deleted_count = len(old_records)

            elif table_name == "suppliers":
                old_records = (
                    session.query(SupplierTable)
                    .filter(SupplierTable.created_at < cutoff_date)
                    .all()
                )

                if old_records:
                    records_data = [
                        {
                            "supplier_id": r.supplier_id,
                            "name": r.name,
                            "contact_email": r.contact_email,
                            "contact_phone": r.contact_phone,
                            "lead_time_days": r.lead_time_days,
                            "reliability_score": r.reliability_score,
                            "average_delivery_days": r.average_delivery_days,
                            "price_competitiveness": r.price_competitiveness,
                            "last_order_date": r.last_order_date.isoformat()
                            if r.last_order_date
                            else None,
                            "total_orders": r.total_orders,
                            "on_time_delivery_rate": r.on_time_delivery_rate,
                            "created_at": r.created_at.isoformat() if r.created_at else None,
                            "updated_at": r.updated_at.isoformat() if r.updated_at else None,
                        }
                        for r in old_records
                    ]

                    archive_key = self._upload_archive_to_s3(
                        table_name, records_data, cutoff_date
                    )
                    archived_count = len(records_data)

                    for record in old_records:
                        session.delete(record)
                    session.commit()
                    deleted_count = len(old_records)

            session.close()

            result = {
                "table_name": table_name,
                "archived_count": archived_count,
                "deleted_count": deleted_count,
                "archive_key": archive_key,
                "cutoff_date": cutoff_date.isoformat(),
                "timestamp": datetime.utcnow().isoformat(),
            }

            logger.info(
                f"Archived {archived_count} records from {table_name} to {archive_key}"
            )
            return result

        except Exception as e:
            logger.error(f"Failed to archive RDS table {table_name}: {str(e)}")
            raise

    def archive_dynamodb_table(
        self,
        table_name: str,
        cutoff_date: datetime,
        batch_size: int = 100,
    ) -> Dict[str, Any]:
        """Archive old records from DynamoDB table to S3.
        
        Args:
            table_name: Name of DynamoDB table to archive
            cutoff_date: Archive records older than this date
            batch_size: Number of records to process per batch
            
        Returns:
            Dictionary with archival statistics
        """
        try:
            table = self.dynamodb.Table(table_name)
            archived_records = []
            deleted_count = 0
            archive_key = None

            # Scan table for old records
            response = table.scan()
            items = response.get("Items", [])

            # Filter items older than cutoff date
            for item in items:
                created_at_str = item.get("created_at")
                if created_at_str:
                    try:
                        created_at = datetime.fromisoformat(created_at_str)
                        if created_at < cutoff_date:
                            archived_records.append(item)
                    except (ValueError, TypeError):
                        pass

            # Upload to S3
            if archived_records:
                archive_key = self._upload_archive_to_s3(
                    table_name, archived_records, cutoff_date
                )

                # Delete archived records from DynamoDB
                with table.batch_writer(batch_size=batch_size) as batch:
                    for item in archived_records:
                        # Get the primary key
                        key = {k: item[k] for k in table.key_schema}
                        batch.delete_item(Key=key)
                        deleted_count += 1

            result = {
                "table_name": table_name,
                "archived_count": len(archived_records),
                "deleted_count": deleted_count,
                "archive_key": archive_key,
                "cutoff_date": cutoff_date.isoformat(),
                "timestamp": datetime.utcnow().isoformat(),
            }

            logger.info(
                f"Archived {len(archived_records)} records from DynamoDB {table_name}"
            )
            return result

        except Exception as e:
            logger.error(f"Failed to archive DynamoDB table {table_name}: {str(e)}")
            raise

    def enforce_retention_policy(self, table_name: str) -> Dict[str, Any]:
        """Enforce retention policy for a table.
        
        Args:
            table_name: Name of table to enforce policy on
            
        Returns:
            Dictionary with enforcement statistics
        """
        if table_name not in self.policies:
            raise ValueError(f"No retention policy defined for {table_name}")

        policy = self.policies[table_name]
        now = datetime.utcnow()

        # Calculate cutoff dates
        archive_cutoff = now - timedelta(days=policy.archive_after_days)
        retention_cutoff = now - timedelta(days=policy.retention_days)

        result = {
            "table_name": table_name,
            "policy": {
                "retention_days": policy.retention_days,
                "archive_after_days": policy.archive_after_days,
            },
            "archive_result": None,
            "deletion_result": None,
        }

        try:
            # Archive old records
            if table_name in ["purchase_orders", "products", "suppliers"]:
                archive_result = self.archive_rds_table(table_name, archive_cutoff)
                result["archive_result"] = archive_result
            elif table_name in ["forecasts", "inventory", "anomalies"]:
                archive_result = self.archive_dynamodb_table(table_name, archive_cutoff)
                result["archive_result"] = archive_result

            logger.info(f"Retention policy enforced for {table_name}")
            return result

        except Exception as e:
            logger.error(f"Failed to enforce retention policy for {table_name}: {str(e)}")
            raise

    def query_archive(
        self,
        table_name: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Query archived data from S3.
        
        Args:
            table_name: Name of table to query archives for
            start_date: Start date for filtering (optional)
            end_date: End date for filtering (optional)
            
        Returns:
            List of archived records matching criteria
        """
        try:
            policy = self.policies.get(table_name)
            if not policy:
                raise ValueError(f"No archival policy defined for {table_name}")

            prefix = policy.archive_prefix
            results = []

            # List all archive files for this table
            response = self.s3_client.list_objects_v2(
                Bucket=self.s3_bucket, Prefix=prefix
            )

            if "Contents" not in response:
                return results

            # Process each archive file
            for obj in response["Contents"]:
                key = obj["Key"]

                # Download and decompress archive
                archive_data = self._download_archive_from_s3(key)

                # Filter by date if specified
                if start_date or end_date:
                    archive_data = self._filter_by_date(
                        archive_data, start_date, end_date
                    )

                results.extend(archive_data)

            logger.info(
                f"Retrieved {len(results)} archived records for {table_name}"
            )
            return results

        except Exception as e:
            logger.error(f"Failed to query archive for {table_name}: {str(e)}")
            raise

    def _upload_archive_to_s3(
        self,
        table_name: str,
        records: List[Dict[str, Any]],
        cutoff_date: datetime,
    ) -> str:
        """Upload archive to S3.
        
        Args:
            table_name: Name of table being archived
            records: Records to archive
            cutoff_date: Cutoff date for the archive
            
        Returns:
            S3 key of uploaded archive
        """
        try:
            policy = self.policies.get(table_name)
            if not policy:
                raise ValueError(f"No archival policy defined for {table_name}")

            # Create archive metadata
            archive_metadata = {
                "table_name": table_name,
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
            compressed.seek(0)

            # Generate S3 key
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            s3_key = f"{policy.archive_prefix}/{table_name}_{timestamp}.json.gz"

            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=s3_key,
                Body=compressed.getvalue(),
                ContentType="application/gzip",
                Metadata={
                    "table_name": table_name,
                    "cutoff_date": cutoff_date.isoformat(),
                    "record_count": str(len(records)),
                },
            )

            logger.info(f"Archive uploaded to S3: {s3_key}")
            return s3_key

        except Exception as e:
            logger.error(f"Failed to upload archive to S3: {str(e)}")
            raise

    def _download_archive_from_s3(self, s3_key: str) -> List[Dict[str, Any]]:
        """Download and decompress archive from S3.
        
        Args:
            s3_key: S3 key of archive file
            
        Returns:
            List of records from archive
        """
        try:
            # Download from S3
            response = self.s3_client.get_object(Bucket=self.s3_bucket, Key=s3_key)
            compressed_data = response["Body"].read()

            # Decompress
            with gzip.GzipFile(fileobj=BytesIO(compressed_data), mode="rb") as gz:
                json_data = gz.read().decode("utf-8")

            # Parse JSON
            archive_metadata = json.loads(json_data)
            records = archive_metadata.get("records", [])

            logger.info(f"Downloaded archive from S3: {s3_key}")
            return records

        except Exception as e:
            logger.error(f"Failed to download archive from S3: {str(e)}")
            raise

    def _filter_by_date(
        self,
        records: List[Dict[str, Any]],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Filter records by date range.
        
        Args:
            records: Records to filter
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            Filtered records
        """
        filtered = []

        for record in records:
            # Try to find a date field
            date_field = None
            for field in ["created_at", "updated_at", "order_date", "forecast_date"]:
                if field in record:
                    date_field = record[field]
                    break

            if not date_field:
                filtered.append(record)
                continue

            try:
                record_date = datetime.fromisoformat(date_field)

                if start_date and record_date < start_date:
                    continue
                if end_date and record_date > end_date:
                    continue

                filtered.append(record)
            except (ValueError, TypeError):
                filtered.append(record)

        return filtered

    def get_archive_statistics(self) -> Dict[str, Any]:
        """Get statistics about archived data.
        
        Returns:
            Dictionary with archive statistics
        """
        try:
            stats = {
                "bucket": self.s3_bucket,
                "tables": {},
                "total_archives": 0,
                "total_size_bytes": 0,
            }

            # List all archives
            response = self.s3_client.list_objects_v2(
                Bucket=self.s3_bucket, Prefix="archives/"
            )

            if "Contents" in response:
                for obj in response["Contents"]:
                    key = obj["Key"]
                    size = obj["Size"]

                    # Extract table name from key (e.g., "archives/purchase_orders/data_1.json.gz")
                    parts = key.split("/")
                    if len(parts) >= 2:
                        # Get the second part which is the table name
                        table_name = parts[1]

                        if table_name not in stats["tables"]:
                            stats["tables"][table_name] = {
                                "archive_count": 0,
                                "total_size_bytes": 0,
                            }

                        stats["tables"][table_name]["archive_count"] += 1
                        stats["tables"][table_name]["total_size_bytes"] += size
                        stats["total_archives"] += 1
                        stats["total_size_bytes"] += size

            logger.info("Archive statistics retrieved")
            return stats

        except Exception as e:
            logger.error(f"Failed to get archive statistics: {str(e)}")
            raise
