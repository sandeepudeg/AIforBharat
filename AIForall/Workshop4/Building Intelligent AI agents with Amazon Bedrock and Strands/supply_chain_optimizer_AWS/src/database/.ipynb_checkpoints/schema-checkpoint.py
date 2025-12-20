"""Database schema creation and management."""

from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
    Date,
    Enum,
    Text,
    ForeignKey,
    UniqueConstraint,
    Index,
    MetaData,
    Table,
)
from sqlalchemy.orm import declarative_base
from datetime import datetime

from src.config import logger
from src.database.connection import get_rds_connection, get_dynamodb_connection

Base = declarative_base()


# RDS Table Definitions
class ProductTable(Base):
    """Product table definition."""

    __tablename__ = "products"

    sku = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    unit_cost = Column(Float, nullable=False)
    holding_cost_per_unit = Column(Float, nullable=False)
    ordering_cost = Column(Float, nullable=False)
    lead_time_days = Column(Integer, nullable=False)
    supplier_id = Column(String(50), ForeignKey("suppliers.supplier_id"), nullable=False)
    reorder_point = Column(Integer, default=0)
    safety_stock = Column(Integer, default=0)
    economic_order_quantity = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (Index("idx_products_category", "category"),)


class SupplierTable(Base):
    """Supplier table definition."""

    __tablename__ = "suppliers"

    supplier_id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    contact_email = Column(String(255), nullable=False)
    contact_phone = Column(String(20), nullable=False)
    lead_time_days = Column(Integer, nullable=False)
    reliability_score = Column(Float, default=0.0)
    average_delivery_days = Column(Float, default=0.0)
    price_competitiveness = Column(Float, default=0.0)
    last_order_date = Column(DateTime)
    total_orders = Column(Integer, default=0)
    on_time_delivery_rate = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (Index("idx_suppliers_name", "name"),)

    def dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            "supplier_id": self.supplier_id,
            "name": self.name,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "lead_time_days": self.lead_time_days,
            "reliability_score": self.reliability_score,
            "average_delivery_days": self.average_delivery_days,
            "price_competitiveness": self.price_competitiveness,
            "last_order_date": self.last_order_date.isoformat() if self.last_order_date else None,
            "total_orders": self.total_orders,
            "on_time_delivery_rate": self.on_time_delivery_rate,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class PurchaseOrderTable(Base):
    """Purchase Order table definition."""

    __tablename__ = "purchase_orders"

    po_id = Column(String(50), primary_key=True)
    sku = Column(String(50), ForeignKey("products.sku"), nullable=False)
    supplier_id = Column(String(50), ForeignKey("suppliers.supplier_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    order_date = Column(DateTime, default=datetime.utcnow)
    expected_delivery_date = Column(Date, nullable=False)
    actual_delivery_date = Column(Date)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_purchase_orders_sku", "sku"),
        Index("idx_purchase_orders_supplier", "supplier_id"),
        Index("idx_purchase_orders_status", "status"),
    )

    def dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            "po_id": self.po_id,
            "sku": self.sku,
            "supplier_id": self.supplier_id,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "total_cost": self.total_cost,
            "order_date": self.order_date.isoformat() if self.order_date else None,
            "expected_delivery_date": self.expected_delivery_date.isoformat() if self.expected_delivery_date else None,
            "actual_delivery_date": self.actual_delivery_date.isoformat() if self.actual_delivery_date else None,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ReportTable(Base):
    """Report table definition."""

    __tablename__ = "reports"

    report_id = Column(String(50), primary_key=True)
    report_type = Column(String(20), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    inventory_turnover = Column(Float, nullable=False)
    stockout_rate = Column(Float, nullable=False)
    supplier_performance_score = Column(Float, nullable=False)
    forecast_accuracy = Column(Float, nullable=False)
    cost_savings = Column(Float, default=0.0)
    recommendations = Column(Text, default="[]")
    generated_at = Column(DateTime, default=datetime.utcnow)
    generated_by = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_reports_type", "report_type"),
        Index("idx_reports_period", "period_start", "period_end"),
    )

    def dict(self):
        """Convert to dictionary for JSON serialization."""
        import json
        return {
            "report_id": self.report_id,
            "report_type": self.report_type,
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
            "inventory_turnover": self.inventory_turnover,
            "stockout_rate": self.stockout_rate,
            "supplier_performance_score": self.supplier_performance_score,
            "forecast_accuracy": self.forecast_accuracy,
            "cost_savings": self.cost_savings,
            "recommendations": json.loads(self.recommendations) if self.recommendations else [],
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
            "generated_by": self.generated_by,
        }


class AnomalyTable(Base):
    """Anomaly table definition."""

    __tablename__ = "anomalies"

    anomaly_id = Column(String(50), primary_key=True)
    anomaly_type = Column(String(50), nullable=False)
    sku = Column(String(50), nullable=False)
    warehouse_id = Column(String(50))
    severity = Column(String(20), nullable=False)
    confidence_score = Column(Float, nullable=False)
    description = Column(Text, nullable=False)
    root_cause = Column(Text)
    recommended_action = Column(Text)
    status = Column(String(20), default="open")
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_anomalies_type", "anomaly_type"),
        Index("idx_anomalies_severity", "severity"),
        Index("idx_anomalies_status", "status"),
        Index("idx_anomalies_sku", "sku"),
    )

    def dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            "anomaly_id": self.anomaly_id,
            "anomaly_type": self.anomaly_type,
            "sku": self.sku,
            "warehouse_id": self.warehouse_id,
            "severity": self.severity,
            "confidence_score": self.confidence_score,
            "description": self.description,
            "root_cause": self.root_cause,
            "recommended_action": self.recommended_action,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }


def create_rds_schema() -> None:
    """Create RDS schema and tables."""
    try:
        engine = get_rds_connection()
        Base.metadata.create_all(engine)
        logger.info("RDS schema created successfully")
    except Exception as e:
        logger.error(f"Failed to create RDS schema: {str(e)}")
        raise


def drop_rds_schema() -> None:
    """Drop RDS schema and tables."""
    try:
        engine = get_rds_connection()
        Base.metadata.drop_all(engine)
        logger.info("RDS schema dropped successfully")
    except Exception as e:
        logger.error(f"Failed to drop RDS schema: {str(e)}")
        raise


def create_dynamodb_tables() -> None:
    """Create DynamoDB tables for real-time data."""
    try:
        dynamodb = get_dynamodb_connection()

        # Inventory table
        try:
            dynamodb.create_table(
                TableName="inventory",
                KeySchema=[
                    {"AttributeName": "inventory_id", "KeyType": "HASH"},
                ],
                AttributeDefinitions=[
                    {"AttributeName": "inventory_id", "AttributeType": "S"},
                    {"AttributeName": "sku", "AttributeType": "S"},
                    {"AttributeName": "warehouse_id", "AttributeType": "S"},
                ],
                GlobalSecondaryIndexes=[
                    {
                        "IndexName": "sku-warehouse-index",
                        "KeySchema": [
                            {"AttributeName": "sku", "KeyType": "HASH"},
                            {"AttributeName": "warehouse_id", "KeyType": "RANGE"},
                        ],
                        "Projection": {"ProjectionType": "ALL"},
                        "ProvisionedThroughput": {
                            "ReadCapacityUnits": 5,
                            "WriteCapacityUnits": 5,
                        },
                    }
                ],
                BillingMode="PAY_PER_REQUEST",
            )
            logger.info("Inventory table created successfully")
        except Exception as e:
            if "ResourceInUseException" not in str(e):
                raise
            logger.info("Inventory table already exists")

        # Forecast table
        try:
            dynamodb.create_table(
                TableName="forecasts",
                KeySchema=[
                    {"AttributeName": "forecast_id", "KeyType": "HASH"},
                ],
                AttributeDefinitions=[
                    {"AttributeName": "forecast_id", "AttributeType": "S"},
                    {"AttributeName": "sku", "AttributeType": "S"},
                    {"AttributeName": "forecast_date", "AttributeType": "S"},
                ],
                GlobalSecondaryIndexes=[
                    {
                        "IndexName": "sku-date-index",
                        "KeySchema": [
                            {"AttributeName": "sku", "KeyType": "HASH"},
                            {"AttributeName": "forecast_date", "KeyType": "RANGE"},
                        ],
                        "Projection": {"ProjectionType": "ALL"},
                        "ProvisionedThroughput": {
                            "ReadCapacityUnits": 5,
                            "WriteCapacityUnits": 5,
                        },
                    }
                ],
                BillingMode="PAY_PER_REQUEST",
            )
            logger.info("Forecast table created successfully")
        except Exception as e:
            if "ResourceInUseException" not in str(e):
                raise
            logger.info("Forecast table already exists")

        # Anomaly table
        try:
            dynamodb.create_table(
                TableName="anomalies",
                KeySchema=[
                    {"AttributeName": "anomaly_id", "KeyType": "HASH"},
                ],
                AttributeDefinitions=[
                    {"AttributeName": "anomaly_id", "AttributeType": "S"},
                    {"AttributeName": "sku", "AttributeType": "S"},
                    {"AttributeName": "created_at", "AttributeType": "S"},
                ],
                GlobalSecondaryIndexes=[
                    {
                        "IndexName": "sku-created-index",
                        "KeySchema": [
                            {"AttributeName": "sku", "KeyType": "HASH"},
                            {"AttributeName": "created_at", "KeyType": "RANGE"},
                        ],
                        "Projection": {"ProjectionType": "ALL"},
                        "ProvisionedThroughput": {
                            "ReadCapacityUnits": 5,
                            "WriteCapacityUnits": 5,
                        },
                    }
                ],
                BillingMode="PAY_PER_REQUEST",
            )
            logger.info("Anomaly table created successfully")
        except Exception as e:
            if "ResourceInUseException" not in str(e):
                raise
            logger.info("Anomaly table already exists")

    except Exception as e:
        logger.error(f"Failed to create DynamoDB tables: {str(e)}")
        raise


def drop_dynamodb_tables() -> None:
    """Drop DynamoDB tables."""
    try:
        dynamodb = get_dynamodb_connection()

        for table_name in ["inventory", "forecasts", "anomalies"]:
            try:
                table = dynamodb.Table(table_name)
                table.delete()
                logger.info(f"Table {table_name} deleted successfully")
            except Exception as e:
                if "ResourceNotFoundException" not in str(e):
                    raise
                logger.info(f"Table {table_name} does not exist")

    except Exception as e:
        logger.error(f"Failed to drop DynamoDB tables: {str(e)}")
        raise
