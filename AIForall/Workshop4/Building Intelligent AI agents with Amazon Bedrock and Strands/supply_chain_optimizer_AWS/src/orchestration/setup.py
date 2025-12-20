"""Setup module for initializing EventBridge rules and Lambda targets."""

from typing import Dict, Any, Optional

from src.config import config, logger
from src.orchestration.orchestrator import Orchestrator


class EventDrivenSetup:
    """Sets up event-driven orchestration infrastructure."""

    def __init__(self):
        """Initialize the setup module."""
        self.orchestrator = Orchestrator()
        self.logger = logger

    def setup_all_rules(
        self,
        lambda_arns: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Set up all EventBridge rules and Lambda targets.

        Args:
            lambda_arns: Dictionary mapping rule names to Lambda function ARNs

        Returns:
            Dictionary with setup results
        """
        results = {
            "inventory_update_rule": None,
            "forecasting_rule": None,
            "optimization_rule": None,
            "anomaly_detection_rule": None,
            "report_generation_rule": None,
            "errors": []
        }

        try:
            # Set up inventory update rule
            try:
                rule_arn = self.orchestrator.setup_inventory_update_rule()
                results["inventory_update_rule"] = {
                    "status": "success",
                    "arn": rule_arn
                }
                
                # Add Lambda target if provided
                if lambda_arns and "inventory_update" in lambda_arns:
                    self.orchestrator.add_lambda_target(
                        "inventory-update-rule",
                        lambda_arns["inventory_update"]
                    )
            except Exception as e:
                self.logger.error(f"Failed to setup inventory update rule: {str(e)}")
                results["errors"].append(f"Inventory update rule: {str(e)}")

            # Set up forecasting rule
            try:
                rule_arn = self.orchestrator.setup_scheduled_forecasting_job()
                results["forecasting_rule"] = {
                    "status": "success",
                    "arn": rule_arn
                }
                
                # Add Lambda target if provided
                if lambda_arns and "forecasting" in lambda_arns:
                    self.orchestrator.add_lambda_target(
                        "daily-forecasting-job",
                        lambda_arns["forecasting"]
                    )
            except Exception as e:
                self.logger.error(f"Failed to setup forecasting rule: {str(e)}")
                results["errors"].append(f"Forecasting rule: {str(e)}")

            # Set up optimization rule
            try:
                rule_arn = self.orchestrator.setup_scheduled_optimization_job()
                results["optimization_rule"] = {
                    "status": "success",
                    "arn": rule_arn
                }
                
                # Add Lambda target if provided
                if lambda_arns and "optimization" in lambda_arns:
                    self.orchestrator.add_lambda_target(
                        "daily-optimization-job",
                        lambda_arns["optimization"]
                    )
            except Exception as e:
                self.logger.error(f"Failed to setup optimization rule: {str(e)}")
                results["errors"].append(f"Optimization rule: {str(e)}")

            # Set up anomaly detection rule
            try:
                rule_arn = self.orchestrator.setup_scheduled_anomaly_detection_job()
                results["anomaly_detection_rule"] = {
                    "status": "success",
                    "arn": rule_arn
                }
                
                # Add Lambda target if provided
                if lambda_arns and "anomaly_detection" in lambda_arns:
                    self.orchestrator.add_lambda_target(
                        "hourly-anomaly-detection-job",
                        lambda_arns["anomaly_detection"]
                    )
            except Exception as e:
                self.logger.error(f"Failed to setup anomaly detection rule: {str(e)}")
                results["errors"].append(f"Anomaly detection rule: {str(e)}")

            # Set up report generation rule
            try:
                rule_arn = self.orchestrator.setup_scheduled_report_generation_job()
                results["report_generation_rule"] = {
                    "status": "success",
                    "arn": rule_arn
                }
                
                # Add Lambda target if provided
                if lambda_arns and "report_generation" in lambda_arns:
                    self.orchestrator.add_lambda_target(
                        "weekly-report-generation-job",
                        lambda_arns["report_generation"]
                    )
            except Exception as e:
                self.logger.error(f"Failed to setup report generation rule: {str(e)}")
                results["errors"].append(f"Report generation rule: {str(e)}")

            results["status"] = "success" if not results["errors"] else "partial"
            return results

        except Exception as e:
            self.logger.error(f"Failed to setup event-driven infrastructure: {str(e)}")
            results["status"] = "error"
            results["errors"].append(str(e))
            return results

    def cleanup_all_rules(self) -> Dict[str, Any]:
        """Clean up all EventBridge rules.

        Returns:
            Dictionary with cleanup results
        """
        results = {
            "deleted_rules": [],
            "errors": []
        }

        rule_names = [
            "inventory-update-rule",
            "daily-forecasting-job",
            "daily-optimization-job",
            "hourly-anomaly-detection-job",
            "weekly-report-generation-job"
        ]

        for rule_name in rule_names:
            try:
                self.orchestrator.delete_rule(rule_name)
                results["deleted_rules"].append(rule_name)
            except Exception as e:
                self.logger.error(f"Failed to delete rule {rule_name}: {str(e)}")
                results["errors"].append(f"{rule_name}: {str(e)}")

        results["status"] = "success" if not results["errors"] else "partial"
        return results
