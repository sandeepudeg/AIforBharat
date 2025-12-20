"""Product data model and validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator


class Product(BaseModel):
    """Product model."""

    sku: str = Field(..., description="Stock Keeping Unit - unique identifier")
    name: str = Field(..., description="Product name")
    category: str = Field(..., description="Product category")
    unit_cost: float = Field(..., gt=0, description="Cost per unit")
    holding_cost_per_unit: float = Field(..., ge=0, description="Annual holding cost per unit")
    ordering_cost: float = Field(..., ge=0, description="Cost per order")
    lead_time_days: int = Field(..., ge=0, description="Lead time in days")
    supplier_id: str = Field(..., description="Primary supplier ID")
    reorder_point: int = Field(default=0, ge=0, description="Reorder point quantity")
    safety_stock: int = Field(default=0, ge=0, description="Safety stock quantity")
    economic_order_quantity: int = Field(default=0, ge=0, description="Economic order quantity")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "sku": "PROD-001",
                "name": "Widget A",
                "category": "Electronics",
                "unit_cost": 10.50,
                "holding_cost_per_unit": 2.10,
                "ordering_cost": 50.00,
                "lead_time_days": 7,
                "supplier_id": "SUP-001",
                "reorder_point": 100,
                "safety_stock": 50,
                "economic_order_quantity": 200,
            }
        }

    @validator("sku")
    def validate_sku(cls, v):
        """Validate SKU format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("SKU cannot be empty")
        if len(v) > 50:
            raise ValueError("SKU cannot exceed 50 characters")
        return v.strip()

    @validator("name")
    def validate_name(cls, v):
        """Validate product name."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Product name cannot be empty")
        if len(v) > 255:
            raise ValueError("Product name cannot exceed 255 characters")
        return v.strip()

    @validator("category")
    def validate_category(cls, v):
        """Validate category."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Category cannot be empty")
        if len(v) > 100:
            raise ValueError("Category cannot exceed 100 characters")
        return v.strip()

    @validator("supplier_id")
    def validate_supplier_id(cls, v):
        """Validate supplier ID."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Supplier ID cannot be empty")
        return v.strip()


class ProductValidator:
    """Validator for Product model."""

    @staticmethod
    def validate(data: dict) -> Product:
        """Validate and create a Product instance."""
        return Product(**data)

    @staticmethod
    def validate_batch(data_list: list) -> list:
        """Validate and create multiple Product instances."""
        return [Product(**data) for data in data_list]
