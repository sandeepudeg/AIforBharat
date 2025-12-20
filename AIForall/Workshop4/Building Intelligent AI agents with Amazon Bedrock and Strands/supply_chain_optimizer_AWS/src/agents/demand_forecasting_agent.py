"""Demand Forecasting Agent for Supply Chain Optimizer.

This agent is responsible for:
- Analyzing historical sales data
- Generating demand forecasts with confidence intervals
- Incorporating seasonality and trends
- Adjusting forecasts for external factors
- Storing forecasts in DynamoDB
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal
import uuid
import math
import statistics

from src.config import logger
from src.models.forecast import Forecast
from src.aws.clients import get_dynamodb_resource


class DemandForecastingAgent:
    """Agent for demand forecasting using statistical methods."""

    def __init__(self):
        """Initialize the Demand Forecasting Agent."""
        self.dynamodb = get_dynamodb_resource()
        self.forecasts_table_name = "forecasts"
        self.logger = logger

    def analyze_sales_history(self, sku: str, sales_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze historical sales data for a product.

        Args:
            sku: Stock Keeping Unit identifier
            sales_data: List of historical sales records with 'date' and 'quantity' fields

        Returns:
            Dictionary containing analysis results:
            - mean: Average daily sales
            - std_dev: Standard deviation of sales
            - trend: Linear trend coefficient
            - min_sales: Minimum daily sales
            - max_sales: Maximum daily sales
            - data_points: Number of data points analyzed
        """
        if not sales_data or len(sales_data) == 0:
            self.logger.warning(f"No sales data available for SKU {sku}")
            return {
                "mean": 0,
                "std_dev": 0,
                "trend": 0,
                "min_sales": 0,
                "max_sales": 0,
                "data_points": 0,
            }

        # Extract quantities from sales data
        quantities = [record.get("quantity", 0) for record in sales_data]

        # Calculate basic statistics
        mean = statistics.mean(quantities) if quantities else 0
        std_dev = statistics.stdev(quantities) if len(quantities) > 1 else 0
        min_sales = min(quantities) if quantities else 0
        max_sales = max(quantities) if quantities else 0

        # Calculate trend using simple linear regression
        trend = self._calculate_trend(quantities)

        analysis = {
            "mean": mean,
            "std_dev": std_dev,
            "trend": trend,
            "min_sales": min_sales,
            "max_sales": max_sales,
            "data_points": len(quantities),
        }

        self.logger.info(f"Sales history analysis for SKU {sku}: {analysis}")
        return analysis

    def generate_forecast(
        self,
        sku: str,
        sales_analysis: Dict[str, Any],
        forecast_days: int = 30,
    ) -> Dict[str, Any]:
        """Generate demand forecast using exponential smoothing.

        Args:
            sku: Stock Keeping Unit identifier
            sales_analysis: Analysis results from analyze_sales_history
            forecast_days: Number of days to forecast (default 30)

        Returns:
            Dictionary containing:
            - forecasted_demand: Point forecast for the period
            - confidence_80: 80% confidence interval
            - confidence_95: 95% confidence interval
            - method: Forecasting method used
        """
        mean = sales_analysis.get("mean", 0)
        std_dev = sales_analysis.get("std_dev", 0)
        trend = sales_analysis.get("trend", 0)

        # Calculate point forecast: mean + trend adjustment
        daily_forecast = mean + (trend * forecast_days / 2)
        forecasted_demand = max(0, int(daily_forecast * forecast_days))

        # Calculate confidence intervals using normal distribution
        # 80% CI: ±1.28 * std_dev
        # 95% CI: ±1.96 * std_dev
        total_std_dev = std_dev * math.sqrt(forecast_days)
        confidence_80 = max(0, int(forecasted_demand - (1.28 * total_std_dev)))
        confidence_95 = max(0, int(forecasted_demand - (1.96 * total_std_dev)))

        forecast_result = {
            "forecasted_demand": forecasted_demand,
            "confidence_80": float(confidence_80),
            "confidence_95": float(confidence_95),
            "method": "exponential_smoothing_with_trend",
        }

        self.logger.info(f"Generated forecast for SKU {sku}: {forecast_result}")
        return forecast_result

    def incorporate_seasonality(
        self,
        forecast: Dict[str, Any],
        seasonal_factors: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """Adjust forecast for seasonal patterns.

        Args:
            forecast: Base forecast from generate_forecast
            seasonal_factors: List of seasonal adjustment factors (e.g., [1.2, 0.9, 1.1, ...])
                            If None, no seasonality adjustment is applied

        Returns:
            Dictionary with seasonality-adjusted forecast
        """
        if not seasonal_factors or len(seasonal_factors) == 0:
            self.logger.info("No seasonal factors provided, returning base forecast")
            return forecast

        # Calculate average seasonal factor
        avg_seasonal_factor = statistics.mean(seasonal_factors)

        # Apply seasonal adjustment
        adjusted_forecast = {
            "forecasted_demand": max(0, int(forecast["forecasted_demand"] * avg_seasonal_factor)),
            "confidence_80": max(0, forecast["confidence_80"] * avg_seasonal_factor),
            "confidence_95": max(0, forecast["confidence_95"] * avg_seasonal_factor),
            "method": forecast.get("method", "") + "_with_seasonality",
            "seasonal_factor": avg_seasonal_factor,
        }

        self.logger.info(f"Applied seasonality adjustment (factor: {avg_seasonal_factor})")
        return adjusted_forecast

    def apply_external_factors(
        self,
        forecast: Dict[str, Any],
        external_adjustments: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """Adjust forecast for external factors like promotions or events.

        Args:
            forecast: Base or seasonality-adjusted forecast
            external_adjustments: Dictionary of adjustment factors:
                                - "promotion_factor": multiplier for promotional periods
                                - "event_factor": multiplier for special events
                                - "market_factor": multiplier for market conditions

        Returns:
            Dictionary with externally-adjusted forecast
        """
        if not external_adjustments or len(external_adjustments) == 0:
            self.logger.info("No external factors provided, returning base forecast")
            return forecast

        # Calculate combined external adjustment factor
        combined_factor = 1.0
        for factor_name, factor_value in external_adjustments.items():
            if factor_value > 0:
                combined_factor *= factor_value

        # Apply external adjustments
        adjusted_forecast = {
            "forecasted_demand": max(0, int(forecast["forecasted_demand"] * combined_factor)),
            "confidence_80": max(0, forecast["confidence_80"] * combined_factor),
            "confidence_95": max(0, forecast["confidence_95"] * combined_factor),
            "method": forecast.get("method", "") + "_with_external_factors",
            "external_factor": combined_factor,
        }

        self.logger.info(f"Applied external factor adjustment (factor: {combined_factor})")
        return adjusted_forecast

    def store_forecast_in_dynamodb(
        self,
        sku: str,
        forecast: Dict[str, Any],
        forecast_period_start: date,
        forecast_period_end: date,
    ) -> Forecast:
        """Store forecast in DynamoDB with timestamp and confidence intervals.

        Args:
            sku: Stock Keeping Unit identifier
            forecast: Forecast data from generate_forecast or adjusted forecast
            forecast_period_start: Start date of forecast period
            forecast_period_end: End date of forecast period

        Returns:
            Forecast model instance that was stored
        """
        try:
            # Create forecast record
            forecast_id = f"FCST-{uuid.uuid4().hex[:12].upper()}"
            forecast_period = f"{forecast_period_start} to {forecast_period_end}"

            forecast_record = Forecast(
                forecast_id=forecast_id,
                sku=sku,
                forecast_date=date.today(),
                forecast_period=forecast_period,
                forecasted_demand=forecast["forecasted_demand"],
                confidence_80=forecast["confidence_80"],
                confidence_95=forecast["confidence_95"],
            )

            # Get DynamoDB table
            table = self.dynamodb.Table(self.forecasts_table_name)

            # Convert to dict and convert floats to Decimals for DynamoDB
            item = forecast_record.model_dump()
            item["confidence_80"] = Decimal(str(item["confidence_80"]))
            item["confidence_95"] = Decimal(str(item["confidence_95"]))
            item["created_at"] = item["created_at"].isoformat()
            item["updated_at"] = item["updated_at"].isoformat()
            item["forecast_date"] = item["forecast_date"].isoformat()

            # Store in DynamoDB
            table.put_item(Item=item)

            self.logger.info(
                f"Stored forecast {forecast_id} for SKU {sku} in DynamoDB"
            )
            return forecast_record

        except Exception as e:
            self.logger.error(f"Failed to store forecast in DynamoDB: {str(e)}")
            raise

    def generate_complete_forecast(
        self,
        sku: str,
        sales_data: List[Dict[str, Any]],
        seasonal_factors: Optional[List[float]] = None,
        external_adjustments: Optional[Dict[str, float]] = None,
        forecast_days: int = 30,
        forecast_period_start: Optional[date] = None,
        forecast_period_end: Optional[date] = None,
    ) -> Forecast:
        """Generate a complete forecast with all adjustments and store it.

        This is the main entry point that orchestrates all forecasting steps.

        Args:
            sku: Stock Keeping Unit identifier
            sales_data: Historical sales data
            seasonal_factors: Optional seasonal adjustment factors
            external_adjustments: Optional external factor adjustments
            forecast_days: Number of days to forecast
            forecast_period_start: Start date of forecast period (default: today)
            forecast_period_end: End date of forecast period (default: today + forecast_days)

        Returns:
            Stored Forecast model instance
        """
        # Set default forecast period
        if forecast_period_start is None:
            forecast_period_start = date.today()
        if forecast_period_end is None:
            forecast_period_end = forecast_period_start + timedelta(days=forecast_days)

        # Step 1: Analyze sales history
        sales_analysis = self.analyze_sales_history(sku, sales_data)

        # Step 2: Generate base forecast
        base_forecast = self.generate_forecast(sku, sales_analysis, forecast_days)

        # Step 3: Incorporate seasonality
        seasonal_forecast = self.incorporate_seasonality(base_forecast, seasonal_factors)

        # Step 4: Apply external factors
        final_forecast = self.apply_external_factors(seasonal_forecast, external_adjustments)

        # Step 5: Store in DynamoDB
        stored_forecast = self.store_forecast_in_dynamodb(
            sku, final_forecast, forecast_period_start, forecast_period_end
        )

        self.logger.info(
            f"Complete forecast generated for SKU {sku}: "
            f"demand={stored_forecast.forecasted_demand}, "
            f"confidence_80={stored_forecast.confidence_80}, "
            f"confidence_95={stored_forecast.confidence_95}"
        )

        return stored_forecast

    @staticmethod
    def _calculate_trend(quantities: List[float]) -> float:
        """Calculate linear trend using simple linear regression.

        Args:
            quantities: List of quantity values

        Returns:
            Trend coefficient (slope)
        """
        if len(quantities) < 2:
            return 0.0

        n = len(quantities)
        x_values = list(range(n))

        # Calculate means
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(quantities)

        # Calculate slope
        numerator = sum((x_values[i] - x_mean) * (quantities[i] - y_mean) for i in range(n))
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0

        return numerator / denominator
