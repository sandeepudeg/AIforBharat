"""CloudWatch metrics and dashboards for Supply Chain Optimizer."""

import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from functools import wraps

import boto3
from botocore.exceptions import ClientError

from src.config import config, logger


class CloudWatchMetrics:
    """Manages CloudWatch metrics for Supply Chain Optimizer."""

    def __init__(self):
        """Initialize CloudWatch client."""
        self.client = boto3.client("cloudwatch", region_name=config.aws.region)
        self.namespace = "SupplyChainOptimizer"

    def put_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "None",
        dimensions: Optional[Dict[str, str]] = None,
    ) -> None:
        """Put a metric to CloudWatch.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            unit: Unit of measurement (Count, Seconds, Bytes, etc.)
            dimensions: Dictionary of dimension names and values
        """
        try:
            metric_data = {
                "MetricName": metric_name,
                "Value": value,
                "Unit": unit,
                "Timestamp": datetime.now(timezone.utc),
            }

            if dimensions:
                metric_data["Dimensions"] = [
                    {"Name": k, "Value": v} for k, v in dimensions.items()
                ]

            self.client.put_metric_data(
                Namespace=self.namespace,
                MetricData=[metric_data],
            )
            logger.debug(f"Metric {metric_name} recorded: {value} {unit}")
        except ClientError as e:
            logger.error(f"Failed to put metric {metric_name}: {str(e)}")

    def record_agent_execution_time(
        self, agent_name: str, execution_time_seconds: float
    ) -> None:
        """Record agent execution time.
        
        Args:
            agent_name: Name of the agent
            execution_time_seconds: Execution time in seconds
        """
        self.put_metric(
            "AgentExecutionTime",
            execution_time_seconds,
            unit="Seconds",
            dimensions={"AgentName": agent_name},
        )

    def record_agent_success(self, agent_name: str) -> None:
        """Record successful agent execution.
        
        Args:
            agent_name: Name of the agent
        """
        self.put_metric(
            "AgentSuccess",
            1,
            unit="Count",
            dimensions={"AgentName": agent_name},
        )

    def record_agent_failure(self, agent_name: str) -> None:
        """Record failed agent execution.
        
        Args:
            agent_name: Name of the agent
        """
        self.put_metric(
            "AgentFailure",
            1,
            unit="Count",
            dimensions={"AgentName": agent_name},
        )

    def record_report_generation_time(self, report_type: str, time_seconds: float) -> None:
        """Record report generation time.
        
        Args:
            report_type: Type of report (daily, weekly, monthly, custom)
            time_seconds: Time taken to generate report in seconds
        """
        self.put_metric(
            "ReportGenerationTime",
            time_seconds,
            unit="Seconds",
            dimensions={"ReportType": report_type},
        )

    def record_inventory_update_count(self, count: int) -> None:
        """Record number of inventory items updated.
        
        Args:
            count: Number of items updated
        """
        self.put_metric(
            "InventoryUpdatesCount",
            count,
            unit="Count",
        )

    def record_anomaly_detection_count(self, anomaly_type: str, count: int) -> None:
        """Record number of anomalies detected.
        
        Args:
            anomaly_type: Type of anomaly
            count: Number of anomalies detected
        """
        self.put_metric(
            "AnomaliesDetected",
            count,
            unit="Count",
            dimensions={"AnomalyType": anomaly_type},
        )

    def record_purchase_order_count(self, status: str, count: int) -> None:
        """Record number of purchase orders.
        
        Args:
            status: Status of purchase orders (pending, confirmed, shipped, delivered)
            count: Number of purchase orders
        """
        self.put_metric(
            "PurchaseOrderCount",
            count,
            unit="Count",
            dimensions={"Status": status},
        )

    def record_forecast_accuracy(self, accuracy_percentage: float) -> None:
        """Record forecast accuracy.
        
        Args:
            accuracy_percentage: Forecast accuracy as percentage (0-100)
        """
        self.put_metric(
            "ForecastAccuracy",
            accuracy_percentage,
            unit="Percent",
        )

    def record_supplier_performance(self, supplier_id: str, score: float) -> None:
        """Record supplier performance score.
        
        Args:
            supplier_id: ID of the supplier
            score: Performance score (0-100)
        """
        self.put_metric(
            "SupplierPerformanceScore",
            score,
            unit="None",
            dimensions={"SupplierId": supplier_id},
        )


def track_agent_performance(agent_name: str):
    """Decorator to track agent performance metrics.
    
    Args:
        agent_name: Name of the agent being tracked
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            metrics = CloudWatchMetrics()
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                metrics.record_agent_execution_time(agent_name, execution_time)
                metrics.record_agent_success(agent_name)
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                metrics.record_agent_execution_time(agent_name, execution_time)
                metrics.record_agent_failure(agent_name)
                logger.error(f"Agent {agent_name} failed: {str(e)}")
                raise
        return wrapper
    return decorator


def track_report_generation(report_type: str):
    """Decorator to track report generation performance.
    
    Args:
        report_type: Type of report being generated
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            metrics = CloudWatchMetrics()
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                metrics.record_report_generation_time(report_type, execution_time)
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                metrics.record_report_generation_time(report_type, execution_time)
                logger.error(f"Report generation for {report_type} failed: {str(e)}")
                raise
        return wrapper
    return decorator
