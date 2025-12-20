"""Purchase Order data model and validation."""

from datetime import datetime, date
from typing import Optional
from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator


class POStatus(str, Enum):
    """Purchase Order status enum."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class PurchaseOrder(BaseModel):
    """Purchase Order model."""

    po_id: str = Field(..., description="Unique purchase order identifier")
    sku: str = Field(..., description="Stock Keeping Unit")
    supplier_id: str = Field(..., description="Supplier identifier")
    quantity: int = Field(..., gt=0, description="Order quantity")
    unit_price: float = Field(..., gt=0, description="Price per unit")
    total_cost: float = Field(default=0.0, ge=0, description="Total order cost")
    order_date: datetime = Field(default_factory=datetime.utcnow)
    expected_delivery_date: date = Field(..., description="Expected delivery date")
    actual_delivery_date: Optional[date] = Field(default=None, description="Actual delivery date")
    status: POStatus = Field(default=POStatus.PENDING, description="Order status")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "po_id": "PO-001",
                "sku": "PROD-001",
                "supplier_id": "SUP-001",
                "quantity": 100,
                "unit_price": 10.50,
                "total_cost": 1050.00,
                "expected_delivery_date": "2024-01-15",
                "status": "pending",
            }
        }

    @field_validator("po_id")
    @classmethod
    def validate_po_id(cls, v):
        """Validate PO ID."""
        if not v or len(v.strip()) == 0:
            raise ValueError("PO ID cannot be empty")
        return v.strip()

    @field_validator("sku")
    @classmethod
    def validate_sku(cls, v):
        """Validate SKU."""
        if not v or len(v.strip()) == 0:
            raise ValueError("SKU cannot be empty")
        return v.strip()

    @field_validator("supplier_id")
    @classmethod
    def validate_supplier_id(cls, v):
        """Validate supplier ID."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Supplier ID cannot be empty")
        return v.strip()

    @model_validator(mode="after")
    def calculate_total_cost(self):
        """Calculate total cost as quantity * unit_price."""
        if self.quantity and self.unit_price:
            self.total_cost = self.quantity * self.unit_price
        return self


class PurchaseOrderValidator:
    """Validator for PurchaseOrder model."""

    @staticmethod
    def validate(data: dict) -> PurchaseOrder:
        """Validate and create a PurchaseOrder instance."""
        return PurchaseOrder(**data)

    @staticmethod
    def validate_batch(data_list: list) -> list:
        """Validate and create multiple PurchaseOrder instances."""
        return [PurchaseOrder(**data) for data in data_list]
