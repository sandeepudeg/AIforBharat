"""Anomaly query API endpoints."""

from flask import Blueprint, request, jsonify
from datetime import datetime
from typing import Dict, Any

from src.config import logger
from src.api.auth import APIAuth
from src.database.connection import get_rds_session
from src.database.schema import AnomalyTable


anomaly_bp = Blueprint("anomaly", __name__, url_prefix="/api/anomalies")


@anomaly_bp.route("", methods=["GET"])
@APIAuth.require_auth
def list_anomalies() -> tuple:
    """List anomalies with optional filtering.
    
    Query Parameters:
        - anomaly_type: Filter by type (inventory_deviation, supplier_delay, demand_spike, inventory_shrinkage)
        - severity: Filter by severity (low, medium, high, critical)
        - status: Filter by status (open, investigating, resolved)
        - sku: Filter by product SKU
        - warehouse_id: Filter by warehouse
        - limit: Number of results (default: 100)
        - offset: Pagination offset (default: 0)
    
    Returns:
        JSON with anomaly records
    """
    try:
        anomaly_type = request.args.get("anomaly_type")
        severity = request.args.get("severity")
        status = request.args.get("status")
        sku = request.args.get("sku")
        warehouse_id = request.args.get("warehouse_id")
        limit = int(request.args.get("limit", 100))
        offset = int(request.args.get("offset", 0))

        if limit < 1 or limit > 1000:
            return jsonify({"error": "Limit must be between 1 and 1000"}), 400

        session = get_rds_session()

        try:
            query = session.query(AnomalyTable)

            if anomaly_type:
                query = query.filter(AnomalyTable.anomaly_type == anomaly_type)
            if severity:
                query = query.filter(AnomalyTable.severity == severity)
            if status:
                query = query.filter(AnomalyTable.status == status)
            if sku:
                query = query.filter(AnomalyTable.sku == sku)
            if warehouse_id:
                query = query.filter(AnomalyTable.warehouse_id == warehouse_id)

            total_count = query.count()
            results = query.order_by(AnomalyTable.created_at.desc()).limit(limit).offset(offset).all()

            logger.info(f"Listed anomalies: type={anomaly_type}, severity={severity}, count={len(results)}")

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
        logger.error(f"Failed to list anomalies: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@anomaly_bp.route("/<anomaly_id>", methods=["GET"])
@APIAuth.require_auth
def get_anomaly(anomaly_id: str) -> tuple:
    """Get anomaly by ID.
    
    Args:
        anomaly_id: Anomaly ID
    
    Returns:
        JSON with anomaly details
    """
    try:
        session = get_rds_session()

        try:
            anomaly = session.query(AnomalyTable).filter(
                AnomalyTable.anomaly_id == anomaly_id
            ).first()

            if not anomaly:
                logger.warning(f"Anomaly not found: {anomaly_id}")
                return jsonify({"error": "Anomaly not found"}), 404

            logger.info(f"Retrieved anomaly: {anomaly_id}")
            return jsonify(anomaly.dict()), 200

        finally:
            session.close()

    except Exception as e:
        logger.error(f"Failed to get anomaly: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@anomaly_bp.route("/critical", methods=["GET"])
@APIAuth.require_auth
def get_critical_anomalies() -> tuple:
    """Get all critical anomalies.
    
    Returns:
        JSON with critical anomalies
    """
    try:
        session = get_rds_session()

        try:
            anomalies = session.query(AnomalyTable).filter(
                AnomalyTable.severity == "critical"
            ).order_by(AnomalyTable.created_at.desc()).all()

            logger.info(f"Retrieved {len(anomalies)} critical anomalies")

            return jsonify({
                "data": [a.dict() for a in anomalies],
                "count": len(anomalies),
            }), 200

        finally:
            session.close()

    except Exception as e:
        logger.error(f"Failed to get critical anomalies: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@anomaly_bp.route("/open", methods=["GET"])
@APIAuth.require_auth
def get_open_anomalies() -> tuple:
    """Get all open anomalies.
    
    Returns:
        JSON with open anomalies
    """
    try:
        session = get_rds_session()

        try:
            anomalies = session.query(AnomalyTable).filter(
                AnomalyTable.status == "open"
            ).order_by(AnomalyTable.created_at.desc()).all()

            logger.info(f"Retrieved {len(anomalies)} open anomalies")

            return jsonify({
                "data": [a.dict() for a in anomalies],
                "count": len(anomalies),
            }), 200

        finally:
            session.close()

    except Exception as e:
        logger.error(f"Failed to get open anomalies: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@anomaly_bp.route("/<anomaly_id>/status", methods=["PATCH"])
@APIAuth.require_auth
def update_anomaly_status(anomaly_id: str) -> tuple:
    """Update anomaly status.
    
    Args:
        anomaly_id: Anomaly ID
    
    Request Body:
        {
            "status": "investigating" or "resolved"
        }
    
    Returns:
        JSON with updated anomaly
    """
    try:
        data = request.get_json()

        if not data or "status" not in data:
            return jsonify({"error": "Status is required"}), 400

        valid_statuses = ["open", "investigating", "resolved"]
        if data["status"] not in valid_statuses:
            return jsonify({"error": f"Invalid status. Must be one of: {valid_statuses}"}), 400

        session = get_rds_session()

        try:
            anomaly = session.query(AnomalyTable).filter(
                AnomalyTable.anomaly_id == anomaly_id
            ).first()

            if not anomaly:
                logger.warning(f"Anomaly not found: {anomaly_id}")
                return jsonify({"error": "Anomaly not found"}), 404

            anomaly.status = data["status"]

            if data["status"] == "resolved":
                anomaly.resolved_at = datetime.utcnow()

            session.commit()

            logger.info(f"Updated anomaly status: {anomaly_id} -> {data['status']}")
            return jsonify(anomaly.dict()), 200

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to update anomaly: {str(e)}")
            return jsonify({"error": "Failed to update anomaly"}), 500
        finally:
            session.close()

    except Exception as e:
        logger.error(f"Failed to process status update: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@anomaly_bp.route("/by-type/<anomaly_type>", methods=["GET"])
@APIAuth.require_auth
def get_anomalies_by_type(anomaly_type: str) -> tuple:
    """Get anomalies by type.
    
    Args:
        anomaly_type: Anomaly type
    
    Returns:
        JSON with anomalies of specified type
    """
    try:
        valid_types = ["inventory_deviation", "supplier_delay", "demand_spike", "inventory_shrinkage"]
        if anomaly_type not in valid_types:
            return jsonify({"error": f"Invalid anomaly type. Must be one of: {valid_types}"}), 400

        limit = int(request.args.get("limit", 100))
        offset = int(request.args.get("offset", 0))

        session = get_rds_session()

        try:
            query = session.query(AnomalyTable).filter(
                AnomalyTable.anomaly_type == anomaly_type
            )

            total_count = query.count()
            anomalies = query.order_by(AnomalyTable.created_at.desc()).limit(limit).offset(offset).all()

            logger.info(f"Retrieved {len(anomalies)} anomalies of type {anomaly_type}")

            return jsonify({
                "data": [a.dict() for a in anomalies],
                "total": total_count,
                "anomaly_type": anomaly_type,
            }), 200

        finally:
            session.close()

    except Exception as e:
        logger.error(f"Failed to get anomalies by type: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
