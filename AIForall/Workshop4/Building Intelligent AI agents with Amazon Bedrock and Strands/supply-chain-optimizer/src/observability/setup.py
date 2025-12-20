"""Setup and initialization for monitoring and observability."""

from typing import Dict, Any

from src.config import config, logger
from .cloudwatch import CloudWatchMetrics
from .alarms import CloudWatchAlarms
from .dashboards import CloudWatchDashboards


class MonitoringSetup:
    """Sets up monitoring and observability for Supply Chain Optimizer."""

    def __init__(self):
        """Initialize monitoring setup."""
        self.metrics = CloudWatchMetrics()
        self.alarms = CloudWatchAlarms()
        self.dashboards = CloudWatchDashboards()

    def setup_all(self) -> Dict[str, Any]:
        """Set up all monitoring and observability components.
        
        Returns:
            Dictionary with setup results
        """
        results = {
            "dashboards": self.setup_dashboards(),
            "alarms": self.setup_alarms(),
        }
        return results

    def setup_dashboards(self) -> Dict[str, bool]:
        """Set up CloudWatch dashboards.
        
        Returns:
            Dictionary with dashboard creation results
        """
        results = {}
        
        try:
            results["main_dashboard"] = self.dashboards.create_main_dashboard()
            results["agent_dashboard"] = self.dashboards.create_agent_dashboard()
            results["sla_dashboard"] = self.dashboards.create_sla_dashboard()
            
            logger.info("CloudWatch dashboards created successfully")
        except Exception as e:
            logger.error(f"Failed to create dashboards: {str(e)}")
            results["error"] = str(e)
        
        return results

    def setup_alarms(self) -> Dict[str, bool]:
        """Set up CloudWatch alarms for SLA violations.
        
        Returns:
            Dictionary with alarm creation results
        """
        results = {}
        
        try:
            # Report generation SLA alarms
            results["standard_report_sla"] = (
                self.alarms.create_report_generation_sla_alarm(
                    alarm_name="StandardReportSLAViolation",
                    threshold_seconds=300,  # 5 minutes
                    report_type="standard",
                )
            )
            
            results["comprehensive_report_sla"] = (
                self.alarms.create_report_generation_sla_alarm(
                    alarm_name="ComprehensiveReportSLAViolation",
                    threshold_seconds=900,  # 15 minutes
                    report_type="comprehensive",
                )
            )
            
            # Agent failure alarms
            agent_names = [
                "DemandForecastingAgent",
                "InventoryOptimizerAgent",
                "SupplierCoordinationAgent",
                "AnomalyDetectionAgent",
                "ReportGenerationAgent",
            ]
            
            for agent_name in agent_names:
                results[f"{agent_name}_failure"] = (
                    self.alarms.create_agent_failure_alarm(agent_name)
                )
            
            # Agent performance alarms
            for agent_name in agent_names:
                results[f"{agent_name}_performance"] = (
                    self.alarms.create_agent_performance_alarm(
                        agent_name, threshold_seconds=60
                    )
                )
            
            # Forecast accuracy alarm
            results["forecast_accuracy"] = (
                self.alarms.create_forecast_accuracy_alarm(threshold_percentage=80)
            )
            
            logger.info("CloudWatch alarms created successfully")
        except Exception as e:
            logger.error(f"Failed to create alarms: {str(e)}")
            results["error"] = str(e)
        
        return results

    def cleanup_dashboards(self) -> Dict[str, bool]:
        """Clean up CloudWatch dashboards.
        
        Returns:
            Dictionary with dashboard deletion results
        """
        results = {}
        
        try:
            dashboard_names = [
                "SupplyChainOptimizer",
                "AgentMetrics",
                "SLAMetrics",
            ]
            
            for dashboard_name in dashboard_names:
                results[dashboard_name] = self.dashboards.delete_dashboard(dashboard_name)
            
            logger.info("CloudWatch dashboards deleted successfully")
        except Exception as e:
            logger.error(f"Failed to delete dashboards: {str(e)}")
            results["error"] = str(e)
        
        return results

    def cleanup_alarms(self) -> Dict[str, bool]:
        """Clean up CloudWatch alarms.
        
        Returns:
            Dictionary with alarm deletion results
        """
        results = {}
        
        try:
            alarm_names = [
                "StandardReportSLAViolation",
                "ComprehensiveReportSLAViolation",
                "DemandForecastingAgentFailureAlarm",
                "InventoryOptimizerAgentFailureAlarm",
                "SupplierCoordinationAgentFailureAlarm",
                "AnomalyDetectionAgentFailureAlarm",
                "ReportGenerationAgentFailureAlarm",
                "DemandForecastingAgentPerformanceAlarm",
                "InventoryOptimizerAgentPerformanceAlarm",
                "SupplierCoordinationAgentPerformanceAlarm",
                "AnomalyDetectionAgentPerformanceAlarm",
                "ReportGenerationAgentPerformanceAlarm",
                "ForecastAccuracyLow",
            ]
            
            for alarm_name in alarm_names:
                results[alarm_name] = self.alarms.delete_alarm(alarm_name)
            
            logger.info("CloudWatch alarms deleted successfully")
        except Exception as e:
            logger.error(f"Failed to delete alarms: {str(e)}")
            results["error"] = str(e)
        
        return results


def setup_monitoring() -> Dict[str, Any]:
    """Set up monitoring and observability for the application.
    
    Returns:
        Dictionary with setup results
    """
    logger.info("Setting up monitoring and observability...")
    
    setup = MonitoringSetup()
    results = setup.setup_all()
    
    logger.info(f"Monitoring setup completed: {results}")
    return results
