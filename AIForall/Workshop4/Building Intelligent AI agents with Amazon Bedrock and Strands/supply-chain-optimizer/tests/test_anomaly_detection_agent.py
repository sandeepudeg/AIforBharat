"""Tests for Anomaly Detection Agent.

Feature: supply-chain-optimizer, Property 14-18: Anomaly Detection
Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5
"""

from datetime import date, timedelta
from typing import List, Dict, Any
import random
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck

from src.agents.anomaly_detection_agent import AnomalyDetectionAgent
from src.models.anomaly import AnomalyType, SeverityLevel, AnomalyStatus


@pytest.fixture
def agent():
    """Create an Anomaly Detection Agent instance."""
    return AnomalyDetectionAgent()


class TestDetectInventoryAnomaly:
    """Test inventory anomaly detection."""

    def test_detect_inventory_anomaly_below_forecast(self, agent):
        """Test detecting inventory below forecast."""
        anomaly = agent.detect_inventory_anomaly(
            sku="PROD-001",
            current_inventory=300,
            forecasted_inventory=500,
            confidence_80=100,
            confidence_95=150,
            warehouse_id="WH-001",
        )

        assert anomaly is not None
        assert anomaly["anomaly_type"] == AnomalyType.INVENTORY_DEVIATION.value
        assert anomaly["sku"] == "PROD-001"
        assert anomaly["warehouse_id"] == "WH-001"
        assert "anomaly_id" in anomaly
        assert "severity" in anomaly
        assert "confidence_score" in anomaly
        assert "description" in anomaly
        assert "root_cause" in anomaly
        assert "recommended_action" in anomaly

    def test_detect_inventory_anomaly_above_forecast(self, agent):
        """Test detecting inventory above forecast."""
        anomaly = agent.detect_inventory_anomaly(
            sku="PROD-001",
            current_inventory=800,
            forecasted_inventory=500,
            confidence_80=100,
            confidence_95=150,
        )

        assert anomaly is not None
        assert anomaly["anomaly_type"] == AnomalyType.INVENTORY_DEVIATION.value
        assert "ABOVE" in anomaly["description"]

    def test_detect_inventory_anomaly_within_bounds(self, agent):
        """Test no anomaly when inventory within confidence bounds."""
        anomaly = agent.detect_inventory_anomaly(
            sku="PROD-001",
            current_inventory=450,
            forecasted_inventory=500,
            confidence_80=100,
            confidence_95=150,
        )

        assert anomaly is None

    def test_detect_inventory_anomaly_critical_severity(self, agent):
        """Test critical severity for large deviation."""
        anomaly = agent.detect_inventory_anomaly(
            sku="PROD-001",
            current_inventory=100,
            forecasted_inventory=500,
            confidence_80=50,
            confidence_95=100,
        )

        assert anomaly is not None
        assert anomaly["severity"] == SeverityLevel.CRITICAL.value

    def test_detect_inventory_anomaly_invalid_sku(self, agent):
        """Test with invalid SKU."""
        with pytest.raises(ValueError):
            agent.detect_inventory_anomaly(
                sku="",
                current_inventory=300,
                forecasted_inventory=500,
                confidence_80=100,
                confidence_95=150,
            )

    def test_detect_inventory_anomaly_negative_inventory(self, agent):
        """Test with negative inventory."""
        with pytest.raises(ValueError):
            agent.detect_inventory_anomaly(
                sku="PROD-001",
                current_inventory=-100,
                forecasted_inventory=500,
                confidence_80=100,
                confidence_95=150,
            )

    def test_detect_inventory_anomaly_negative_confidence(self, agent):
        """Test with negative confidence interval."""
        with pytest.raises(ValueError):
            agent.detect_inventory_anomaly(
                sku="PROD-001",
                current_inventory=300,
                forecasted_inventory=500,
                confidence_80=-100,
                confidence_95=150,
            )


class TestDetectSupplierAnomaly:
    """Test supplier anomaly detection."""

    def test_detect_supplier_anomaly_degraded_performance(self, agent):
        """Test detecting supplier performance degradation."""
        anomaly = agent.detect_supplier_anomaly(
            supplier_id="SUP-001",
            on_time_delivery_rate=0.70,
            average_delivery_days=10,
            expected_lead_time=7,
            historical_on_time_rate=0.95,
        )

        assert anomaly is not None
        assert anomaly["anomaly_type"] == AnomalyType.SUPPLIER_DELAY.value
        assert anomaly["sku"] == "SUP-001"
        assert "anomaly_id" in anomaly
        assert "severity" in anomaly
        assert "confidence_score" in anomaly

    def test_detect_supplier_anomaly_good_performance(self, agent):
        """Test no anomaly with good supplier performance."""
        anomaly = agent.detect_supplier_anomaly(
            supplier_id="SUP-001",
            on_time_delivery_rate=0.95,
            average_delivery_days=7,
            expected_lead_time=7,
            historical_on_time_rate=0.95,
        )

        assert anomaly is None

    def test_detect_supplier_anomaly_critical_severity(self, agent):
        """Test critical severity for severe degradation."""
        anomaly = agent.detect_supplier_anomaly(
            supplier_id="SUP-001",
            on_time_delivery_rate=0.50,
            average_delivery_days=15,
            expected_lead_time=7,
            historical_on_time_rate=0.95,
        )

        assert anomaly is not None
        assert anomaly["severity"] == SeverityLevel.CRITICAL.value

    def test_detect_supplier_anomaly_invalid_supplier_id(self, agent):
        """Test with invalid supplier ID."""
        with pytest.raises(ValueError):
            agent.detect_supplier_anomaly(
                supplier_id="",
                on_time_delivery_rate=0.70,
                average_delivery_days=10,
                expected_lead_time=7,
                historical_on_time_rate=0.95,
            )

    def test_detect_supplier_anomaly_invalid_delivery_rate(self, agent):
        """Test with invalid delivery rate."""
        with pytest.raises(ValueError):
            agent.detect_supplier_anomaly(
                supplier_id="SUP-001",
                on_time_delivery_rate=1.5,
                average_delivery_days=10,
                expected_lead_time=7,
                historical_on_time_rate=0.95,
            )


class TestDetectDemandSpike:
    """Test demand spike detection."""

    def test_detect_demand_spike_above_confidence(self, agent):
        """Test detecting demand spike above confidence interval."""
        anomaly = agent.detect_demand_spike(
            sku="PROD-001",
            current_demand=1500,
            forecasted_demand=1000,
            confidence_95=200,
        )

        assert anomaly is not None
        assert anomaly["anomaly_type"] == AnomalyType.DEMAND_SPIKE.value
        assert anomaly["sku"] == "PROD-001"
        assert "anomaly_id" in anomaly
        assert "severity" in anomaly

    def test_detect_demand_spike_within_bounds(self, agent):
        """Test no spike when demand within confidence bounds."""
        anomaly = agent.detect_demand_spike(
            sku="PROD-001",
            current_demand=1100,
            forecasted_demand=1000,
            confidence_95=200,
        )

        assert anomaly is None

    def test_detect_demand_spike_critical_severity(self, agent):
        """Test critical severity for large spike."""
        anomaly = agent.detect_demand_spike(
            sku="PROD-001",
            current_demand=2500,
            forecasted_demand=1000,
            confidence_95=200,
        )

        assert anomaly is not None
        assert anomaly["severity"] == SeverityLevel.CRITICAL.value

    def test_detect_demand_spike_invalid_sku(self, agent):
        """Test with invalid SKU."""
        with pytest.raises(ValueError):
            agent.detect_demand_spike(
                sku="",
                current_demand=1500,
                forecasted_demand=1000,
                confidence_95=200,
            )

    def test_detect_demand_spike_negative_demand(self, agent):
        """Test with negative demand."""
        with pytest.raises(ValueError):
            agent.detect_demand_spike(
                sku="PROD-001",
                current_demand=-100,
                forecasted_demand=1000,
                confidence_95=200,
            )


class TestAnalyzeRootCause:
    """Test root cause analysis."""

    def test_analyze_root_cause_inventory_deviation(self, agent):
        """Test root cause analysis for inventory deviation."""
        analysis = agent.analyze_root_cause(
            anomaly_type=AnomalyType.INVENTORY_DEVIATION.value,
            sku="PROD-001",
            current_value=300,
            expected_value=500,
        )

        assert analysis["anomaly_type"] == AnomalyType.INVENTORY_DEVIATION.value
        assert analysis["sku"] == "PROD-001"
        assert "deviation" in analysis
        assert "deviation_percentage" in analysis
        assert "possible_causes" in analysis
        assert len(analysis["possible_causes"]) > 0
        assert "confidence_level" in analysis

    def test_analyze_root_cause_supplier_delay(self, agent):
        """Test root cause analysis for supplier delay."""
        analysis = agent.analyze_root_cause(
            anomaly_type=AnomalyType.SUPPLIER_DELAY.value,
            sku="SUP-001",
            current_value=10,
            expected_value=7,
        )

        assert analysis["anomaly_type"] == AnomalyType.SUPPLIER_DELAY.value
        assert len(analysis["possible_causes"]) > 0

    def test_analyze_root_cause_demand_spike(self, agent):
        """Test root cause analysis for demand spike."""
        analysis = agent.analyze_root_cause(
            anomaly_type=AnomalyType.DEMAND_SPIKE.value,
            sku="PROD-001",
            current_value=1500,
            expected_value=1000,
        )

        assert analysis["anomaly_type"] == AnomalyType.DEMAND_SPIKE.value
        assert len(analysis["possible_causes"]) > 0

    def test_analyze_root_cause_with_historical_data(self, agent):
        """Test root cause analysis with historical data."""
        historical_data = [100, 110, 105, 108, 102, 500]  # Last value is outlier

        analysis = agent.analyze_root_cause(
            anomaly_type=AnomalyType.INVENTORY_DEVIATION.value,
            sku="PROD-001",
            current_value=500,
            expected_value=105,
            historical_data=historical_data,
        )

        assert "trend_analysis" in analysis
        assert analysis["trend_analysis"] is not None
        assert "z_score" in analysis["trend_analysis"]
        assert analysis["trend_analysis"]["is_outlier"] is True

    def test_analyze_root_cause_invalid_anomaly_type(self, agent):
        """Test with invalid anomaly type."""
        with pytest.raises(ValueError):
            agent.analyze_root_cause(
                anomaly_type="",
                sku="PROD-001",
                current_value=300,
                expected_value=500,
            )


class TestGenerateRecommendations:
    """Test recommendation generation."""

    def test_generate_recommendations_inventory_low(self, agent):
        """Test recommendations for low inventory."""
        recommendations = agent.generate_recommendations(
            anomaly_type=AnomalyType.INVENTORY_DEVIATION.value,
            severity=SeverityLevel.HIGH.value,
            current_value=300,
            expected_value=500,
        )

        assert recommendations["anomaly_type"] == AnomalyType.INVENTORY_DEVIATION.value
        assert recommendations["severity"] == SeverityLevel.HIGH.value
        assert "immediate_actions" in recommendations
        assert "short_term_actions" in recommendations
        assert "long_term_actions" in recommendations
        assert len(recommendations["immediate_actions"]) > 0
        assert recommendations["priority_level"] > 0

    def test_generate_recommendations_supplier_delay(self, agent):
        """Test recommendations for supplier delay."""
        recommendations = agent.generate_recommendations(
            anomaly_type=AnomalyType.SUPPLIER_DELAY.value,
            severity=SeverityLevel.CRITICAL.value,
            current_value=10,
            expected_value=7,
        )

        assert recommendations["anomaly_type"] == AnomalyType.SUPPLIER_DELAY.value
        assert recommendations["priority_level"] == 5  # Critical = priority 5

    def test_generate_recommendations_demand_spike(self, agent):
        """Test recommendations for demand spike."""
        recommendations = agent.generate_recommendations(
            anomaly_type=AnomalyType.DEMAND_SPIKE.value,
            severity=SeverityLevel.HIGH.value,
            current_value=1500,
            expected_value=1000,
        )

        assert recommendations["anomaly_type"] == AnomalyType.DEMAND_SPIKE.value
        assert len(recommendations["immediate_actions"]) > 0

    def test_generate_recommendations_priority_levels(self, agent):
        """Test that priority levels are correct for each severity."""
        severity_priority_map = {
            SeverityLevel.LOW.value: 1,
            SeverityLevel.MEDIUM.value: 2,
            SeverityLevel.HIGH.value: 3,
            SeverityLevel.CRITICAL.value: 5,
        }

        for severity, expected_priority in severity_priority_map.items():
            recommendations = agent.generate_recommendations(
                anomaly_type=AnomalyType.INVENTORY_DEVIATION.value,
                severity=severity,
                current_value=300,
                expected_value=500,
            )
            assert recommendations["priority_level"] == expected_priority

    def test_generate_recommendations_invalid_anomaly_type(self, agent):
        """Test with invalid anomaly type."""
        with pytest.raises(ValueError):
            agent.generate_recommendations(
                anomaly_type="",
                severity=SeverityLevel.HIGH.value,
                current_value=300,
                expected_value=500,
            )


class TestInventoryDeviationDetectionPropertyBased:
    """Property-based tests for inventory deviation detection.
    
    Feature: supply-chain-optimizer, Property 14: Inventory Deviation Detection
    Validates: Requirements 4.1
    """

    @given(
        forecasted_inventory=st.integers(min_value=100, max_value=5000),
        confidence_95=st.integers(min_value=10, max_value=500),
        is_anomaly=st.booleans(),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow])
    def test_inventory_deviation_detection(self, agent, forecasted_inventory, confidence_95, is_anomaly):
        """Property: For any inventory level that deviates significantly from
        the forecasted level (beyond confidence intervals), the system should
        flag the deviation and provide root cause analysis.
        
        Property 14: Inventory Deviation Detection
        For any inventory level that deviates significantly from the forecasted 
        level (beyond confidence intervals), the system should flag the deviation 
        and provide root cause analysis.
        
        Validates: Requirements 4.1
        """
        # Generate current inventory based on whether we want an anomaly
        if is_anomaly:
            # Generate outside bounds
            if random.random() < 0.5:
                # Below lower bound
                current_inventory = max(0, forecasted_inventory - confidence_95 - random.randint(1, 100))
            else:
                # Above upper bound
                current_inventory = forecasted_inventory + confidence_95 + random.randint(1, 100)
        else:
            # Generate within bounds
            current_inventory = forecasted_inventory + random.randint(
                -confidence_95 + 1, confidence_95 - 1
            )
        
        anomaly = agent.detect_inventory_anomaly(
            sku="PROD-TEST",
            current_inventory=current_inventory,
            forecasted_inventory=forecasted_inventory,
            confidence_80=confidence_95 // 2,
            confidence_95=confidence_95,
        )

        # Calculate bounds
        lower_bound = forecasted_inventory - confidence_95
        upper_bound = forecasted_inventory + confidence_95

        # If within bounds, no anomaly should be detected
        if lower_bound <= current_inventory <= upper_bound:
            assert anomaly is None
        else:
            # If outside bounds, anomaly should be detected
            assert anomaly is not None
            assert anomaly["anomaly_type"] == AnomalyType.INVENTORY_DEVIATION.value
            assert anomaly["sku"] == "PROD-TEST"
            assert "severity" in anomaly
            assert 0 <= anomaly["confidence_score"] <= 1
            assert "description" in anomaly
            assert "root_cause" in anomaly
            assert "recommended_action" in anomaly


class TestSupplierPerformanceDegradationDetectionPropertyBased:
    """Property-based tests for supplier performance degradation detection.
    
    Feature: supply-chain-optimizer, Property 15: Supplier Performance Degradation Detection
    Validates: Requirements 4.2
    """

    @given(
        on_time_rate=st.floats(min_value=0, max_value=1),
        historical_rate=st.floats(min_value=0, max_value=1),
        avg_delivery_days=st.floats(min_value=0, max_value=30),
        expected_lead_time=st.floats(min_value=0, max_value=30),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_supplier_performance_degradation_detection(
        self, agent, on_time_rate, historical_rate, avg_delivery_days, expected_lead_time
    ):
        """Property: For any supplier with declining on-time delivery rate or
        increasing average delivery time, the system should alert the manager
        and suggest alternative suppliers.
        
        Property 15: Supplier Performance Degradation Detection
        For any supplier with declining on-time delivery rate or increasing 
        average delivery time, the system should alert the manager and suggest 
        alternative suppliers.
        
        Validates: Requirements 4.2
        """
        anomaly = agent.detect_supplier_anomaly(
            supplier_id="SUP-TEST",
            on_time_delivery_rate=on_time_rate,
            average_delivery_days=avg_delivery_days,
            expected_lead_time=expected_lead_time,
            historical_on_time_rate=historical_rate,
        )

        # Calculate degradation metrics
        rate_decline = historical_rate - on_time_rate
        delivery_delay = avg_delivery_days - expected_lead_time

        # If significant degradation, anomaly should be detected
        if rate_decline > 0.1 or delivery_delay > 2:
            assert anomaly is not None
            assert anomaly["anomaly_type"] == AnomalyType.SUPPLIER_DELAY.value
            assert anomaly["sku"] == "SUP-TEST"
            assert "severity" in anomaly
            assert 0 <= anomaly["confidence_score"] <= 1
        else:
            # If no significant degradation, no anomaly
            assert anomaly is None


class TestDemandSpikeDetectionPropertyBased:
    """Property-based tests for demand spike detection.
    
    Feature: supply-chain-optimizer, Property 16: Demand Spike Detection
    Validates: Requirements 4.3
    """

    @given(
        current_demand=st.integers(min_value=0, max_value=10000),
        forecasted_demand=st.integers(min_value=1, max_value=10000),
        confidence_95=st.integers(min_value=1, max_value=5000),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_demand_spike_detection(self, agent, current_demand, forecasted_demand, confidence_95):
        """Property: For any demand that exceeds the 95% confidence interval
        of the forecast, the system should identify it as a spike and recommend
        emergency procurement actions.
        
        Property 16: Demand Spike Detection
        For any demand that exceeds the 95% confidence interval of the forecast, 
        the system should identify it as a spike and recommend emergency 
        procurement actions.
        
        Validates: Requirements 4.3
        """
        anomaly = agent.detect_demand_spike(
            sku="PROD-TEST",
            current_demand=current_demand,
            forecasted_demand=forecasted_demand,
            confidence_95=confidence_95,
        )

        # Calculate upper bound
        upper_bound = forecasted_demand + confidence_95

        # If demand exceeds upper bound, spike should be detected
        if current_demand > upper_bound:
            assert anomaly is not None
            assert anomaly["anomaly_type"] == AnomalyType.DEMAND_SPIKE.value
            assert anomaly["sku"] == "PROD-TEST"
            assert "severity" in anomaly
            assert 0 <= anomaly["confidence_score"] <= 1
            assert "description" in anomaly
            assert "recommended_action" in anomaly
        else:
            # If within bounds, no spike
            assert anomaly is None


class TestInventoryShrinkageDetectionPropertyBased:
    """Property-based tests for inventory shrinkage detection.
    
    Feature: supply-chain-optimizer, Property 17: Inventory Shrinkage Detection
    Validates: Requirements 4.4
    """

    @given(
        system_records=st.integers(min_value=1, max_value=10000),
        actual_count=st.integers(min_value=0, max_value=10000),
        confidence_95=st.integers(min_value=100, max_value=5000),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_inventory_shrinkage_detection(self, agent, system_records, actual_count, confidence_95):
        """Property: For any inventory discrepancy where actual count differs
        from system records, the system should log the anomaly with severity
        level and recommend investigation.
        
        Property 17: Inventory Shrinkage Detection
        For any inventory discrepancy where actual count differs from system 
        records, the system should log the anomaly with severity level and 
        recommend investigation.
        
        Validates: Requirements 4.4
        """
        # Treat system_records as the forecasted/expected inventory
        # and actual_count as the current inventory
        anomaly = agent.detect_inventory_anomaly(
            sku="PROD-TEST",
            current_inventory=actual_count,
            forecasted_inventory=system_records,
            confidence_80=confidence_95 // 2,
            confidence_95=confidence_95,
        )

        # Calculate the discrepancy
        discrepancy = system_records - actual_count
        discrepancy_percentage = (
            (discrepancy / system_records * 100) if system_records > 0 else 0
        )

        # Calculate bounds
        lower_bound = system_records - confidence_95
        upper_bound = system_records + confidence_95

        # If there's a significant discrepancy (outside confidence bounds),
        # an anomaly should be detected
        if actual_count < lower_bound or actual_count > upper_bound:
            assert anomaly is not None, (
                f"Expected anomaly for discrepancy of {discrepancy_percentage:.1f}% "
                f"(actual={actual_count}, system_records={system_records})"
            )
            
            # Verify anomaly has all required fields for shrinkage detection
            assert "anomaly_id" in anomaly
            assert len(anomaly["anomaly_id"]) > 0
            
            assert "anomaly_type" in anomaly
            assert anomaly["anomaly_type"] == AnomalyType.INVENTORY_DEVIATION.value
            
            assert "sku" in anomaly
            assert anomaly["sku"] == "PROD-TEST"
            
            assert "severity" in anomaly
            assert anomaly["severity"] in [
                SeverityLevel.LOW.value,
                SeverityLevel.MEDIUM.value,
                SeverityLevel.HIGH.value,
                SeverityLevel.CRITICAL.value,
            ]
            
            assert "confidence_score" in anomaly
            assert 0 <= anomaly["confidence_score"] <= 1
            
            assert "description" in anomaly
            assert len(anomaly["description"]) > 0
            
            assert "root_cause" in anomaly
            assert len(anomaly["root_cause"]) > 0
            # For shrinkage (actual < system_records), root cause should mention shrinkage
            if actual_count < system_records:
                assert "shrinkage" in anomaly["root_cause"].lower() or \
                       "loss" in anomaly["root_cause"].lower() or \
                       "discrepancy" in anomaly["root_cause"].lower() or \
                       "error" in anomaly["root_cause"].lower()
            
            assert "recommended_action" in anomaly
            assert len(anomaly["recommended_action"]) > 0
            # For shrinkage, recommendation should suggest investigation
            assert "investigate" in anomaly["recommended_action"].lower() or \
                   "review" in anomaly["recommended_action"].lower() or \
                   "audit" in anomaly["recommended_action"].lower()
            
            assert "status" in anomaly
            assert anomaly["status"] == AnomalyStatus.OPEN.value
            
            assert "created_at" in anomaly
            assert len(anomaly["created_at"]) > 0
        else:
            # If within bounds, no anomaly should be detected
            assert anomaly is None, (
                f"Expected no anomaly for discrepancy of {discrepancy_percentage:.1f}% "
                f"(within confidence bounds)"
            )


class TestAnomalyOutputCompletenessPropertyBased:
    """Property-based tests for anomaly output completeness.
    
    Feature: supply-chain-optimizer, Property 18: Anomaly Output Completeness
    Validates: Requirements 4.5
    """

    @given(
        current_inventory=st.integers(min_value=0, max_value=10000),
        forecasted_inventory=st.integers(min_value=1, max_value=10000),
        confidence_95=st.integers(min_value=100, max_value=5000),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_anomaly_output_completeness(self, agent, current_inventory, forecasted_inventory, confidence_95):
        """Property: For any detected anomaly, the system should provide a
        confidence score (0-1), severity level, root cause analysis, and
        recommended actions.
        
        Property 18: Anomaly Output Completeness
        For any detected anomaly, the system should provide a confidence score 
        (0-1), severity level, root cause analysis, and recommended actions.
        
        Validates: Requirements 4.5
        """
        anomaly = agent.detect_inventory_anomaly(
            sku="PROD-TEST",
            current_inventory=current_inventory,
            forecasted_inventory=forecasted_inventory,
            confidence_80=confidence_95 // 2,
            confidence_95=confidence_95,
        )

        # Only check completeness if anomaly was detected
        if anomaly is not None:
            # Verify all required fields are present
            assert "anomaly_id" in anomaly
            assert "anomaly_type" in anomaly
            assert "sku" in anomaly
            assert "severity" in anomaly
            assert "confidence_score" in anomaly
            assert "description" in anomaly
            assert "root_cause" in anomaly
            assert "recommended_action" in anomaly
            assert "status" in anomaly
            assert "created_at" in anomaly

            # Verify field values are valid
            assert len(anomaly["anomaly_id"]) > 0
            assert anomaly["anomaly_type"] in [
                AnomalyType.INVENTORY_DEVIATION.value,
                AnomalyType.SUPPLIER_DELAY.value,
                AnomalyType.DEMAND_SPIKE.value,
                AnomalyType.INVENTORY_SHRINKAGE.value,
            ]
            assert anomaly["severity"] in [
                SeverityLevel.LOW.value,
                SeverityLevel.MEDIUM.value,
                SeverityLevel.HIGH.value,
                SeverityLevel.CRITICAL.value,
            ]
            assert 0 <= anomaly["confidence_score"] <= 1
            assert len(anomaly["description"]) > 0
            assert len(anomaly["root_cause"]) > 0
            assert len(anomaly["recommended_action"]) > 0
            assert anomaly["status"] in [
                AnomalyStatus.OPEN.value,
                AnomalyStatus.INVESTIGATING.value,
                AnomalyStatus.RESOLVED.value,
            ]


class TestInventoryDeviationThresholds:
    """Unit tests for inventory deviation detection with various thresholds."""

    def test_inventory_deviation_low_threshold(self, agent):
        """Test low severity threshold (15% deviation)."""
        anomaly = agent.detect_inventory_anomaly(
            sku="PROD-001",
            current_inventory=425,  # 15% below 500, but within 95% confidence (350-650)
            forecasted_inventory=500,
            confidence_80=50,
            confidence_95=100,
        )

        # Should not detect anomaly since within confidence bounds
        assert anomaly is None

    def test_inventory_deviation_medium_threshold(self, agent):
        """Test medium severity threshold (15-30% deviation)."""
        anomaly = agent.detect_inventory_anomaly(
            sku="PROD-001",
            current_inventory=350,  # 30% below 500
            forecasted_inventory=500,
            confidence_80=50,
            confidence_95=100,
        )

        assert anomaly is not None
        assert anomaly["severity"] == SeverityLevel.MEDIUM.value
        assert anomaly["confidence_score"] == 0.75

    def test_inventory_deviation_high_threshold(self, agent):
        """Test high severity threshold (30-50% deviation)."""
        anomaly = agent.detect_inventory_anomaly(
            sku="PROD-001",
            current_inventory=250,  # 50% below 500
            forecasted_inventory=500,
            confidence_80=50,
            confidence_95=100,
        )

        assert anomaly is not None
        assert anomaly["severity"] == SeverityLevel.HIGH.value
        assert anomaly["confidence_score"] == 0.85

    def test_inventory_deviation_critical_threshold(self, agent):
        """Test critical severity threshold (>50% deviation)."""
        anomaly = agent.detect_inventory_anomaly(
            sku="PROD-001",
            current_inventory=200,  # 60% below 500
            forecasted_inventory=500,
            confidence_80=50,
            confidence_95=100,
        )

        assert anomaly is not None
        assert anomaly["severity"] == SeverityLevel.CRITICAL.value
        assert anomaly["confidence_score"] == 0.95

    def test_inventory_deviation_zero_forecast(self, agent):
        """Test with zero forecasted inventory."""
        anomaly = agent.detect_inventory_anomaly(
            sku="PROD-001",
            current_inventory=100,
            forecasted_inventory=0,
            confidence_80=0,
            confidence_95=0,
        )

        # Should detect anomaly since current > forecast (100 > 0)
        # Deviation percentage is 0 when forecast is 0, so severity is LOW
        assert anomaly is not None
        assert anomaly["severity"] == SeverityLevel.LOW.value

    def test_inventory_deviation_exact_bounds(self, agent):
        """Test inventory exactly at confidence bounds."""
        # At lower bound
        anomaly = agent.detect_inventory_anomaly(
            sku="PROD-001",
            current_inventory=350,  # Exactly at lower bound (500 - 150)
            forecasted_inventory=500,
            confidence_80=100,
            confidence_95=150,
        )

        # Should not detect anomaly (at boundary)
        assert anomaly is None

        # At upper bound
        anomaly = agent.detect_inventory_anomaly(
            sku="PROD-001",
            current_inventory=650,  # Exactly at upper bound (500 + 150)
            forecasted_inventory=500,
            confidence_80=100,
            confidence_95=150,
        )

        # Should not detect anomaly (at boundary)
        assert anomaly is None

    def test_inventory_deviation_just_outside_bounds(self, agent):
        """Test inventory just outside confidence bounds."""
        # Just below lower bound
        anomaly = agent.detect_inventory_anomaly(
            sku="PROD-001",
            current_inventory=349,  # Just below lower bound (500 - 150 = 350)
            forecasted_inventory=500,
            confidence_80=100,
            confidence_95=150,
        )

        assert anomaly is not None

        # Just above upper bound
        anomaly = agent.detect_inventory_anomaly(
            sku="PROD-001",
            current_inventory=651,  # Just above upper bound (500 + 150 = 650)
            forecasted_inventory=500,
            confidence_80=100,
            confidence_95=150,
        )

        assert anomaly is not None


class TestSupplierPerformanceMonitoring:
    """Unit tests for supplier performance monitoring."""

    def test_supplier_performance_slight_decline(self, agent):
        """Test slight performance decline (10-20%)."""
        anomaly = agent.detect_supplier_anomaly(
            supplier_id="SUP-001",
            on_time_delivery_rate=0.86,  # 9% decline (below 10% threshold)
            average_delivery_days=7,  # No delay
            expected_lead_time=7,
            historical_on_time_rate=0.95,
        )

        # 9% decline is below threshold (> 0.1), so should not detect
        assert anomaly is None

    def test_supplier_performance_moderate_decline(self, agent):
        """Test moderate performance decline (20-30%)."""
        anomaly = agent.detect_supplier_anomaly(
            supplier_id="SUP-001",
            on_time_delivery_rate=0.70,  # 25% decline
            average_delivery_days=10,
            expected_lead_time=7,
            historical_on_time_rate=0.95,
        )

        assert anomaly is not None
        assert anomaly["severity"] == SeverityLevel.HIGH.value

    def test_supplier_performance_severe_decline(self, agent):
        """Test severe performance decline (>30%)."""
        anomaly = agent.detect_supplier_anomaly(
            supplier_id="SUP-001",
            on_time_delivery_rate=0.50,  # 45% decline
            average_delivery_days=15,
            expected_lead_time=7,
            historical_on_time_rate=0.95,
        )

        assert anomaly is not None
        assert anomaly["severity"] == SeverityLevel.CRITICAL.value

    def test_supplier_performance_delivery_delay_only(self, agent):
        """Test detection based on delivery delay only."""
        anomaly = agent.detect_supplier_anomaly(
            supplier_id="SUP-001",
            on_time_delivery_rate=0.95,  # No decline
            average_delivery_days=10,  # 3 days delay
            expected_lead_time=7,
            historical_on_time_rate=0.95,
        )

        assert anomaly is not None
        # 3 days delay is > 1 but <= 3, so MEDIUM severity
        assert anomaly["severity"] == SeverityLevel.MEDIUM.value

    def test_supplier_performance_rate_decline_only(self, agent):
        """Test detection based on rate decline only."""
        anomaly = agent.detect_supplier_anomaly(
            supplier_id="SUP-001",
            on_time_delivery_rate=0.80,  # 15% decline
            average_delivery_days=7,  # No delay
            expected_lead_time=7,
            historical_on_time_rate=0.95,
        )

        assert anomaly is not None
        assert anomaly["severity"] == SeverityLevel.MEDIUM.value

    def test_supplier_performance_no_degradation(self, agent):
        """Test no anomaly with stable performance."""
        anomaly = agent.detect_supplier_anomaly(
            supplier_id="SUP-001",
            on_time_delivery_rate=0.95,
            average_delivery_days=7,
            expected_lead_time=7,
            historical_on_time_rate=0.95,
        )

        assert anomaly is None

    def test_supplier_performance_improvement(self, agent):
        """Test no anomaly with improved performance."""
        anomaly = agent.detect_supplier_anomaly(
            supplier_id="SUP-001",
            on_time_delivery_rate=0.98,  # Improved
            average_delivery_days=6,  # Faster
            expected_lead_time=7,
            historical_on_time_rate=0.95,
        )

        assert anomaly is None

    def test_supplier_performance_multiple_suppliers(self, agent):
        """Test monitoring multiple suppliers."""
        suppliers = [
            ("SUP-001", 0.95, 7, 7, 0.95),  # Good
            ("SUP-002", 0.70, 10, 7, 0.95),  # Degraded
            ("SUP-003", 0.84, 8, 7, 0.95),  # 11% decline + 1 day delay = anomaly
        ]

        anomalies = []
        for supplier_id, rate, avg_days, expected, historical in suppliers:
            anomaly = agent.detect_supplier_anomaly(
                supplier_id=supplier_id,
                on_time_delivery_rate=rate,
                average_delivery_days=avg_days,
                expected_lead_time=expected,
                historical_on_time_rate=historical,
            )
            if anomaly:
                anomalies.append(anomaly)

        # Should detect 2 anomalies (SUP-002 and SUP-003)
        assert len(anomalies) == 2
        assert anomalies[0]["sku"] == "SUP-002"
        assert anomalies[1]["sku"] == "SUP-003"


class TestDemandSpikeIdentification:
    """Unit tests for demand spike identification."""

    def test_demand_spike_small_spike(self, agent):
        """Test small demand spike (25-50% above forecast)."""
        anomaly = agent.detect_demand_spike(
            sku="PROD-001",
            current_demand=1250,  # 25% above forecast
            forecasted_demand=1000,
            confidence_95=200,
        )

        assert anomaly is not None
        # 25% spike is > 25% but <= 50%, so LOW severity
        assert anomaly["severity"] == SeverityLevel.LOW.value

    def test_demand_spike_moderate_spike(self, agent):
        """Test moderate demand spike (50-100% above forecast)."""
        anomaly = agent.detect_demand_spike(
            sku="PROD-001",
            current_demand=1500,  # 50% above forecast
            forecasted_demand=1000,
            confidence_95=200,
        )

        assert anomaly is not None
        # 50% spike is > 25% but <= 50%, so MEDIUM severity
        assert anomaly["severity"] == SeverityLevel.MEDIUM.value

    def test_demand_spike_large_spike(self, agent):
        """Test large demand spike (>100% above forecast)."""
        anomaly = agent.detect_demand_spike(
            sku="PROD-001",
            current_demand=2500,  # 150% above forecast
            forecasted_demand=1000,
            confidence_95=200,
        )

        assert anomaly is not None
        assert anomaly["severity"] == SeverityLevel.CRITICAL.value

    def test_demand_spike_at_confidence_bound(self, agent):
        """Test demand at upper confidence bound."""
        anomaly = agent.detect_demand_spike(
            sku="PROD-001",
            current_demand=1200,  # Exactly at upper bound (1000 + 200)
            forecasted_demand=1000,
            confidence_95=200,
        )

        # Should not detect spike (at boundary)
        assert anomaly is None

    def test_demand_spike_just_above_bound(self, agent):
        """Test demand just above upper confidence bound."""
        anomaly = agent.detect_demand_spike(
            sku="PROD-001",
            current_demand=1201,  # Just above upper bound
            forecasted_demand=1000,
            confidence_95=200,
        )

        assert anomaly is not None
        assert anomaly["severity"] == SeverityLevel.LOW.value

    def test_demand_spike_zero_forecast(self, agent):
        """Test demand spike with zero forecast."""
        anomaly = agent.detect_demand_spike(
            sku="PROD-001",
            current_demand=100,
            forecasted_demand=0,
            confidence_95=0,
        )

        # Should detect spike since current > upper bound (0 + 0)
        assert anomaly is not None

    def test_demand_spike_multiple_products(self, agent):
        """Test demand spike detection for multiple products."""
        products = [
            ("PROD-001", 1000, 1000, 200),  # No spike
            ("PROD-002", 1500, 1000, 200),  # Spike
            ("PROD-003", 1100, 1000, 200),  # No spike
            ("PROD-004", 2500, 1000, 200),  # Large spike
        ]

        spikes = []
        for sku, current, forecast, conf in products:
            anomaly = agent.detect_demand_spike(
                sku=sku,
                current_demand=current,
                forecasted_demand=forecast,
                confidence_95=conf,
            )
            if anomaly:
                spikes.append(anomaly)

        # Should detect 2 spikes (PROD-002 and PROD-004)
        assert len(spikes) == 2
        assert spikes[0]["sku"] == "PROD-002"
        assert spikes[1]["sku"] == "PROD-004"


class TestRootCauseAnalysis:
    """Unit tests for root cause analysis."""

    def test_root_cause_inventory_low(self, agent):
        """Test root cause analysis for low inventory."""
        analysis = agent.analyze_root_cause(
            anomaly_type=AnomalyType.INVENTORY_DEVIATION.value,
            sku="PROD-001",
            current_value=300,
            expected_value=500,
        )

        assert analysis["deviation"] == -200
        assert analysis["deviation_percentage"] == -40.0
        assert len(analysis["possible_causes"]) > 0
        # Should mention demand or supply issues
        causes_text = " ".join(analysis["possible_causes"]).lower()
        assert "demand" in causes_text or "supply" in causes_text or "shrinkage" in causes_text

    def test_root_cause_inventory_high(self, agent):
        """Test root cause analysis for high inventory."""
        analysis = agent.analyze_root_cause(
            anomaly_type=AnomalyType.INVENTORY_DEVIATION.value,
            sku="PROD-001",
            current_value=700,
            expected_value=500,
        )

        assert analysis["deviation"] == 200
        assert analysis["deviation_percentage"] == 40.0
        assert len(analysis["possible_causes"]) > 0
        # Should mention demand or supply issues
        causes_text = " ".join(analysis["possible_causes"]).lower()
        assert "demand" in causes_text or "excess" in causes_text

    def test_root_cause_with_outlier_detection(self, agent):
        """Test root cause analysis with outlier detection."""
        historical_data = [100, 105, 102, 103, 104, 500]  # Last is outlier

        analysis = agent.analyze_root_cause(
            anomaly_type=AnomalyType.INVENTORY_DEVIATION.value,
            sku="PROD-001",
            current_value=500,
            expected_value=103,
            historical_data=historical_data,
        )

        assert analysis["trend_analysis"] is not None
        assert analysis["trend_analysis"]["is_outlier"] is True
        assert analysis["confidence_level"] == 0.9  # Increased confidence for outlier

    def test_root_cause_without_outlier(self, agent):
        """Test root cause analysis without outlier."""
        historical_data = [100, 105, 102, 103, 104, 101]  # No outlier

        analysis = agent.analyze_root_cause(
            anomaly_type=AnomalyType.INVENTORY_DEVIATION.value,
            sku="PROD-001",
            current_value=101,
            expected_value=103,
            historical_data=historical_data,
        )

        assert analysis["trend_analysis"] is not None
        assert analysis["trend_analysis"]["is_outlier"] is False
        assert analysis["confidence_level"] == 0.7  # Default confidence

    def test_root_cause_supplier_delay(self, agent):
        """Test root cause analysis for supplier delay."""
        analysis = agent.analyze_root_cause(
            anomaly_type=AnomalyType.SUPPLIER_DELAY.value,
            sku="SUP-001",
            current_value=10,
            expected_value=7,
        )

        assert analysis["deviation"] == 3
        assert len(analysis["possible_causes"]) > 0
        # Should mention supplier issues
        causes_text = " ".join(analysis["possible_causes"]).lower()
        assert "supplier" in causes_text or "capacity" in causes_text or "disruption" in causes_text

    def test_root_cause_demand_spike(self, agent):
        """Test root cause analysis for demand spike."""
        analysis = agent.analyze_root_cause(
            anomaly_type=AnomalyType.DEMAND_SPIKE.value,
            sku="PROD-001",
            current_value=1500,
            expected_value=1000,
        )

        assert analysis["deviation"] == 500
        assert analysis["deviation_percentage"] == 50.0
        assert len(analysis["possible_causes"]) > 0
        # Should mention demand-related causes
        causes_text = " ".join(analysis["possible_causes"]).lower()
        assert "demand" in causes_text or "viral" in causes_text or "competitor" in causes_text

    def test_root_cause_inventory_shrinkage(self, agent):
        """Test root cause analysis for inventory shrinkage."""
        analysis = agent.analyze_root_cause(
            anomaly_type=AnomalyType.INVENTORY_SHRINKAGE.value,
            sku="PROD-001",
            current_value=400,
            expected_value=500,
        )

        assert analysis["deviation"] == -100
        assert len(analysis["possible_causes"]) > 0
        # Should mention shrinkage-related causes
        causes_text = " ".join(analysis["possible_causes"]).lower()
        assert "theft" in causes_text or "loss" in causes_text or "damage" in causes_text or "error" in causes_text

    def test_root_cause_zero_expected_value(self, agent):
        """Test root cause analysis with zero expected value."""
        analysis = agent.analyze_root_cause(
            anomaly_type=AnomalyType.INVENTORY_DEVIATION.value,
            sku="PROD-001",
            current_value=100,
            expected_value=0,
        )

        # Should handle division by zero gracefully
        assert analysis["deviation"] == 100
        assert analysis["deviation_percentage"] == 0.0  # Handled gracefully
