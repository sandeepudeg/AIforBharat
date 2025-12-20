"""Anomaly data model and validation."""

from datetime import datetime
from typing import Optional
from enum import Enum

from pydantic import BaseModel, Field, validator


class AnomalyType(str, Enum):
    """Anomaly type enum."""

    INVENTORY_DEVIATION = "inventory_deviation"
    SUPPLIER_DELAY = "supplier_delay"
    DEMAND_SPIKE = "demand_spike"
    INVENTORY_SHRINKAGE = "inventory_shrinkage"


class SeverityLevel(str, Enum):
    """Severity level enum."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnomalyStatus(str, Enum):
    """Anomaly status enum."""

    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"


class Anomaly(BaseModel):
    """Anomaly model."""

    anomaly_id: str = Field(..., description="Unique anomaly identifier")
    anomaly_type: AnomalyType = Field(..., description="Type of anomaly")
    sku: str = Field(..., description="Stock Keeping Unit")
    warehouse_id: Optional[str] = Field(default=None, description="Warehouse identifier if applicable")
    severity: SeverityLevel = Field(..., description="Severity level")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence score 0-1")
    description: str = Field(..., description="Anomaly description")
    root_cause: Optional[str] = Field(default=None, description="Root cause analysis")
    recommended_action: Optional[str] = Field(default=None, description="Recommended action")
    status: AnomalyStatus = Field(default=AnomalyStatus.OPEN, description="Anomaly status")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = Field(default=None, description="Resolution timestamp")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "anomaly_id": "ANM-001",
                "anomaly_type": "inventory_deviation",
                "sku": "PROD-001",
                "warehouse_id": "WH-001",
                "severity": "high",
                "confidence_score": 0.95,
                "description": "Inventory level 30% below forecast",
                "root_cause": "Unexpected demand spike",
                "recommended_action": "Emergency procurement",
                "status": "open",
            }
        }

    @validator("anomaly_id")
    def validate_anomaly_id(cls, v):
        """Validate anomaly ID."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Anomaly ID cannot be empty")
        return v.strip()

    @validator("sku")
    def validate_sku(cls, v):
        """Validate SKU."""
        if not v or len(v.strip()) == 0:
            raise ValueError("SKU cannot be empty")
        return v.strip()

    @validator("description")
    def validate_description(cls, v):
        """Validate description."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Description cannot be empty")
        if len(v) > 1000:
            raise ValueError("Description cannot exceed 1000 characters")
        return v.strip()


class AnomalyValidator:
    """Validator for Anomaly model."""

    @staticmethod
    def validate(data: dict) -> Anomaly:
        """Validate and create an Anomaly instance."""
        return Anomaly(**data)

    @staticmethod
    def validate_batch(data_list: list) -> list:
        """Validate and create multiple Anomaly instances."""
        return [Anomaly(**data) for data in data_list]
