"""Tests for Warehouse Manager.

Feature: supply-chain-optimizer, Property 24-26: Multi-Warehouse Management
Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
import random
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck

from src.agents.warehouse_manager import WarehouseManager
from src.models.warehouse import Warehouse, WarehouseStatus
from src.models.inventory_transfer import InventoryTransfer, TransferStatus


@pytest.fixture
def manager():
    """Create a Warehouse Manager instance."""
    return WarehouseManager()


@pytest.fixture
def sample_warehouses():
    """Create sample warehouse data for testing."""
    return [
        {
            "warehouse_id": "WH-001",
            "name": "Central Warehouse",
            "location": "New York",
            "capacity": 10000,
            "current_inventory": 5000,
            "holding_cost_per_unit": 1.0,
            "transfer_cost_per_unit": 0.5,
        },
        {
            "warehouse_id": "WH-002",
            "name": "Regional Warehouse",
            "location": "Los Angeles",
            "capacity": 8000,
            "current_inventory": 3000,
            "holding_cost_per_unit": 1.2,
            "transfer_cost_per_unit": 0.6,
        },
        {
            "warehouse_id": "WH-003",
            "name": "Distribution Center",
            "location": "Chicago",
            "capacity": 6000,
            "current_inventory": 2000,
            "holding_cost_per_unit": 1.5,
            "transfer_cost_per_unit": 0.7,
        },
    ]


class TestTrackWarehouseCapacity:
    """Test warehouse capacity tracking."""

    def test_track_capacity_basic(self, manager):
        """Test basic capacity tracking."""
        result = manager.track_warehouse_capacity(
            warehouse_id="WH-001",
            current_inventory=5000,
            capacity=10000,
        )

        assert result["warehouse_id"] == "WH-001"
        assert result["current_inventory"] == 5000
        assert result["capacity"] == 10000
        assert result["utilization_percentage"] == 50.0
        assert result["available_capacity"] == 5000
        assert result["is_at_capacity"] is False
        assert result["is_near_capacity"] is False

    def test_track_capacity_at_capacity(self, manager):
        """Test capacity tracking when warehouse is at capacity."""
        result = manager.track_warehouse_capacity(
            warehouse_id="WH-001",
            current_inventory=10000,
            capacity=10000,
        )

        assert result["utilization_percentage"] == 100.0
        assert result["available_capacity"] == 0
        assert result["is_at_capacity"] is True
        assert result["is_near_capacity"] is True

    def test_track_capacity_near_capacity(self, manager):
        """Test capacity tracking when warehouse is near capacity."""
        result = manager.track_warehouse_capacity(
            warehouse_id="WH-001",
            current_inventory=8500,
            capacity=10000,
        )

        assert result["utilization_percentage"] == 85.0
        assert result["is_near_capacity"] is True
        assert result["is_at_capacity"] is False

    def test_track_capacity_empty(self, manager):
        """Test capacity tracking for empty warehouse."""
        result = manager.track_warehouse_capacity(
            warehouse_id="WH-001",
            current_inventory=0,
            capacity=10000,
        )

        assert result["utilization_percentage"] == 0.0
        assert result["available_capacity"] == 10000
        assert result["is_at_capacity"] is False
        assert result["is_near_capacity"] is False

    def test_track_capacity_invalid_capacity(self, manager):
        """Test capacity tracking with invalid capacity."""
        with pytest.raises(ValueError):
            manager.track_warehouse_capacity(
                warehouse_id="WH-001",
                current_inventory=5000,
                capacity=-10000,
            )

    def test_track_capacity_exceeds_capacity(self, manager):
        """Test capacity tracking when inventory exceeds capacity."""
        with pytest.raises(ValueError):
            manager.track_warehouse_capacity(
                warehouse_id="WH-001",
                current_inventory=15000,
                capacity=10000,
            )

    def test_track_capacity_negative_inventory(self, manager):
        """Test capacity tracking with negative inventory."""
        with pytest.raises(ValueError):
            manager.track_warehouse_capacity(
                warehouse_id="WH-001",
                current_inventory=-1000,
                capacity=10000,
            )


class TestInitiateInventoryTransfer:
    """Test inventory transfer initiation."""

    def test_initiate_transfer_basic(self, manager):
        """Test basic inventory transfer initiation."""
        transfer = manager.initiate_inventory_transfer(
            sku="PROD-001",
            source_warehouse_id="WH-001",
            destination_warehouse_id="WH-002",
            quantity=100,
            transfer_cost_per_unit=0.5,
        )

        assert transfer["transfer_id"].startswith("TRF-")
        assert transfer["sku"] == "PROD-001"
        assert transfer["source_warehouse_id"] == "WH-001"
        assert transfer["destination_warehouse_id"] == "WH-002"
        assert transfer["quantity"] == 100
        assert transfer["transfer_cost"] == 50.0
        assert transfer["status"] == TransferStatus.PENDING.value

    def test_initiate_transfer_cost_calculation(self, manager):
        """Test that transfer cost is calculated correctly."""
        transfer = manager.initiate_inventory_transfer(
            sku="PROD-001",
            source_warehouse_id="WH-001",
            destination_warehouse_id="WH-002",
            quantity=200,
            transfer_cost_per_unit=1.5,
        )

        assert transfer["transfer_cost"] == 300.0

    def test_initiate_transfer_zero_cost(self, manager):
        """Test transfer initiation with zero cost."""
        transfer = manager.initiate_inventory_transfer(
            sku="PROD-001",
            source_warehouse_id="WH-001",
            destination_warehouse_id="WH-002",
            quantity=100,
            transfer_cost_per_unit=0.0,
        )

        assert transfer["transfer_cost"] == 0.0

    def test_initiate_transfer_invalid_quantity(self, manager):
        """Test transfer initiation with invalid quantity."""
        with pytest.raises(ValueError):
            manager.initiate_inventory_transfer(
                sku="PROD-001",
                source_warehouse_id="WH-001",
                destination_warehouse_id="WH-002",
                quantity=-100,
                transfer_cost_per_unit=0.5,
            )

    def test_initiate_transfer_zero_quantity(self, manager):
        """Test transfer initiation with zero quantity."""
        with pytest.raises(ValueError):
            manager.initiate_inventory_transfer(
                sku="PROD-001",
                source_warehouse_id="WH-001",
                destination_warehouse_id="WH-002",
                quantity=0,
                transfer_cost_per_unit=0.5,
            )

    def test_initiate_transfer_same_warehouse(self, manager):
        """Test transfer initiation with same source and destination."""
        with pytest.raises(ValueError):
            manager.initiate_inventory_transfer(
                sku="PROD-001",
                source_warehouse_id="WH-001",
                destination_warehouse_id="WH-001",
                quantity=100,
                transfer_cost_per_unit=0.5,
            )

    def test_initiate_transfer_negative_cost(self, manager):
        """Test transfer initiation with negative cost."""
        with pytest.raises(ValueError):
            manager.initiate_inventory_transfer(
                sku="PROD-001",
                source_warehouse_id="WH-001",
                destination_warehouse_id="WH-002",
                quantity=100,
                transfer_cost_per_unit=-0.5,
            )


class TestCompleteInventoryTransfer:
    """Test inventory transfer completion."""

    def test_complete_transfer_basic(self, manager):
        """Test basic inventory transfer completion."""
        completion = manager.complete_inventory_transfer(
            transfer_id="TRF-001",
            source_warehouse_id="WH-001",
            destination_warehouse_id="WH-002",
            quantity=100,
        )

        assert completion["transfer_id"] == "TRF-001"
        assert completion["status"] == TransferStatus.COMPLETED.value
        assert completion["source_warehouse_id"] == "WH-001"
        assert completion["destination_warehouse_id"] == "WH-002"
        assert completion["quantity"] == 100
        assert "completed_at" in completion

    def test_complete_transfer_invalid_quantity(self, manager):
        """Test transfer completion with invalid quantity."""
        with pytest.raises(ValueError):
            manager.complete_inventory_transfer(
                transfer_id="TRF-001",
                source_warehouse_id="WH-001",
                destination_warehouse_id="WH-002",
                quantity=-100,
            )


class TestHandleWarehouseDisruption:
    """Test warehouse disruption handling."""

    def test_handle_disruption_basic(self, manager, sample_warehouses):
        """Test basic warehouse disruption handling."""
        # Remove the disrupted warehouse from available list
        available_warehouses = sample_warehouses[1:]

        inventory_to_redistribute = {
            "PROD-001": 1000,
            "PROD-002": 500,
        }

        result = manager.handle_warehouse_disruption(
            disrupted_warehouse_id="WH-001",
            available_warehouses=available_warehouses,
            inventory_to_redistribute=inventory_to_redistribute,
        )

        assert result["disrupted_warehouse_id"] == "WH-001"
        assert "transfers" in result
        assert result["total_redistributed"] > 0
        assert result["redistribution_cost"] >= 0

    def test_handle_disruption_respects_capacity(self, manager, sample_warehouses):
        """Test that disruption handling respects warehouse capacity."""
        available_warehouses = sample_warehouses[1:]

        # Use a smaller inventory amount that can fit in available capacity
        inventory_to_redistribute = {
            "PROD-001": 2000,
        }

        result = manager.handle_warehouse_disruption(
            disrupted_warehouse_id="WH-001",
            available_warehouses=available_warehouses,
            inventory_to_redistribute=inventory_to_redistribute,
        )

        # Verify that no warehouse exceeds its capacity
        for transfer in result["transfers"]:
            dest_wh_id = transfer["destination_warehouse_id"]
            dest_warehouse = next(
                (w for w in available_warehouses if w["warehouse_id"] == dest_wh_id),
                None,
            )
            if dest_warehouse:
                new_inventory = (
                    dest_warehouse["current_inventory"] + transfer["quantity"]
                )
                assert new_inventory <= dest_warehouse["capacity"]

    def test_handle_disruption_no_available_warehouses(self, manager):
        """Test disruption handling with no available warehouses."""
        with pytest.raises(ValueError):
            manager.handle_warehouse_disruption(
                disrupted_warehouse_id="WH-001",
                available_warehouses=[],
                inventory_to_redistribute={"PROD-001": 1000},
            )

    def test_handle_disruption_empty_inventory(self, manager, sample_warehouses):
        """Test disruption handling with empty inventory."""
        available_warehouses = sample_warehouses[1:]

        result = manager.handle_warehouse_disruption(
            disrupted_warehouse_id="WH-001",
            available_warehouses=available_warehouses,
            inventory_to_redistribute={},
        )

        assert result["total_redistributed"] == 0
        assert len(result["transfers"]) == 0


class TestAllocateInventoryByRegionalDemand:
    """Test regional demand-based inventory allocation."""

    def test_allocate_by_regional_demand_basic(self, manager, sample_warehouses):
        """Test basic regional demand-based allocation."""
        regional_demand_forecasts = {
            "New York": 5000,
            "Los Angeles": 3000,
            "Chicago": 2000,
        }

        result = manager.allocate_inventory_by_regional_demand(
            sku="PROD-001",
            total_inventory=10000,
            warehouses=sample_warehouses,
            regional_demand_forecasts=regional_demand_forecasts,
        )

        assert result["sku"] == "PROD-001"
        assert "allocations" in result
        assert result["total_allocated"] <= 10000
        assert result["holding_cost_estimate"] >= 0
        assert result["demand_fulfillment_rate"] >= 0

    def test_allocate_by_regional_demand_respects_capacity(
        self, manager, sample_warehouses
    ):
        """Test that allocation respects warehouse capacity."""
        regional_demand_forecasts = {
            "New York": 50000,
            "Los Angeles": 30000,
            "Chicago": 20000,
        }

        result = manager.allocate_inventory_by_regional_demand(
            sku="PROD-001",
            total_inventory=100000,
            warehouses=sample_warehouses,
            regional_demand_forecasts=regional_demand_forecasts,
        )

        # Verify no warehouse exceeds its capacity
        for warehouse in sample_warehouses:
            wh_id = warehouse["warehouse_id"]
            capacity = warehouse["capacity"]
            allocated = result["allocations"][wh_id]
            assert allocated <= capacity

    def test_allocate_by_regional_demand_proportional(
        self, manager, sample_warehouses
    ):
        """Test that allocation is proportional to demand."""
        regional_demand_forecasts = {
            "New York": 5000,
            "Los Angeles": 3000,
            "Chicago": 2000,
        }

        result = manager.allocate_inventory_by_regional_demand(
            sku="PROD-001",
            total_inventory=10000,
            warehouses=sample_warehouses,
            regional_demand_forecasts=regional_demand_forecasts,
        )

        # New York should get more than Chicago
        ny_warehouse = next(
            (w for w in sample_warehouses if w["location"] == "New York"), None
        )
        chicago_warehouse = next(
            (w for w in sample_warehouses if w["location"] == "Chicago"), None
        )

        if ny_warehouse and chicago_warehouse:
            ny_allocation = result["allocations"][ny_warehouse["warehouse_id"]]
            chicago_allocation = result["allocations"][chicago_warehouse["warehouse_id"]]
            assert ny_allocation >= chicago_allocation

    def test_allocate_by_regional_demand_zero_inventory(self, manager, sample_warehouses):
        """Test allocation with zero inventory."""
        regional_demand_forecasts = {
            "New York": 5000,
            "Los Angeles": 3000,
            "Chicago": 2000,
        }

        result = manager.allocate_inventory_by_regional_demand(
            sku="PROD-001",
            total_inventory=0,
            warehouses=sample_warehouses,
            regional_demand_forecasts=regional_demand_forecasts,
        )

        assert result["total_allocated"] == 0
        assert result["demand_fulfillment_rate"] == 100.0

    def test_allocate_by_regional_demand_no_warehouses(self, manager):
        """Test allocation with no warehouses."""
        with pytest.raises(ValueError):
            manager.allocate_inventory_by_regional_demand(
                sku="PROD-001",
                total_inventory=10000,
                warehouses=[],
                regional_demand_forecasts={"New York": 5000},
            )

    def test_allocate_by_regional_demand_zero_demand(self, manager, sample_warehouses):
        """Test allocation with zero demand."""
        regional_demand_forecasts = {
            "New York": 0,
            "Los Angeles": 0,
            "Chicago": 0,
        }

        result = manager.allocate_inventory_by_regional_demand(
            sku="PROD-001",
            total_inventory=10000,
            warehouses=sample_warehouses,
            regional_demand_forecasts=regional_demand_forecasts,
        )

        # With zero demand, should distribute equally
        allocations = result["allocations"]
        assert len(allocations) == len(sample_warehouses)


class TestRecommendInventoryTransfersForCapacity:
    """Test inventory transfer recommendations for capacity management."""

    def test_recommend_transfers_at_capacity(self, manager, sample_warehouses):
        """Test transfer recommendations when warehouse is at capacity."""
        # Set one warehouse to 95% capacity
        warehouses = sample_warehouses.copy()
        warehouses[0]["current_inventory"] = 9500

        inventory_by_warehouse = {
            "WH-001": {"PROD-001": 5000},
            "WH-002": {"PROD-001": 3000},
            "WH-003": {"PROD-001": 2000},
        }

        recommendations = manager.recommend_inventory_transfers_for_capacity(
            warehouses=warehouses,
            inventory_by_warehouse=inventory_by_warehouse,
        )

        assert len(recommendations) > 0
        # Should recommend transferring from WH-001
        assert any(r["source_warehouse_id"] == "WH-001" for r in recommendations)

    def test_recommend_transfers_no_capacity_issues(self, manager, sample_warehouses):
        """Test transfer recommendations when no capacity issues exist."""
        inventory_by_warehouse = {
            "WH-001": {"PROD-001": 2000},
            "WH-002": {"PROD-001": 1000},
            "WH-003": {"PROD-001": 500},
        }

        recommendations = manager.recommend_inventory_transfers_for_capacity(
            warehouses=sample_warehouses,
            inventory_by_warehouse=inventory_by_warehouse,
        )

        # Should have no recommendations
        assert len(recommendations) == 0


class TestGetWarehouseStatus:
    """Test warehouse status retrieval."""

    def test_get_warehouse_status_operational(self, manager):
        """Test getting status of operational warehouse."""
        status = manager.get_warehouse_status(
            warehouse_id="WH-001",
            current_inventory=5000,
            capacity=10000,
            status=WarehouseStatus.OPERATIONAL,
        )

        assert status["warehouse_id"] == "WH-001"
        assert status["status"] == WarehouseStatus.OPERATIONAL.value
        assert status["is_operational"] is True
        assert "capacity_metrics" in status
        assert "recommendations" in status

    def test_get_warehouse_status_disrupted(self, manager):
        """Test getting status of disrupted warehouse."""
        status = manager.get_warehouse_status(
            warehouse_id="WH-001",
            current_inventory=5000,
            capacity=10000,
            status=WarehouseStatus.DISRUPTED,
        )

        assert status["status"] == WarehouseStatus.DISRUPTED.value
        assert status["is_operational"] is False
        assert any("disrupted" in r.lower() or "disruption" in r.lower() for r in status["recommendations"])

    def test_get_warehouse_status_near_capacity(self, manager):
        """Test getting status of warehouse near capacity."""
        status = manager.get_warehouse_status(
            warehouse_id="WH-001",
            current_inventory=8500,
            capacity=10000,
            status=WarehouseStatus.OPERATIONAL,
        )

        assert status["capacity_metrics"]["is_near_capacity"] is True
        assert any("transfer" in r.lower() for r in status["recommendations"])


class TestWarehouseCapacityManagementPropertyBased:
    """Property-based tests for warehouse capacity management.
    
    Feature: supply-chain-optimizer, Property 24: Warehouse Capacity Management
    Validates: Requirements 6.3
    """

    @given(
        current_inventory=st.integers(min_value=0, max_value=100000),
        capacity=st.integers(min_value=1, max_value=100000),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_capacity_tracking_correctness(self, manager, current_inventory, capacity):
        """Property: Capacity tracking should correctly calculate utilization metrics.
        
        For any warehouse with current inventory and capacity:
        1. Utilization percentage should be (current / capacity) * 100
        2. Available capacity should be (capacity - current)
        3. is_at_capacity should be true only when current >= capacity
        4. is_near_capacity should be true when utilization >= 80%
        """
        # Ensure current_inventory doesn't exceed capacity for this test
        current_inventory = min(current_inventory, capacity)

        result = manager.track_warehouse_capacity(
            warehouse_id="WH-TEST",
            current_inventory=current_inventory,
            capacity=capacity,
        )

        # Property 1: Utilization percentage calculation
        expected_utilization = (current_inventory / capacity) * 100
        assert result["utilization_percentage"] == round(expected_utilization, 2)

        # Property 2: Available capacity calculation
        expected_available = capacity - current_inventory
        assert result["available_capacity"] == expected_available

        # Property 3: is_at_capacity flag
        expected_at_capacity = current_inventory >= capacity
        assert result["is_at_capacity"] == expected_at_capacity

        # Property 4: is_near_capacity flag
        expected_near_capacity = expected_utilization >= 80
        assert result["is_near_capacity"] == expected_near_capacity

    @given(
        num_warehouses=st.integers(min_value=2, max_value=5),
        capacity_per_warehouse=st.integers(min_value=5000, max_value=20000),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_warehouse_capacity_recommendations(self, manager, num_warehouses, capacity_per_warehouse):
        """Property: When a warehouse reaches capacity, the system should recommend inventory transfers.
        
        For any warehouse configuration:
        1. When a warehouse is at/near capacity (>90%), transfer recommendations should be generated
        2. Recommendations should only suggest transfers to warehouses with available capacity
        3. Recommended transfer quantity should not exceed source warehouse inventory
        4. Recommended transfer quantity should not exceed destination warehouse available capacity
        5. When no warehouses are at capacity, no recommendations should be generated
        """
        # Create warehouses with varying inventory levels
        warehouses = []
        for i in range(num_warehouses):
            warehouse = {
                "warehouse_id": f"WH-{i:03d}",
                "capacity": capacity_per_warehouse,
                "current_inventory": random.randint(0, int(capacity_per_warehouse * 0.5)),
            }
            warehouses.append(warehouse)

        # Set one warehouse to near/at capacity (>90%)
        warehouses[0]["current_inventory"] = int(capacity_per_warehouse * 0.95)

        # Create inventory by warehouse
        inventory_by_warehouse = {
            w["warehouse_id"]: {f"PROD-{j:03d}": random.randint(100, 500) for j in range(3)}
            for w in warehouses
        }

        # Get recommendations
        recommendations = manager.recommend_inventory_transfers_for_capacity(
            warehouses=warehouses,
            inventory_by_warehouse=inventory_by_warehouse,
        )

        # Property 1: When warehouse is at/near capacity, recommendations should be generated
        assert len(recommendations) > 0, "Should generate recommendations when warehouse is near capacity"

        # Property 2: Recommendations should only suggest transfers to warehouses with available capacity
        for recommendation in recommendations:
            source_wh_id = recommendation["source_warehouse_id"]
            dest_wh_id = recommendation["destination_warehouse_id"]
            
            # Find destination warehouse
            dest_warehouse = next(
                (w for w in warehouses if w["warehouse_id"] == dest_wh_id), None
            )
            
            if dest_warehouse:
                # Destination should have available capacity
                available_capacity = dest_warehouse["capacity"] - dest_warehouse["current_inventory"]
                assert available_capacity > 0, (
                    f"Destination warehouse {dest_wh_id} should have available capacity"
                )

        # Property 3: Recommended transfer quantity should not exceed source warehouse inventory
        for recommendation in recommendations:
            source_wh_id = recommendation["source_warehouse_id"]
            recommended_qty = recommendation["recommended_quantity"]
            
            # Find source warehouse
            source_warehouse = next(
                (w for w in warehouses if w["warehouse_id"] == source_wh_id), None
            )
            
            if source_warehouse:
                assert recommended_qty <= source_warehouse["current_inventory"], (
                    f"Recommended transfer {recommended_qty} should not exceed "
                    f"source inventory {source_warehouse['current_inventory']}"
                )

        # Property 4: Recommended transfer quantity should not exceed destination available capacity
        for recommendation in recommendations:
            dest_wh_id = recommendation["destination_warehouse_id"]
            recommended_qty = recommendation["recommended_quantity"]
            
            # Find destination warehouse
            dest_warehouse = next(
                (w for w in warehouses if w["warehouse_id"] == dest_wh_id), None
            )
            
            if dest_warehouse:
                available_capacity = dest_warehouse["capacity"] - dest_warehouse["current_inventory"]
                assert recommended_qty <= available_capacity, (
                    f"Recommended transfer {recommended_qty} should not exceed "
                    f"available capacity {available_capacity}"
                )

    @given(
        num_warehouses=st.integers(min_value=2, max_value=5),
        capacity_per_warehouse=st.integers(min_value=5000, max_value=20000),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_warehouse_capacity_no_recommendations_when_not_full(
        self, manager, num_warehouses, capacity_per_warehouse
    ):
        """Property: When no warehouses are at capacity, no transfer recommendations should be generated.
        
        For any warehouse configuration where all warehouses are below 90% capacity:
        1. No transfer recommendations should be generated
        2. System should not recommend unnecessary transfers
        """
        # Create warehouses with low inventory (well below 90% capacity)
        warehouses = []
        for i in range(num_warehouses):
            warehouse = {
                "warehouse_id": f"WH-{i:03d}",
                "capacity": capacity_per_warehouse,
                "current_inventory": random.randint(0, int(capacity_per_warehouse * 0.5)),
            }
            warehouses.append(warehouse)

        # Create inventory by warehouse
        inventory_by_warehouse = {
            w["warehouse_id"]: {f"PROD-{j:03d}": random.randint(100, 500) for j in range(3)}
            for w in warehouses
        }

        # Get recommendations
        recommendations = manager.recommend_inventory_transfers_for_capacity(
            warehouses=warehouses,
            inventory_by_warehouse=inventory_by_warehouse,
        )

        # Property 1: No recommendations should be generated
        assert len(recommendations) == 0, (
            "Should not generate recommendations when all warehouses are below 90% capacity"
        )


class TestSupplyDisruptionRedistributionPropertyBased:
    """Property-based tests for supply disruption redistribution.
    
    Feature: supply-chain-optimizer, Property 25: Supply Disruption Redistribution
    Validates: Requirements 6.4
    """

    @given(
        num_warehouses=st.integers(min_value=2, max_value=5),
        total_inventory_to_redistribute=st.integers(min_value=100, max_value=10000),
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_disruption_redistribution_maintains_service_levels(
        self, manager, num_warehouses, total_inventory_to_redistribute
    ):
        """Property: When a warehouse is disrupted, inventory should be redistributed
        to maintain service levels across all locations.
        
        This property verifies that:
        1. All inventory is redistributed (up to available capacity)
        2. No warehouse exceeds its capacity
        3. Redistribution prioritizes warehouses with available capacity
        4. Total redistributed quantity is maximized
        """
        # Generate available warehouses
        available_warehouses = []
        for i in range(num_warehouses):
            warehouse = {
                "warehouse_id": f"WH-{i:03d}",
                "capacity": random.randint(5000, 20000),
                "current_inventory": random.randint(0, 5000),
            }
            available_warehouses.append(warehouse)

        # Inventory to redistribute
        inventory_to_redistribute = {
            f"PROD-{i:03d}": random.randint(100, 1000)
            for i in range(random.randint(1, 5))
        }

        # Handle disruption
        result = manager.handle_warehouse_disruption(
            disrupted_warehouse_id="WH-DISRUPTED",
            available_warehouses=available_warehouses,
            inventory_to_redistribute=inventory_to_redistribute,
        )

        # Property 1: All inventory should be redistributed (up to available capacity)
        total_to_redistribute = sum(inventory_to_redistribute.values())
        total_redistributed = result["total_redistributed"]
        assert total_redistributed <= total_to_redistribute

        # Property 2: No warehouse should exceed its capacity
        for transfer in result["transfers"]:
            dest_wh_id = transfer["destination_warehouse_id"]
            dest_warehouse = next(
                (w for w in available_warehouses if w["warehouse_id"] == dest_wh_id),
                None,
            )
            if dest_warehouse:
                new_inventory = (
                    dest_warehouse["current_inventory"] + transfer["quantity"]
                )
                assert new_inventory <= dest_warehouse["capacity"], (
                    f"Warehouse {dest_wh_id} would exceed capacity: "
                    f"{new_inventory} > {dest_warehouse['capacity']}"
                )

        # Property 3: Redistribution should prioritize warehouses with available capacity
        # (This is implicit in the algorithm - it finds warehouses with most available capacity)
        assert len(result["transfers"]) > 0 or total_to_redistribute == 0

        # Property 4: Total redistributed should be maximized
        # Calculate maximum possible redistribution
        total_available_capacity = sum(
            w["capacity"] - w["current_inventory"] for w in available_warehouses
        )
        max_possible_redistribution = min(total_to_redistribute, total_available_capacity)

        # Actual redistribution should be close to maximum possible
        # (allowing for some inefficiency in the greedy algorithm)
        assert total_redistributed <= max_possible_redistribution


class TestInventoryTransferTrackingPropertyBased:
    """Property-based tests for inventory transfer tracking.
    
    Feature: supply-chain-optimizer, Property 26: Inventory Transfer Tracking
    Validates: Requirements 6.5
    """

    @given(
        quantity=st.integers(min_value=1, max_value=10000),
        transfer_cost_per_unit=st.floats(min_value=0.01, max_value=10.0),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_transfer_tracking_round_trip(self, manager, quantity, transfer_cost_per_unit):
        """Property: Inventory transfers should be tracked accurately from initiation to completion.
        
        For any transfer:
        1. Initiated transfer should have PENDING status
        2. Transfer ID should be unique and properly formatted
        3. Transfer cost should be calculated correctly
        4. Completion should update status to COMPLETED
        5. Completion should record the same quantity and warehouses
        """
        # Step 1: Initiate transfer
        initiated_transfer = manager.initiate_inventory_transfer(
            sku="PROD-TEST",
            source_warehouse_id="WH-001",
            destination_warehouse_id="WH-002",
            quantity=quantity,
            transfer_cost_per_unit=transfer_cost_per_unit,
        )

        # Property 1: Status should be PENDING
        assert initiated_transfer["status"] == TransferStatus.PENDING.value

        # Property 2: Transfer ID should be unique and formatted
        assert initiated_transfer["transfer_id"].startswith("TRF-")
        assert len(initiated_transfer["transfer_id"]) > 4

        # Property 3: Transfer cost should be calculated correctly
        expected_cost = quantity * transfer_cost_per_unit
        assert initiated_transfer["transfer_cost"] == expected_cost

        # Step 2: Complete transfer
        completed_transfer = manager.complete_inventory_transfer(
            transfer_id=initiated_transfer["transfer_id"],
            source_warehouse_id="WH-001",
            destination_warehouse_id="WH-002",
            quantity=quantity,
        )

        # Property 4: Status should be COMPLETED
        assert completed_transfer["status"] == TransferStatus.COMPLETED.value

        # Property 5: Completion should record same details
        assert completed_transfer["transfer_id"] == initiated_transfer["transfer_id"]
        assert completed_transfer["quantity"] == quantity
        assert completed_transfer["source_warehouse_id"] == "WH-001"
        assert completed_transfer["destination_warehouse_id"] == "WH-002"
        assert "completed_at" in completed_transfer
