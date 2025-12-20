"""Warehouse data model and validation."""

from datetime import datetime
from typing import Optional
from enum import Enum

from pydantic import BaseModel, Field, validator


class WarehouseStatus(str, Enum):
    """Warehouse operational status."""

    OPERATIONAL = "operational"
    DISRUPTED = "disrupted"
    MAINTENANCE = "maintenance"
    CLOSED = "closed"


class Warehouse(BaseModel):
    """Warehouse model."""

    warehouse_id: str = Field(..., description="Unique warehouse identifier")
    name: str = Field(..., description="Warehouse name")
    location: str = Field(..., description="Warehouse location/region")
    capacity: int = Field(..., ge=0, description="Maximum warehouse capacity")
    current_inventory: int = Field(default=0, ge=0, description="Current total inventory")
    status: WarehouseStatus = Field(
        default=WarehouseStatus.OPERATIONAL, description="Warehouse operational status"
    )
    holding_cost_per_unit: float = Field(
        default=1.0, ge=0, description="Holding cost per unit per year"
    )
    transfer_cost_per_unit: float = Field(
        default=0.5, ge=0, description="Cost to transfer one unit to another warehouse"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "warehouse_id": "WH-001",
                "name": "Central Warehouse",
                "location": "New York",
                "capacity": 10000,
                "current_inventory": 5000,
                "status": "operational",
                "holding_cost_per_unit": 1.0,
                "transfer_cost_per_unit": 0.5,
            }
        }

    @validator("warehouse_id")
    def validate_warehouse_id(cls, v):
        """Validate warehouse ID."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Warehouse ID cannot be empty")
        return v.strip()

    @validator("name")
    def validate_name(cls, v):
        """Validate warehouse name."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Warehouse name cannot be empty")
        return v.strip()

    @validator("location")
    def validate_location(cls, v):
        """Validate warehouse location."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Warehouse location cannot be empty")
        return v.strip()

    @validator("current_inventory")
    def validate_current_inventory(cls, v, values):
        """Validate current inventory does not exceed capacity."""
        if "capacity" in values and v > values["capacity"]:
            raise ValueError("Current inventory cannot exceed warehouse capacity")
        return v


class WarehouseValidator:
    """Validator for Warehouse model."""

    @staticmethod
    def validate(data: dict) -> Warehouse:
        """Validate and create a Warehouse instance."""
        return Warehouse(**data)

    @staticmethod
    def validate_batch(data_list: list) -> list:
        """Validate and create multiple Warehouse instances."""
        return [Warehouse(**data) for data in data_list]
