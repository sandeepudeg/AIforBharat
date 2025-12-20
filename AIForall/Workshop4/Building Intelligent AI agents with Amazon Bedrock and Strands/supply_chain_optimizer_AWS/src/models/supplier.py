"""Supplier data model and validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator, EmailStr


class Supplier(BaseModel):
    """Supplier model."""

    supplier_id: str = Field(..., description="Unique supplier identifier")
    name: str = Field(..., description="Supplier name")
    contact_email: str = Field(..., description="Contact email address")
    contact_phone: str = Field(..., description="Contact phone number")
    lead_time_days: int = Field(..., ge=0, description="Average lead time in days")
    reliability_score: float = Field(default=0.0, ge=0, le=100, description="Reliability score 0-100")
    average_delivery_days: float = Field(default=0.0, ge=0, description="Average delivery time in days")
    price_competitiveness: float = Field(default=0.0, ge=0, le=100, description="Price competitiveness score 0-100")
    last_order_date: Optional[datetime] = Field(default=None, description="Date of last order")
    total_orders: int = Field(default=0, ge=0, description="Total number of orders")
    on_time_delivery_rate: float = Field(default=0.0, ge=0, le=1, description="On-time delivery rate 0-1")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "supplier_id": "SUP-001",
                "name": "Acme Supplies",
                "contact_email": "contact@acme.com",
                "contact_phone": "+1-555-0100",
                "lead_time_days": 7,
                "reliability_score": 95.0,
                "average_delivery_days": 6.5,
                "price_competitiveness": 85.0,
                "total_orders": 50,
                "on_time_delivery_rate": 0.95,
            }
        }

    @validator("supplier_id")
    def validate_supplier_id(cls, v):
        """Validate supplier ID."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Supplier ID cannot be empty")
        return v.strip()

    @validator("name")
    def validate_name(cls, v):
        """Validate supplier name."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Supplier name cannot be empty")
        if len(v) > 255:
            raise ValueError("Supplier name cannot exceed 255 characters")
        return v.strip()

    @validator("contact_email")
    def validate_email(cls, v):
        """Validate email format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Contact email cannot be empty")
        if "@" not in v:
            raise ValueError("Invalid email format")
        return v.strip()

    @validator("contact_phone")
    def validate_phone(cls, v):
        """Validate phone number."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Contact phone cannot be empty")
        return v.strip()


class SupplierValidator:
    """Validator for Supplier model."""

    @staticmethod
    def validate(data: dict) -> Supplier:
        """Validate and create a Supplier instance."""
        return Supplier(**data)

    @staticmethod
    def validate_batch(data_list: list) -> list:
        """Validate and create multiple Supplier instances."""
        return [Supplier(**data) for data in data_list]
