"""Purchase order management API endpoints."""

from flask import Blueprint, request, jsonify
from datetime import datetime
from typing import Dict, Any

from src.config import logger
from src.api.auth import APIAuth
from src.database.connection import get_rds_session
from src.database.schema import PurchaseOrderTable


po_bp = Blueprint("purchase_order", __name__, url_prefix="/api/purchase-orders")


@po_bp.route("", methods=["GET"])
@APIAuth.require_auth
def list_purchase_orders() -> tuple:
    """List purchase orders with optional filtering.
    
    Query Parameters:
        - status: Filter by status (pending, confirmed, shipped, delivered, cancelled)
        - supplier_id: Filter by supplier
        - sku: Filter by product SKU
        - limit: Number of results (default: 100)
        - offset: Pagination offset (default: 0)
    
    Returns:
        JSON with purchase order records
    """
    try:
        status = request.args.get("status")
        supplier_id = request.args.get("supplier_id")
        sku = request.args.get("sku")
        limit = int(request.args.get("limit", 100))
        offset = int(request.args.get("offset", 0))

        if limit < 1 or limit > 1000:
            return jsonify({"error": "Limit must be between 1 and 1000"}), 400

        session = get_rds_session()

        try:
            query = session.query(PurchaseOrderTable)

            if status:
                query = query.filter(PurchaseOrderTable.status == status)
            if supplier_id:
                query = query.filter(PurchaseOrderTable.supplier_id == supplier_id)
            if sku:
                query = query.filter(PurchaseOrderTable.sku == sku)

            total_count = query.count()
            results = query.limit(limit).offset(offset).all()

            logger.info(f"Listed purchase orders: status={status}, supplier={supplier_id}, count={len(results)}")

            return jsonify({
                "data": [r.dict() for r in results],
                "total": total_count,
                "limit": limit,
                "offset": offset,
            }), 200

        finally:
            session.close()

    except ValueError as e:
        logger.error(f"Invalid query parameters: {str(e)}")
        return jsonify({"error": "Invalid query parameters"}), 400
    except Exception as e:
        logger.error(f"Failed to list purchase orders: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@po_bp.route("/<po_id>", methods=["GET"])
@APIAuth.require_auth
def get_purchase_order(po_id: str) -> tuple:
    """Get purchase order by ID.
    
    Args:
        po_id: Purchase order ID
    
    Returns:
        JSON with purchase order details
    """
    try:
        session = get_rds_session()

        try:
            po = session.query(PurchaseOrderTable).filter(
                PurchaseOrderTable.po_id == po_id
            ).first()

            if not po:
                logger.warning(f"Purchase order not found: {po_id}")
                return jsonify({"error": "Purchase order not found"}), 404

            logger.info(f"Retrieved purchase order: {po_id}")
            return jsonify(po.dict()), 200

        finally:
            session.close()

    except Exception as e:
        logger.error(f"Failed to get purchase order: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@po_bp.route("", methods=["POST"])
@APIAuth.require_auth
def create_purchase_order() -> tuple:
    """Create a new purchase order.
    
    Request Body:
        {
            "sku": "PROD-001",
            "supplier_id": "SUP-001",
            "quantity": 100,
            "unit_price": 10.50,
            "expected_delivery_date": "2024-02-15"
        }
    
    Returns:
        JSON with created purchase order
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        # Validate required fields
        required_fields = ["sku", "supplier_id", "quantity", "unit_price", "expected_delivery_date"]
        missing_fields = [f for f in required_fields if f not in data]

        if missing_fields:
            return jsonify({"error": f"Missing required fields: {missing_fields}"}), 400

        # Validate data
        try:
            po_data = {
                "po_id": f"PO-{datetime.utcnow().timestamp()}",
                "sku": data["sku"],
                "supplier_id": data["supplier_id"],
                "quantity": int(data["quantity"]),
                "unit_price": float(data["unit_price"]),
                "total_cost": int(data["quantity"]) * float(data["unit_price"]),
                "order_date": datetime.utcnow(),
                "expected_delivery_date": datetime.fromisoformat(data["expected_delivery_date"]).date(),
                "status": "pending",
            }
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            return jsonify({"error": f"Validation error: {str(e)}"}), 400

        session = get_rds_session()

        try:
            po_obj = PurchaseOrderTable(
                po_id=po_data["po_id"],
                sku=po_data["sku"],
                supplier_id=po_data["supplier_id"],
                quantity=po_data["quantity"],
                unit_price=po_data["unit_price"],
                total_cost=po_data["total_cost"],
                order_date=po_data["order_date"],
                expected_delivery_date=po_data["expected_delivery_date"],
                status=po_data["status"],
            )
            session.add(po_obj)
            session.commit()

            logger.info(f"Created purchase order: {po_obj.po_id}")
            return jsonify(po_obj.dict()), 201

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to create purchase order: {str(e)}")
            return jsonify({"error": "Failed to create purchase order"}), 500
        finally:
            session.close()

    except Exception as e:
        logger.error(f"Failed to process purchase order creation: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@po_bp.route("/<po_id>/status", methods=["PATCH"])
@APIAuth.require_auth
def update_purchase_order_status(po_id: str) -> tuple:
    """Update purchase order status.
    
    Args:
        po_id: Purchase order ID
    
    Request Body:
        {
            "status": "shipped",
            "actual_delivery_date": "2024-02-14" (optional)
        }
    
    Returns:
        JSON with updated purchase order
    """
    try:
        data = request.get_json()

        if not data or "status" not in data:
            return jsonify({"error": "Status is required"}), 400

        valid_statuses = ["pending", "confirmed", "shipped", "delivered", "cancelled"]
        if data["status"] not in valid_statuses:
            return jsonify({"error": f"Invalid status. Must be one of: {valid_statuses}"}), 400

        session = get_rds_session()

        try:
            po = session.query(PurchaseOrderTable).filter(
                PurchaseOrderTable.po_id == po_id
            ).first()

            if not po:
                logger.warning(f"Purchase order not found: {po_id}")
                return jsonify({"error": "Purchase order not found"}), 404

            po.status = data["status"]

            if data["status"] == "delivered" and "actual_delivery_date" in data:
                po.actual_delivery_date = datetime.fromisoformat(data["actual_delivery_date"]).date()

            session.commit()

            logger.info(f"Updated purchase order status: {po_id} -> {data['status']}")
            return jsonify(po.dict()), 200

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to update purchase order: {str(e)}")
            return jsonify({"error": "Failed to update purchase order"}), 500
        finally:
            session.close()

    except Exception as e:
        logger.error(f"Failed to process status update: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@po_bp.route("/<po_id>", methods=["DELETE"])
@APIAuth.require_auth
def cancel_purchase_order(po_id: str) -> tuple:
    """Cancel a purchase order.
    
    Args:
        po_id: Purchase order ID
    
    Returns:
        JSON with cancellation confirmation
    """
    try:
        session = get_rds_session()

        try:
            po = session.query(PurchaseOrderTable).filter(
                PurchaseOrderTable.po_id == po_id
            ).first()

            if not po:
                logger.warning(f"Purchase order not found: {po_id}")
                return jsonify({"error": "Purchase order not found"}), 404

            if po.status == "delivered":
                return jsonify({"error": "Cannot cancel delivered orders"}), 400

            po.status = "cancelled"
            session.commit()

            logger.info(f"Cancelled purchase order: {po_id}")
            return jsonify({"message": "Purchase order cancelled", "po_id": po_id}), 200

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to cancel purchase order: {str(e)}")
            return jsonify({"error": "Failed to cancel purchase order"}), 500
        finally:
            session.close()

    except Exception as e:
        logger.error(f"Failed to process cancellation: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
