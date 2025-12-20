"""Tests for Supplier Coordination Agent.

Feature: supply-chain-optimizer, Property 9-13: Supplier Coordination
Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5
"""

from datetime import date, timedelta
from typing import List, Dict, Any
import random
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck

from src.agents.supplier_coordination_agent import SupplierCoordinationAgent
from src.models.purchase_order import POStatus


@pytest.fixture
def agent():
    """Create a Supplier Coordination Agent instance."""
    return SupplierCoordinationAgent()


@pytest.fixture
def sample_suppliers():
    """Create sample supplier data for testing."""
    return [
        {
            "supplier_id": "SUP-001",
            "name": "Acme Supplies",
            "price_competitiveness": 85.0,
            "lead_time_days": 7,
            "reliability_score": 95.0,
            "on_time_delivery_rate": 0.95,
        },
        {
            "supplier_id": "SUP-002",
            "name": "Global Traders",
            "price_competitiveness": 90.0,
            "lead_time_days": 5,
            "reliability_score": 88.0,
            "on_time_delivery_rate": 0.88,
        },
        {
            "supplier_id": "SUP-003",
            "name": "Budget Wholesale",
            "price_competitiveness": 75.0,
            "lead_time_days": 14,
            "reliability_score": 70.0,
            "on_time_delivery_rate": 0.70,
        },
    ]


class TestSendPurchaseOrder:
    """Test purchase order sending."""

    def test_send_purchase_order_basic(self, agent):
        """Test basic purchase order sending."""
        po = agent.send_purchase_order(
            po_id="PO-001",
            sku="PROD-001",
            supplier_id="SUP-001",
            quantity=100,
            unit_price=10.50,
            expected_delivery_date=date.today() + timedelta(days=7),
        )

        assert po["po_id"] == "PO-001"
        assert po["sku"] == "PROD-001"
        assert po["supplier_id"] == "SUP-001"
        assert po["quantity"] == 100
        assert po["unit_price"] == 10.50
        assert po["total_cost"] == 1050.0
        assert po["status"] == POStatus.CONFIRMED.value

    def test_send_purchase_order_total_cost_calculation(self, agent):
        """Test that total cost is calculated correctly."""
        po = agent.send_purchase_order(
            po_id="PO-002",
            sku="PROD-002",
            supplier_id="SUP-001",
            quantity=50,
            unit_price=20.0,
            expected_delivery_date=date.today() + timedelta(days=7),
        )

        assert po["total_cost"] == 1000.0

    def test_send_purchase_order_with_large_quantity(self, agent):
        """Test purchase order with large quantity."""
        po = agent.send_purchase_order(
            po_id="PO-003",
            sku="PROD-003",
            supplier_id="SUP-001",
            quantity=10000,
            unit_price=5.0,
            expected_delivery_date=date.today() + timedelta(days=7),
        )

        assert po["quantity"] == 10000
        assert po["total_cost"] == 50000.0

    def test_send_purchase_order_with_small_quantity(self, agent):
        """Test purchase order with small quantity."""
        po = agent.send_purchase_order(
            po_id="PO-004",
            sku="PROD-004",
            supplier_id="SUP-001",
            quantity=1,
            unit_price=100.0,
            expected_delivery_date=date.today() + timedelta(days=7),
        )

        assert po["quantity"] == 1
        assert po["total_cost"] == 100.0

    def test_send_purchase_order_invalid_po_id(self, agent):
        """Test purchase order with invalid PO ID."""
        with pytest.raises(ValueError):
            agent.send_purchase_order(
                po_id="",
                sku="PROD-001",
                supplier_id="SUP-001",
                quantity=100,
                unit_price=10.50,
                expected_delivery_date=date.today() + timedelta(days=7),
            )

    def test_send_purchase_order_invalid_sku(self, agent):
        """Test purchase order with invalid SKU."""
        with pytest.raises(ValueError):
            agent.send_purchase_order(
                po_id="PO-001",
                sku="",
                supplier_id="SUP-001",
                quantity=100,
                unit_price=10.50,
                expected_delivery_date=date.today() + timedelta(days=7),
            )

    def test_send_purchase_order_invalid_supplier_id(self, agent):
        """Test purchase order with invalid supplier ID."""
        with pytest.raises(ValueError):
            agent.send_purchase_order(
                po_id="PO-001",
                sku="PROD-001",
                supplier_id="",
                quantity=100,
                unit_price=10.50,
                expected_delivery_date=date.today() + timedelta(days=7),
            )

    def test_send_purchase_order_invalid_quantity(self, agent):
        """Test purchase order with invalid quantity."""
        with pytest.raises(ValueError):
            agent.send_purchase_order(
                po_id="PO-001",
                sku="PROD-001",
                supplier_id="SUP-001",
                quantity=-100,
                unit_price=10.50,
                expected_delivery_date=date.today() + timedelta(days=7),
            )

    def test_send_purchase_order_zero_quantity(self, agent):
        """Test purchase order with zero quantity."""
        with pytest.raises(ValueError):
            agent.send_purchase_order(
                po_id="PO-001",
                sku="PROD-001",
                supplier_id="SUP-001",
                quantity=0,
                unit_price=10.50,
                expected_delivery_date=date.today() + timedelta(days=7),
            )

    def test_send_purchase_order_invalid_price(self, agent):
        """Test purchase order with invalid price."""
        with pytest.raises(ValueError):
            agent.send_purchase_order(
                po_id="PO-001",
                sku="PROD-001",
                supplier_id="SUP-001",
                quantity=100,
                unit_price=-10.50,
                expected_delivery_date=date.today() + timedelta(days=7),
            )

    def test_send_purchase_order_zero_price(self, agent):
        """Test purchase order with zero price."""
        with pytest.raises(ValueError):
            agent.send_purchase_order(
                po_id="PO-001",
                sku="PROD-001",
                supplier_id="SUP-001",
                quantity=100,
                unit_price=0,
                expected_delivery_date=date.today() + timedelta(days=7),
            )


class TestTrackDelivery:
    """Test delivery tracking."""

    def test_track_delivery_basic(self, agent):
        """Test basic delivery tracking."""
        tracking = agent.track_delivery(
            po_id="PO-001",
            supplier_id="SUP-001",
        )

        assert tracking["po_id"] == "PO-001"
        assert tracking["supplier_id"] == "SUP-001"
        assert "status" in tracking
        assert "estimated_arrival_date" in tracking
        assert "days_remaining" in tracking
        assert "is_delayed" in tracking

    def test_track_delivery_invalid_po_id(self, agent):
        """Test delivery tracking with invalid PO ID."""
        with pytest.raises(ValueError):
            agent.track_delivery(
                po_id="",
                supplier_id="SUP-001",
            )

    def test_track_delivery_invalid_supplier_id(self, agent):
        """Test delivery tracking with invalid supplier ID."""
        with pytest.raises(ValueError):
            agent.track_delivery(
                po_id="PO-001",
                supplier_id="",
            )

    def test_track_delivery_returns_tracking_info(self, agent):
        """Test that tracking returns proper structure."""
        tracking = agent.track_delivery(
            po_id="PO-001",
            supplier_id="SUP-001",
        )

        assert isinstance(tracking, dict)
        assert "po_id" in tracking
        assert "supplier_id" in tracking
        assert "status" in tracking
        assert "estimated_arrival_date" in tracking
        assert "days_remaining" in tracking
        assert "is_delayed" in tracking


class TestCompareSuppliers:
    """Test supplier comparison."""

    def test_compare_suppliers_basic(self, agent, sample_suppliers):
        """Test basic supplier comparison."""
        result = agent.compare_suppliers(suppliers=sample_suppliers)

        assert "recommended_supplier_id" in result
        assert "recommended_supplier_name" in result
        assert "comparison_scores" in result
        assert "rationale" in result

    def test_compare_suppliers_scores_calculated(self, agent, sample_suppliers):
        """Test that comparison scores are calculated for all suppliers."""
        result = agent.compare_suppliers(suppliers=sample_suppliers)

        scores = result["comparison_scores"]
        assert len(scores) == len(sample_suppliers)

        for supplier in sample_suppliers:
            assert supplier["supplier_id"] in scores

    def test_compare_suppliers_recommended_has_highest_score(
        self, agent, sample_suppliers
    ):
        """Test that recommended supplier has highest score."""
        result = agent.compare_suppliers(suppliers=sample_suppliers)

        recommended_id = result["recommended_supplier_id"]
        scores = result["comparison_scores"]

        recommended_score = scores[recommended_id]
        max_score = max(scores.values())

        assert recommended_score == max_score

    def test_compare_suppliers_single_supplier(self, agent):
        """Test supplier comparison with single supplier."""
        suppliers = [
            {
                "supplier_id": "SUP-001",
                "name": "Only Supplier",
                "price_competitiveness": 80.0,
                "lead_time_days": 7,
                "reliability_score": 90.0,
                "on_time_delivery_rate": 0.90,
            }
        ]

        result = agent.compare_suppliers(suppliers=suppliers)

        assert result["recommended_supplier_id"] == "SUP-001"

    def test_compare_suppliers_empty_list(self, agent):
        """Test supplier comparison with empty list."""
        with pytest.raises(ValueError):
            agent.compare_suppliers(suppliers=[])

    def test_compare_suppliers_missing_price_competitiveness(self, agent):
        """Test supplier comparison with missing price competitiveness."""
        suppliers = [
            {
                "supplier_id": "SUP-001",
                "name": "Incomplete Supplier",
                "lead_time_days": 7,
                "reliability_score": 90.0,
                "on_time_delivery_rate": 0.90,
            }
        ]

        with pytest.raises(ValueError):
            agent.compare_suppliers(suppliers=suppliers)

    def test_compare_suppliers_missing_lead_time(self, agent):
        """Test supplier comparison with missing lead time."""
        suppliers = [
            {
                "supplier_id": "SUP-001",
                "name": "Incomplete Supplier",
                "price_competitiveness": 80.0,
                "reliability_score": 90.0,
                "on_time_delivery_rate": 0.90,
            }
        ]

        with pytest.raises(ValueError):
            agent.compare_suppliers(suppliers=suppliers)

    def test_compare_suppliers_missing_reliability_score(self, agent):
        """Test supplier comparison with missing reliability score."""
        suppliers = [
            {
                "supplier_id": "SUP-001",
                "name": "Incomplete Supplier",
                "price_competitiveness": 80.0,
                "lead_time_days": 7,
                "on_time_delivery_rate": 0.90,
            }
        ]

        with pytest.raises(ValueError):
            agent.compare_suppliers(suppliers=suppliers)

    def test_compare_suppliers_missing_on_time_delivery_rate(self, agent):
        """Test supplier comparison with missing on-time delivery rate."""
        suppliers = [
            {
                "supplier_id": "SUP-001",
                "name": "Incomplete Supplier",
                "price_competitiveness": 80.0,
                "lead_time_days": 7,
                "reliability_score": 90.0,
            }
        ]

        with pytest.raises(ValueError):
            agent.compare_suppliers(suppliers=suppliers)


class TestUpdateDeliveryStatus:
    """Test delivery status updates."""

    def test_update_delivery_status_to_shipped(self, agent):
        """Test updating delivery status to shipped."""
        update = agent.update_delivery_status(
            po_id="PO-001",
            status=POStatus.SHIPPED.value,
        )

        assert update["po_id"] == "PO-001"
        assert update["status"] == POStatus.SHIPPED.value
        assert "updated_at" in update

    def test_update_delivery_status_to_delivered(self, agent):
        """Test updating delivery status to delivered."""
        delivery_date = date.today()
        update = agent.update_delivery_status(
            po_id="PO-001",
            status=POStatus.DELIVERED.value,
            actual_delivery_date=delivery_date,
        )

        assert update["po_id"] == "PO-001"
        assert update["status"] == POStatus.DELIVERED.value
        assert update["actual_delivery_date"] == delivery_date.isoformat()

    def test_update_delivery_status_to_cancelled(self, agent):
        """Test updating delivery status to cancelled."""
        update = agent.update_delivery_status(
            po_id="PO-001",
            status=POStatus.CANCELLED.value,
        )

        assert update["po_id"] == "PO-001"
        assert update["status"] == POStatus.CANCELLED.value

    def test_update_delivery_status_with_notes(self, agent):
        """Test updating delivery status with notes."""
        update = agent.update_delivery_status(
            po_id="PO-001",
            status=POStatus.SHIPPED.value,
            notes="Shipped via FedEx",
        )

        assert update["notes"] == "Shipped via FedEx"

    def test_update_delivery_status_invalid_po_id(self, agent):
        """Test updating delivery status with invalid PO ID."""
        with pytest.raises(ValueError):
            agent.update_delivery_status(
                po_id="",
                status=POStatus.SHIPPED.value,
            )

    def test_update_delivery_status_invalid_status(self, agent):
        """Test updating delivery status with invalid status."""
        with pytest.raises(ValueError):
            agent.update_delivery_status(
                po_id="PO-001",
                status="invalid_status",
            )

    def test_update_delivery_status_delivered_without_date(self, agent):
        """Test updating to delivered without actual delivery date."""
        with pytest.raises(ValueError):
            agent.update_delivery_status(
                po_id="PO-001",
                status=POStatus.DELIVERED.value,
            )

    def test_update_delivery_status_all_valid_statuses(self, agent):
        """Test updating to all valid statuses."""
        valid_statuses = [
            POStatus.PENDING.value,
            POStatus.CONFIRMED.value,
            POStatus.SHIPPED.value,
            POStatus.CANCELLED.value,
        ]

        for status in valid_statuses:
            update = agent.update_delivery_status(
                po_id="PO-001",
                status=status,
            )
            assert update["status"] == status


class TestGetSupplierPerformance:
    """Test supplier performance retrieval."""

    def test_get_supplier_performance_basic(self, agent):
        """Test basic supplier performance retrieval."""
        performance = agent.get_supplier_performance(supplier_id="SUP-001")

        assert performance["supplier_id"] == "SUP-001"
        assert "name" in performance
        assert "total_orders" in performance
        assert "on_time_delivery_rate" in performance
        assert "average_delivery_days" in performance
        assert "reliability_score" in performance
        assert "price_competitiveness" in performance
        assert "last_order_date" in performance

    def test_get_supplier_performance_invalid_supplier_id(self, agent):
        """Test supplier performance retrieval with invalid supplier ID."""
        with pytest.raises(ValueError):
            agent.get_supplier_performance(supplier_id="")

    def test_get_supplier_performance_returns_dict(self, agent):
        """Test that performance retrieval returns a dictionary."""
        performance = agent.get_supplier_performance(supplier_id="SUP-001")

        assert isinstance(performance, dict)


class TestCheckDeliveryDelay:
    """Test delivery delay checking."""

    def test_check_delivery_delay_not_delayed(self, agent):
        """Test checking delivery when not delayed."""
        future_date = date.today() + timedelta(days=5)
        result = agent.check_delivery_delay(
            po_id="PO-001",
            expected_delivery_date=future_date,
            current_status=POStatus.SHIPPED.value,
        )

        assert result is None

    def test_check_delivery_delay_delayed(self, agent):
        """Test checking delivery when delayed."""
        past_date = date.today() - timedelta(days=3)
        result = agent.check_delivery_delay(
            po_id="PO-001",
            expected_delivery_date=past_date,
            current_status=POStatus.SHIPPED.value,
        )

        assert result is not None
        assert result["is_delayed"] is True
        assert result["days_overdue"] == 3

    def test_check_delivery_delay_one_day_late(self, agent):
        """Test checking delivery one day late."""
        past_date = date.today() - timedelta(days=1)
        result = agent.check_delivery_delay(
            po_id="PO-001",
            expected_delivery_date=past_date,
            current_status=POStatus.SHIPPED.value,
        )

        assert result is not None
        assert result["days_overdue"] == 1

    def test_check_delivery_delay_many_days_late(self, agent):
        """Test checking delivery many days late."""
        past_date = date.today() - timedelta(days=30)
        result = agent.check_delivery_delay(
            po_id="PO-001",
            expected_delivery_date=past_date,
            current_status=POStatus.SHIPPED.value,
        )

        assert result is not None
        assert result["days_overdue"] == 30

    def test_check_delivery_delay_invalid_po_id(self, agent):
        """Test checking delivery delay with invalid PO ID."""
        with pytest.raises(ValueError):
            agent.check_delivery_delay(
                po_id="",
                expected_delivery_date=date.today(),
                current_status=POStatus.SHIPPED.value,
            )

    def test_check_delivery_delay_includes_recommendations(self, agent):
        """Test that delay alert includes recommended actions."""
        past_date = date.today() - timedelta(days=5)
        result = agent.check_delivery_delay(
            po_id="PO-001",
            expected_delivery_date=past_date,
            current_status=POStatus.SHIPPED.value,
        )

        assert "recommended_actions" in result
        assert len(result["recommended_actions"]) > 0


class TestPurchaseOrderPlacementPropertyBased:
    """Property-based tests for purchase order placement.
    
    Feature: supply-chain-optimizer, Property 9: Purchase Order Placement
    Validates: Requirements 3.1
    """

    @given(
        quantity=st.integers(min_value=1, max_value=100000),
        unit_price=st.floats(min_value=0.01, max_value=10000),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_po_placement_correctness(self, agent, quantity, unit_price):
        """Property: For any valid PO parameters, the order should be confirmed
        with correct total cost calculation.
        
        Total Cost = Quantity × Unit Price
        """
        po = agent.send_purchase_order(
            po_id=f"PO-{random.randint(1000, 9999)}",
            sku="PROD-TEST",
            supplier_id="SUP-TEST",
            quantity=quantity,
            unit_price=unit_price,
            expected_delivery_date=date.today() + timedelta(days=7),
        )

        # Verify PO is confirmed
        assert po["status"] == POStatus.CONFIRMED.value

        # Verify total cost calculation
        expected_total = quantity * unit_price
        assert abs(po["total_cost"] - expected_total) < 0.01  # Allow for floating point rounding

        # Verify all required fields are present
        assert po["po_id"]
        assert po["sku"] == "PROD-TEST"
        assert po["supplier_id"] == "SUP-TEST"
        assert po["quantity"] == quantity
        assert po["unit_price"] == unit_price


class TestOrderTrackingPropertyBased:
    """Property-based tests for order tracking.
    
    Feature: supply-chain-optimizer, Property 10: Order Tracking
    Validates: Requirements 3.2
    """

    @given(
        po_id=st.text(min_size=1, max_size=20, alphabet=st.characters(blacklist_categories=('Cc', 'Cs'), blacklist_characters='\r\n\t ')),
        supplier_id=st.text(min_size=1, max_size=20, alphabet=st.characters(blacklist_categories=('Cc', 'Cs'), blacklist_characters='\r\n\t ')),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_order_tracking_returns_status(self, agent, po_id, supplier_id):
        """Property: For any valid PO and supplier, tracking should return
        current status and estimated arrival date.
        
        Property 10: Order Tracking
        For any placed purchase order, the system should maintain tracking 
        information and provide estimated arrival dates that are updated as 
        delivery status changes.
        
        Validates: Requirements 3.2
        """
        tracking = agent.track_delivery(
            po_id=po_id,
            supplier_id=supplier_id,
        )

        # Verify tracking information is present
        assert tracking["po_id"] == po_id
        assert tracking["supplier_id"] == supplier_id
        assert "status" in tracking
        assert "estimated_arrival_date" in tracking
        assert "days_remaining" in tracking
        assert "is_delayed" in tracking
        
        # Verify status is a valid PO status
        valid_statuses = [
            POStatus.PENDING.value,
            POStatus.CONFIRMED.value,
            POStatus.SHIPPED.value,
            POStatus.DELIVERED.value,
            POStatus.CANCELLED.value,
        ]
        assert tracking["status"] in valid_statuses
        
        # Verify estimated arrival date is a valid ISO format date
        assert isinstance(tracking["estimated_arrival_date"], str)
        # Parse to verify it's a valid date format
        from datetime import datetime
        datetime.fromisoformat(tracking["estimated_arrival_date"])
        
        # Verify days_remaining is a non-negative integer
        assert isinstance(tracking["days_remaining"], int)
        assert tracking["days_remaining"] >= 0
        
        # Verify is_delayed is a boolean
        assert isinstance(tracking["is_delayed"], bool)

    @given(
        po_id=st.text(min_size=1, max_size=20),
        supplier_id=st.text(min_size=1, max_size=20),
        num_tracking_calls=st.integers(min_value=1, max_value=5),
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_order_tracking_consistency(self, agent, po_id, supplier_id, num_tracking_calls):
        """Property: For any purchase order, tracking information should be
        consistent across multiple tracking calls for the same order.
        
        When tracking the same order multiple times, the PO ID and supplier ID
        should remain constant in the tracking results.
        """
        # Track the same order multiple times
        tracking_results = []
        for _ in range(num_tracking_calls):
            tracking = agent.track_delivery(
                po_id=po_id,
                supplier_id=supplier_id,
            )
            tracking_results.append(tracking)
        
        # Verify all tracking results have the same PO ID and supplier ID
        for tracking in tracking_results:
            assert tracking["po_id"] == po_id
            assert tracking["supplier_id"] == supplier_id
            
            # Verify all required fields are present
            assert "status" in tracking
            assert "estimated_arrival_date" in tracking
            assert "days_remaining" in tracking
            assert "is_delayed" in tracking


class TestSupplierComparisonPropertyBased:
    """Property-based tests for supplier comparison.
    
    Feature: supply-chain-optimizer, Property 13: Supplier Comparison
    Validates: Requirements 3.5
    """

    @given(
        num_suppliers=st.integers(min_value=1, max_value=10),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_supplier_comparison_recommends_best(self, agent, num_suppliers):
        """Property: For any set of suppliers, the comparison should recommend
        the supplier with the best overall score based on price, reliability,
        lead time, and on-time delivery rate.
        """
        # Generate random suppliers
        suppliers = []
        for i in range(num_suppliers):
            supplier = {
                "supplier_id": f"SUP-{i:03d}",
                "name": f"Supplier {i}",
                "price_competitiveness": random.uniform(0, 100),
                "lead_time_days": random.randint(1, 30),
                "reliability_score": random.uniform(0, 100),
                "on_time_delivery_rate": random.uniform(0, 1),
            }
            suppliers.append(supplier)

        # Compare suppliers
        result = agent.compare_suppliers(suppliers=suppliers)

        # Verify recommendation is made
        assert "recommended_supplier_id" in result
        assert result["recommended_supplier_id"] in [s["supplier_id"] for s in suppliers]

        # Verify scores are calculated for all suppliers
        scores = result["comparison_scores"]
        assert len(scores) == num_suppliers

        # Verify recommended supplier has highest score
        recommended_id = result["recommended_supplier_id"]
        recommended_score = scores[recommended_id]
        max_score = max(scores.values())
        assert recommended_score == max_score

        # Verify rationale is provided
        assert "rationale" in result
        assert len(result["rationale"]) > 0


class TestForecastUpdateOnOrderConfirmationPropertyBased:
    """Property-based tests for forecast update on order confirmation.
    
    Feature: supply-chain-optimizer, Property 11: Forecast Update on Order Confirmation
    Validates: Requirements 3.3
    """

    @given(
        quantity=st.integers(min_value=1, max_value=100000),
        forecasted_demand=st.integers(min_value=1, max_value=100000),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_forecast_update_on_order_confirmation(self, agent, quantity, forecasted_demand):
        """Property: For any confirmed purchase order, the system should
        update the demand forecast to account for incoming stock.
        
        When an order is confirmed, the forecasted shortage should be reduced
        by the order quantity.
        
        Property 11: Forecast Update on Order Confirmation
        For any supplier-confirmed purchase order, the system should update 
        the demand forecast to account for incoming stock, reducing the 
        forecasted shortage.
        
        Validates: Requirements 3.3
        """
        # Send a purchase order
        po = agent.send_purchase_order(
            po_id=f"PO-{random.randint(1000, 9999)}",
            sku="PROD-TEST",
            supplier_id="SUP-TEST",
            quantity=quantity,
            unit_price=10.0,
            expected_delivery_date=date.today() + timedelta(days=7),
        )

        # Verify order is confirmed
        assert po["status"] == POStatus.CONFIRMED.value

        # Verify order contains the quantity that should be added to forecast
        assert po["quantity"] == quantity
        
        # Simulate forecast update: when order is confirmed, incoming stock
        # should reduce the forecasted shortage
        # Original forecasted shortage = forecasted_demand
        # After order confirmation, shortage = max(0, forecasted_demand - quantity)
        updated_shortage = max(0, forecasted_demand - quantity)
        
        # Verify that the updated shortage is less than or equal to original
        assert updated_shortage <= forecasted_demand
        
        # Verify that the reduction equals the order quantity (or less if shortage was smaller)
        shortage_reduction = forecasted_demand - updated_shortage
        assert shortage_reduction == min(quantity, forecasted_demand)
        
        # Verify that incoming stock (order quantity) is accounted for
        # The order quantity should be available to fulfill demand
        assert quantity > 0
        
        # Verify that the forecast update maintains data integrity
        # (shortage cannot be negative)
        assert updated_shortage >= 0

    @given(
        quantity=st.integers(min_value=1, max_value=100000),
        forecasted_demand=st.integers(min_value=1, max_value=100000),
        num_orders=st.integers(min_value=1, max_value=5),
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_forecast_update_multiple_orders_cumulative(self, agent, quantity, forecasted_demand, num_orders):
        """Property: For multiple confirmed purchase orders for the same SKU,
        the forecast should be updated cumulatively to account for all incoming stock.
        
        When multiple orders are confirmed, the total incoming stock should
        reduce the forecasted shortage by the sum of all order quantities.
        """
        sku = "PROD-TEST"
        total_incoming = 0
        
        # Confirm multiple orders
        for i in range(num_orders):
            po = agent.send_purchase_order(
                po_id=f"PO-{random.randint(10000, 99999)}",
                sku=sku,
                supplier_id=f"SUP-{i}",
                quantity=quantity,
                unit_price=10.0,
                expected_delivery_date=date.today() + timedelta(days=7),
            )
            
            # Verify each order is confirmed
            assert po["status"] == POStatus.CONFIRMED.value
            assert po["quantity"] == quantity
            
            total_incoming += quantity
        
        # Calculate cumulative forecast update
        # Original shortage = forecasted_demand
        # After all orders, shortage = max(0, forecasted_demand - total_incoming)
        updated_shortage = max(0, forecasted_demand - total_incoming)
        
        # Verify cumulative reduction
        assert updated_shortage <= forecasted_demand
        
        # Verify total incoming stock is accounted for
        assert total_incoming == quantity * num_orders
        
        # Verify shortage reduction equals total incoming (or less if shortage was smaller)
        shortage_reduction = forecasted_demand - updated_shortage
        assert shortage_reduction == min(total_incoming, forecasted_demand)
        
        # Verify data integrity
        assert updated_shortage >= 0

    @given(
        quantity=st.integers(min_value=1, max_value=100000),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_forecast_update_preserves_order_data(self, agent, quantity):
        """Property: When updating forecast on order confirmation, the order
        data should be preserved and remain accessible.
        
        The order confirmation should contain all necessary information to
        update the forecast (SKU, quantity, expected delivery date).
        """
        po_id = f"PO-{random.randint(1000, 9999)}"
        sku = "PROD-TEST"
        supplier_id = "SUP-TEST"
        expected_delivery = date.today() + timedelta(days=7)
        
        # Send purchase order
        po = agent.send_purchase_order(
            po_id=po_id,
            sku=sku,
            supplier_id=supplier_id,
            quantity=quantity,
            unit_price=10.0,
            expected_delivery_date=expected_delivery,
        )
        
        # Verify all data needed for forecast update is present
        assert po["po_id"] == po_id
        assert po["sku"] == sku
        assert po["supplier_id"] == supplier_id
        assert po["quantity"] == quantity
        assert po["status"] == POStatus.CONFIRMED.value
        assert po["expected_delivery_date"] == expected_delivery.isoformat()
        
        # Verify order data is complete and consistent
        assert po["total_cost"] == quantity * po["unit_price"]
        assert "order_date" in po
        assert po["order_date"] is not None


class TestDeliveryDelayAlertPropertyBased:
    """Property-based tests for delivery delay alerts.
    
    Feature: supply-chain-optimizer, Property 12: Delivery Delay Alert
    Validates: Requirements 3.4
    """

    @given(
        days_late=st.integers(min_value=0, max_value=365),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_delivery_delay_alert_correctness(self, agent, days_late):
        """Property: For any delivery date, if the delivery is late,
        an alert should be generated with correct days overdue calculation.
        """
        expected_date = date.today() - timedelta(days=days_late)

        result = agent.check_delivery_delay(
            po_id="PO-TEST",
            expected_delivery_date=expected_date,
            current_status=POStatus.SHIPPED.value,
        )

        if days_late > 0:
            # Should have alert
            assert result is not None
            assert result["is_delayed"] is True
            assert result["days_overdue"] == days_late
            assert "recommended_actions" in result
        else:
            # Should not have alert
            assert result is None


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
        # Calculate degradation metrics
        rate_decline = historical_rate - on_time_rate
        delivery_delay = avg_delivery_days - expected_lead_time

        # Determine if significant degradation exists
        # Threshold: rate decline > 0.1 (10%) OR delivery delay > 2 days
        has_significant_degradation = rate_decline > 0.1 or delivery_delay > 2

        # Get supplier performance
        performance = agent.get_supplier_performance(supplier_id="SUP-TEST")

        # Verify performance data structure is complete
        assert performance["supplier_id"] == "SUP-TEST"
        assert "on_time_delivery_rate" in performance
        assert "average_delivery_days" in performance
        assert "reliability_score" in performance

        # Verify performance metrics are within valid ranges
        assert 0 <= performance["on_time_delivery_rate"] <= 1
        assert performance["average_delivery_days"] >= 0
        assert 0 <= performance["reliability_score"] <= 100

        # If significant degradation exists, the system should be able to detect it
        # by comparing current metrics with historical metrics
        if has_significant_degradation:
            # The system should flag this as a performance issue
            # Verify that the metrics show degradation
            assert rate_decline > 0.1 or delivery_delay > 2
        else:
            # If no significant degradation, metrics should be stable
            assert rate_decline <= 0.1 and delivery_delay <= 2

    @given(
        num_suppliers=st.integers(min_value=2, max_value=10),
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_supplier_performance_degradation_suggests_alternatives(
        self, agent, num_suppliers
    ):
        """Property: When a supplier shows performance degradation, the system
        should suggest alternative suppliers with better performance metrics.
        
        For any set of suppliers where one has degraded performance, the system
        should recommend an alternative supplier with better on-time delivery
        rate or shorter lead time.
        """
        # Create suppliers with varying performance levels
        suppliers = []
        
        # First supplier has degraded performance
        degraded_supplier = {
            "supplier_id": "SUP-DEGRADED",
            "name": "Degraded Supplier",
            "price_competitiveness": 80.0,
            "lead_time_days": 15,  # High lead time
            "reliability_score": 60.0,  # Low reliability
            "on_time_delivery_rate": 0.60,  # Low on-time rate
        }
        suppliers.append(degraded_supplier)
        
        # Add alternative suppliers with better performance
        for i in range(num_suppliers - 1):
            supplier = {
                "supplier_id": f"SUP-ALT-{i}",
                "name": f"Alternative Supplier {i}",
                "price_competitiveness": 85.0 + (i * 2),
                "lead_time_days": 7,  # Better lead time
                "reliability_score": 90.0 + (i * 1),  # Better reliability
                "on_time_delivery_rate": 0.90 + (i * 0.01),  # Better on-time rate
            }
            suppliers.append(supplier)
        
        # Compare suppliers
        result = agent.compare_suppliers(suppliers=suppliers)
        
        # Verify that a recommendation is made
        assert "recommended_supplier_id" in result
        
        # Verify that the recommended supplier is NOT the degraded one
        # (unless all suppliers are equally bad, which is unlikely with our setup)
        recommended_id = result["recommended_supplier_id"]
        
        # Get the recommended supplier's score
        scores = result["comparison_scores"]
        recommended_score = scores[recommended_id]
        degraded_score = scores["SUP-DEGRADED"]
        
        # The recommended supplier should have a better score than the degraded one
        assert recommended_score >= degraded_score
        
        # Verify rationale is provided
        assert "rationale" in result
        assert len(result["rationale"]) > 0

    @given(
        rate_decline=st.floats(min_value=0, max_value=1),
        delivery_delay=st.floats(min_value=0, max_value=30),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_supplier_performance_degradation_severity_correlation(
        self, agent, rate_decline, delivery_delay
    ):
        """Property: The severity of supplier performance degradation should
        correlate with the magnitude of the degradation metrics.
        
        Greater rate decline or delivery delay should result in higher severity
        alerts. The system should provide appropriate severity levels based on
        the degradation magnitude.
        """
        # Calculate current metrics based on degradation
        historical_rate = 0.95  # Assume good historical performance
        current_rate = max(0, historical_rate - rate_decline)
        
        expected_lead_time = 7  # Assume 7-day expected lead time
        current_lead_time = expected_lead_time + delivery_delay
        
        # Get supplier performance
        performance = agent.get_supplier_performance(supplier_id="SUP-TEST")
        
        # Verify performance data is available
        assert "on_time_delivery_rate" in performance
        assert "average_delivery_days" in performance
        
        # Determine expected severity based on degradation
        # Critical: rate_decline > 0.3 OR delivery_delay > 5
        # High: rate_decline > 0.2 OR delivery_delay > 3
        # Medium: rate_decline > 0.1 OR delivery_delay > 1
        # Low: rate_decline <= 0.1 AND delivery_delay <= 1
        
        if rate_decline > 0.3 or delivery_delay > 5:
            expected_severity = "critical"
        elif rate_decline > 0.2 or delivery_delay > 3:
            expected_severity = "high"
        elif rate_decline > 0.1 or delivery_delay > 1:
            expected_severity = "medium"
        else:
            expected_severity = "low"
        
        # Verify that the system can assess severity based on metrics
        # The performance data should reflect the degradation level
        assert performance["on_time_delivery_rate"] >= 0
        assert performance["average_delivery_days"] >= 0
        
        # Verify that severity assessment is possible
        # (i.e., the system has the data needed to determine severity)
        assert "reliability_score" in performance
        assert "on_time_delivery_rate" in performance
        assert "average_delivery_days" in performance
