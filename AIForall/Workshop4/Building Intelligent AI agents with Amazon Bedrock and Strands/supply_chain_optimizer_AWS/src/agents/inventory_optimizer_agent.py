"""Inventory Optimizer Agent for Supply Chain Optimizer.

This agent is responsible for:
- Calculating Economic Order Quantity (EOQ)
- Determining reorder points
- Optimizing multi-warehouse inventory distribution
- Generating purchase order recommendations
- Triggering PO recommendations when inventory falls below reorder point
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal
import uuid
import math
import statistics

from src.config import logger
from src.models.product import Product
from src.models.inventory import Inventory
from src.models.purchase_order import PurchaseOrder, POStatus
from src.aws.clients import get_dynamodb_resource


class InventoryOptimizerAgent:
    """Agent for inventory optimization using EOQ and reorder point calculations."""

    def __init__(self):
        """Initialize the Inventory Optimizer Agent."""
        self.dynamodb = get_dynamodb_resource()
        self.products_table_name = "products"
        self.inventory_table_name = "inventory"
        self.purchase_orders_table_name = "purchase_orders"
        self.logger = logger

    def calculate_eoq(
        self,
        annual_demand: float,
        ordering_cost: float,
        holding_cost_per_unit: float,
    ) -> int:
        """Calculate Economic Order Quantity using EOQ formula.

        EOQ = √(2DS/H)
        where:
        - D = annual demand
        - S = ordering cost per order
        - H = holding cost per unit per year

        Args:
            annual_demand: Total annual demand for the product
            ordering_cost: Cost to place one order
            holding_cost_per_unit: Annual holding cost per unit

        Returns:
            Economic Order Quantity (rounded to nearest integer)

        Raises:
            ValueError: If any parameter is invalid
        """
        if annual_demand <= 0:
            raise ValueError("Annual demand must be positive")
        if ordering_cost < 0:
            raise ValueError("Ordering cost cannot be negative")
        if holding_cost_per_unit <= 0:
            raise ValueError("Holding cost per unit must be positive")

        # Calculate EOQ using the formula
        numerator = 2 * annual_demand * ordering_cost
        denominator = holding_cost_per_unit

        eoq = math.sqrt(numerator / denominator)
        eoq_rounded = max(1, int(round(eoq)))

        self.logger.info(
            f"Calculated EOQ: {eoq_rounded} "
            f"(demand={annual_demand}, ordering_cost={ordering_cost}, "
            f"holding_cost={holding_cost_per_unit})"
        )

        return eoq_rounded

    def calculate_reorder_point(
        self,
        average_daily_demand: float,
        lead_time_days: int,
        safety_stock: int,
    ) -> int:
        """Calculate reorder point for a product.

        Reorder Point = (Average Daily Demand × Lead Time) + Safety Stock

        Args:
            average_daily_demand: Average daily demand for the product
            lead_time_days: Lead time from supplier in days
            safety_stock: Safety stock quantity to maintain

        Returns:
            Reorder point quantity

        Raises:
            ValueError: If any parameter is invalid
        """
        if average_daily_demand < 0:
            raise ValueError("Average daily demand cannot be negative")
        if lead_time_days < 0:
            raise ValueError("Lead time cannot be negative")
        if safety_stock < 0:
            raise ValueError("Safety stock cannot be negative")

        # Calculate reorder point
        reorder_point = int((average_daily_demand * lead_time_days) + safety_stock)

        self.logger.info(
            f"Calculated reorder point: {reorder_point} "
            f"(daily_demand={average_daily_demand}, lead_time={lead_time_days}, "
            f"safety_stock={safety_stock})"
        )

        return reorder_point

    def optimize_warehouse_distribution(
        self,
        sku: str,
        total_inventory: int,
        warehouses: List[Dict[str, Any]],
        demand_forecasts: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """Optimize inventory distribution across multiple warehouses.

        Allocates inventory to warehouses based on:
        - Regional demand forecasts
        - Warehouse capacity constraints
        - Minimizing total holding costs

        Args:
            sku: Stock Keeping Unit identifier
            total_inventory: Total inventory quantity to distribute
            warehouses: List of warehouse data with keys:
                - warehouse_id: Warehouse identifier
                - capacity: Maximum capacity
                - current_inventory: Current inventory level
                - holding_cost_per_unit: Holding cost for this warehouse
            demand_forecasts: Optional dict mapping warehouse_id to forecasted demand

        Returns:
            Dictionary with:
            - allocations: Dict mapping warehouse_id to allocated quantity
            - total_allocated: Total quantity allocated
            - holding_cost_estimate: Estimated total holding cost
        """
        if not warehouses or len(warehouses) == 0:
            raise ValueError("At least one warehouse must be provided")

        if total_inventory < 0:
            raise ValueError("Total inventory cannot be negative")

        # If no demand forecasts provided, distribute equally
        if not demand_forecasts:
            demand_forecasts = {wh["warehouse_id"]: 1.0 for wh in warehouses}

        # Normalize demand forecasts to sum to 1.0
        total_demand = sum(demand_forecasts.values())
        if total_demand == 0:
            normalized_forecasts = {wh["warehouse_id"]: 1.0 / len(warehouses) for wh in warehouses}
        else:
            normalized_forecasts = {
                wh_id: demand / total_demand for wh_id, demand in demand_forecasts.items()
            }

        # Allocate inventory based on normalized demand
        allocations = {}
        total_allocated = 0
        holding_cost_estimate = 0.0

        for warehouse in warehouses:
            wh_id = warehouse["warehouse_id"]
            capacity = warehouse.get("capacity", float("inf"))
            holding_cost = warehouse.get("holding_cost_per_unit", 0.0)

            # Calculate allocation based on demand forecast
            allocation = int(total_inventory * normalized_forecasts.get(wh_id, 0))

            # Respect warehouse capacity
            allocation = min(allocation, capacity)

            allocations[wh_id] = allocation
            total_allocated += allocation
            holding_cost_estimate += allocation * holding_cost

        self.logger.info(
            f"Optimized warehouse distribution for SKU {sku}: "
            f"allocations={allocations}, total_allocated={total_allocated}, "
            f"holding_cost_estimate={holding_cost_estimate}"
        )

        return {
            "allocations": allocations,
            "total_allocated": total_allocated,
            "holding_cost_estimate": holding_cost_estimate,
        }

    def generate_po_recommendation(
        self,
        sku: str,
        supplier_id: str,
        quantity: int,
        unit_price: float,
        lead_time_days: int,
    ) -> Dict[str, Any]:
        """Generate a purchase order recommendation.

        Args:
            sku: Stock Keeping Unit identifier
            supplier_id: Supplier identifier
            quantity: Recommended order quantity
            unit_price: Price per unit
            lead_time_days: Expected lead time in days

        Returns:
            Dictionary with PO recommendation details:
            - po_id: Generated PO ID
            - sku: Stock Keeping Unit
            - supplier_id: Supplier ID
            - quantity: Order quantity
            - unit_price: Price per unit
            - total_cost: Total order cost
            - expected_delivery_date: Expected delivery date
            - status: Order status (pending)
        """
        if quantity <= 0:
            raise ValueError("Order quantity must be positive")
        if unit_price <= 0:
            raise ValueError("Unit price must be positive")
        if lead_time_days < 0:
            raise ValueError("Lead time cannot be negative")

        # Generate PO ID
        po_id = f"PO-{uuid.uuid4().hex[:12].upper()}"

        # Calculate total cost
        total_cost = quantity * unit_price

        # Calculate expected delivery date
        expected_delivery_date = date.today() + timedelta(days=lead_time_days)

        po_recommendation = {
            "po_id": po_id,
            "sku": sku,
            "supplier_id": supplier_id,
            "quantity": quantity,
            "unit_price": unit_price,
            "total_cost": total_cost,
            "expected_delivery_date": expected_delivery_date.isoformat(),
            "status": POStatus.PENDING.value,
        }

        self.logger.info(
            f"Generated PO recommendation {po_id} for SKU {sku}: "
            f"quantity={quantity}, total_cost={total_cost}, "
            f"expected_delivery={expected_delivery_date}"
        )

        return po_recommendation

    def trigger_po_recommendation_if_needed(
        self,
        sku: str,
        current_inventory: int,
        reorder_point: int,
        supplier_id: str,
        eoq: int,
        unit_price: float,
        lead_time_days: int,
    ) -> Optional[Dict[str, Any]]:
        """Trigger a PO recommendation if inventory falls below reorder point.

        Args:
            sku: Stock Keeping Unit identifier
            current_inventory: Current inventory level
            reorder_point: Reorder point threshold
            supplier_id: Supplier identifier
            eoq: Economic Order Quantity
            unit_price: Price per unit
            lead_time_days: Lead time in days

        Returns:
            PO recommendation if triggered, None otherwise
        """
        if current_inventory < reorder_point:
            self.logger.warning(
                f"Inventory for SKU {sku} ({current_inventory}) "
                f"has fallen below reorder point ({reorder_point}). "
                f"Triggering PO recommendation."
            )

            po_recommendation = self.generate_po_recommendation(
                sku=sku,
                supplier_id=supplier_id,
                quantity=eoq,
                unit_price=unit_price,
                lead_time_days=lead_time_days,
            )

            return po_recommendation

        return None

    def optimize_product_inventory(
        self,
        product: Product,
        annual_demand: float,
        average_daily_demand: float,
        safety_stock: int,
    ) -> Dict[str, Any]:
        """Optimize inventory parameters for a product.

        This is the main entry point that orchestrates all optimization steps.

        Args:
            product: Product model instance
            annual_demand: Total annual demand for the product
            average_daily_demand: Average daily demand
            safety_stock: Safety stock quantity to maintain

        Returns:
            Dictionary with optimized inventory parameters:
            - sku: Stock Keeping Unit
            - eoq: Economic Order Quantity
            - reorder_point: Reorder point
            - safety_stock: Safety stock
            - annual_demand: Annual demand
            - average_daily_demand: Average daily demand
        """
        # Step 1: Calculate EOQ
        eoq = self.calculate_eoq(
            annual_demand=annual_demand,
            ordering_cost=product.ordering_cost,
            holding_cost_per_unit=product.holding_cost_per_unit,
        )

        # Step 2: Calculate reorder point
        reorder_point = self.calculate_reorder_point(
            average_daily_demand=average_daily_demand,
            lead_time_days=product.lead_time_days,
            safety_stock=safety_stock,
        )

        optimization_result = {
            "sku": product.sku,
            "eoq": eoq,
            "reorder_point": reorder_point,
            "safety_stock": safety_stock,
            "annual_demand": annual_demand,
            "average_daily_demand": average_daily_demand,
        }

        self.logger.info(
            f"Optimized inventory for SKU {product.sku}: "
            f"eoq={eoq}, reorder_point={reorder_point}"
        )

        return optimization_result

    def store_optimization_results(
        self,
        sku: str,
        optimization_results: Dict[str, Any],
    ) -> None:
        """Store optimization results in the database.

        Args:
            sku: Stock Keeping Unit identifier
            optimization_results: Optimization results to store
        """
        try:
            table = self.dynamodb.Table(self.products_table_name)

            # Update product with optimization results
            update_expression = (
                "SET reorder_point = :rp, "
                "economic_order_quantity = :eoq, "
                "updated_at = :updated_at"
            )

            expression_values = {
                ":rp": optimization_results["reorder_point"],
                ":eoq": optimization_results["eoq"],
                ":updated_at": datetime.utcnow().isoformat(),
            }

            table.update_item(
                Key={"sku": sku},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values,
            )

            self.logger.info(
                f"Stored optimization results for SKU {sku} in database"
            )

        except Exception as e:
            self.logger.error(
                f"Failed to store optimization results for SKU {sku}: {str(e)}"
            )
            raise
