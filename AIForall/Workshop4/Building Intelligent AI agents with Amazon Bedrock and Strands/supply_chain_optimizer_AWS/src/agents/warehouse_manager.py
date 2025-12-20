"""Warehouse Manager for multi-warehouse inventory management.

This module is responsible for:
- Warehouse capacity tracking
- Inventory transfer logic between warehouses
- Warehouse disruption handling
- Regional demand-based allocation
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import uuid
import math

from src.config import logger
from src.models.warehouse import Warehouse, WarehouseStatus
from src.models.inventory_transfer import InventoryTransfer, TransferStatus
from src.models.inventory import Inventory
from src.aws.clients import get_dynamodb_resource


class WarehouseManager:
    """Manager for multi-warehouse operations."""

    def __init__(self):
        """Initialize the Warehouse Manager."""
        self.dynamodb = get_dynamodb_resource()
        self.warehouses_table_name = "warehouses"
        self.transfers_table_name = "inventory_transfers"
        self.inventory_table_name = "inventory"
        self.logger = logger

    def track_warehouse_capacity(
        self,
        warehouse_id: str,
        current_inventory: int,
        capacity: int,
    ) -> Dict[str, Any]:
        """Track warehouse capacity utilization.

        Args:
            warehouse_id: Warehouse identifier
            current_inventory: Current inventory level
            capacity: Maximum warehouse capacity

        Returns:
            Dictionary with capacity metrics:
            - warehouse_id: Warehouse identifier
            - current_inventory: Current inventory level
            - capacity: Maximum capacity
            - utilization_percentage: Percentage of capacity used
            - available_capacity: Remaining capacity
            - is_at_capacity: Boolean indicating if warehouse is at capacity
            - is_near_capacity: Boolean indicating if warehouse is >80% full
        """
        if capacity <= 0:
            raise ValueError("Warehouse capacity must be positive")
        if current_inventory < 0:
            raise ValueError("Current inventory cannot be negative")
        if current_inventory > capacity:
            raise ValueError("Current inventory cannot exceed warehouse capacity")

        utilization_percentage = (current_inventory / capacity) * 100
        available_capacity = capacity - current_inventory
        is_at_capacity = current_inventory >= capacity
        is_near_capacity = utilization_percentage >= 80

        capacity_metrics = {
            "warehouse_id": warehouse_id,
            "current_inventory": current_inventory,
            "capacity": capacity,
            "utilization_percentage": round(utilization_percentage, 2),
            "available_capacity": available_capacity,
            "is_at_capacity": is_at_capacity,
            "is_near_capacity": is_near_capacity,
        }

        self.logger.info(
            f"Warehouse {warehouse_id} capacity tracking: "
            f"utilization={utilization_percentage:.2f}%, "
            f"available={available_capacity}"
        )

        return capacity_metrics

    def initiate_inventory_transfer(
        self,
        sku: str,
        source_warehouse_id: str,
        destination_warehouse_id: str,
        quantity: int,
        transfer_cost_per_unit: float,
    ) -> Dict[str, Any]:
        """Initiate an inventory transfer between warehouses.

        Args:
            sku: Stock Keeping Unit
            source_warehouse_id: Source warehouse identifier
            destination_warehouse_id: Destination warehouse identifier
            quantity: Quantity to transfer
            transfer_cost_per_unit: Cost per unit to transfer

        Returns:
            Dictionary with transfer details:
            - transfer_id: Generated transfer ID
            - sku: Stock Keeping Unit
            - source_warehouse_id: Source warehouse
            - destination_warehouse_id: Destination warehouse
            - quantity: Transfer quantity
            - transfer_cost: Total transfer cost
            - status: Transfer status (pending)
            - initiated_at: Timestamp of initiation
        """
        if quantity <= 0:
            raise ValueError("Transfer quantity must be positive")
        if transfer_cost_per_unit < 0:
            raise ValueError("Transfer cost cannot be negative")
        if source_warehouse_id == destination_warehouse_id:
            raise ValueError("Source and destination warehouses must be different")

        # Generate transfer ID
        transfer_id = f"TRF-{uuid.uuid4().hex[:12].upper()}"

        # Calculate total transfer cost
        total_transfer_cost = quantity * transfer_cost_per_unit

        # Create transfer record
        transfer_record = {
            "transfer_id": transfer_id,
            "sku": sku,
            "source_warehouse_id": source_warehouse_id,
            "destination_warehouse_id": destination_warehouse_id,
            "quantity": quantity,
            "transfer_cost": total_transfer_cost,
            "status": TransferStatus.PENDING.value,
            "initiated_at": datetime.utcnow().isoformat(),
        }

        self.logger.info(
            f"Initiated inventory transfer {transfer_id}: "
            f"SKU={sku}, from {source_warehouse_id} to {destination_warehouse_id}, "
            f"quantity={quantity}, cost={total_transfer_cost}"
        )

        return transfer_record

    def complete_inventory_transfer(
        self,
        transfer_id: str,
        source_warehouse_id: str,
        destination_warehouse_id: str,
        quantity: int,
    ) -> Dict[str, Any]:
        """Complete an inventory transfer between warehouses.

        Args:
            transfer_id: Transfer identifier
            source_warehouse_id: Source warehouse identifier
            destination_warehouse_id: Destination warehouse identifier
            quantity: Quantity transferred

        Returns:
            Dictionary with completion details:
            - transfer_id: Transfer ID
            - status: Transfer status (completed)
            - completed_at: Completion timestamp
            - source_warehouse_id: Source warehouse
            - destination_warehouse_id: Destination warehouse
            - quantity: Transferred quantity
        """
        if quantity <= 0:
            raise ValueError("Transfer quantity must be positive")

        completion_record = {
            "transfer_id": transfer_id,
            "status": TransferStatus.COMPLETED.value,
            "completed_at": datetime.utcnow().isoformat(),
            "source_warehouse_id": source_warehouse_id,
            "destination_warehouse_id": destination_warehouse_id,
            "quantity": quantity,
        }

        self.logger.info(
            f"Completed inventory transfer {transfer_id}: "
            f"moved {quantity} units from {source_warehouse_id} to {destination_warehouse_id}"
        )

        return completion_record

    def handle_warehouse_disruption(
        self,
        disrupted_warehouse_id: str,
        available_warehouses: List[Dict[str, Any]],
        inventory_to_redistribute: Dict[str, int],
    ) -> Dict[str, Any]:
        """Handle warehouse disruption by redistributing inventory.

        When a warehouse experiences a disruption, this function redistributes
        its inventory to other available warehouses to maintain service levels.

        Args:
            disrupted_warehouse_id: ID of disrupted warehouse
            available_warehouses: List of available warehouses with:
                - warehouse_id: Warehouse identifier
                - current_inventory: Current inventory level
                - capacity: Maximum capacity
                - holding_cost_per_unit: Holding cost
            inventory_to_redistribute: Dict mapping SKU to quantity to redistribute

        Returns:
            Dictionary with redistribution plan:
            - disrupted_warehouse_id: Disrupted warehouse ID
            - transfers: List of transfer recommendations
            - total_redistributed: Total quantity redistributed
            - redistribution_cost: Total cost of redistribution
        """
        if not available_warehouses or len(available_warehouses) == 0:
            raise ValueError("At least one available warehouse must be provided")

        transfers = []
        total_redistributed = 0
        redistribution_cost = 0.0

        # For each SKU to redistribute
        for sku, quantity in inventory_to_redistribute.items():
            remaining_quantity = quantity
            remaining_warehouses = available_warehouses.copy()

            # Distribute to warehouses with available capacity
            while remaining_quantity > 0 and remaining_warehouses:
                # Find warehouse with most available capacity
                best_warehouse = None
                max_available_capacity = 0

                for warehouse in remaining_warehouses:
                    available_capacity = (
                        warehouse["capacity"] - warehouse["current_inventory"]
                    )
                    if available_capacity > max_available_capacity:
                        max_available_capacity = available_capacity
                        best_warehouse = warehouse

                if best_warehouse is None or max_available_capacity == 0:
                    # No more capacity available
                    break

                # Calculate quantity to transfer to this warehouse
                transfer_quantity = min(remaining_quantity, max_available_capacity)

                # Create transfer recommendation
                transfer = {
                    "sku": sku,
                    "source_warehouse_id": disrupted_warehouse_id,
                    "destination_warehouse_id": best_warehouse["warehouse_id"],
                    "quantity": transfer_quantity,
                    "transfer_cost": transfer_quantity * 0.5,  # Default transfer cost
                }

                transfers.append(transfer)
                total_redistributed += transfer_quantity
                redistribution_cost += transfer["transfer_cost"]
                remaining_quantity -= transfer_quantity

                # Update warehouse inventory for next iteration
                best_warehouse["current_inventory"] += transfer_quantity

                # Remove warehouse if at capacity
                if best_warehouse["current_inventory"] >= best_warehouse["capacity"]:
                    remaining_warehouses.remove(best_warehouse)

        redistribution_plan = {
            "disrupted_warehouse_id": disrupted_warehouse_id,
            "transfers": transfers,
            "total_redistributed": total_redistributed,
            "redistribution_cost": redistribution_cost,
        }

        self.logger.warning(
            f"Warehouse {disrupted_warehouse_id} disruption handled: "
            f"redistributed {total_redistributed} units across {len(transfers)} transfers, "
            f"cost={redistribution_cost}"
        )

        return redistribution_plan

    def allocate_inventory_by_regional_demand(
        self,
        sku: str,
        total_inventory: int,
        warehouses: List[Dict[str, Any]],
        regional_demand_forecasts: Dict[str, float],
    ) -> Dict[str, Any]:
        """Allocate inventory to warehouses based on regional demand forecasts.

        This function distributes inventory proportionally to regional demand
        while respecting warehouse capacity constraints.

        Args:
            sku: Stock Keeping Unit
            total_inventory: Total inventory to allocate
            warehouses: List of warehouses with:
                - warehouse_id: Warehouse identifier
                - location: Warehouse location/region
                - capacity: Maximum capacity
                - current_inventory: Current inventory level
                - holding_cost_per_unit: Holding cost
            regional_demand_forecasts: Dict mapping region to forecasted demand

        Returns:
            Dictionary with allocation plan:
            - sku: Stock Keeping Unit
            - allocations: Dict mapping warehouse_id to allocated quantity
            - total_allocated: Total quantity allocated
            - holding_cost_estimate: Estimated total holding cost
            - demand_fulfillment_rate: Percentage of demand that can be fulfilled
        """
        if not warehouses or len(warehouses) == 0:
            raise ValueError("At least one warehouse must be provided")
        if total_inventory < 0:
            raise ValueError("Total inventory cannot be negative")

        allocations = {}
        total_allocated = 0
        holding_cost_estimate = 0.0

        # Calculate total demand
        total_demand = sum(regional_demand_forecasts.values())

        if total_demand == 0:
            # No demand, distribute equally
            per_warehouse = total_inventory // len(warehouses)
            for warehouse in warehouses:
                wh_id = warehouse["warehouse_id"]
                capacity = warehouse.get("capacity", float("inf"))
                allocation = min(per_warehouse, capacity)
                allocations[wh_id] = allocation
                total_allocated += allocation
        else:
            # Allocate based on regional demand
            for warehouse in warehouses:
                wh_id = warehouse["warehouse_id"]
                location = warehouse.get("location", "unknown")
                capacity = warehouse.get("capacity", float("inf"))
                holding_cost = warehouse.get("holding_cost_per_unit", 0.0)

                # Get demand for this warehouse's region
                regional_demand = regional_demand_forecasts.get(location, 0.0)

                # Calculate allocation based on demand proportion
                if total_demand > 0:
                    demand_proportion = regional_demand / total_demand
                    allocation = int(total_inventory * demand_proportion)
                else:
                    allocation = 0

                # Respect warehouse capacity
                allocation = min(allocation, capacity)

                allocations[wh_id] = allocation
                total_allocated += allocation
                holding_cost_estimate += allocation * holding_cost

        # Calculate demand fulfillment rate
        demand_fulfillment_rate = (
            (total_allocated / total_inventory * 100) if total_inventory > 0 else 100.0
        )

        allocation_plan = {
            "sku": sku,
            "allocations": allocations,
            "total_allocated": total_allocated,
            "holding_cost_estimate": holding_cost_estimate,
            "demand_fulfillment_rate": round(demand_fulfillment_rate, 2),
        }

        self.logger.info(
            f"Allocated inventory for SKU {sku} by regional demand: "
            f"total_allocated={total_allocated}, "
            f"fulfillment_rate={demand_fulfillment_rate:.2f}%, "
            f"holding_cost={holding_cost_estimate}"
        )

        return allocation_plan

    def recommend_inventory_transfers_for_capacity(
        self,
        warehouses: List[Dict[str, Any]],
        inventory_by_warehouse: Dict[str, Dict[str, int]],
    ) -> List[Dict[str, Any]]:
        """Recommend inventory transfers when a warehouse reaches capacity.

        Args:
            warehouses: List of warehouses with capacity info
            inventory_by_warehouse: Dict mapping warehouse_id to {sku: quantity}

        Returns:
            List of transfer recommendations
        """
        recommendations = []

        for warehouse in warehouses:
            wh_id = warehouse["warehouse_id"]
            capacity = warehouse.get("capacity", float("inf"))
            current_inventory = warehouse.get("current_inventory", 0)

            # Check if warehouse is at or near capacity
            if current_inventory >= capacity * 0.9:  # 90% full
                # Find other warehouses with available capacity
                for other_warehouse in warehouses:
                    other_wh_id = other_warehouse["warehouse_id"]
                    if other_wh_id == wh_id:
                        continue

                    other_capacity = other_warehouse.get("capacity", float("inf"))
                    other_inventory = other_warehouse.get("current_inventory", 0)
                    other_available = other_capacity - other_inventory

                    if other_available > 0:
                        # Recommend transferring inventory to other warehouse
                        # Transfer up to 20% of current inventory or available capacity
                        transfer_quantity = min(
                            int(current_inventory * 0.2), other_available
                        )

                        if transfer_quantity > 0:
                            recommendation = {
                                "source_warehouse_id": wh_id,
                                "destination_warehouse_id": other_wh_id,
                                "recommended_quantity": transfer_quantity,
                                "reason": "Source warehouse at capacity",
                            }
                            recommendations.append(recommendation)

        self.logger.info(
            f"Generated {len(recommendations)} inventory transfer recommendations "
            f"for capacity management"
        )

        return recommendations

    def get_warehouse_status(
        self,
        warehouse_id: str,
        current_inventory: int,
        capacity: int,
        status: WarehouseStatus,
    ) -> Dict[str, Any]:
        """Get comprehensive warehouse status.

        Args:
            warehouse_id: Warehouse identifier
            current_inventory: Current inventory level
            capacity: Maximum capacity
            status: Warehouse operational status

        Returns:
            Dictionary with warehouse status:
            - warehouse_id: Warehouse identifier
            - status: Operational status
            - capacity_metrics: Capacity utilization metrics
            - is_operational: Boolean indicating if warehouse is operational
            - recommendations: List of recommended actions
        """
        capacity_metrics = self.track_warehouse_capacity(
            warehouse_id, current_inventory, capacity
        )

        is_operational = status == WarehouseStatus.OPERATIONAL

        recommendations = []
        if capacity_metrics["is_near_capacity"]:
            recommendations.append("Consider transferring inventory to other warehouses")
        if not is_operational:
            recommendations.append(f"Warehouse is {status.value} - plan redistribution")

        warehouse_status = {
            "warehouse_id": warehouse_id,
            "status": status.value,
            "capacity_metrics": capacity_metrics,
            "is_operational": is_operational,
            "recommendations": recommendations,
        }

        return warehouse_status
