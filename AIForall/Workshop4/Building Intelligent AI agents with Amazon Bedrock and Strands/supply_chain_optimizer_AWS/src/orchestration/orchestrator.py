"""Orchestrator for coordinating agent execution and workflows."""

import json
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from src.config import config, logger
from src.aws.clients import (
    get_eventbridge_client,
    get_lambda_client,
)


class Orchestrator:
    """Orchestrates agent execution and event-driven workflows."""

    def __init__(self):
        """Initialize the Orchestrator."""
        self.eventbridge_client = get_eventbridge_client()
        self.lambda_client = get_lambda_client()
        self.logger = logger

    def setup_inventory_update_rule(self, rule_name: str = "inventory-update-rule") -> str:
        """Set up EventBridge rule for inventory updates.

        Args:
            rule_name: Name of the EventBridge rule

        Returns:
            ARN of the created rule
        """
        try:
            # Create or update the rule
            response = self.eventbridge_client.put_rule(
                Name=rule_name,
                EventPattern=json.dumps({
                    "source": ["supply-chain.inventory"],
                    "detail-type": ["Inventory Update"],
                    "detail": {
                        "event_type": ["inventory_changed"]
                    }
                }),
                State="ENABLED",
                Description="Triggers agent workflows on inventory updates"
            )
            self.logger.info(f"Created EventBridge rule: {rule_name}")
            return response["RuleArn"]
        except Exception as e:
            self.logger.error(f"Failed to create inventory update rule: {str(e)}")
            raise

    def setup_scheduled_forecasting_job(
        self,
        rule_name: str = "daily-forecasting-job",
        schedule_expression: str = "cron(0 2 * * ? *)"
    ) -> str:
        """Set up scheduled daily forecasting job.

        Args:
            rule_name: Name of the EventBridge rule
            schedule_expression: Cron expression for scheduling (default: 2 AM UTC daily)

        Returns:
            ARN of the created rule
        """
        try:
            response = self.eventbridge_client.put_rule(
                Name=rule_name,
                ScheduleExpression=schedule_expression,
                State="ENABLED",
                Description="Triggers daily demand forecasting for all products"
            )
            self.logger.info(f"Created scheduled forecasting rule: {rule_name}")
            return response["RuleArn"]
        except Exception as e:
            self.logger.error(f"Failed to create forecasting job rule: {str(e)}")
            raise

    def setup_scheduled_optimization_job(
        self,
        rule_name: str = "daily-optimization-job",
        schedule_expression: str = "cron(0 3 * * ? *)"
    ) -> str:
        """Set up scheduled daily inventory optimization job.

        Args:
            rule_name: Name of the EventBridge rule
            schedule_expression: Cron expression for scheduling (default: 3 AM UTC daily)

        Returns:
            ARN of the created rule
        """
        try:
            response = self.eventbridge_client.put_rule(
                Name=rule_name,
                ScheduleExpression=schedule_expression,
                State="ENABLED",
                Description="Triggers daily inventory optimization for all products"
            )
            self.logger.info(f"Created scheduled optimization rule: {rule_name}")
            return response["RuleArn"]
        except Exception as e:
            self.logger.error(f"Failed to create optimization job rule: {str(e)}")
            raise

    def setup_scheduled_anomaly_detection_job(
        self,
        rule_name: str = "hourly-anomaly-detection-job",
        schedule_expression: str = "cron(0 * * * ? *)"
    ) -> str:
        """Set up scheduled hourly anomaly detection job.

        Args:
            rule_name: Name of the EventBridge rule
            schedule_expression: Cron expression for scheduling (default: every hour)

        Returns:
            ARN of the created rule
        """
        try:
            response = self.eventbridge_client.put_rule(
                Name=rule_name,
                ScheduleExpression=schedule_expression,
                State="ENABLED",
                Description="Triggers hourly anomaly detection across all metrics"
            )
            self.logger.info(f"Created scheduled anomaly detection rule: {rule_name}")
            return response["RuleArn"]
        except Exception as e:
            self.logger.error(f"Failed to create anomaly detection job rule: {str(e)}")
            raise

    def setup_scheduled_report_generation_job(
        self,
        rule_name: str = "weekly-report-generation-job",
        schedule_expression: str = "cron(0 4 ? * MON *)"
    ) -> str:
        """Set up scheduled weekly report generation job.

        Args:
            rule_name: Name of the EventBridge rule
            schedule_expression: Cron expression for scheduling (default: Monday 4 AM UTC)

        Returns:
            ARN of the created rule
        """
        try:
            response = self.eventbridge_client.put_rule(
                Name=rule_name,
                ScheduleExpression=schedule_expression,
                State="ENABLED",
                Description="Triggers weekly supply chain analytics report generation"
            )
            self.logger.info(f"Created scheduled report generation rule: {rule_name}")
            return response["RuleArn"]
        except Exception as e:
            self.logger.error(f"Failed to create report generation job rule: {str(e)}")
            raise

    def add_lambda_target(
        self,
        rule_name: str,
        lambda_function_arn: str,
        input_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add Lambda function as target for an EventBridge rule.

        Args:
            rule_name: Name of the EventBridge rule
            lambda_function_arn: ARN of the Lambda function
            input_data: Optional input data to pass to Lambda

        Returns:
            Target ID
        """
        try:
            target_input = json.dumps(input_data) if input_data else None
            
            response = self.eventbridge_client.put_targets(
                Rule=rule_name,
                Targets=[
                    {
                        "Id": "1",
                        "Arn": lambda_function_arn,
                        "RoleArn": config.lambda_config.role_arn,
                        **({"Input": target_input} if target_input else {})
                    }
                ]
            )
            self.logger.info(f"Added Lambda target to rule {rule_name}")
            return response["FailedEntryCount"] == 0
        except Exception as e:
            self.logger.error(f"Failed to add Lambda target: {str(e)}")
            raise

    def trigger_agent_workflow(
        self,
        workflow_type: str,
        payload: Dict[str, Any]
    ) -> str:
        """Trigger an agent workflow by sending an event to EventBridge.

        Args:
            workflow_type: Type of workflow (e.g., 'forecasting', 'optimization')
            payload: Workflow payload data

        Returns:
            Event ID
        """
        try:
            response = self.eventbridge_client.put_events(
                Entries=[
                    {
                        "Source": "supply-chain.orchestrator",
                        "DetailType": f"Agent Workflow: {workflow_type}",
                        "Detail": json.dumps(payload),
                        "Resources": []
                    }
                ]
            )
            
            if response["FailedEntryCount"] == 0:
                self.logger.info(f"Triggered {workflow_type} workflow")
                return response["Entries"][0]["EventId"]
            else:
                raise Exception(f"Failed to trigger workflow: {response['Entries']}")
        except Exception as e:
            self.logger.error(f"Failed to trigger agent workflow: {str(e)}")
            raise

    def list_rules(self) -> List[Dict[str, Any]]:
        """List all EventBridge rules.

        Returns:
            List of rule details
        """
        try:
            response = self.eventbridge_client.list_rules()
            return response.get("Rules", [])
        except Exception as e:
            self.logger.error(f"Failed to list rules: {str(e)}")
            raise

    def delete_rule(self, rule_name: str) -> None:
        """Delete an EventBridge rule.

        Args:
            rule_name: Name of the rule to delete
        """
        try:
            # Remove targets first
            self.eventbridge_client.remove_targets(Rule=rule_name, Ids=["1"])
            # Then delete the rule
            self.eventbridge_client.delete_rule(Name=rule_name)
            self.logger.info(f"Deleted rule: {rule_name}")
        except Exception as e:
            self.logger.error(f"Failed to delete rule: {str(e)}")
            raise

    def enable_rule(self, rule_name: str) -> None:
        """Enable an EventBridge rule.

        Args:
            rule_name: Name of the rule to enable
        """
        try:
            self.eventbridge_client.enable_rule(Name=rule_name)
            self.logger.info(f"Enabled rule: {rule_name}")
        except Exception as e:
            self.logger.error(f"Failed to enable rule: {str(e)}")
            raise

    def disable_rule(self, rule_name: str) -> None:
        """Disable an EventBridge rule.

        Args:
            rule_name: Name of the rule to disable
        """
        try:
            self.eventbridge_client.disable_rule(Name=rule_name)
            self.logger.info(f"Disabled rule: {rule_name}")
        except Exception as e:
            self.logger.error(f"Failed to disable rule: {str(e)}")
            raise
