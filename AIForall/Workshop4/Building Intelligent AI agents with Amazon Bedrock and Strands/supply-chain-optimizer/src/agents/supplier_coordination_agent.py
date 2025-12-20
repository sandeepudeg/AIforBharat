"""Supplier Coordination Agent for Supply Chain Optimizer.

This agent is responsible for:
- Managing supplier communication
- Placing and tracking orders
- Comparing supplier options
- Handling delivery status updates
- Retrieving supplier performance metrics
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
import uuid

from src.config import logger
from src.models.supplier import Supplier
from src.models.purchase_order import PurchaseOrder, POStatus
from src.aws.clients import get_dynamodb_resource


class SupplierCoordinationAgent:
    """Agent for supplier coordination and order management."""

    def __init__(self):
        """Initialize the Supplier Coordination Agent."""
        self.dynamodb = get_dynamodb_resource()
        self.suppliers_table_name = "suppliers"
        self.purchase_orders_table_name = "purchase_orders"
        self.logger = logger

    def send_purchase_order(
        self,
        po_id: str,
        sku: str,
        supplier_id: str,
        quantity: int,
        unit_price: float,
        expected_delivery_date: date,
    ) -> Dict[str, Any]:
        """Send a purchase order to a supplier.

        Args:
            po_id: Purchase order identifier
            sku: Stock Keeping Unit
            supplier_id: Supplier identifier
            quantity: Order quantity
            unit_price: Price per unit
            expected_delivery_date: Expected delivery date

        Returns:
            Dictionary with order confirmation details:
            - po_id: Purchase order ID
            - sku: Stock Keeping Unit
            - supplier_id: Supplier ID
            - quantity: Order quantity
            - unit_price: Price per unit
            - total_cost: Total order cost
            - order_date: Order placement date
            - expected_delivery_date: Expected delivery date
            - status: Order status (confirmed)

        Raises:
            ValueError: If any parameter is invalid
        """
        if not po_id or len(po_id.strip()) == 0:
            raise ValueError("PO ID cannot be empty")
        if not sku or len(sku.strip()) == 0:
            raise ValueError("SKU cannot be empty")
        if not supplier_id or len(supplier_id.strip()) == 0:
            raise ValueError("Supplier ID cannot be empty")
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if unit_price <= 0:
            raise ValueError("Unit price must be positive")

        # Calculate total cost
        total_cost = quantity * unit_price

        # Create order confirmation
        order_confirmation = {
            "po_id": po_id,
            "sku": sku,
            "supplier_id": supplier_id,
            "quantity": quantity,
            "unit_price": unit_price,
            "total_cost": total_cost,
            "order_date": datetime.utcnow().isoformat(),
            "expected_delivery_date": expected_delivery_date.isoformat(),
            "status": POStatus.CONFIRMED.value,
        }

        self.logger.info(
            f"Sent purchase order {po_id} to supplier {supplier_id}: "
            f"SKU={sku}, quantity={quantity}, total_cost={total_cost}"
        )

        return order_confirmation

    def track_delivery(
        self,
        po_id: str,
        supplier_id: str,
    ) -> Dict[str, Any]:
        """Track delivery status of a purchase order.

        Args:
            po_id: Purchase order identifier
            supplier_id: Supplier identifier

        Returns:
            Dictionary with tracking information:
            - po_id: Purchase order ID
            - supplier_id: Supplier ID
            - status: Current order status
            - estimated_arrival_date: Estimated arrival date
            - days_remaining: Days until expected delivery
            - is_delayed: Whether delivery is delayed

        Raises:
            ValueError: If PO or supplier ID is invalid
        """
        if not po_id or len(po_id.strip()) == 0:
            raise ValueError("PO ID cannot be empty")
        if not supplier_id or len(supplier_id.strip()) == 0:
            raise ValueError("Supplier ID cannot be empty")

        # In a real implementation, this would query the supplier's system
        # For now, we'll return a tracking structure
        tracking_info = {
            "po_id": po_id,
            "supplier_id": supplier_id,
            "status": POStatus.SHIPPED.value,
            "estimated_arrival_date": (date.today() + timedelta(days=3)).isoformat(),
            "days_remaining": 3,
            "is_delayed": False,
        }

        self.logger.info(
            f"Tracked delivery for PO {po_id} from supplier {supplier_id}: "
            f"status={tracking_info['status']}, "
            f"estimated_arrival={tracking_info['estimated_arrival_date']}"
        )

        return tracking_info

    def compare_suppliers(
        self,
        suppliers: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Compare multiple suppliers and recommend the best option.

        Comparison criteria:
        - Price competitiveness (lower is better)
        - Lead time (shorter is better)
        - Reliability score (higher is better)
        - On-time delivery rate (higher is better)

        Args:
            suppliers: List of supplier data dictionaries with keys:
                - supplier_id: Supplier identifier
                - name: Supplier name
                - price_competitiveness: Price score (0-100)
                - lead_time_days: Lead time in days
                - reliability_score: Reliability score (0-100)
                - on_time_delivery_rate: On-time delivery rate (0-1)

        Returns:
            Dictionary with comparison results:
            - recommended_supplier_id: ID of recommended supplier
            - recommended_supplier_name: Name of recommended supplier
            - comparison_scores: Dict mapping supplier_id to overall score
            - rationale: Explanation of recommendation

        Raises:
            ValueError: If suppliers list is empty or invalid
        """
        if not suppliers or len(suppliers) == 0:
            raise ValueError("At least one supplier must be provided")

        # Validate supplier data
        for supplier in suppliers:
            if "supplier_id" not in supplier:
                raise ValueError("Supplier must have supplier_id")
            if "price_competitiveness" not in supplier:
                raise ValueError("Supplier must have price_competitiveness")
            if "lead_time_days" not in supplier:
                raise ValueError("Supplier must have lead_time_days")
            if "reliability_score" not in supplier:
                raise ValueError("Supplier must have reliability_score")
            if "on_time_delivery_rate" not in supplier:
                raise ValueError("Supplier must have on_time_delivery_rate")

        # Calculate overall score for each supplier
        # Score = (price_competitiveness + reliability_score) / 2 - (lead_time_days / 10)
        # Higher score is better
        comparison_scores = {}

        for supplier in suppliers:
            supplier_id = supplier["supplier_id"]

            # Normalize scores
            price_score = supplier.get("price_competitiveness", 0) / 100.0
            reliability_score = supplier.get("reliability_score", 0) / 100.0
            on_time_rate = supplier.get("on_time_delivery_rate", 0)
            lead_time = supplier.get("lead_time_days", 0)

            # Calculate weighted score
            # 40% price, 30% reliability, 20% on-time delivery, -10% lead time penalty
            overall_score = (
                (price_score * 0.4)
                + (reliability_score * 0.3)
                + (on_time_rate * 0.2)
                - (lead_time / 100.0 * 0.1)
            )

            comparison_scores[supplier_id] = round(overall_score, 4)

        # Find recommended supplier (highest score)
        recommended_supplier_id = max(
            comparison_scores, key=comparison_scores.get
        )
        recommended_supplier = next(
            (s for s in suppliers if s["supplier_id"] == recommended_supplier_id),
            None,
        )

        rationale = (
            f"Supplier {recommended_supplier_id} recommended based on "
            f"best overall score ({comparison_scores[recommended_supplier_id]:.4f}). "
            f"Factors: price competitiveness, reliability, and on-time delivery rate."
        )

        result = {
            "recommended_supplier_id": recommended_supplier_id,
            "recommended_supplier_name": recommended_supplier.get("name", "Unknown"),
            "comparison_scores": comparison_scores,
            "rationale": rationale,
        }

        self.logger.info(
            f"Compared {len(suppliers)} suppliers. "
            f"Recommended: {recommended_supplier_id} with score {comparison_scores[recommended_supplier_id]:.4f}"
        )

        return result

    def update_delivery_status(
        self,
        po_id: str,
        status: str,
        actual_delivery_date: Optional[date] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update delivery status of a purchase order.

        Args:
            po_id: Purchase order identifier
            status: New status (pending, confirmed, shipped, delivered, cancelled)
            actual_delivery_date: Actual delivery date (if delivered)
            notes: Optional notes about the delivery

        Returns:
            Dictionary with updated delivery information:
            - po_id: Purchase order ID
            - status: Updated status
            - actual_delivery_date: Actual delivery date (if applicable)
            - updated_at: Timestamp of update
            - notes: Any notes provided

        Raises:
            ValueError: If status is invalid or required fields are missing
        """
        if not po_id or len(po_id.strip()) == 0:
            raise ValueError("PO ID cannot be empty")

        # Validate status
        valid_statuses = [
            POStatus.PENDING.value,
            POStatus.CONFIRMED.value,
            POStatus.SHIPPED.value,
            POStatus.DELIVERED.value,
            POStatus.CANCELLED.value,
        ]

        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")

        # If status is delivered, actual_delivery_date is required
        if status == POStatus.DELIVERED.value and actual_delivery_date is None:
            raise ValueError(
                "actual_delivery_date is required when status is 'delivered'"
            )

        delivery_update = {
            "po_id": po_id,
            "status": status,
            "actual_delivery_date": (
                actual_delivery_date.isoformat() if actual_delivery_date else None
            ),
            "updated_at": datetime.utcnow().isoformat(),
            "notes": notes,
        }

        self.logger.info(
            f"Updated delivery status for PO {po_id}: "
            f"status={status}, "
            f"actual_delivery_date={actual_delivery_date}"
        )

        return delivery_update

    def get_supplier_performance(
        self,
        supplier_id: str,
    ) -> Dict[str, Any]:
        """Retrieve performance metrics for a supplier.

        Args:
            supplier_id: Supplier identifier

        Returns:
            Dictionary with supplier performance metrics:
            - supplier_id: Supplier ID
            - name: Supplier name
            - total_orders: Total number of orders
            - on_time_delivery_rate: On-time delivery rate (0-1)
            - average_delivery_days: Average delivery time in days
            - reliability_score: Reliability score (0-100)
            - price_competitiveness: Price competitiveness score (0-100)
            - last_order_date: Date of last order

        Raises:
            ValueError: If supplier ID is invalid
        """
        if not supplier_id or len(supplier_id.strip()) == 0:
            raise ValueError("Supplier ID cannot be empty")

        # In a real implementation, this would query the database
        # For now, we'll return a performance structure
        performance = {
            "supplier_id": supplier_id,
            "name": f"Supplier {supplier_id}",
            "total_orders": 0,
            "on_time_delivery_rate": 0.0,
            "average_delivery_days": 0.0,
            "reliability_score": 0.0,
            "price_competitiveness": 0.0,
            "last_order_date": None,
        }

        self.logger.info(
            f"Retrieved performance metrics for supplier {supplier_id}"
        )

        return performance

    def check_delivery_delay(
        self,
        po_id: str,
        expected_delivery_date: date,
        current_status: str,
    ) -> Optional[Dict[str, Any]]:
        """Check if a delivery is delayed and generate alert if needed.

        Args:
            po_id: Purchase order identifier
            expected_delivery_date: Expected delivery date
            current_status: Current order status

        Returns:
            Dictionary with delay alert if delayed, None otherwise:
            - po_id: Purchase order ID
            - is_delayed: Whether delivery is delayed
            - days_overdue: Number of days overdue
            - impact: Estimated inventory impact
            - recommended_actions: List of recommended actions

        Raises:
            ValueError: If parameters are invalid
        """
        if not po_id or len(po_id.strip()) == 0:
            raise ValueError("PO ID cannot be empty")

        # Check if delivery is delayed
        today = date.today()
        is_delayed = today > expected_delivery_date

        if not is_delayed:
            return None

        # Calculate days overdue
        days_overdue = (today - expected_delivery_date).days

        delay_alert = {
            "po_id": po_id,
            "is_delayed": True,
            "days_overdue": days_overdue,
            "impact": f"Delivery is {days_overdue} days late",
            "recommended_actions": [
                "Contact supplier for updated delivery date",
                "Consider alternative suppliers",
                "Adjust inventory forecasts",
                "Notify stakeholders of potential stockout risk",
            ],
        }

        self.logger.warning(
            f"Delivery delay detected for PO {po_id}: "
            f"{days_overdue} days overdue"
        )

        return delay_alert

    def store_purchase_order(
        self,
        po_data: Dict[str, Any],
    ) -> None:
        """Store purchase order in the database.

        Args:
            po_data: Purchase order data to store

        Raises:
            Exception: If database operation fails
        """
        try:
            table = self.dynamodb.Table(self.purchase_orders_table_name)

            # Add metadata
            po_data["created_at"] = datetime.utcnow().isoformat()
            po_data["updated_at"] = datetime.utcnow().isoformat()

            # Store in database
            table.put_item(Item=po_data)

            self.logger.info(
                f"Stored purchase order {po_data.get('po_id')} in database"
            )

        except Exception as e:
            self.logger.error(
                f"Failed to store purchase order: {str(e)}"
            )
            raise

    def store_supplier(
        self,
        supplier_data: Dict[str, Any],
    ) -> None:
        """Store supplier information in the database.

        Args:
            supplier_data: Supplier data to store

        Raises:
            Exception: If database operation fails
        """
        try:
            table = self.dynamodb.Table(self.suppliers_table_name)

            # Add metadata
            supplier_data["created_at"] = datetime.utcnow().isoformat()
            supplier_data["updated_at"] = datetime.utcnow().isoformat()

            # Store in database
            table.put_item(Item=supplier_data)

            self.logger.info(
                f"Stored supplier {supplier_data.get('supplier_id')} in database"
            )

        except Exception as e:
            self.logger.error(
                f"Failed to store supplier: {str(e)}"
            )
            raise

    def retrieve_purchase_order(
        self,
        po_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Retrieve a purchase order from the database.

        Args:
            po_id: Purchase order identifier

        Returns:
            Purchase order data if found, None otherwise

        Raises:
            Exception: If database operation fails
        """
        try:
            table = self.dynamodb.Table(self.purchase_orders_table_name)

            response = table.get_item(Key={"po_id": po_id})

            if "Item" in response:
                self.logger.info(f"Retrieved purchase order {po_id} from database")
                return response["Item"]

            self.logger.warning(f"Purchase order {po_id} not found in database")
            return None

        except Exception as e:
            self.logger.error(
                f"Failed to retrieve purchase order {po_id}: {str(e)}"
            )
            raise

    def retrieve_supplier(
        self,
        supplier_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Retrieve supplier information from the database.

        Args:
            supplier_id: Supplier identifier

        Returns:
            Supplier data if found, None otherwise

        Raises:
            Exception: If database operation fails
        """
        try:
            table = self.dynamodb.Table(self.suppliers_table_name)

            response = table.get_item(Key={"supplier_id": supplier_id})

            if "Item" in response:
                self.logger.info(f"Retrieved supplier {supplier_id} from database")
                return response["Item"]

            self.logger.warning(f"Supplier {supplier_id} not found in database")
            return None

        except Exception as e:
            self.logger.error(
                f"Failed to retrieve supplier {supplier_id}: {str(e)}"
            )
            raise
