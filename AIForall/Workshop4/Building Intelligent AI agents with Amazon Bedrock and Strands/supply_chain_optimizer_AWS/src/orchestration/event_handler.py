"""Event handler for processing EventBridge events and triggering agent workflows."""

import json
from typing import Any, Dict, Optional
from datetime import datetime

from src.config import logger
from src.agents.demand_forecasting_agent import DemandForecastingAgent
from src.agents.inventory_optimizer_agent import InventoryOptimizerAgent
from src.agents.anomaly_detection_agent import AnomalyDetectionAgent
from src.agents.report_generation_agent import ReportGenerationAgent
from src.agents.supplier_coordination_agent import SupplierCoordinationAgent


class EventHandler:
    """Handles EventBridge events and orchestrates agent execution."""

    def __init__(self):
        """Initialize the Event Handler."""
        self.logger = logger
        self.demand_forecasting_agent = DemandForecastingAgent()
        self.inventory_optimizer_agent = InventoryOptimizerAgent()
        self.anomaly_detection_agent = AnomalyDetectionAgent()
        self.report_generation_agent = ReportGenerationAgent()
        self.supplier_coordination_agent = SupplierCoordinationAgent()

    def handle_inventory_update_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle inventory update events.

        Args:
            event: EventBridge event containing inventory update details

        Returns:
            Result of the workflow execution
        """
        try:
            detail = event.get("detail", {})
            sku = detail.get("sku")
            warehouse_id = detail.get("warehouse_id")
            
            self.logger.info(f"Processing inventory update for SKU: {sku}, Warehouse: {warehouse_id}")
            
            # Trigger demand forecasting
            forecast_result = self.demand_forecasting_agent.generate_forecast(sku)
            
            # Trigger inventory optimization
            optimization_result = self.inventory_optimizer_agent.optimize_inventory(sku)
            
            # Trigger anomaly detection
            anomaly_result = self.anomaly_detection_agent.detect_anomalies(sku)
            
            return {
                "status": "success",
                "event_type": "inventory_update",
                "sku": sku,
                "warehouse_id": warehouse_id,
                "forecast": forecast_result,
                "optimization": optimization_result,
                "anomalies": anomaly_result,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Failed to handle inventory update event: {str(e)}")
            return {
                "status": "error",
                "event_type": "inventory_update",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def handle_forecasting_job_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle scheduled forecasting job events.

        Args:
            event: EventBridge scheduled event

        Returns:
            Result of the forecasting job
        """
        try:
            self.logger.info("Processing scheduled forecasting job")
            
            # Get all SKUs and generate forecasts
            all_skus = self._get_all_skus()
            forecast_results = []
            
            for sku in all_skus:
                try:
                    result = self.demand_forecasting_agent.generate_forecast(sku)
                    forecast_results.append({
                        "sku": sku,
                        "status": "success",
                        "forecast": result
                    })
                except Exception as e:
                    self.logger.error(f"Failed to forecast SKU {sku}: {str(e)}")
                    forecast_results.append({
                        "sku": sku,
                        "status": "error",
                        "error": str(e)
                    })
            
            return {
                "status": "success",
                "job_type": "forecasting",
                "skus_processed": len(all_skus),
                "results": forecast_results,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Failed to handle forecasting job event: {str(e)}")
            return {
                "status": "error",
                "job_type": "forecasting",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def handle_optimization_job_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle scheduled optimization job events.

        Args:
            event: EventBridge scheduled event

        Returns:
            Result of the optimization job
        """
        try:
            self.logger.info("Processing scheduled optimization job")
            
            # Get all SKUs and optimize inventory
            all_skus = self._get_all_skus()
            optimization_results = []
            
            for sku in all_skus:
                try:
                    result = self.inventory_optimizer_agent.optimize_inventory(sku)
                    optimization_results.append({
                        "sku": sku,
                        "status": "success",
                        "optimization": result
                    })
                except Exception as e:
                    self.logger.error(f"Failed to optimize SKU {sku}: {str(e)}")
                    optimization_results.append({
                        "sku": sku,
                        "status": "error",
                        "error": str(e)
                    })
            
            return {
                "status": "success",
                "job_type": "optimization",
                "skus_processed": len(all_skus),
                "results": optimization_results,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Failed to handle optimization job event: {str(e)}")
            return {
                "status": "error",
                "job_type": "optimization",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def handle_anomaly_detection_job_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle scheduled anomaly detection job events.

        Args:
            event: EventBridge scheduled event

        Returns:
            Result of the anomaly detection job
        """
        try:
            self.logger.info("Processing scheduled anomaly detection job")
            
            # Get all SKUs and detect anomalies
            all_skus = self._get_all_skus()
            anomaly_results = []
            
            for sku in all_skus:
                try:
                    result = self.anomaly_detection_agent.detect_anomalies(sku)
                    anomaly_results.append({
                        "sku": sku,
                        "status": "success",
                        "anomalies": result
                    })
                except Exception as e:
                    self.logger.error(f"Failed to detect anomalies for SKU {sku}: {str(e)}")
                    anomaly_results.append({
                        "sku": sku,
                        "status": "error",
                        "error": str(e)
                    })
            
            return {
                "status": "success",
                "job_type": "anomaly_detection",
                "skus_processed": len(all_skus),
                "results": anomaly_results,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Failed to handle anomaly detection job event: {str(e)}")
            return {
                "status": "error",
                "job_type": "anomaly_detection",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def handle_report_generation_job_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle scheduled report generation job events.

        Args:
            event: EventBridge scheduled event

        Returns:
            Result of the report generation job
        """
        try:
            self.logger.info("Processing scheduled report generation job")
            
            # Generate comprehensive report
            report_result = self.report_generation_agent.generate_report()
            
            return {
                "status": "success",
                "job_type": "report_generation",
                "report": report_result,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Failed to handle report generation job event: {str(e)}")
            return {
                "status": "error",
                "job_type": "report_generation",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def handle_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Route events to appropriate handlers.

        Args:
            event: EventBridge event

        Returns:
            Result of the event handling
        """
        try:
            detail_type = event.get("detail-type", "")
            source = event.get("source", "")
            
            self.logger.info(f"Handling event: {detail_type} from {source}")
            
            if "Inventory Update" in detail_type:
                return self.handle_inventory_update_event(event)
            elif "Forecasting" in detail_type:
                return self.handle_forecasting_job_event(event)
            elif "Optimization" in detail_type:
                return self.handle_optimization_job_event(event)
            elif "Anomaly Detection" in detail_type:
                return self.handle_anomaly_detection_job_event(event)
            elif "Report Generation" in detail_type:
                return self.handle_report_generation_job_event(event)
            else:
                self.logger.warning(f"Unknown event type: {detail_type}")
                return {
                    "status": "unknown",
                    "detail_type": detail_type,
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            self.logger.error(f"Failed to handle event: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def _get_all_skus(self) -> list:
        """Get all SKUs from the system.

        Returns:
            List of all SKUs
        """
        # This would typically query the database for all SKUs
        # For now, return empty list as placeholder
        return []
