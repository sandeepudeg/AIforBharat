"""Inventory data model and validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator


class Inventory(BaseModel):
    """Inventory model."""

    inventory_id: str = Field(..., description="Unique inventory record identifier")
    sku: str = Field(..., description="Stock Keeping Unit")
    warehouse_id: str = Field(..., description="Warehouse identifier")
    quantity_on_hand: int = Field(..., ge=0, description="Quantity physically in warehouse")
    quantity_reserved: int = Field(default=0, ge=0, description="Quantity reserved for orders")
    quantity_available: int = Field(default=0, ge=0, description="Quantity available for sale")
    reorder_point: int = Field(default=0, ge=0, description="Reorder point for this SKU")
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    last_counted: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "inventory_id": "INV-001",
                "sku": "PROD-001",
                "warehouse_id": "WH-001",
                "quantity_on_hand": 500,
                "quantity_reserved": 100,
                "quantity_available": 400,
                "reorder_point": 100,
            }
        }

    @validator("inventory_id")
    def validate_inventory_id(cls, v):
        """Validate inventory ID."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Inventory ID cannot be empty")
        return v.strip()

    @validator("sku")
    def validate_sku(cls, v):
        """Validate SKU."""
        if not v or len(v.strip()) == 0:
            raise ValueError("SKU cannot be empty")
        return v.strip()

    @validator("warehouse_id")
    def validate_warehouse_id(cls, v):
        """Validate warehouse ID."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Warehouse ID cannot be empty")
        return v.strip()

    @validator("quantity_available", always=True)
    def calculate_available(cls, v, values):
        """Calculate available quantity as on_hand - reserved."""
        if "quantity_on_hand" in values and "quantity_reserved" in values:
            return values["quantity_on_hand"] - values["quantity_reserved"]
        return v


class InventoryValidator:
    """Validator for Inventory model."""

    @staticmethod
    def validate(data: dict) -> Inventory:
        """Validate and create an Inventory instance."""
        return Inventory(**data)

    @staticmethod
    def validate_batch(data_list: list) -> list:
        """Validate and create multiple Inventory instances."""
        return [Inventory(**data) for data in data_list]
