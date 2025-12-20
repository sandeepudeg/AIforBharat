"""Tests for Report Generation Agent.

Feature: supply-chain-optimizer, Property 19-23: Report Generation Properties
Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5
"""

from datetime import date, timedelta
from typing import List, Dict, Any
import random
import statistics
import pytest
from unittest.mock import MagicMock, patch
from hypothesis import given, strategies as st, settings, HealthCheck

from src.agents.report_generation_agent import ReportGenerationAgent
from src.models.report import Report, ReportType


@pytest.fixture
def agent():
    """Create a Report Generation Agent instance."""
    with patch("src.agents.report_generation_agent.get_s3_client"):
        with patch("src.agents.report_generation_agent.get_dynamodb_resource"):
            return ReportGenerationAgent()


def generate_inventory_data(
    num_records: int = 50,
    base_quantity: int = 100,
    variance: int = 30,
) -> List[Dict[str, Any]]:
    """Generate synthetic inventory data for testing.

    Args:
        num_records: Number of inventory records
        base_quantity: Base quantity level
        variance: Random variance in quantity

    Returns:
        List of inventory records
    """
    inventory_data = []
    for i in range(num_records):
        quantity = max(0, base_quantity + random.randint(-variance, variance))
        inventory_data.append({
            "sku": f"PROD-{i:03d}",
            "quantity_on_hand": quantity,
            "unit_cost": random.uniform(10, 100),
        })
    return inventory_data


def generate_forecast_data(
    num_records: int = 50,
    accuracy_rate: float = 0.85,
) -> List[Dict[str, Any]]:
    """Generate synthetic forecast data for testing.

    Args:
        num_records: Number of forecast records
        accuracy_rate: Accuracy rate of forecasts (0-1)

    Returns:
        List of forecast records
    """
    forecast_data = []
    for i in range(num_records):
        forecasted = random.randint(50, 200)
        # Generate actual based on accuracy rate
        error_factor = random.uniform(1 - (1 - accuracy_rate), 1 + (1 - accuracy_rate))
        actual = max(0, int(forecasted * error_factor))
        forecast_data.append({
            "sku": f"PROD-{i:03d}",
            "forecasted_demand": forecasted,
            "actual_demand": actual,
        })
    return forecast_data


def generate_supplier_data(
    num_records: int = 10,
    base_score: float = 85.0,
) -> List[Dict[str, Any]]:
    """Generate synthetic supplier data for testing.

    Args:
        num_records: Number of supplier records
        base_score: Base reliability score

    Returns:
        List of supplier records
    """
    supplier_data = []
    for i in range(num_records):
        score = max(0, min(100, base_score + random.uniform(-10, 10)))
        supplier_data.append({
            "supplier_id": f"SUP-{i:03d}",
            "reliability_score": score,
        })
    return supplier_data


class TestCalculateKPIs:
    """Test KPI calculation."""

    def test_calculate_kpis_with_valid_data(self, agent):
        """Test calculating KPIs with valid data."""
        inventory_data = generate_inventory_data(num_records=50)
        forecast_data = generate_forecast_data(num_records=50)
        supplier_data = generate_supplier_data(num_records=10)
        period_start = date.today() - timedelta(days=7)
        period_end = date.today()

        kpis = agent.calculate_kpis(
            inventory_data, forecast_data, supplier_data, period_start, period_end
        )

        assert "inventory_turnover" in kpis
        assert "stockout_rate" in kpis
        assert "supplier_performance_score" in kpis
        assert "forecast_accuracy" in kpis
        assert kpis["inventory_turnover"] >= 0
        assert 0 <= kpis["stockout_rate"] <= 1
        assert 0 <= kpis["supplier_performance_score"] <= 100
        assert 0 <= kpis["forecast_accuracy"] <= 100

    def test_calculate_kpis_with_empty_data(self, agent):
        """Test calculating KPIs with empty data."""
        kpis = agent.calculate_kpis([], [], [], date.today(), date.today())

        assert kpis["inventory_turnover"] == 0.0
        assert kpis["stockout_rate"] == 0.0
        assert kpis["supplier_performance_score"] == 0.0
        assert kpis["forecast_accuracy"] == 0.0

    def test_calculate_kpis_with_high_stockout_rate(self, agent):
        """Test KPI calculation with high stockout rate."""
        # Create inventory data with many zero quantities
        inventory_data = [{"sku": f"PROD-{i}", "quantity_on_hand": 0, "unit_cost": 50}
                         for i in range(30)]
        inventory_data += [{"sku": f"PROD-{i}", "quantity_on_hand": 100, "unit_cost": 50}
                          for i in range(30, 50)]
        forecast_data = generate_forecast_data(num_records=50)
        supplier_data = generate_supplier_data(num_records=10)

        kpis = agent.calculate_kpis(
            inventory_data, forecast_data, supplier_data, date.today(), date.today()
        )

        assert kpis["stockout_rate"] > 0.5  # Should be high

    def test_calculate_kpis_with_perfect_forecast(self, agent):
        """Test KPI calculation with perfect forecast accuracy."""
        inventory_data = generate_inventory_data(num_records=50)
        # Create forecast data with perfect accuracy
        forecast_data = [
            {"sku": f"PROD-{i}", "forecasted_demand": 100, "actual_demand": 100}
            for i in range(50)
        ]
        supplier_data = generate_supplier_data(num_records=10)

        kpis = agent.calculate_kpis(
            inventory_data, forecast_data, supplier_data, date.today(), date.today()
        )

        assert kpis["forecast_accuracy"] == 100.0


class TestGenerateReport:
    """Test report generation."""

    def test_generate_report_basic(self, agent):
        """Test generating a basic report."""
        kpis = {
            "inventory_turnover": 4.5,
            "stockout_rate": 0.02,
            "supplier_performance_score": 92.0,
            "forecast_accuracy": 88.5,
        }

        report = agent.generate_report(
            report_type=ReportType.WEEKLY,
            period_start=date.today() - timedelta(days=7),
            period_end=date.today(),
            kpis=kpis,
        )

        assert isinstance(report, Report)
        assert report.report_type == ReportType.WEEKLY
        assert report.inventory_turnover == 4.5
        assert report.stockout_rate == 0.02
        assert report.supplier_performance_score == 92.0
        assert report.forecast_accuracy == 88.5
        assert report.generated_by == "Report Generation Agent"

    def test_generate_report_with_recommendations(self, agent):
        """Test generating report with recommendations."""
        kpis = {
            "inventory_turnover": 4.5,
            "stockout_rate": 0.02,
            "supplier_performance_score": 92.0,
            "forecast_accuracy": 88.5,
        }
        recommendations = ["Increase safety stock", "Review supplier contracts"]

        report = agent.generate_report(
            report_type=ReportType.MONTHLY,
            period_start=date.today() - timedelta(days=30),
            period_end=date.today(),
            kpis=kpis,
            recommendations=recommendations,
        )

        assert len(report.recommendations) == 2
        assert "Increase safety stock" in report.recommendations

    def test_generate_report_with_cost_savings(self, agent):
        """Test generating report with cost savings."""
        kpis = {
            "inventory_turnover": 4.5,
            "stockout_rate": 0.02,
            "supplier_performance_score": 92.0,
            "forecast_accuracy": 88.5,
        }

        report = agent.generate_report(
            report_type=ReportType.DAILY,
            period_start=date.today(),
            period_end=date.today(),
            kpis=kpis,
            cost_savings=5000.0,
        )

        assert report.cost_savings == 5000.0

    def test_generate_report_all_types(self, agent):
        """Test generating reports of all types."""
        kpis = {
            "inventory_turnover": 4.5,
            "stockout_rate": 0.02,
            "supplier_performance_score": 92.0,
            "forecast_accuracy": 88.5,
        }

        for report_type in ReportType:
            report = agent.generate_report(
                report_type=report_type,
                period_start=date.today(),
                period_end=date.today(),
                kpis=kpis,
            )

            assert report.report_type == report_type


class TestCreateVisualizations:
    """Test visualization creation."""

    def test_create_visualizations_basic(self, agent):
        """Test creating basic visualizations."""
        report = Report(
            report_id="RPT-001",
            report_type=ReportType.WEEKLY,
            period_start=date.today() - timedelta(days=7),
            period_end=date.today(),
            inventory_turnover=4.5,
            stockout_rate=0.02,
            supplier_performance_score=92.0,
            forecast_accuracy=88.5,
            generated_by="Report Generation Agent",
        )

        visualizations = agent.create_visualizations(report)

        assert "charts" in visualizations
        assert "data_points" in visualizations
        assert "visualization_types" in visualizations
        assert len(visualizations["charts"]) > 0
        assert len(visualizations["visualization_types"]) > 0

    def test_create_visualizations_with_historical_data(self, agent):
        """Test creating visualizations with historical data."""
        report = Report(
            report_id="RPT-001",
            report_type=ReportType.WEEKLY,
            period_start=date.today() - timedelta(days=7),
            period_end=date.today(),
            inventory_turnover=4.5,
            stockout_rate=0.02,
            supplier_performance_score=92.0,
            forecast_accuracy=88.5,
            generated_by="Report Generation Agent",
        )
        historical_data = {
            "inventory_turnover": [4.0, 4.2, 4.5],
            "forecast_accuracy": [85.0, 86.5, 88.5],
        }

        visualizations = agent.create_visualizations(report, historical_data)

        assert visualizations["data_points"] > 0
        assert "line" in visualizations["visualization_types"]

    def test_create_visualizations_includes_all_chart_types(self, agent):
        """Test that visualizations include all expected chart types."""
        report = Report(
            report_id="RPT-001",
            report_type=ReportType.WEEKLY,
            period_start=date.today() - timedelta(days=7),
            period_end=date.today(),
            inventory_turnover=4.5,
            stockout_rate=0.02,
            supplier_performance_score=92.0,
            forecast_accuracy=88.5,
            generated_by="Report Generation Agent",
        )

        visualizations = agent.create_visualizations(report)

        assert "bar" in visualizations["visualization_types"]
        assert "gauge" in visualizations["visualization_types"]


class TestComparePeriods:
    """Test period-over-period comparison."""

    def test_compare_periods_improving_metrics(self, agent):
        """Test comparing periods with improving metrics."""
        current_kpis = {
            "inventory_turnover": 5.0,
            "stockout_rate": 0.01,
            "supplier_performance_score": 95.0,
            "forecast_accuracy": 90.0,
        }
        previous_kpis = {
            "inventory_turnover": 4.0,
            "stockout_rate": 0.03,
            "supplier_performance_score": 90.0,
            "forecast_accuracy": 85.0,
        }

        comparison = agent.compare_periods(
            current_kpis,
            previous_kpis,
            date.today() - timedelta(days=7),
            date.today(),
            date.today() - timedelta(days=14),
            date.today() - timedelta(days=7),
        )

        assert "period_comparison" in comparison
        assert "trend_direction" in comparison
        assert "variance_percentage" in comparison
        # Stockout rate improved (lower is better)
        assert comparison["trend_direction"]["stockout_rate"] == "improving"
        # Other metrics improved (higher is better)
        assert comparison["trend_direction"]["inventory_turnover"] == "improving"

    def test_compare_periods_declining_metrics(self, agent):
        """Test comparing periods with declining metrics."""
        current_kpis = {
            "inventory_turnover": 3.0,
            "stockout_rate": 0.05,
            "supplier_performance_score": 80.0,
            "forecast_accuracy": 75.0,
        }
        previous_kpis = {
            "inventory_turnover": 4.0,
            "stockout_rate": 0.02,
            "supplier_performance_score": 90.0,
            "forecast_accuracy": 85.0,
        }

        comparison = agent.compare_periods(
            current_kpis,
            previous_kpis,
            date.today() - timedelta(days=7),
            date.today(),
            date.today() - timedelta(days=14),
            date.today() - timedelta(days=7),
        )

        # All metrics should be declining
        assert comparison["trend_direction"]["inventory_turnover"] == "declining"
        assert comparison["trend_direction"]["stockout_rate"] == "declining"

    def test_compare_periods_calculates_variance(self, agent):
        """Test that period comparison calculates variance correctly."""
        current_kpis = {
            "inventory_turnover": 5.0,
            "stockout_rate": 0.01,
            "supplier_performance_score": 95.0,
            "forecast_accuracy": 90.0,
        }
        previous_kpis = {
            "inventory_turnover": 4.0,
            "stockout_rate": 0.02,
            "supplier_performance_score": 90.0,
            "forecast_accuracy": 80.0,
        }

        comparison = agent.compare_periods(
            current_kpis,
            previous_kpis,
            date.today() - timedelta(days=7),
            date.today(),
            date.today() - timedelta(days=14),
            date.today() - timedelta(days=7),
        )

        # Inventory turnover: (5.0 - 4.0) / 4.0 * 100 = 25%
        assert comparison["variance_percentage"]["inventory_turnover"] == 25.0


class TestGenerateRecommendations:
    """Test recommendation generation."""

    def test_generate_recommendations_low_inventory_turnover(self, agent):
        """Test recommendations for low inventory turnover."""
        kpis = {
            "inventory_turnover": 1.5,
            "stockout_rate": 0.02,
            "supplier_performance_score": 92.0,
            "forecast_accuracy": 88.5,
        }

        recommendations = agent.generate_recommendations(kpis)

        assert len(recommendations) > 0
        assert any("inventory turnover" in rec.lower() for rec in recommendations)

    def test_generate_recommendations_high_stockout_rate(self, agent):
        """Test recommendations for high stockout rate."""
        kpis = {
            "inventory_turnover": 4.5,
            "stockout_rate": 0.10,
            "supplier_performance_score": 92.0,
            "forecast_accuracy": 88.5,
        }

        recommendations = agent.generate_recommendations(kpis)

        assert len(recommendations) > 0
        assert any("stockout" in rec.lower() for rec in recommendations)

    def test_generate_recommendations_low_supplier_score(self, agent):
        """Test recommendations for low supplier performance."""
        kpis = {
            "inventory_turnover": 4.5,
            "stockout_rate": 0.02,
            "supplier_performance_score": 70.0,
            "forecast_accuracy": 88.5,
        }

        recommendations = agent.generate_recommendations(kpis)

        assert len(recommendations) > 0
        assert any("supplier" in rec.lower() for rec in recommendations)

    def test_generate_recommendations_low_forecast_accuracy(self, agent):
        """Test recommendations for low forecast accuracy."""
        kpis = {
            "inventory_turnover": 4.5,
            "stockout_rate": 0.02,
            "supplier_performance_score": 92.0,
            "forecast_accuracy": 60.0,
        }

        recommendations = agent.generate_recommendations(kpis)

        assert len(recommendations) > 0
        assert any("forecast" in rec.lower() for rec in recommendations)

    def test_generate_recommendations_with_anomalies(self, agent):
        """Test recommendations with anomalies."""
        kpis = {
            "inventory_turnover": 4.5,
            "stockout_rate": 0.02,
            "supplier_performance_score": 92.0,
            "forecast_accuracy": 88.5,
        }
        anomalies = [
            {
                "severity": "critical",
                "description": "Inventory shrinkage detected",
                "recommended_action": "Investigate immediately",
            }
        ]

        recommendations = agent.generate_recommendations(kpis, anomalies)

        assert len(recommendations) > 0
        assert any("critical" in rec.lower() for rec in recommendations)

    def test_generate_recommendations_with_trends(self, agent):
        """Test recommendations with trend information."""
        kpis = {
            "inventory_turnover": 4.5,
            "stockout_rate": 0.02,
            "supplier_performance_score": 92.0,
            "forecast_accuracy": 88.5,
        }
        trends = {
            "inventory_turnover": "declining",
            "forecast_accuracy": "improving",
        }

        recommendations = agent.generate_recommendations(kpis, trends=trends)

        assert len(recommendations) > 0


class TestCalculateInventoryTurnover:
    """Test inventory turnover calculation."""

    def test_calculate_inventory_turnover_with_valid_data(self, agent):
        """Test inventory turnover calculation with valid data."""
        inventory_data = [
            {"quantity": 100, "unit_cost": 50},
            {"quantity": 200, "unit_cost": 30},
            {"quantity": 150, "unit_cost": 40},
        ]

        turnover = agent._calculate_inventory_turnover(inventory_data)

        assert turnover > 0

    def test_calculate_inventory_turnover_with_empty_data(self, agent):
        """Test inventory turnover calculation with empty data."""
        turnover = agent._calculate_inventory_turnover([])

        assert turnover == 0.0

    def test_calculate_inventory_turnover_with_zero_cost(self, agent):
        """Test inventory turnover calculation with zero cost items."""
        inventory_data = [
            {"quantity": 100, "unit_cost": 0},
            {"quantity": 200, "unit_cost": 0},
        ]

        turnover = agent._calculate_inventory_turnover(inventory_data)

        assert turnover == 0.0


class TestCalculateStockoutRate:
    """Test stockout rate calculation."""

    def test_calculate_stockout_rate_with_no_stockouts(self, agent):
        """Test stockout rate with no stockouts."""
        inventory_data = [
            {"quantity_on_hand": 100},
            {"quantity_on_hand": 200},
            {"quantity_on_hand": 150},
        ]

        rate = agent._calculate_stockout_rate(inventory_data)

        assert rate == 0.0

    def test_calculate_stockout_rate_with_all_stockouts(self, agent):
        """Test stockout rate with all stockouts."""
        inventory_data = [
            {"quantity_on_hand": 0},
            {"quantity_on_hand": 0},
            {"quantity_on_hand": 0},
        ]

        rate = agent._calculate_stockout_rate(inventory_data)

        assert rate == 1.0

    def test_calculate_stockout_rate_with_partial_stockouts(self, agent):
        """Test stockout rate with partial stockouts."""
        inventory_data = [
            {"quantity_on_hand": 0},
            {"quantity_on_hand": 100},
            {"quantity_on_hand": 0},
            {"quantity_on_hand": 200},
        ]

        rate = agent._calculate_stockout_rate(inventory_data)

        assert rate == 0.5

    def test_calculate_stockout_rate_with_empty_data(self, agent):
        """Test stockout rate with empty data."""
        rate = agent._calculate_stockout_rate([])

        assert rate == 0.0


class TestCalculateSupplierPerformance:
    """Test supplier performance calculation."""

    def test_calculate_supplier_performance_with_valid_data(self, agent):
        """Test supplier performance calculation with valid data."""
        supplier_data = [
            {"reliability_score": 90},
            {"reliability_score": 85},
            {"reliability_score": 95},
        ]

        score = agent._calculate_supplier_performance(supplier_data)

        assert score == 90.0

    def test_calculate_supplier_performance_with_empty_data(self, agent):
        """Test supplier performance calculation with empty data."""
        score = agent._calculate_supplier_performance([])

        assert score == 0.0

    def test_calculate_supplier_performance_with_perfect_scores(self, agent):
        """Test supplier performance with perfect scores."""
        supplier_data = [
            {"reliability_score": 100},
            {"reliability_score": 100},
            {"reliability_score": 100},
        ]

        score = agent._calculate_supplier_performance(supplier_data)

        assert score == 100.0


class TestCalculateForecastAccuracy:
    """Test forecast accuracy calculation."""

    def test_calculate_forecast_accuracy_perfect_forecast(self, agent):
        """Test forecast accuracy with perfect forecasts."""
        forecast_data = [
            {"forecasted_demand": 100, "actual_demand": 100},
            {"forecasted_demand": 200, "actual_demand": 200},
            {"forecasted_demand": 150, "actual_demand": 150},
        ]

        accuracy = agent._calculate_forecast_accuracy(forecast_data)

        assert accuracy == 100.0

    def test_calculate_forecast_accuracy_with_errors(self, agent):
        """Test forecast accuracy with forecast errors."""
        forecast_data = [
            {"forecasted_demand": 100, "actual_demand": 110},
            {"forecasted_demand": 200, "actual_demand": 180},
            {"forecasted_demand": 150, "actual_demand": 150},
        ]

        accuracy = agent._calculate_forecast_accuracy(forecast_data)

        assert 0 <= accuracy <= 100

    def test_calculate_forecast_accuracy_with_zero_actual(self, agent):
        """Test forecast accuracy when actual demand is zero."""
        forecast_data = [
            {"forecasted_demand": 0, "actual_demand": 0},
            {"forecasted_demand": 100, "actual_demand": 0},
        ]

        accuracy = agent._calculate_forecast_accuracy(forecast_data)

        # First record: 100% accurate (both 0)
        # Second record: 0% accurate (forecast 100, actual 0)
        # Average: 50%
        assert accuracy == 50.0

    def test_calculate_forecast_accuracy_with_empty_data(self, agent):
        """Test forecast accuracy with empty data."""
        accuracy = agent._calculate_forecast_accuracy([])

        assert accuracy == 0.0


class TestGenerateCompleteReport:
    """Test complete report generation workflow."""

    def test_generate_complete_report_basic(self, agent):
        """Test generating a complete report."""
        inventory_data = generate_inventory_data(num_records=50)
        forecast_data = generate_forecast_data(num_records=50)
        supplier_data = generate_supplier_data(num_records=10)

        with patch.object(agent, "store_report_in_s3", return_value="s3://bucket/key"):
            with patch.object(agent, "store_report_metadata_in_rds"):
                report = agent.generate_complete_report(
                    report_type=ReportType.WEEKLY,
                    period_start=date.today() - timedelta(days=7),
                    period_end=date.today(),
                    inventory_data=inventory_data,
                    forecast_data=forecast_data,
                    supplier_data=supplier_data,
                )

        assert isinstance(report, Report)
        assert report.report_type == ReportType.WEEKLY
        assert len(report.recommendations) > 0

    def test_generate_complete_report_with_anomalies(self, agent):
        """Test generating complete report with anomalies."""
        inventory_data = generate_inventory_data(num_records=50)
        forecast_data = generate_forecast_data(num_records=50)
        supplier_data = generate_supplier_data(num_records=10)
        anomalies = [
            {
                "severity": "high",
                "description": "Unusual inventory pattern",
                "recommended_action": "Review inventory",
            }
        ]

        with patch.object(agent, "store_report_in_s3", return_value="s3://bucket/key"):
            with patch.object(agent, "store_report_metadata_in_rds"):
                report = agent.generate_complete_report(
                    report_type=ReportType.MONTHLY,
                    period_start=date.today() - timedelta(days=30),
                    period_end=date.today(),
                    inventory_data=inventory_data,
                    forecast_data=forecast_data,
                    supplier_data=supplier_data,
                    anomalies=anomalies,
                )

        assert isinstance(report, Report)
        assert len(report.recommendations) > 0

    def test_generate_complete_report_with_period_comparison(self, agent):
        """Test generating complete report with period comparison."""
        inventory_data = generate_inventory_data(num_records=50)
        forecast_data = generate_forecast_data(num_records=50)
        supplier_data = generate_supplier_data(num_records=10)
        previous_kpis = {
            "inventory_turnover": 4.0,
            "stockout_rate": 0.03,
            "supplier_performance_score": 90.0,
            "forecast_accuracy": 85.0,
        }

        with patch.object(agent, "store_report_in_s3", return_value="s3://bucket/key"):
            with patch.object(agent, "store_report_metadata_in_rds"):
                report = agent.generate_complete_report(
                    report_type=ReportType.WEEKLY,
                    period_start=date.today() - timedelta(days=7),
                    period_end=date.today(),
                    inventory_data=inventory_data,
                    forecast_data=forecast_data,
                    supplier_data=supplier_data,
                    previous_period_kpis=previous_kpis,
                    previous_period_start=date.today() - timedelta(days=14),
                    previous_period_end=date.today() - timedelta(days=7),
                )

        assert isinstance(report, Report)
        assert len(report.recommendations) > 0



# Property-Based Tests using Hypothesis

@given(
    st.lists(
        st.fixed_dictionaries({
            "sku": st.text(min_size=1),
            "quantity_on_hand": st.integers(min_value=0, max_value=1000),
            "unit_cost": st.floats(min_value=0.01, max_value=1000),
        }),
        min_size=1,
        max_size=100,
    )
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
def test_property_report_generation_completeness(inventory_data):
    """Property 19: Report Generation Completeness.
    
    For any valid inventory, forecast, and supplier data, generating a report
    should produce a report containing all required KPI fields.
    
    Validates: Requirements 5.1
    """
    agent = ReportGenerationAgent()
    forecast_data = generate_forecast_data(num_records=len(inventory_data))
    supplier_data = generate_supplier_data(num_records=5)

    with patch.object(agent, "store_report_in_s3", return_value="s3://bucket/key"):
        with patch.object(agent, "store_report_metadata_in_rds"):
            report = agent.generate_complete_report(
                report_type=ReportType.WEEKLY,
                period_start=date.today() - timedelta(days=7),
                period_end=date.today(),
                inventory_data=inventory_data,
                forecast_data=forecast_data,
                supplier_data=supplier_data,
            )

    # All required fields must be present
    assert report.report_id is not None
    assert report.inventory_turnover >= 0
    assert 0 <= report.stockout_rate <= 1
    assert 0 <= report.supplier_performance_score <= 100
    assert 0 <= report.forecast_accuracy <= 100


@given(
    report_kpis=st.fixed_dictionaries({
        "inventory_turnover": st.floats(min_value=0.1, max_value=20),
        "stockout_rate": st.floats(min_value=0, max_value=0.1),
        "supplier_performance_score": st.floats(min_value=50, max_value=100),
        "forecast_accuracy": st.floats(min_value=50, max_value=100),
    }),
    include_historical_data=st.booleans(),
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_report_visualization_inclusion(report_kpis, include_historical_data):
    """Property 20: Report Visualization Inclusion.
    
    For any generated report, the visualizations should include all required
    chart types (bar, gauge, and optionally line for trends). When historical
    data is provided, trend visualizations should be included.
    
    Validates: Requirements 5.2
    """
    agent = ReportGenerationAgent()
    
    # Create a report with the generated KPI values
    report = Report(
        report_id="RPT-001",
        report_type=ReportType.WEEKLY,
        period_start=date.today() - timedelta(days=7),
        period_end=date.today(),
        inventory_turnover=report_kpis["inventory_turnover"],
        stockout_rate=report_kpis["stockout_rate"],
        supplier_performance_score=report_kpis["supplier_performance_score"],
        forecast_accuracy=report_kpis["forecast_accuracy"],
        generated_by="Report Generation Agent",
    )

    # Optionally include historical data for trend visualization
    historical_data = None
    if include_historical_data:
        historical_data = {
            "inventory_turnover": [random.uniform(0.1, 20) for _ in range(5)],
            "stockout_rate": [random.uniform(0, 0.1) for _ in range(5)],
            "forecast_accuracy": [random.uniform(50, 100) for _ in range(5)],
        }

    visualizations = agent.create_visualizations(report, historical_data)

    # Visualizations must include required structure
    assert "charts" in visualizations, "Visualizations must have 'charts' key"
    assert "data_points" in visualizations, "Visualizations must have 'data_points' key"
    assert "visualization_types" in visualizations, "Visualizations must have 'visualization_types' key"
    
    # Charts must be a non-empty list
    assert isinstance(visualizations["charts"], list), "Charts must be a list"
    assert len(visualizations["charts"]) > 0, "Charts list must not be empty"
    
    # Visualization types must be a non-empty list
    assert isinstance(visualizations["visualization_types"], list), "Visualization types must be a list"
    assert len(visualizations["visualization_types"]) > 0, "Visualization types list must not be empty"
    
    # All required chart types must be present
    assert "bar" in visualizations["visualization_types"], \
        "Bar chart (KPI summary) must be included in visualizations"
    assert "gauge" in visualizations["visualization_types"], \
        "Gauge chart (performance score) must be included in visualizations"
    
    # If historical data provided, line chart should be included
    if include_historical_data and historical_data:
        assert "line" in visualizations["visualization_types"], \
            "Line chart (trends) must be included when historical data is provided"
        assert visualizations["data_points"] > 0, \
            "Data points count must be greater than 0 when historical data is provided"
    
    # Each chart must have required fields
    for chart in visualizations["charts"]:
        assert "type" in chart, "Each chart must have a 'type' field"
        assert "title" in chart, "Each chart must have a 'title' field"
        assert isinstance(chart["type"], str), "Chart type must be a string"
        assert isinstance(chart["title"], str), "Chart title must be a string"
        assert len(chart["title"]) > 0, "Chart title must not be empty"
        assert chart["type"] in visualizations["visualization_types"], \
            "Chart type must be in visualization_types list"
        
        # Validate chart-specific fields
        if chart["type"] == "bar":
            assert "metrics" in chart, "Bar chart must have 'metrics' field"
            assert isinstance(chart["metrics"], dict), "Bar chart metrics must be a dictionary"
            assert len(chart["metrics"]) > 0, "Bar chart must contain at least one metric"
        
        elif chart["type"] == "gauge":
            assert "value" in chart, "Gauge chart must have 'value' field"
            assert isinstance(chart["value"], (int, float)), "Gauge value must be numeric"
            assert 0 <= chart["value"] <= 100, "Gauge value should be between 0 and 100"
        
        elif chart["type"] == "line":
            assert "data" in chart, "Line chart must have 'data' field"
            assert isinstance(chart["data"], dict), "Line chart data must be a dictionary"
            assert len(chart["data"]) > 0, "Line chart must contain at least one data series"


@given(
    current_kpis=st.fixed_dictionaries({
        "inventory_turnover": st.floats(min_value=0, max_value=20),
        "stockout_rate": st.floats(min_value=0, max_value=1),
        "supplier_performance_score": st.floats(min_value=0, max_value=100),
        "forecast_accuracy": st.floats(min_value=0, max_value=100),
    }),
    previous_kpis=st.fixed_dictionaries({
        "inventory_turnover": st.floats(min_value=0, max_value=20),
        "stockout_rate": st.floats(min_value=0, max_value=1),
        "supplier_performance_score": st.floats(min_value=0, max_value=100),
        "forecast_accuracy": st.floats(min_value=0, max_value=100),
    }),
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
def test_property_period_comparison(current_kpis, previous_kpis):
    """Property 21: Period Comparison.
    
    For any two sets of KPIs from different periods, comparing them should
    produce variance percentages and trend directions for all metrics.
    
    Validates: Requirements 5.3
    """
    agent = ReportGenerationAgent()

    comparison = agent.compare_periods(
        current_kpis,
        previous_kpis,
        date.today() - timedelta(days=7),
        date.today(),
        date.today() - timedelta(days=14),
        date.today() - timedelta(days=7),
    )

    # Comparison must include all required fields
    assert "period_comparison" in comparison
    assert "trend_direction" in comparison
    assert "variance_percentage" in comparison

    # All metrics must have trend direction
    for metric in current_kpis.keys():
        assert metric in comparison["trend_direction"]
        assert comparison["trend_direction"][metric] in ["improving", "declining"]
        assert metric in comparison["variance_percentage"]


@given(
    st.lists(
        st.fixed_dictionaries({
            "sku": st.text(min_size=1),
            "quantity_on_hand": st.integers(min_value=0, max_value=1000),
            "unit_cost": st.floats(min_value=0.01, max_value=1000),
        }),
        min_size=1,
        max_size=50,
    )
)
@settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
def test_property_report_generation_performance(inventory_data):
    """Property 22: Report Generation Performance.
    
    For any valid input data, generating a report should complete within
    reasonable time bounds (5 seconds for standard reports).
    
    Validates: Requirements 5.4
    """
    import time
    
    agent = ReportGenerationAgent()
    forecast_data = generate_forecast_data(num_records=len(inventory_data))
    supplier_data = generate_supplier_data(num_records=5)

    start_time = time.time()

    with patch.object(agent, "store_report_in_s3", return_value="s3://bucket/key"):
        with patch.object(agent, "store_report_metadata_in_rds"):
            report = agent.generate_complete_report(
                report_type=ReportType.WEEKLY,
                period_start=date.today() - timedelta(days=7),
                period_end=date.today(),
                inventory_data=inventory_data,
                forecast_data=forecast_data,
                supplier_data=supplier_data,
            )

    elapsed_time = time.time() - start_time

    # Report generation should complete within 5 seconds
    assert elapsed_time < 5.0
    assert report is not None


@given(
    kpis=st.fixed_dictionaries({
        "inventory_turnover": st.floats(min_value=0, max_value=20),
        "stockout_rate": st.floats(min_value=0, max_value=1),
        "supplier_performance_score": st.floats(min_value=0, max_value=100),
        "forecast_accuracy": st.floats(min_value=0, max_value=100),
    })
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
def test_property_report_recommendations(kpis):
    """Property 23: Report Recommendations.
    
    For any set of KPIs, generating recommendations should produce a list
    of actionable recommendations based on the KPI values.
    
    Validates: Requirements 5.5
    """
    agent = ReportGenerationAgent()

    recommendations = agent.generate_recommendations(kpis)

    # Recommendations should be a list
    assert isinstance(recommendations, list)
    # Recommendations should be strings
    for rec in recommendations:
        assert isinstance(rec, str)
        assert len(rec) > 0
