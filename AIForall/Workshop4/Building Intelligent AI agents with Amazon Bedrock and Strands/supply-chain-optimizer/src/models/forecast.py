"""Forecast data model and validation."""

from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, Field, validator


class Forecast(BaseModel):
    """Forecast model."""

    forecast_id: str = Field(..., description="Unique forecast identifier")
    sku: str = Field(..., description="Stock Keeping Unit")
    forecast_date: date = Field(..., description="Date forecast was generated")
    forecast_period: str = Field(..., description="Period covered by forecast (e.g., 2024-01-01 to 2024-01-30)")
    forecasted_demand: int = Field(..., ge=0, description="Forecasted demand quantity")
    confidence_80: float = Field(..., ge=0, description="80% confidence interval")
    confidence_95: float = Field(..., ge=0, description="95% confidence interval")
    actual_demand: Optional[int] = Field(default=None, ge=0, description="Actual demand after period ends")
    accuracy_percentage: Optional[float] = Field(default=None, ge=0, le=100, description="Forecast accuracy percentage")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "forecast_id": "FCST-001",
                "sku": "PROD-001",
                "forecast_date": "2024-01-01",
                "forecast_period": "2024-01-01 to 2024-01-30",
                "forecasted_demand": 1000,
                "confidence_80": 950,
                "confidence_95": 900,
                "actual_demand": None,
                "accuracy_percentage": None,
            }
        }

    @validator("forecast_id")
    def validate_forecast_id(cls, v):
        """Validate forecast ID."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Forecast ID cannot be empty")
        return v.strip()

    @validator("sku")
    def validate_sku(cls, v):
        """Validate SKU."""
        if not v or len(v.strip()) == 0:
            raise ValueError("SKU cannot be empty")
        return v.strip()

    @validator("forecast_period")
    def validate_forecast_period(cls, v):
        """Validate forecast period."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Forecast period cannot be empty")
        return v.strip()

    @validator("confidence_95")
    def validate_confidence_intervals(cls, v, values):
        """Validate that confidence intervals are in correct order."""
        if "confidence_80" in values:
            if v > values["confidence_80"]:
                raise ValueError("95% confidence interval must be <= 80% confidence interval")
        return v


class ForecastValidator:
    """Validator for Forecast model."""

    @staticmethod
    def validate(data: dict) -> Forecast:
        """Validate and create a Forecast instance."""
        return Forecast(**data)

    @staticmethod
    def validate_batch(data_list: list) -> list:
        """Validate and create multiple Forecast instances."""
        return [Forecast(**data) for data in data_list]
