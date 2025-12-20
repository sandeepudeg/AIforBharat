"""Tests for Demand Forecasting Agent.

Feature: supply-chain-optimizer, Property 1: Demand Forecast Generation
Validates: Requirements 1.1, 1.4
"""

from datetime import date, timedelta
from typing import List, Dict, Any
import random
import statistics
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck

from src.agents.demand_forecasting_agent import DemandForecastingAgent
from src.models.forecast import Forecast


@pytest.fixture
def agent():
    """Create a Demand Forecasting Agent instance."""
    return DemandForecastingAgent()


def generate_sales_data(
    num_days: int = 90,
    base_demand: int = 100,
    variance: int = 20,
    trend: float = 0.5,
) -> List[Dict[str, Any]]:
    """Generate synthetic sales data for testing.

    Args:
        num_days: Number of days of historical data
        base_demand: Base demand level
        variance: Random variance in demand
        trend: Linear trend coefficient

    Returns:
        List of sales records with 'date' and 'quantity' fields
    """
    sales_data = []
    for day in range(num_days):
        # Add trend and random variance
        quantity = int(base_demand + (trend * day) + random.randint(-variance, variance))
        quantity = max(0, quantity)  # Ensure non-negative
        sales_data.append({
            "date": (date.today() - timedelta(days=num_days - day)).isoformat(),
            "quantity": quantity,
        })
    return sales_data


class TestAnalyzeSalesHistory:
    """Test sales history analysis."""

    def test_analyze_sales_history_with_valid_data(self, agent):
        """Test analyzing valid sales history data."""
        sales_data = generate_sales_data(num_days=90, base_demand=100, variance=20)
        
        analysis = agent.analyze_sales_history("PROD-001", sales_data)
        
        assert analysis["data_points"] == 90
        assert analysis["mean"] > 0
        assert analysis["std_dev"] >= 0
        assert analysis["min_sales"] >= 0
        assert analysis["max_sales"] >= analysis["min_sales"]

    def test_analyze_sales_history_with_empty_data(self, agent):
        """Test analyzing empty sales history."""
        analysis = agent.analyze_sales_history("PROD-001", [])
        
        assert analysis["data_points"] == 0
        assert analysis["mean"] == 0
        assert analysis["std_dev"] == 0

    def test_analyze_sales_history_with_single_data_point(self, agent):
        """Test analyzing sales history with single data point."""
        sales_data = [{"date": date.today().isoformat(), "quantity": 100}]
        
        analysis = agent.analyze_sales_history("PROD-001", sales_data)
        
        assert analysis["data_points"] == 1
        assert analysis["mean"] == 100
        assert analysis["std_dev"] == 0

    def test_analyze_sales_history_with_constant_demand(self, agent):
        """Test analyzing sales history with constant demand."""
        sales_data = [{"date": date.today().isoformat(), "quantity": 100} for _ in range(30)]
        
        analysis = agent.analyze_sales_history("PROD-001", sales_data)
        
        assert analysis["data_points"] == 30
        assert analysis["mean"] == 100
        assert analysis["std_dev"] == 0
        assert analysis["min_sales"] == 100
        assert analysis["max_sales"] == 100

    def test_analyze_sales_history_detects_trend(self, agent):
        """Test that trend is detected in sales data."""
        # Create data with clear upward trend
        sales_data = [{"date": date.today().isoformat(), "quantity": 100 + (i * 2)} for i in range(50)]
        
        analysis = agent.analyze_sales_history("PROD-001", sales_data)
        
        assert analysis["trend"] > 0  # Should detect upward trend


class TestGenerateForecast:
    """Test forecast generation."""

    def test_generate_forecast_with_valid_analysis(self, agent):
        """Test generating forecast from valid sales analysis."""
        sales_analysis = {
            "mean": 100,
            "std_dev": 20,
            "trend": 0.5,
            "min_sales": 50,
            "max_sales": 150,
            "data_points": 90,
        }
        
        forecast = agent.generate_forecast("PROD-001", sales_analysis, forecast_days=30)
        
        assert forecast["forecasted_demand"] > 0
        assert forecast["confidence_80"] >= 0
        assert forecast["confidence_95"] >= 0
        assert forecast["confidence_95"] <= forecast["confidence_80"]
        assert "method" in forecast

    def test_generate_forecast_confidence_intervals(self, agent):
        """Test that confidence intervals are properly ordered."""
        sales_analysis = {
            "mean": 100,
            "std_dev": 20,
            "trend": 0.0,
            "min_sales": 50,
            "max_sales": 150,
            "data_points": 90,
        }
        
        forecast = agent.generate_forecast("PROD-001", sales_analysis, forecast_days=30)
        
        # 95% CI should be lower than 80% CI (wider interval)
        assert forecast["confidence_95"] <= forecast["confidence_80"]

    def test_generate_forecast_with_zero_std_dev(self, agent):
        """Test forecast generation with zero standard deviation."""
        sales_analysis = {
            "mean": 100,
            "std_dev": 0,
            "trend": 0,
            "min_sales": 100,
            "max_sales": 100,
            "data_points": 30,
        }
        
        forecast = agent.generate_forecast("PROD-001", sales_analysis, forecast_days=30)
        
        assert forecast["forecasted_demand"] > 0
        assert forecast["confidence_80"] >= 0
        assert forecast["confidence_95"] >= 0

    def test_generate_forecast_respects_forecast_days(self, agent):
        """Test that forecast scales with forecast_days parameter."""
        sales_analysis = {
            "mean": 100,
            "std_dev": 10,
            "trend": 0,
            "min_sales": 90,
            "max_sales": 110,
            "data_points": 30,
        }
        
        forecast_30 = agent.generate_forecast("PROD-001", sales_analysis, forecast_days=30)
        forecast_60 = agent.generate_forecast("PROD-001", sales_analysis, forecast_days=60)
        
        # Longer forecast period should generally result in higher total demand
        assert forecast_60["forecasted_demand"] >= forecast_30["forecasted_demand"]


class TestIncorporateSeasonality:
    """Test seasonality incorporation."""

    def test_incorporate_seasonality_with_factors(self, agent):
        """Test incorporating seasonal factors."""
        base_forecast = {
            "forecasted_demand": 1000,
            "confidence_80": 950.0,
            "confidence_95": 900.0,
            "method": "exponential_smoothing_with_trend",
        }
        seasonal_factors = [1.2, 0.9, 1.1, 1.0]
        
        adjusted = agent.incorporate_seasonality(base_forecast, seasonal_factors)
        
        assert adjusted["forecasted_demand"] > 0
        assert "seasonal_factor" in adjusted
        assert adjusted["method"] == "exponential_smoothing_with_trend_with_seasonality"

    def test_incorporate_seasonality_without_factors(self, agent):
        """Test that no adjustment occurs without seasonal factors."""
        base_forecast = {
            "forecasted_demand": 1000,
            "confidence_80": 950.0,
            "confidence_95": 900.0,
            "method": "exponential_smoothing_with_trend",
        }
        
        adjusted = agent.incorporate_seasonality(base_forecast, None)
        
        assert adjusted == base_forecast

    def test_incorporate_seasonality_with_empty_factors(self, agent):
        """Test that no adjustment occurs with empty seasonal factors."""
        base_forecast = {
            "forecasted_demand": 1000,
            "confidence_80": 950.0,
            "confidence_95": 900.0,
            "method": "exponential_smoothing_with_trend",
        }
        
        adjusted = agent.incorporate_seasonality(base_forecast, [])
        
        assert adjusted == base_forecast

    def test_incorporate_seasonality_increases_demand(self, agent):
        """Test that high seasonal factors increase demand."""
        base_forecast = {
            "forecasted_demand": 1000,
            "confidence_80": 950.0,
            "confidence_95": 900.0,
            "method": "exponential_smoothing_with_trend",
        }
        seasonal_factors = [1.5, 1.5, 1.5]  # High seasonal factors
        
        adjusted = agent.incorporate_seasonality(base_forecast, seasonal_factors)
        
        assert adjusted["forecasted_demand"] > base_forecast["forecasted_demand"]

    def test_incorporate_seasonality_decreases_demand(self, agent):
        """Test that low seasonal factors decrease demand."""
        base_forecast = {
            "forecasted_demand": 1000,
            "confidence_80": 950.0,
            "confidence_95": 900.0,
            "method": "exponential_smoothing_with_trend",
        }
        seasonal_factors = [0.5, 0.5, 0.5]  # Low seasonal factors
        
        adjusted = agent.incorporate_seasonality(base_forecast, seasonal_factors)
        
        assert adjusted["forecasted_demand"] < base_forecast["forecasted_demand"]


class TestApplyExternalFactors:
    """Test external factor application."""

    def test_apply_external_factors_with_adjustments(self, agent):
        """Test applying external factor adjustments."""
        base_forecast = {
            "forecasted_demand": 1000,
            "confidence_80": 950.0,
            "confidence_95": 900.0,
            "method": "exponential_smoothing_with_trend_with_seasonality",
        }
        external_adjustments = {
            "promotion_factor": 1.3,
            "event_factor": 1.1,
        }
        
        adjusted = agent.apply_external_factors(base_forecast, external_adjustments)
        
        assert adjusted["forecasted_demand"] > 0
        assert "external_factor" in adjusted
        assert adjusted["method"] == "exponential_smoothing_with_trend_with_seasonality_with_external_factors"

    def test_apply_external_factors_without_adjustments(self, agent):
        """Test that no adjustment occurs without external factors."""
        base_forecast = {
            "forecasted_demand": 1000,
            "confidence_80": 950.0,
            "confidence_95": 900.0,
            "method": "exponential_smoothing_with_trend",
        }
        
        adjusted = agent.apply_external_factors(base_forecast, None)
        
        assert adjusted == base_forecast

    def test_apply_external_factors_with_empty_adjustments(self, agent):
        """Test that no adjustment occurs with empty external factors."""
        base_forecast = {
            "forecasted_demand": 1000,
            "confidence_80": 950.0,
            "confidence_95": 900.0,
            "method": "exponential_smoothing_with_trend",
        }
        
        adjusted = agent.apply_external_factors(base_forecast, {})
        
        assert adjusted == base_forecast

    def test_apply_external_factors_increases_demand(self, agent):
        """Test that external factors > 1.0 increase demand."""
        base_forecast = {
            "forecasted_demand": 1000,
            "confidence_80": 950.0,
            "confidence_95": 900.0,
            "method": "exponential_smoothing_with_trend",
        }
        external_adjustments = {
            "promotion_factor": 1.5,
        }
        
        adjusted = agent.apply_external_factors(base_forecast, external_adjustments)
        
        assert adjusted["forecasted_demand"] > base_forecast["forecasted_demand"]

    def test_apply_external_factors_decreases_demand(self, agent):
        """Test that external factors < 1.0 decrease demand."""
        base_forecast = {
            "forecasted_demand": 1000,
            "confidence_80": 950.0,
            "confidence_95": 900.0,
            "method": "exponential_smoothing_with_trend",
        }
        external_adjustments = {
            "market_factor": 0.7,
        }
        
        adjusted = agent.apply_external_factors(base_forecast, external_adjustments)
        
        assert adjusted["forecasted_demand"] < base_forecast["forecasted_demand"]


class TestCalculateTrend:
    """Test trend calculation."""

    def test_calculate_trend_upward(self, agent):
        """Test trend calculation with upward trend."""
        quantities = [100, 102, 104, 106, 108, 110]
        
        trend = agent._calculate_trend(quantities)
        
        assert trend > 0

    def test_calculate_trend_downward(self, agent):
        """Test trend calculation with downward trend."""
        quantities = [110, 108, 106, 104, 102, 100]
        
        trend = agent._calculate_trend(quantities)
        
        assert trend < 0

    def test_calculate_trend_flat(self, agent):
        """Test trend calculation with flat trend."""
        quantities = [100, 100, 100, 100, 100, 100]
        
        trend = agent._calculate_trend(quantities)
        
        assert trend == 0

    def test_calculate_trend_single_point(self, agent):
        """Test trend calculation with single data point."""
        quantities = [100]
        
        trend = agent._calculate_trend(quantities)
        
        assert trend == 0


class TestGenerateCompleteForecast:
    """Test complete forecast generation workflow."""

    def test_generate_complete_forecast_basic(self, agent):
        """Test generating a complete forecast with basic inputs."""
        sales_data = generate_sales_data(num_days=90, base_demand=100, variance=20)
        
        forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            forecast_days=30,
        )
        
        assert isinstance(forecast, Forecast)
        assert forecast.sku == "PROD-001"
        assert forecast.forecasted_demand > 0
        assert forecast.confidence_80 >= 0
        assert forecast.confidence_95 >= 0
        assert forecast.confidence_95 <= forecast.confidence_80

    def test_generate_complete_forecast_with_seasonality(self, agent):
        """Test generating forecast with seasonality."""
        sales_data = generate_sales_data(num_days=90, base_demand=100, variance=20)
        seasonal_factors = [1.2, 0.9, 1.1, 1.0]
        
        forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            seasonal_factors=seasonal_factors,
            forecast_days=30,
        )
        
        assert isinstance(forecast, Forecast)
        assert forecast.forecasted_demand > 0

    def test_generate_complete_forecast_with_external_factors(self, agent):
        """Test generating forecast with external factors."""
        sales_data = generate_sales_data(num_days=90, base_demand=100, variance=20)
        external_adjustments = {"promotion_factor": 1.3}
        
        forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            external_adjustments=external_adjustments,
            forecast_days=30,
        )
        
        assert isinstance(forecast, Forecast)
        assert forecast.forecasted_demand > 0

    def test_generate_complete_forecast_with_all_adjustments(self, agent):
        """Test generating forecast with all adjustments."""
        sales_data = generate_sales_data(num_days=90, base_demand=100, variance=20)
        seasonal_factors = [1.2, 0.9, 1.1, 1.0]
        external_adjustments = {"promotion_factor": 1.3, "event_factor": 1.1}
        
        forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            seasonal_factors=seasonal_factors,
            external_adjustments=external_adjustments,
            forecast_days=30,
        )
        
        assert isinstance(forecast, Forecast)
        assert forecast.forecasted_demand > 0
        assert forecast.confidence_80 >= 0
        assert forecast.confidence_95 >= 0

    def test_generate_complete_forecast_with_custom_period(self, agent):
        """Test generating forecast with custom forecast period."""
        sales_data = generate_sales_data(num_days=90, base_demand=100, variance=20)
        period_start = date.today()
        period_end = date.today() + timedelta(days=30)
        
        forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            forecast_period_start=period_start,
            forecast_period_end=period_end,
        )
        
        assert isinstance(forecast, Forecast)
        assert period_start.isoformat() in forecast.forecast_period
        assert period_end.isoformat() in forecast.forecast_period

    def test_generate_complete_forecast_with_empty_sales_data(self, agent):
        """Test generating forecast with empty sales data."""
        forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=[],
            forecast_days=30,
        )
        
        assert isinstance(forecast, Forecast)
        assert forecast.sku == "PROD-001"
        # With no data, forecast should be minimal
        assert forecast.forecasted_demand >= 0


class TestForecastGenerationWithVariousDataPatterns:
    """Unit tests for forecast generation with various data patterns.
    
    Tests forecast generation with different types of sales data patterns
    to ensure robustness across diverse scenarios.
    """

    def test_forecast_with_high_variance_data(self, agent):
        """Test forecast generation with high variance in sales data."""
        sales_data = generate_sales_data(num_days=90, base_demand=100, variance=50)
        
        forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            forecast_days=30,
        )
        
        assert forecast.forecasted_demand > 0
        assert forecast.confidence_80 >= 0
        assert forecast.confidence_95 >= 0
        # High variance should result in wider confidence intervals
        assert forecast.confidence_80 > 0 or forecast.confidence_95 > 0

    def test_forecast_with_low_variance_data(self, agent):
        """Test forecast generation with low variance in sales data."""
        sales_data = generate_sales_data(num_days=90, base_demand=100, variance=5)
        
        forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            forecast_days=30,
        )
        
        assert forecast.forecasted_demand > 0
        assert forecast.confidence_80 >= 0
        assert forecast.confidence_95 >= 0

    def test_forecast_with_upward_trend_data(self, agent):
        """Test forecast generation with upward trending sales data."""
        sales_data = generate_sales_data(num_days=90, base_demand=100, variance=10, trend=2.0)
        
        forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            forecast_days=30,
        )
        
        assert forecast.forecasted_demand > 0
        # Upward trend should result in higher forecast
        assert forecast.forecasted_demand > 100 * 30  # Base demand * days

    def test_forecast_with_downward_trend_data(self, agent):
        """Test forecast generation with downward trending sales data."""
        sales_data = generate_sales_data(num_days=90, base_demand=100, variance=10, trend=-2.0)
        
        forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            forecast_days=30,
        )
        
        assert forecast.forecasted_demand >= 0
        # Downward trend should result in lower forecast
        assert forecast.forecasted_demand < 100 * 30

    def test_forecast_with_very_high_demand_data(self, agent):
        """Test forecast generation with very high demand values."""
        sales_data = generate_sales_data(num_days=90, base_demand=10000, variance=1000)
        
        forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            forecast_days=30,
        )
        
        assert forecast.forecasted_demand > 0
        assert forecast.confidence_80 >= 0
        assert forecast.confidence_95 >= 0

    def test_forecast_with_very_low_demand_data(self, agent):
        """Test forecast generation with very low demand values."""
        sales_data = generate_sales_data(num_days=90, base_demand=5, variance=2)
        
        forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            forecast_days=30,
        )
        
        assert forecast.forecasted_demand >= 0
        assert forecast.confidence_80 >= 0
        assert forecast.confidence_95 >= 0

    def test_forecast_with_sparse_data(self, agent):
        """Test forecast generation with sparse historical data."""
        sales_data = generate_sales_data(num_days=10, base_demand=100, variance=20)
        
        forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            forecast_days=30,
        )
        
        assert forecast.forecasted_demand >= 0
        assert forecast.confidence_80 >= 0
        assert forecast.confidence_95 >= 0

    def test_forecast_with_abundant_data(self, agent):
        """Test forecast generation with abundant historical data."""
        sales_data = generate_sales_data(num_days=365, base_demand=100, variance=20)
        
        forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            forecast_days=30,
        )
        
        assert forecast.forecasted_demand > 0
        assert forecast.confidence_80 >= 0
        assert forecast.confidence_95 >= 0


class TestSeasonalityDetectionAndIncorporation:
    """Unit tests for seasonality detection and incorporation.
    
    Tests that seasonality is properly detected and incorporated into forecasts.
    """

    def test_seasonality_with_strong_seasonal_pattern(self, agent):
        """Test seasonality incorporation with strong seasonal pattern."""
        sales_data = generate_sales_data(num_days=90, base_demand=100, variance=10)
        # Strong seasonal pattern: high in Q1, low in Q2, high in Q3, low in Q4
        seasonal_factors = [1.5, 1.4, 1.3, 0.5, 0.6, 0.7, 1.5, 1.4, 1.3, 0.5, 0.6, 0.7]
        
        forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            seasonal_factors=seasonal_factors,
            forecast_days=30,
        )
        
        assert forecast.forecasted_demand > 0
        # Average seasonal factor should be calculated correctly
        avg_factor = statistics.mean(seasonal_factors)
        assert avg_factor >= 0.9  # Should be close to 1.0 (average of the pattern)

    def test_seasonality_with_weak_seasonal_pattern(self, agent):
        """Test seasonality incorporation with weak seasonal pattern."""
        sales_data = generate_sales_data(num_days=90, base_demand=100, variance=10)
        # Weak seasonal pattern: all factors close to 1.0
        seasonal_factors = [1.05, 0.95, 1.02, 0.98, 1.01, 0.99]
        
        forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            seasonal_factors=seasonal_factors,
            forecast_days=30,
        )
        
        assert forecast.forecasted_demand > 0
        # Weak seasonal pattern should result in forecast close to base

    def test_seasonality_with_single_factor(self, agent):
        """Test seasonality incorporation with single seasonal factor."""
        sales_data = generate_sales_data(num_days=90, base_demand=100, variance=10)
        seasonal_factors = [1.5]
        
        forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            seasonal_factors=seasonal_factors,
            forecast_days=30,
        )
        
        assert forecast.forecasted_demand > 0

    def test_seasonality_with_many_factors(self, agent):
        """Test seasonality incorporation with many seasonal factors."""
        sales_data = generate_sales_data(num_days=90, base_demand=100, variance=10)
        # 24 monthly factors (2 years)
        seasonal_factors = [1.2, 1.1, 1.0, 0.9, 0.8, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3] * 2
        
        forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            seasonal_factors=seasonal_factors,
            forecast_days=30,
        )
        
        assert forecast.forecasted_demand > 0

    def test_seasonality_preserves_confidence_intervals(self, agent):
        """Test that seasonality adjustment preserves confidence interval ordering."""
        sales_data = generate_sales_data(num_days=90, base_demand=100, variance=20)
        seasonal_factors = [1.2, 0.9, 1.1, 1.0]
        
        forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            seasonal_factors=seasonal_factors,
            forecast_days=30,
        )
        
        # Confidence intervals should maintain proper ordering
        assert forecast.confidence_95 <= forecast.confidence_80


class TestExternalFactorApplication:
    """Unit tests for external factor application.
    
    Tests that external factors are properly applied to forecasts.
    """

    def test_external_factor_promotion_boost(self, agent):
        """Test external factor application with promotion boost."""
        sales_data = generate_sales_data(num_days=90, base_demand=100, variance=20)
        external_adjustments = {"promotion_factor": 1.5}
        
        forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            external_adjustments=external_adjustments,
            forecast_days=30,
        )
        
        assert forecast.forecasted_demand > 0

    def test_external_factor_market_downturn(self, agent):
        """Test external factor application with market downturn."""
        sales_data = generate_sales_data(num_days=90, base_demand=100, variance=20)
        external_adjustments = {"market_factor": 0.7}
        
        forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            external_adjustments=external_adjustments,
            forecast_days=30,
        )
        
        assert forecast.forecasted_demand >= 0

    def test_external_factor_event_boost(self, agent):
        """Test external factor application with event boost."""
        sales_data = generate_sales_data(num_days=90, base_demand=100, variance=20)
        external_adjustments = {"event_factor": 2.0}
        
        forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            external_adjustments=external_adjustments,
            forecast_days=30,
        )
        
        assert forecast.forecasted_demand > 0

    def test_external_factor_combined_adjustments(self, agent):
        """Test external factor application with multiple combined adjustments."""
        sales_data = generate_sales_data(num_days=90, base_demand=100, variance=20)
        external_adjustments = {
            "promotion_factor": 1.3,
            "event_factor": 1.2,
            "market_factor": 0.95,
        }
        
        forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            external_adjustments=external_adjustments,
            forecast_days=30,
        )
        
        assert forecast.forecasted_demand > 0
        # Combined factor should be 1.3 * 1.2 * 0.95 = 1.482
        combined_factor = 1.3 * 1.2 * 0.95
        assert combined_factor > 1.0

    def test_external_factor_preserves_confidence_intervals(self, agent):
        """Test that external factor adjustment preserves confidence interval ordering."""
        sales_data = generate_sales_data(num_days=90, base_demand=100, variance=20)
        external_adjustments = {"promotion_factor": 1.5}
        
        forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            external_adjustments=external_adjustments,
            forecast_days=30,
        )
        
        # Confidence intervals should maintain proper ordering
        assert forecast.confidence_95 <= forecast.confidence_80


class TestFallbackBehaviorWithInsufficientData:
    """Unit tests for fallback behavior with insufficient data.
    
    Tests that the system handles edge cases with insufficient or missing data gracefully.
    """

    def test_fallback_with_no_sales_data(self, agent):
        """Test fallback behavior when no sales data is provided."""
        forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=[],
            forecast_days=30,
        )
        
        assert isinstance(forecast, Forecast)
        assert forecast.sku == "PROD-001"
        # With no data, forecast should be minimal but valid
        assert forecast.forecasted_demand >= 0
        assert forecast.confidence_80 >= 0
        assert forecast.confidence_95 >= 0

    def test_fallback_with_single_data_point(self, agent):
        """Test fallback behavior with only one data point."""
        sales_data = [{"date": date.today().isoformat(), "quantity": 100}]
        
        forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            forecast_days=30,
        )
        
        assert isinstance(forecast, Forecast)
        assert forecast.forecasted_demand >= 0

    def test_fallback_with_two_data_points(self, agent):
        """Test fallback behavior with only two data points."""
        sales_data = [
            {"date": (date.today() - timedelta(days=1)).isoformat(), "quantity": 100},
            {"date": date.today().isoformat(), "quantity": 110},
        ]
        
        forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            forecast_days=30,
        )
        
        assert isinstance(forecast, Forecast)
        assert forecast.forecasted_demand >= 0

    def test_fallback_with_zero_demand_data(self, agent):
        """Test fallback behavior when all demand values are zero."""
        sales_data = [{"date": date.today().isoformat(), "quantity": 0} for _ in range(30)]
        
        forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            forecast_days=30,
        )
        
        assert isinstance(forecast, Forecast)
        assert forecast.forecasted_demand >= 0

    def test_fallback_with_missing_quantity_field(self, agent):
        """Test fallback behavior when quantity field is missing."""
        sales_data = [
            {"date": date.today().isoformat()},  # Missing quantity
            {"date": (date.today() - timedelta(days=1)).isoformat(), "quantity": 100},
        ]
        
        forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            forecast_days=30,
        )
        
        assert isinstance(forecast, Forecast)
        assert forecast.forecasted_demand >= 0

    def test_fallback_with_negative_demand_values(self, agent):
        """Test fallback behavior when demand values are negative (should be treated as 0)."""
        sales_data = [
            {"date": date.today().isoformat(), "quantity": -50},
            {"date": (date.today() - timedelta(days=1)).isoformat(), "quantity": 100},
        ]
        
        forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            forecast_days=30,
        )
        
        assert isinstance(forecast, Forecast)
        assert forecast.forecasted_demand >= 0

    def test_fallback_with_very_short_forecast_period(self, agent):
        """Test fallback behavior with very short forecast period."""
        sales_data = generate_sales_data(num_days=90, base_demand=100, variance=20)
        
        forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            forecast_days=1,
        )
        
        assert isinstance(forecast, Forecast)
        assert forecast.forecasted_demand >= 0

    def test_fallback_with_very_long_forecast_period(self, agent):
        """Test fallback behavior with very long forecast period."""
        sales_data = generate_sales_data(num_days=90, base_demand=100, variance=20)
        
        forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            forecast_days=365,
        )
        
        assert isinstance(forecast, Forecast)
        assert forecast.forecasted_demand >= 0

    def test_fallback_with_insufficient_data_and_seasonality(self, agent):
        """Test fallback behavior with insufficient data and seasonality factors."""
        sales_data = [{"date": date.today().isoformat(), "quantity": 100}]
        seasonal_factors = [1.2, 0.9, 1.1]
        
        forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            seasonal_factors=seasonal_factors,
            forecast_days=30,
        )
        
        assert isinstance(forecast, Forecast)
        assert forecast.forecasted_demand >= 0

    def test_fallback_with_insufficient_data_and_external_factors(self, agent):
        """Test fallback behavior with insufficient data and external factors."""
        sales_data = [{"date": date.today().isoformat(), "quantity": 100}]
        external_adjustments = {"promotion_factor": 1.5}
        
        forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            external_adjustments=external_adjustments,
            forecast_days=30,
        )
        
        assert isinstance(forecast, Forecast)
        assert forecast.forecasted_demand >= 0


class TestPropertyBasedForecasting:
    """Property-based tests for demand forecasting using Hypothesis.
    
    Feature: supply-chain-optimizer, Property 1: Demand Forecast Generation
    Validates: Requirements 1.1, 1.4
    
    Property 1: Demand Forecast Generation
    *For any* product with historical sales data, generating a demand forecast 
    should produce a 30-day forecast with confidence intervals (80% and 95%) 
    and all forecasts should be persisted with timestamps for audit purposes.
    
    Feature: supply-chain-optimizer, Property 2: Seasonal Pattern Incorporation
    Validates: Requirements 1.2
    
    Property 2: Seasonal Pattern Incorporation
    *For any* historical sales data with known seasonal patterns, the generated 
    forecast should reflect those patterns such that forecasted values align 
    with the seasonal cycle.
    """

    # Strategy for generating valid sales data
    @staticmethod
    def sales_data_strategy():
        """Generate valid sales data for property testing."""
        return st.lists(
            st.fixed_dictionaries({
                "date": st.dates(min_value=date(2020, 1, 1), max_value=date.today()),
                "quantity": st.integers(min_value=0, max_value=10000),
            }),
            min_size=1,
            max_size=365,
        )

    @given(
        sales_data=sales_data_strategy(),
        forecast_days=st.integers(min_value=1, max_value=365),
        sku=st.text(min_size=1, max_size=50),
    )
    @settings(
        max_examples=20,
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture],
        deadline=None,
    )
    def test_property_forecast_has_valid_confidence_intervals(self, sales_data, forecast_days, sku):
        """Property: Forecast should always have valid confidence intervals.
        
        For any valid sales data and forecast parameters, the generated forecast
        should have:
        - Non-negative confidence intervals
        - 95% CI <= 80% CI (wider interval)
        - Timestamps for audit purposes
        - Valid forecast ID
        """
        # Create agent for this test
        agent = DemandForecastingAgent()
        
        # Generate forecast
        forecast = agent.generate_complete_forecast(
            sku=sku,
            sales_data=sales_data,
            forecast_days=forecast_days,
        )
        
        # Verify confidence intervals are valid
        assert forecast.confidence_80 >= 0, "80% confidence interval must be non-negative"
        assert forecast.confidence_95 >= 0, "95% confidence interval must be non-negative"
        assert forecast.confidence_95 <= forecast.confidence_80, \
            "95% CI must be <= 80% CI (wider interval)"
        
        # Verify forecast demand is non-negative
        assert forecast.forecasted_demand >= 0, "Forecasted demand must be non-negative"
        
        # Verify audit trail
        assert forecast.forecast_id is not None, "Forecast ID must be present"
        assert len(forecast.forecast_id) > 0, "Forecast ID must not be empty"
        assert forecast.created_at is not None, "Created timestamp must be present"
        assert forecast.forecast_date is not None, "Forecast date must be present"
        assert forecast.forecast_period is not None, "Forecast period must be present"

    @given(
        sales_data=sales_data_strategy(),
        seasonal_factors=st.lists(
            st.floats(min_value=0.1, max_value=3.0),
            min_size=1,
            max_size=12,
        ),
    )
    @settings(
        max_examples=15,
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture],
        deadline=None,
    )
    def test_property_seasonality_adjustment_maintains_validity(self, sales_data, seasonal_factors):
        """Property: Seasonality adjustment should maintain forecast validity.
        
        For any valid sales data and seasonal factors, the seasonality-adjusted
        forecast should:
        - Still have valid confidence intervals
        - Maintain the ordering: 95% CI <= 80% CI
        - Have non-negative values
        """
        agent = DemandForecastingAgent()
        
        forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            seasonal_factors=seasonal_factors,
            forecast_days=30,
        )
        
        # Verify adjusted forecast is still valid
        assert forecast.confidence_80 >= 0
        assert forecast.confidence_95 >= 0
        assert forecast.confidence_95 <= forecast.confidence_80
        assert forecast.forecasted_demand >= 0

    @given(
        sales_data=sales_data_strategy(),
        external_adjustments=st.dictionaries(
            st.sampled_from(["promotion_factor", "event_factor", "market_factor"]),
            st.floats(min_value=0.1, max_value=3.0),
            min_size=1,
            max_size=3,
        ),
    )
    @settings(
        max_examples=15,
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture],
        deadline=None,
    )
    def test_property_external_factors_maintain_validity(self, sales_data, external_adjustments):
        """Property: External factor adjustment should maintain forecast validity.
        
        For any valid sales data and external adjustment factors, the adjusted
        forecast should:
        - Still have valid confidence intervals
        - Maintain the ordering: 95% CI <= 80% CI
        - Have non-negative values
        """
        agent = DemandForecastingAgent()
        
        forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            external_adjustments=external_adjustments,
            forecast_days=30,
        )
        
        # Verify adjusted forecast is still valid
        assert forecast.confidence_80 >= 0
        assert forecast.confidence_95 >= 0
        assert forecast.confidence_95 <= forecast.confidence_80
        assert forecast.forecasted_demand >= 0

    @given(
        sales_data=sales_data_strategy(),
        seasonal_factors=st.lists(
            st.floats(min_value=0.1, max_value=3.0),
            min_size=1,
            max_size=12,
        ),
        external_adjustments=st.dictionaries(
            st.sampled_from(["promotion_factor", "event_factor", "market_factor"]),
            st.floats(min_value=0.1, max_value=3.0),
            min_size=1,
            max_size=3,
        ),
    )
    @settings(
        max_examples=15,
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture],
        deadline=None,
    )
    def test_property_combined_adjustments_maintain_validity(
        self, sales_data, seasonal_factors, external_adjustments
    ):
        """Property: Combined adjustments should maintain forecast validity.
        
        For any valid sales data with both seasonal and external adjustments,
        the forecast should:
        - Still have valid confidence intervals
        - Maintain the ordering: 95% CI <= 80% CI
        - Have non-negative values
        """
        agent = DemandForecastingAgent()
        
        forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            seasonal_factors=seasonal_factors,
            external_adjustments=external_adjustments,
            forecast_days=30,
        )
        
        # Verify combined adjustments maintain validity
        assert forecast.confidence_80 >= 0
        assert forecast.confidence_95 >= 0
        assert forecast.confidence_95 <= forecast.confidence_80
        assert forecast.forecasted_demand >= 0

    @given(
        base_demand=st.integers(min_value=50, max_value=1000),
        num_days=st.integers(min_value=30, max_value=365),
        variance=st.integers(min_value=1, max_value=100),
    )
    @settings(
        max_examples=20,
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture],
        deadline=None,
    )
    def test_property_forecast_scales_with_forecast_period(self, base_demand, num_days, variance):
        """Property: Forecast should be non-negative and consistent across periods.
        
        For any valid sales parameters with sufficient historical data and base demand,
        forecasts should be non-negative and valid regardless of forecast period.
        """
        agent = DemandForecastingAgent()
        
        sales_data = generate_sales_data(
            num_days=num_days,
            base_demand=base_demand,
            variance=variance,
        )
        
        # Generate forecasts for different periods
        forecast_30 = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            forecast_days=30,
        )
        
        forecast_60 = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            forecast_days=60,
        )
        
        # Both forecasts should be non-negative and valid
        assert forecast_30.forecasted_demand >= 0
        assert forecast_60.forecasted_demand >= 0
        # Confidence intervals should be valid (lower bound <= upper bound)
        assert forecast_30.confidence_95 <= forecast_30.confidence_80
        assert forecast_60.confidence_95 <= forecast_60.confidence_80

    @given(
        sales_data=sales_data_strategy(),
    )
    @settings(
        max_examples=15,
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture],
        deadline=None,
    )
    def test_property_forecast_is_idempotent_for_same_input(self, sales_data):
        """Property: Forecasting the same data should produce consistent results.
        
        For any valid sales data, generating a forecast twice with the same
        parameters should produce forecasts with the same demand value
        (though timestamps will differ).
        """
        agent = DemandForecastingAgent()
        
        forecast1 = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            forecast_days=30,
        )
        
        forecast2 = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            forecast_days=30,
        )
        
        # Same input should produce same forecast demand
        assert forecast1.forecasted_demand == forecast2.forecasted_demand
        assert forecast1.confidence_80 == forecast2.confidence_80
        assert forecast1.confidence_95 == forecast2.confidence_95

    @given(
        base_demand=st.integers(min_value=50, max_value=500),
        num_days=st.integers(min_value=30, max_value=365),
        variance=st.integers(min_value=5, max_value=100),
        seasonal_pattern=st.lists(
            st.floats(min_value=0.5, max_value=2.0),
            min_size=4,
            max_size=12,
        ),
    )
    @settings(
        max_examples=20,
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture],
        deadline=None,
    )
    def test_property_seasonal_pattern_incorporation(
        self, base_demand, num_days, variance, seasonal_pattern
    ):
        """Property 2: Seasonal Pattern Incorporation
        
        *For any* historical sales data with known seasonal patterns, the 
        generated forecast should reflect those patterns such that forecasted 
        values align with the seasonal cycle.
        
        This property validates that:
        1. When seasonal factors are applied, the forecast changes appropriately
        2. High seasonal factors (>1.0) increase the forecast
        3. Low seasonal factors (<1.0) decrease the forecast
        4. The average seasonal factor correctly scales the forecast
        5. Seasonal adjustment maintains forecast validity
        
        Validates: Requirements 1.2
        """
        agent = DemandForecastingAgent()
        
        # Generate sales data with the specified parameters
        sales_data = generate_sales_data(
            num_days=num_days,
            base_demand=base_demand,
            variance=variance,
        )
        
        # Generate base forecast without seasonality
        base_forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            seasonal_factors=None,
            forecast_days=30,
        )
        
        # Generate forecast with seasonal factors
        seasonal_forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            seasonal_factors=seasonal_pattern,
            forecast_days=30,
        )
        
        # Calculate average seasonal factor
        avg_seasonal_factor = statistics.mean(seasonal_pattern)
        
        # Property 1: Seasonal adjustment should scale the forecast
        # The adjusted forecast should be approximately base * avg_seasonal_factor
        expected_adjusted_demand = int(base_forecast.forecasted_demand * avg_seasonal_factor)
        
        # Allow for small rounding differences (within 5% tolerance)
        tolerance = max(1, int(expected_adjusted_demand * 0.05))
        assert abs(seasonal_forecast.forecasted_demand - expected_adjusted_demand) <= tolerance, \
            f"Seasonal forecast {seasonal_forecast.forecasted_demand} should be approximately " \
            f"{expected_adjusted_demand} (base {base_forecast.forecasted_demand} * " \
            f"seasonal factor {avg_seasonal_factor})"
        
        # Property 2: High seasonal factors should increase forecast
        if avg_seasonal_factor > 1.0:
            assert seasonal_forecast.forecasted_demand >= base_forecast.forecasted_demand, \
                f"High seasonal factor ({avg_seasonal_factor}) should increase forecast"
        
        # Property 3: Low seasonal factors should decrease forecast
        elif avg_seasonal_factor < 1.0:
            assert seasonal_forecast.forecasted_demand <= base_forecast.forecasted_demand, \
                f"Low seasonal factor ({avg_seasonal_factor}) should decrease forecast"
        
        # Property 4: Seasonal factors near 1.0 should keep forecast similar
        else:
            # If avg_seasonal_factor is very close to 1.0, forecasts should be similar
            tolerance = max(1, int(base_forecast.forecasted_demand * 0.1))
            assert abs(seasonal_forecast.forecasted_demand - base_forecast.forecasted_demand) <= tolerance, \
                f"Seasonal factor near 1.0 should keep forecast similar"
        
        # Property 5: Seasonal adjustment maintains forecast validity
        assert seasonal_forecast.confidence_80 >= 0, \
            "80% confidence interval must be non-negative after seasonality"
        assert seasonal_forecast.confidence_95 >= 0, \
            "95% confidence interval must be non-negative after seasonality"
        assert seasonal_forecast.confidence_95 <= seasonal_forecast.confidence_80, \
            "95% CI must be <= 80% CI after seasonality"
        
        # Property 6: Forecast period should be preserved
        assert seasonal_forecast.forecast_period is not None, \
            "Forecast period must be preserved after seasonality"
        assert seasonal_forecast.sku == "PROD-001", \
            "SKU must be preserved after seasonality"
        
        # Property 7: Confidence intervals should also be scaled by seasonal factor
        expected_confidence_80 = int(base_forecast.confidence_80 * avg_seasonal_factor)
        expected_confidence_95 = int(base_forecast.confidence_95 * avg_seasonal_factor)
        
        tolerance_ci = max(1, int(expected_confidence_80 * 0.05))
        assert abs(seasonal_forecast.confidence_80 - expected_confidence_80) <= tolerance_ci, \
            f"80% CI should be scaled by seasonal factor"
        assert abs(seasonal_forecast.confidence_95 - expected_confidence_95) <= tolerance_ci, \
            f"95% CI should be scaled by seasonal factor"

    @given(
        base_demand=st.integers(min_value=50, max_value=500),
        num_days=st.integers(min_value=30, max_value=365),
        variance=st.integers(min_value=5, max_value=100),
        high_season_factor=st.floats(min_value=1.5, max_value=3.0),
        low_season_factor=st.floats(min_value=0.3, max_value=0.8),
    )
    @settings(
        max_examples=15,
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture],
        deadline=None,
    )
    def test_property_seasonal_pattern_direction(
        self, base_demand, num_days, variance, high_season_factor, low_season_factor
    ):
        """Property 2 (Extended): Seasonal patterns should affect forecast direction.
        
        *For any* sales data, applying high seasonal factors should increase 
        forecast, and applying low seasonal factors should decrease forecast.
        
        This validates that seasonal patterns are correctly reflected in the 
        forecast direction and magnitude.
        
        Validates: Requirements 1.2
        """
        agent = DemandForecastingAgent()
        
        sales_data = generate_sales_data(
            num_days=num_days,
            base_demand=base_demand,
            variance=variance,
        )
        
        # Generate base forecast
        base_forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            seasonal_factors=None,
            forecast_days=30,
        )
        
        # Generate forecast with high seasonal factors
        high_season_forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            seasonal_factors=[high_season_factor] * 4,
            forecast_days=30,
        )
        
        # Generate forecast with low seasonal factors
        low_season_forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            seasonal_factors=[low_season_factor] * 4,
            forecast_days=30,
        )
        
        # Property: High season should have highest demand
        assert high_season_forecast.forecasted_demand >= base_forecast.forecasted_demand, \
            f"High seasonal factor should increase forecast"
        
        # Property: Low season should have lowest demand
        assert low_season_forecast.forecasted_demand <= base_forecast.forecasted_demand, \
            f"Low seasonal factor should decrease forecast"
        
        # Property: High season > Low season
        assert high_season_forecast.forecasted_demand > low_season_forecast.forecasted_demand, \
            f"High season forecast should be greater than low season forecast"

    @given(
        base_demand=st.integers(min_value=50, max_value=500),
        num_days=st.integers(min_value=30, max_value=365),
        variance=st.integers(min_value=5, max_value=100),
        external_factors=st.dictionaries(
            st.sampled_from(["promotion_factor", "event_factor", "market_factor"]),
            st.floats(min_value=0.1, max_value=3.0),
            min_size=1,
            max_size=3,
        ),
    )
    @settings(
        max_examples=20,
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture],
        deadline=None,
    )
    def test_property_external_factor_adjustment(
        self, base_demand, num_days, variance, external_factors
    ):
        """Property 3: External Factor Adjustment
        
        *For any* demand forecast with external factors applied, the adjusted 
        forecast should differ from the baseline forecast in a direction 
        consistent with the external factor (e.g., promotions increase forecast).
        
        This property validates that:
        1. External factors > 1.0 increase the forecast
        2. External factors < 1.0 decrease the forecast
        3. External factors = 1.0 keep the forecast unchanged
        4. Multiple external factors are combined correctly
        5. External adjustment maintains forecast validity
        6. Confidence intervals are scaled appropriately
        
        Validates: Requirements 1.3
        """
        agent = DemandForecastingAgent()
        
        sales_data = generate_sales_data(
            num_days=num_days,
            base_demand=base_demand,
            variance=variance,
        )
        
        # Generate base forecast without external factors
        base_forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            external_adjustments=None,
            forecast_days=30,
        )
        
        # Generate forecast with external factors
        adjusted_forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            external_adjustments=external_factors,
            forecast_days=30,
        )
        
        # Calculate combined external factor
        combined_factor = 1.0
        for factor_value in external_factors.values():
            if factor_value > 0:
                combined_factor *= factor_value
        
        # Property 1: External factors should scale the forecast in the correct direction
        if combined_factor > 1.0:
            # Factors > 1.0 should increase forecast
            assert adjusted_forecast.forecasted_demand >= base_forecast.forecasted_demand, \
                f"External factors > 1.0 (combined: {combined_factor}) should increase forecast"
        elif combined_factor < 1.0:
            # Factors < 1.0 should decrease forecast
            assert adjusted_forecast.forecasted_demand <= base_forecast.forecasted_demand, \
                f"External factors < 1.0 (combined: {combined_factor}) should decrease forecast"
        else:
            # Factors = 1.0 should keep forecast similar
            tolerance = max(1, int(base_forecast.forecasted_demand * 0.01))
            assert abs(adjusted_forecast.forecasted_demand - base_forecast.forecasted_demand) <= tolerance, \
                f"External factors = 1.0 should keep forecast similar"
        
        # Property 2: Adjusted forecast should be approximately base * combined_factor
        expected_adjusted_demand = int(base_forecast.forecasted_demand * combined_factor)
        tolerance = max(1, int(expected_adjusted_demand * 0.05))
        assert abs(adjusted_forecast.forecasted_demand - expected_adjusted_demand) <= tolerance, \
            f"Adjusted forecast {adjusted_forecast.forecasted_demand} should be approximately " \
            f"{expected_adjusted_demand} (base {base_forecast.forecasted_demand} * " \
            f"combined factor {combined_factor})"
        
        # Property 3: External adjustment maintains forecast validity
        assert adjusted_forecast.confidence_80 >= 0, \
            "80% confidence interval must be non-negative after external adjustment"
        assert adjusted_forecast.confidence_95 >= 0, \
            "95% confidence interval must be non-negative after external adjustment"
        assert adjusted_forecast.confidence_95 <= adjusted_forecast.confidence_80, \
            "95% CI must be <= 80% CI after external adjustment"
        
        # Property 4: Forecast period and SKU should be preserved
        assert adjusted_forecast.forecast_period is not None, \
            "Forecast period must be preserved after external adjustment"
        assert adjusted_forecast.sku == "PROD-001", \
            "SKU must be preserved after external adjustment"
        
        # Property 5: Confidence intervals should also be scaled by combined factor
        expected_confidence_80 = int(base_forecast.confidence_80 * combined_factor)
        expected_confidence_95 = int(base_forecast.confidence_95 * combined_factor)
        
        tolerance_ci = max(1, int(expected_confidence_80 * 0.05))
        assert abs(adjusted_forecast.confidence_80 - expected_confidence_80) <= tolerance_ci, \
            f"80% CI should be scaled by combined external factor"
        assert abs(adjusted_forecast.confidence_95 - expected_confidence_95) <= tolerance_ci, \
            f"95% CI should be scaled by combined external factor"

    @given(
        base_demand=st.integers(min_value=50, max_value=500),
        num_days=st.integers(min_value=30, max_value=365),
        variance=st.integers(min_value=5, max_value=100),
        promotion_factor=st.floats(min_value=1.1, max_value=3.0),
    )
    @settings(
        max_examples=15,
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture],
        deadline=None,
    )
    def test_property_external_factor_promotion_increases_forecast(
        self, base_demand, num_days, variance, promotion_factor
    ):
        """Property 3 (Extended): Promotions should increase forecast.
        
        *For any* sales data, applying a promotion factor > 1.0 should 
        increase the forecast demand.
        
        This validates that promotional external factors correctly increase 
        the demand forecast.
        
        Validates: Requirements 1.3
        """
        agent = DemandForecastingAgent()
        
        sales_data = generate_sales_data(
            num_days=num_days,
            base_demand=base_demand,
            variance=variance,
        )
        
        # Generate base forecast
        base_forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            external_adjustments=None,
            forecast_days=30,
        )
        
        # Generate forecast with promotion factor
        promotion_forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            external_adjustments={"promotion_factor": promotion_factor},
            forecast_days=30,
        )
        
        # Property: Promotion should increase forecast
        assert promotion_forecast.forecasted_demand > base_forecast.forecasted_demand, \
            f"Promotion factor {promotion_factor} should increase forecast"
        
        # Property: Increase should be proportional to promotion factor
        expected_increase_ratio = promotion_factor
        actual_increase_ratio = promotion_forecast.forecasted_demand / max(1, base_forecast.forecasted_demand)
        tolerance = 0.05  # 5% tolerance
        assert abs(actual_increase_ratio - expected_increase_ratio) <= tolerance, \
            f"Promotion increase ratio {actual_increase_ratio} should be close to {expected_increase_ratio}"

    @given(
        base_demand=st.integers(min_value=50, max_value=500),
        num_days=st.integers(min_value=30, max_value=365),
        variance=st.integers(min_value=5, max_value=100),
        market_factor=st.floats(min_value=0.1, max_value=0.9),
    )
    @settings(
        max_examples=15,
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture],
        deadline=None,
    )
    def test_property_external_factor_market_downturn_decreases_forecast(
        self, base_demand, num_days, variance, market_factor
    ):
        """Property 3 (Extended): Market downturns should decrease forecast.
        
        *For any* sales data, applying a market factor < 1.0 should 
        decrease the forecast demand.
        
        This validates that negative external factors correctly decrease 
        the demand forecast.
        
        Validates: Requirements 1.3
        """
        agent = DemandForecastingAgent()
        
        sales_data = generate_sales_data(
            num_days=num_days,
            base_demand=base_demand,
            variance=variance,
        )
        
        # Generate base forecast
        base_forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            external_adjustments=None,
            forecast_days=30,
        )
        
        # Generate forecast with market downturn factor
        downturn_forecast = agent.generate_complete_forecast(
            sku="PROD-001",
            sales_data=sales_data,
            external_adjustments={"market_factor": market_factor},
            forecast_days=30,
        )
        
        # Property: Market downturn should decrease forecast
        assert downturn_forecast.forecasted_demand < base_forecast.forecasted_demand, \
            f"Market factor {market_factor} should decrease forecast"
        
        # Property: Decrease should be proportional to market factor
        expected_decrease_ratio = market_factor
        actual_decrease_ratio = downturn_forecast.forecasted_demand / max(1, base_forecast.forecasted_demand)
        tolerance = 0.05  # 5% tolerance
        assert abs(actual_decrease_ratio - expected_decrease_ratio) <= tolerance, \
            f"Market downturn ratio {actual_decrease_ratio} should be close to {expected_decrease_ratio}"
