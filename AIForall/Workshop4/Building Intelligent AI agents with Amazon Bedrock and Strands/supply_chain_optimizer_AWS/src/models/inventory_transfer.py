"""Inventory Transfer data model and validation."""

from datetime import datetime
from typing import Optional
from enum import Enum

from pydantic import BaseModel, Field, validator


class TransferStatus(str, Enum):
    """Inventory transfer status."""

    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class InventoryTransfer(BaseModel):
    """Inventory Transfer model."""

    transfer_id: str = Field(..., description="Unique transfer identifier")
    sku: str = Field(..., description="Stock Keeping Unit")
    source_warehouse_id: str = Field(..., description="Source warehouse identifier")
    destination_warehouse_id: str = Field(..., description="Destination warehouse identifier")
    quantity: int = Field(..., ge=1, description="Quantity to transfer")
    status: TransferStatus = Field(
        default=TransferStatus.PENDING, description="Transfer status"
    )
    transfer_cost: float = Field(default=0.0, ge=0, description="Total transfer cost")
    initiated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None, description="Completion timestamp")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "transfer_id": "TRF-001",
                "sku": "PROD-001",
                "source_warehouse_id": "WH-001",
                "destination_warehouse_id": "WH-002",
                "quantity": 100,
                "status": "pending",
                "transfer_cost": 50.0,
            }
        }

    @validator("transfer_id")
    def validate_transfer_id(cls, v):
        """Validate transfer ID."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Transfer ID cannot be empty")
        return v.strip()

    @validator("sku")
    def validate_sku(cls, v):
        """Validate SKU."""
        if not v or len(v.strip()) == 0:
            raise ValueError("SKU cannot be empty")
        return v.strip()

    @validator("source_warehouse_id")
    def validate_source_warehouse_id(cls, v):
        """Validate source warehouse ID."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Source warehouse ID cannot be empty")
        return v.strip()

    @validator("destination_warehouse_id")
    def validate_destination_warehouse_id(cls, v, values):
        """Validate destination warehouse ID."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Destination warehouse ID cannot be empty")
        if "source_warehouse_id" in values:
            if v.strip() == values["source_warehouse_id"]:
                raise ValueError("Source and destination warehouses cannot be the same")
        return v.strip()


class InventoryTransferValidator:
    """Validator for InventoryTransfer model."""

    @staticmethod
    def validate(data: dict) -> InventoryTransfer:
        """Validate and create an InventoryTransfer instance."""
        return InventoryTransfer(**data)

    @staticmethod
    def validate_batch(data_list: list) -> list:
        """Validate and create multiple InventoryTransfer instances."""
        return [InventoryTransfer(**data) for data in data_list]
