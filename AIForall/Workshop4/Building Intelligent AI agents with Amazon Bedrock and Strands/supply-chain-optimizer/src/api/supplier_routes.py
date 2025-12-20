"""Supplier management API endpoints."""

from flask import Blueprint, request, jsonify
from datetime import datetime
from typing import Dict, Any

from src.config import logger
from src.api.auth import APIAuth
from src.database.connection import get_rds_session
from src.database.schema import SupplierTable


supplier_bp = Blueprint("supplier", __name__, url_prefix="/api/suppliers")


@supplier_bp.route("", methods=["GET"])
@APIAuth.require_auth
def list_suppliers() -> tuple:
    """List suppliers with optional filtering.
    
    Query Parameters:
        - name: Filter by supplier name (partial match)
        - min_reliability: Filter by minimum reliability score (0-100)
        - limit: Number of results (default: 100)
        - offset: Pagination offset (default: 0)
    
    Returns:
        JSON with supplier records
    """
    try:
        name = request.args.get("name")
        min_reliability = request.args.get("min_reliability")
        limit = int(request.args.get("limit", 100))
        offset = int(request.args.get("offset", 0))

        if limit < 1 or limit > 1000:
            return jsonify({"error": "Limit must be between 1 and 1000"}), 400

        session = get_rds_session()

        try:
            query = session.query(SupplierTable)

            if name:
                query = query.filter(SupplierTable.name.ilike(f"%{name}%"))

            if min_reliability:
                try:
                    min_rel = float(min_reliability)
                    if min_rel < 0 or min_rel > 100:
                        return jsonify({"error": "Reliability score must be between 0 and 100"}), 400
                    query = query.filter(SupplierTable.reliability_score >= min_rel)
                except ValueError:
                    return jsonify({"error": "Invalid reliability score"}), 400

            total_count = query.count()
            results = query.limit(limit).offset(offset).all()

            logger.info(f"Listed suppliers: name={name}, count={len(results)}")

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
        logger.error(f"Failed to list suppliers: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@supplier_bp.route("/<supplier_id>", methods=["GET"])
@APIAuth.require_auth
def get_supplier(supplier_id: str) -> tuple:
    """Get supplier by ID.
    
    Args:
        supplier_id: Supplier ID
    
    Returns:
        JSON with supplier details
    """
    try:
        session = get_rds_session()

        try:
            supplier = session.query(SupplierTable).filter(
                SupplierTable.supplier_id == supplier_id
            ).first()

            if not supplier:
                logger.warning(f"Supplier not found: {supplier_id}")
                return jsonify({"error": "Supplier not found"}), 404

            logger.info(f"Retrieved supplier: {supplier_id}")
            return jsonify(supplier.dict()), 200

        finally:
            session.close()

    except Exception as e:
        logger.error(f"Failed to get supplier: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@supplier_bp.route("", methods=["POST"])
@APIAuth.require_auth
def create_supplier() -> tuple:
    """Create a new supplier.
    
    Request Body:
        {
            "name": "Supplier Name",
            "contact_email": "contact@supplier.com",
            "contact_phone": "+1-555-0123",
            "lead_time_days": 7,
            "reliability_score": 95.0,
            "price_competitiveness": 85.0
        }
    
    Returns:
        JSON with created supplier
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        # Validate required fields
        required_fields = ["name", "contact_email", "contact_phone", "lead_time_days"]
        missing_fields = [f for f in required_fields if f not in data]

        if missing_fields:
            return jsonify({"error": f"Missing required fields: {missing_fields}"}), 400

        # Validate data
        try:
            supplier_data = {
                "supplier_id": f"SUP-{datetime.utcnow().timestamp()}",
                "name": data["name"],
                "contact_email": data["contact_email"],
                "contact_phone": data["contact_phone"],
                "lead_time_days": int(data["lead_time_days"]),
                "reliability_score": float(data.get("reliability_score", 50.0)),
                "average_delivery_days": float(data.get("average_delivery_days", data["lead_time_days"])),
                "price_competitiveness": float(data.get("price_competitiveness", 50.0)),
                "on_time_delivery_rate": float(data.get("on_time_delivery_rate", 0.5)),
                "total_orders": 0,
            }
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            return jsonify({"error": f"Validation error: {str(e)}"}), 400

        session = get_rds_session()

        try:
            supplier_obj = SupplierTable(
                supplier_id=supplier_data["supplier_id"],
                name=supplier_data["name"],
                contact_email=supplier_data["contact_email"],
                contact_phone=supplier_data["contact_phone"],
                lead_time_days=supplier_data["lead_time_days"],
                reliability_score=supplier_data["reliability_score"],
                average_delivery_days=supplier_data["average_delivery_days"],
                price_competitiveness=supplier_data["price_competitiveness"],
                on_time_delivery_rate=supplier_data["on_time_delivery_rate"],
                total_orders=supplier_data["total_orders"],
            )
            session.add(supplier_obj)
            session.commit()

            logger.info(f"Created supplier: {supplier_obj.supplier_id}")
            return jsonify(supplier_obj.dict()), 201

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to create supplier: {str(e)}")
            return jsonify({"error": "Failed to create supplier"}), 500
        finally:
            session.close()

    except Exception as e:
        logger.error(f"Failed to process supplier creation: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@supplier_bp.route("/<supplier_id>", methods=["PUT"])
@APIAuth.require_auth
def update_supplier(supplier_id: str) -> tuple:
    """Update supplier information.
    
    Args:
        supplier_id: Supplier ID
    
    Request Body:
        {
            "name": "Updated Name",
            "contact_email": "new@supplier.com",
            "reliability_score": 98.0,
            "on_time_delivery_rate": 0.95
        }
    
    Returns:
        JSON with updated supplier
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        session = get_rds_session()

        try:
            supplier = session.query(SupplierTable).filter(
                SupplierTable.supplier_id == supplier_id
            ).first()

            if not supplier:
                logger.warning(f"Supplier not found: {supplier_id}")
                return jsonify({"error": "Supplier not found"}), 404

            # Update fields if provided
            if "name" in data:
                supplier.name = data["name"]
            if "contact_email" in data:
                supplier.contact_email = data["contact_email"]
            if "contact_phone" in data:
                supplier.contact_phone = data["contact_phone"]
            if "lead_time_days" in data:
                supplier.lead_time_days = int(data["lead_time_days"])
            if "reliability_score" in data:
                supplier.reliability_score = float(data["reliability_score"])
            if "average_delivery_days" in data:
                supplier.average_delivery_days = float(data["average_delivery_days"])
            if "price_competitiveness" in data:
                supplier.price_competitiveness = float(data["price_competitiveness"])
            if "on_time_delivery_rate" in data:
                supplier.on_time_delivery_rate = float(data["on_time_delivery_rate"])

            supplier.updated_at = datetime.utcnow()
            session.commit()

            logger.info(f"Updated supplier: {supplier_id}")
            return jsonify(supplier.dict()), 200

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to update supplier: {str(e)}")
            return jsonify({"error": "Failed to update supplier"}), 500
        finally:
            session.close()

    except Exception as e:
        logger.error(f"Failed to process supplier update: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@supplier_bp.route("/<supplier_id>/performance", methods=["GET"])
@APIAuth.require_auth
def get_supplier_performance(supplier_id: str) -> tuple:
    """Get supplier performance metrics.
    
    Args:
        supplier_id: Supplier ID
    
    Returns:
        JSON with performance metrics
    """
    try:
        session = get_rds_session()

        try:
            supplier = session.query(SupplierTable).filter(
                SupplierTable.supplier_id == supplier_id
            ).first()

            if not supplier:
                logger.warning(f"Supplier not found: {supplier_id}")
                return jsonify({"error": "Supplier not found"}), 404

            performance = {
                "supplier_id": supplier.supplier_id,
                "name": supplier.name,
                "reliability_score": supplier.reliability_score,
                "on_time_delivery_rate": supplier.on_time_delivery_rate,
                "average_delivery_days": supplier.average_delivery_days,
                "price_competitiveness": supplier.price_competitiveness,
                "total_orders": supplier.total_orders,
                "last_order_date": supplier.last_order_date.isoformat() if supplier.last_order_date else None,
            }

            logger.info(f"Retrieved performance metrics for supplier: {supplier_id}")
            return jsonify(performance), 200

        finally:
            session.close()

    except Exception as e:
        logger.error(f"Failed to get supplier performance: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@supplier_bp.route("/top-performers", methods=["GET"])
@APIAuth.require_auth
def get_top_performers() -> tuple:
    """Get top performing suppliers.
    
    Query Parameters:
        - limit: Number of results (default: 10)
    
    Returns:
        JSON with top suppliers
    """
    try:
        limit = int(request.args.get("limit", 10))

        if limit < 1 or limit > 100:
            return jsonify({"error": "Limit must be between 1 and 100"}), 400

        session = get_rds_session()

        try:
            suppliers = session.query(SupplierTable).order_by(
                SupplierTable.reliability_score.desc()
            ).limit(limit).all()

            logger.info(f"Retrieved top {len(suppliers)} performing suppliers")

            return jsonify({
                "data": [s.dict() for s in suppliers],
                "count": len(suppliers),
            }), 200

        finally:
            session.close()

    except ValueError as e:
        logger.error(f"Invalid query parameters: {str(e)}")
        return jsonify({"error": "Invalid query parameters"}), 400
    except Exception as e:
        logger.error(f"Failed to get top performers: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
