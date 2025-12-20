"""Inventory query API endpoints."""

from flask import Blueprint, request, jsonify
from typing import Dict, Any

from src.config import logger
from src.api.auth import APIAuth
from src.database.connection import get_dynamodb_connection
from src.models.inventory import Inventory


inventory_bp = Blueprint("inventory", __name__, url_prefix="/api/inventory")


@inventory_bp.route("/query", methods=["GET"])
@APIAuth.require_auth
def query_inventory() -> tuple:
    """Query inventory by SKU and warehouse.
    
    Query Parameters:
        - sku: Product SKU (optional)
        - warehouse_id: Warehouse ID (optional)
        - limit: Number of results (default: 100)
        - offset: Pagination offset (default: 0)
    
    Returns:
        JSON with inventory records
    """
    try:
        sku = request.args.get("sku")
        warehouse_id = request.args.get("warehouse_id")
        limit = int(request.args.get("limit", 100))
        offset = int(request.args.get("offset", 0))

        # Validate pagination parameters
        if limit < 1 or limit > 1000:
            return jsonify({"error": "Limit must be between 1 and 1000"}), 400
        if offset < 0:
            return jsonify({"error": "Offset must be non-negative"}), 400

        dynamodb = get_dynamodb_connection()
        table = dynamodb.Table("inventory")

        try:
            # Build query
            if sku and warehouse_id:
                response = table.query(
                    KeyConditionExpression="sku = :sku AND warehouse_id = :warehouse_id",
                    ExpressionAttributeValues={
                        ":sku": sku,
                        ":warehouse_id": warehouse_id,
                    }
                )
            elif sku:
                response = table.query(
                    IndexName="sku-warehouse-index",
                    KeyConditionExpression="sku = :sku",
                    ExpressionAttributeValues={":sku": sku}
                )
            elif warehouse_id:
                response = table.scan(
                    FilterExpression="warehouse_id = :warehouse_id",
                    ExpressionAttributeValues={":warehouse_id": warehouse_id}
                )
            else:
                response = table.scan()

            items = response.get("Items", [])
            total_count = response.get("Count", 0)

            # Apply pagination
            paginated_items = items[offset:offset + limit]

            logger.info(f"Queried inventory: sku={sku}, warehouse={warehouse_id}, count={len(paginated_items)}")

            return jsonify({
                "data": paginated_items,
                "total": total_count,
                "limit": limit,
                "offset": offset,
            }), 200

        except Exception as e:
            logger.error(f"Failed to query inventory: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500

    except ValueError as e:
        logger.error(f"Invalid query parameters: {str(e)}")
        return jsonify({"error": "Invalid query parameters"}), 400
    except Exception as e:
        logger.error(f"Failed to query inventory: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@inventory_bp.route("/<inventory_id>", methods=["GET"])
@APIAuth.require_auth
def get_inventory(inventory_id: str) -> tuple:
    """Get inventory by ID.
    
    Args:
        inventory_id: Inventory record ID
    
    Returns:
        JSON with inventory record
    """
    try:
        dynamodb = get_dynamodb_connection()
        table = dynamodb.Table("inventory")

        try:
            response = table.get_item(Key={"inventory_id": inventory_id})

            if "Item" not in response:
                logger.warning(f"Inventory not found: {inventory_id}")
                return jsonify({"error": "Inventory not found"}), 404

            logger.info(f"Retrieved inventory: {inventory_id}")
            return jsonify(response["Item"]), 200

        except Exception as e:
            logger.error(f"Failed to get inventory: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500

    except Exception as e:
        logger.error(f"Failed to get inventory: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@inventory_bp.route("/warehouse/<warehouse_id>", methods=["GET"])
@APIAuth.require_auth
def get_warehouse_inventory(warehouse_id: str) -> tuple:
    """Get all inventory for a warehouse.
    
    Args:
        warehouse_id: Warehouse ID
    
    Returns:
        JSON with inventory records for warehouse
    """
    try:
        limit = int(request.args.get("limit", 100))
        offset = int(request.args.get("offset", 0))

        if limit < 1 or limit > 1000:
            return jsonify({"error": "Limit must be between 1 and 1000"}), 400

        dynamodb = get_dynamodb_connection()
        table = dynamodb.Table("inventory")

        try:
            response = table.scan(
                FilterExpression="warehouse_id = :warehouse_id",
                ExpressionAttributeValues={":warehouse_id": warehouse_id}
            )

            items = response.get("Items", [])
            total_count = response.get("Count", 0)

            # Apply pagination
            paginated_items = items[offset:offset + limit]

            logger.info(f"Retrieved inventory for warehouse {warehouse_id}: {len(paginated_items)} items")

            return jsonify({
                "data": paginated_items,
                "total": total_count,
                "warehouse_id": warehouse_id,
            }), 200

        except Exception as e:
            logger.error(f"Failed to get warehouse inventory: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500

    except ValueError as e:
        logger.error(f"Invalid query parameters: {str(e)}")
        return jsonify({"error": "Invalid query parameters"}), 400
    except Exception as e:
        logger.error(f"Failed to get warehouse inventory: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@inventory_bp.route("/low-stock", methods=["GET"])
@APIAuth.require_auth
def get_low_stock_items() -> tuple:
    """Get inventory items below reorder point.
    
    Returns:
        JSON with low stock items
    """
    try:
        dynamodb = get_dynamodb_connection()
        table = dynamodb.Table("inventory")

        try:
            response = table.scan(
                FilterExpression="quantity_on_hand <= reorder_point"
            )

            items = response.get("Items", [])

            logger.info(f"Retrieved {len(items)} low stock items")

            return jsonify({
                "data": items,
                "count": len(items),
            }), 200

        except Exception as e:
            logger.error(f"Failed to get low stock items: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500

    except Exception as e:
        logger.error(f"Failed to get low stock items: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
