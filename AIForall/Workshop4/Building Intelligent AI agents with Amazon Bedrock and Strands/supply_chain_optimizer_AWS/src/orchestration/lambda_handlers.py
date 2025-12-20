"""Lambda handler functions for EventBridge-triggered workflows."""

import json
from typing import Any, Dict

from src.config import logger
from src.orchestration.event_handler import EventHandler


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Main Lambda handler for EventBridge events.

    Args:
        event: EventBridge event
        context: Lambda context

    Returns:
        Response with status and results
    """
    try:
        logger.info(f"Lambda handler invoked with event: {json.dumps(event)}")
        
        handler = EventHandler()
        result = handler.handle_event(event)
        
        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }
    except Exception as e:
        logger.error(f"Lambda handler error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "status": "error",
                "error": str(e)
            })
        }


def forecasting_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for forecasting jobs.

    Args:
        event: EventBridge scheduled event
        context: Lambda context

    Returns:
        Response with forecasting results
    """
    try:
        logger.info("Forecasting Lambda handler invoked")
        
        handler = EventHandler()
        result = handler.handle_forecasting_job_event(event)
        
        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }
    except Exception as e:
        logger.error(f"Forecasting handler error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "status": "error",
                "error": str(e)
            })
        }


def optimization_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for optimization jobs.

    Args:
        event: EventBridge scheduled event
        context: Lambda context

    Returns:
        Response with optimization results
    """
    try:
        logger.info("Optimization Lambda handler invoked")
        
        handler = EventHandler()
        result = handler.handle_optimization_job_event(event)
        
        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }
    except Exception as e:
        logger.error(f"Optimization handler error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "status": "error",
                "error": str(e)
            })
        }


def anomaly_detection_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for anomaly detection jobs.

    Args:
        event: EventBridge scheduled event
        context: Lambda context

    Returns:
        Response with anomaly detection results
    """
    try:
        logger.info("Anomaly detection Lambda handler invoked")
        
        handler = EventHandler()
        result = handler.handle_anomaly_detection_job_event(event)
        
        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }
    except Exception as e:
        logger.error(f"Anomaly detection handler error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "status": "error",
                "error": str(e)
            })
        }


def report_generation_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for report generation jobs.

    Args:
        event: EventBridge scheduled event
        context: Lambda context

    Returns:
        Response with report generation results
    """
    try:
        logger.info("Report generation Lambda handler invoked")
        
        handler = EventHandler()
        result = handler.handle_report_generation_job_event(event)
        
        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }
    except Exception as e:
        logger.error(f"Report generation handler error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "status": "error",
                "error": str(e)
            })
        }


def inventory_update_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for inventory update events.

    Args:
        event: EventBridge event
        context: Lambda context

    Returns:
        Response with inventory update workflow results
    """
    try:
        logger.info("Inventory update Lambda handler invoked")
        
        handler = EventHandler()
        result = handler.handle_inventory_update_event(event)
        
        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }
    except Exception as e:
        logger.error(f"Inventory update handler error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "status": "error",
                "error": str(e)
            })
        }
