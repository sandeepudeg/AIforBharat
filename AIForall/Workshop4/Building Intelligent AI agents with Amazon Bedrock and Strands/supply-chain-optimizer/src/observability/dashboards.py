"""CloudWatch dashboards for Supply Chain Optimizer."""

import json
from typing import Dict, Any

import boto3
from botocore.exceptions import ClientError

from src.config import config, logger


class CloudWatchDashboards:
    """Manages CloudWatch dashboards for Supply Chain Optimizer."""

    def __init__(self):
        """Initialize CloudWatch client."""
        self.client = boto3.client("cloudwatch", region_name=config.aws.region)
        self.namespace = "SupplyChainOptimizer"

    def create_main_dashboard(self, dashboard_name: str = "SupplyChainOptimizer") -> bool:
        """Create main dashboard with key metrics.
        
        Args:
            dashboard_name: Name of the dashboard
        
        Returns:
            True if dashboard created successfully, False otherwise
        """
        dashboard_body = {
            "widgets": [
                {
                    "type": "metric",
                    "properties": {
                        "metrics": [
                            [self.namespace, "AgentExecutionTime", {"stat": "Average"}],
                            [".", "AgentSuccess", {"stat": "Sum"}],
                            [".", "AgentFailure", {"stat": "Sum"}],
                        ],
                        "period": 300,
                        "stat": "Average",
                        "region": config.aws.region,
                        "title": "Agent Performance",
                    },
                },
                {
                    "type": "metric",
                    "properties": {
                        "metrics": [
                            [self.namespace, "ReportGenerationTime", {"stat": "Maximum"}],
                            [".", "ForecastAccuracy", {"stat": "Average"}],
                        ],
                        "period": 300,
                        "stat": "Average",
                        "region": config.aws.region,
                        "title": "Report Generation & Forecast Accuracy",
                    },
                },
                {
                    "type": "metric",
                    "properties": {
                        "metrics": [
                            [self.namespace, "InventoryUpdatesCount", {"stat": "Sum"}],
                            [".", "AnomaliesDetected", {"stat": "Sum"}],
                            [".", "PurchaseOrderCount", {"stat": "Sum"}],
                        ],
                        "period": 300,
                        "stat": "Sum",
                        "region": config.aws.region,
                        "title": "Supply Chain Activity",
                    },
                },
                {
                    "type": "metric",
                    "properties": {
                        "metrics": [
                            [self.namespace, "SupplierPerformanceScore", {"stat": "Average"}],
                        ],
                        "period": 3600,
                        "stat": "Average",
                        "region": config.aws.region,
                        "title": "Supplier Performance",
                    },
                },
            ]
        }

        try:
            self.client.put_dashboard(
                DashboardName=dashboard_name,
                DashboardBody=json.dumps(dashboard_body),
            )
            logger.info(f"Created dashboard: {dashboard_name}")
            return True
        except ClientError as e:
            logger.error(f"Failed to create dashboard {dashboard_name}: {str(e)}")
            return False

    def create_agent_dashboard(self, dashboard_name: str = "AgentMetrics") -> bool:
        """Create dashboard for agent-specific metrics.
        
        Args:
            dashboard_name: Name of the dashboard
        
        Returns:
            True if dashboard created successfully, False otherwise
        """
        dashboard_body = {
            "widgets": [
                {
                    "type": "metric",
                    "properties": {
                        "metrics": [
                            [
                                self.namespace,
                                "AgentExecutionTime",
                                {"dimensions": {"AgentName": "DemandForecastingAgent"}},
                            ],
                            [
                                ".",
                                ".",
                                {"dimensions": {"AgentName": "InventoryOptimizerAgent"}},
                            ],
                            [
                                ".",
                                ".",
                                {"dimensions": {"AgentName": "SupplierCoordinationAgent"}},
                            ],
                            [
                                ".",
                                ".",
                                {"dimensions": {"AgentName": "AnomalyDetectionAgent"}},
                            ],
                            [
                                ".",
                                ".",
                                {"dimensions": {"AgentName": "ReportGenerationAgent"}},
                            ],
                        ],
                        "period": 300,
                        "stat": "Average",
                        "region": config.aws.region,
                        "title": "Agent Execution Times",
                    },
                },
                {
                    "type": "metric",
                    "properties": {
                        "metrics": [
                            [
                                self.namespace,
                                "AgentSuccess",
                                {"dimensions": {"AgentName": "DemandForecastingAgent"}},
                            ],
                            [
                                ".",
                                ".",
                                {"dimensions": {"AgentName": "InventoryOptimizerAgent"}},
                            ],
                            [
                                ".",
                                ".",
                                {"dimensions": {"AgentName": "SupplierCoordinationAgent"}},
                            ],
                            [
                                ".",
                                ".",
                                {"dimensions": {"AgentName": "AnomalyDetectionAgent"}},
                            ],
                            [
                                ".",
                                ".",
                                {"dimensions": {"AgentName": "ReportGenerationAgent"}},
                            ],
                        ],
                        "period": 300,
                        "stat": "Sum",
                        "region": config.aws.region,
                        "title": "Agent Success Count",
                    },
                },
                {
                    "type": "metric",
                    "properties": {
                        "metrics": [
                            [
                                self.namespace,
                                "AgentFailure",
                                {"dimensions": {"AgentName": "DemandForecastingAgent"}},
                            ],
                            [
                                ".",
                                ".",
                                {"dimensions": {"AgentName": "InventoryOptimizerAgent"}},
                            ],
                            [
                                ".",
                                ".",
                                {"dimensions": {"AgentName": "SupplierCoordinationAgent"}},
                            ],
                            [
                                ".",
                                ".",
                                {"dimensions": {"AgentName": "AnomalyDetectionAgent"}},
                            ],
                            [
                                ".",
                                ".",
                                {"dimensions": {"AgentName": "ReportGenerationAgent"}},
                            ],
                        ],
                        "period": 300,
                        "stat": "Sum",
                        "region": config.aws.region,
                        "title": "Agent Failure Count",
                    },
                },
            ]
        }

        try:
            self.client.put_dashboard(
                DashboardName=dashboard_name,
                DashboardBody=json.dumps(dashboard_body),
            )
            logger.info(f"Created dashboard: {dashboard_name}")
            return True
        except ClientError as e:
            logger.error(f"Failed to create dashboard {dashboard_name}: {str(e)}")
            return False

    def create_sla_dashboard(self, dashboard_name: str = "SLAMetrics") -> bool:
        """Create dashboard for SLA metrics.
        
        Args:
            dashboard_name: Name of the dashboard
        
        Returns:
            True if dashboard created successfully, False otherwise
        """
        dashboard_body = {
            "widgets": [
                {
                    "type": "metric",
                    "properties": {
                        "metrics": [
                            [
                                self.namespace,
                                "ReportGenerationTime",
                                {"dimensions": {"ReportType": "standard"}},
                            ],
                            [
                                ".",
                                ".",
                                {"dimensions": {"ReportType": "comprehensive"}},
                            ],
                        ],
                        "period": 300,
                        "stat": "Maximum",
                        "region": config.aws.region,
                        "title": "Report Generation Time (SLA: 5min standard, 15min comprehensive)",
                        "yAxis": {"left": {"min": 0, "max": 900}},
                    },
                },
                {
                    "type": "metric",
                    "properties": {
                        "metrics": [
                            [self.namespace, "ForecastAccuracy", {"stat": "Average"}],
                        ],
                        "period": 3600,
                        "stat": "Average",
                        "region": config.aws.region,
                        "title": "Forecast Accuracy",
                        "yAxis": {"left": {"min": 0, "max": 100}},
                    },
                },
                {
                    "type": "metric",
                    "properties": {
                        "metrics": [
                            [self.namespace, "SupplierPerformanceScore", {"stat": "Average"}],
                        ],
                        "period": 3600,
                        "stat": "Average",
                        "region": config.aws.region,
                        "title": "Supplier Performance Score",
                        "yAxis": {"left": {"min": 0, "max": 100}},
                    },
                },
            ]
        }

        try:
            self.client.put_dashboard(
                DashboardName=dashboard_name,
                DashboardBody=json.dumps(dashboard_body),
            )
            logger.info(f"Created dashboard: {dashboard_name}")
            return True
        except ClientError as e:
            logger.error(f"Failed to create dashboard {dashboard_name}: {str(e)}")
            return False

    def delete_dashboard(self, dashboard_name: str) -> bool:
        """Delete a CloudWatch dashboard.
        
        Args:
            dashboard_name: Name of the dashboard to delete
        
        Returns:
            True if dashboard deleted successfully, False otherwise
        """
        try:
            self.client.delete_dashboards(DashboardNames=[dashboard_name])
            logger.info(f"Deleted dashboard: {dashboard_name}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete dashboard {dashboard_name}: {str(e)}")
            return False

    def list_dashboards(self) -> list:
        """List all CloudWatch dashboards.
        
        Returns:
            List of dashboard names
        """
        try:
            response = self.client.list_dashboards()
            dashboards = [d["DashboardName"] for d in response.get("DashboardEntries", [])]
            return dashboards
        except ClientError as e:
            logger.error(f"Failed to list dashboards: {str(e)}")
            return []
