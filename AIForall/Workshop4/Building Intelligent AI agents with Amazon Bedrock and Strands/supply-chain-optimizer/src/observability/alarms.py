"""CloudWatch alarms for SLA violations in Supply Chain Optimizer."""

from typing import Optional

import boto3
from botocore.exceptions import ClientError

from src.config import config, logger


class CloudWatchAlarms:
    """Manages CloudWatch alarms for SLA violations."""

    def __init__(self):
        """Initialize CloudWatch client."""
        self.client = boto3.client("cloudwatch", region_name=config.aws.region)
        self.sns_topic_arn = config.sns.topic_arn_alerts
        self.namespace = "SupplyChainOptimizer"

    def create_report_generation_sla_alarm(
        self,
        alarm_name: str = "ReportGenerationSLAViolation",
        threshold_seconds: int = 300,  # 5 minutes for standard reports
        report_type: str = "standard",
    ) -> bool:
        """Create alarm for report generation SLA violations.
        
        Args:
            alarm_name: Name of the alarm
            threshold_seconds: Threshold in seconds (5 min for standard, 15 min for comprehensive)
            report_type: Type of report (standard or comprehensive)
        
        Returns:
            True if alarm created successfully, False otherwise
        """
        try:
            self.client.put_metric_alarm(
                AlarmName=alarm_name,
                ComparisonOperator="GreaterThanThreshold",
                EvaluationPeriods=1,
                MetricName="ReportGenerationTime",
                Namespace=self.namespace,
                Period=60,
                Statistic="Maximum",
                Threshold=threshold_seconds,
                ActionsEnabled=True,
                AlarmActions=[self.sns_topic_arn] if self.sns_topic_arn else [],
                AlarmDescription=f"Alert when {report_type} report generation exceeds {threshold_seconds} seconds",
                Dimensions=[
                    {
                        "Name": "ReportType",
                        "Value": report_type,
                    }
                ],
            )
            logger.info(f"Created alarm: {alarm_name}")
            return True
        except ClientError as e:
            logger.error(f"Failed to create alarm {alarm_name}: {str(e)}")
            return False

    def create_agent_failure_alarm(
        self,
        agent_name: str,
        alarm_name: Optional[str] = None,
    ) -> bool:
        """Create alarm for agent failures.
        
        Args:
            agent_name: Name of the agent
            alarm_name: Name of the alarm (auto-generated if not provided)
        
        Returns:
            True if alarm created successfully, False otherwise
        """
        if not alarm_name:
            alarm_name = f"{agent_name}FailureAlarm"

        try:
            self.client.put_metric_alarm(
                AlarmName=alarm_name,
                ComparisonOperator="GreaterThanOrEqualToThreshold",
                EvaluationPeriods=1,
                MetricName="AgentFailure",
                Namespace=self.namespace,
                Period=300,  # 5 minutes
                Statistic="Sum",
                Threshold=1,
                ActionsEnabled=True,
                AlarmActions=[self.sns_topic_arn] if self.sns_topic_arn else [],
                AlarmDescription=f"Alert when {agent_name} agent fails",
                Dimensions=[
                    {
                        "Name": "AgentName",
                        "Value": agent_name,
                    }
                ],
            )
            logger.info(f"Created alarm: {alarm_name}")
            return True
        except ClientError as e:
            logger.error(f"Failed to create alarm {alarm_name}: {str(e)}")
            return False

    def create_agent_performance_alarm(
        self,
        agent_name: str,
        threshold_seconds: float = 60,
        alarm_name: Optional[str] = None,
    ) -> bool:
        """Create alarm for agent performance degradation.
        
        Args:
            agent_name: Name of the agent
            threshold_seconds: Threshold for execution time in seconds
            alarm_name: Name of the alarm (auto-generated if not provided)
        
        Returns:
            True if alarm created successfully, False otherwise
        """
        if not alarm_name:
            alarm_name = f"{agent_name}PerformanceAlarm"

        try:
            self.client.put_metric_alarm(
                AlarmName=alarm_name,
                ComparisonOperator="GreaterThanThreshold",
                EvaluationPeriods=2,
                MetricName="AgentExecutionTime",
                Namespace=self.namespace,
                Period=300,  # 5 minutes
                Statistic="Average",
                Threshold=threshold_seconds,
                ActionsEnabled=True,
                AlarmActions=[self.sns_topic_arn] if self.sns_topic_arn else [],
                AlarmDescription=f"Alert when {agent_name} execution time exceeds {threshold_seconds} seconds",
                Dimensions=[
                    {
                        "Name": "AgentName",
                        "Value": agent_name,
                    }
                ],
            )
            logger.info(f"Created alarm: {alarm_name}")
            return True
        except ClientError as e:
            logger.error(f"Failed to create alarm {alarm_name}: {str(e)}")
            return False

    def create_forecast_accuracy_alarm(
        self,
        threshold_percentage: float = 80,
        alarm_name: str = "ForecastAccuracyLow",
    ) -> bool:
        """Create alarm for low forecast accuracy.
        
        Args:
            threshold_percentage: Threshold for forecast accuracy (0-100)
            alarm_name: Name of the alarm
        
        Returns:
            True if alarm created successfully, False otherwise
        """
        try:
            self.client.put_metric_alarm(
                AlarmName=alarm_name,
                ComparisonOperator="LessThanThreshold",
                EvaluationPeriods=1,
                MetricName="ForecastAccuracy",
                Namespace=self.namespace,
                Period=3600,  # 1 hour
                Statistic="Average",
                Threshold=threshold_percentage,
                ActionsEnabled=True,
                AlarmActions=[self.sns_topic_arn] if self.sns_topic_arn else [],
                AlarmDescription=f"Alert when forecast accuracy drops below {threshold_percentage}%",
            )
            logger.info(f"Created alarm: {alarm_name}")
            return True
        except ClientError as e:
            logger.error(f"Failed to create alarm {alarm_name}: {str(e)}")
            return False

    def create_supplier_performance_alarm(
        self,
        supplier_id: str,
        threshold_score: float = 70,
        alarm_name: Optional[str] = None,
    ) -> bool:
        """Create alarm for supplier performance degradation.
        
        Args:
            supplier_id: ID of the supplier
            threshold_score: Threshold for performance score (0-100)
            alarm_name: Name of the alarm (auto-generated if not provided)
        
        Returns:
            True if alarm created successfully, False otherwise
        """
        if not alarm_name:
            alarm_name = f"Supplier{supplier_id}PerformanceAlarm"

        try:
            self.client.put_metric_alarm(
                AlarmName=alarm_name,
                ComparisonOperator="LessThanThreshold",
                EvaluationPeriods=1,
                MetricName="SupplierPerformanceScore",
                Namespace=self.namespace,
                Period=3600,  # 1 hour
                Statistic="Average",
                Threshold=threshold_score,
                ActionsEnabled=True,
                AlarmActions=[self.sns_topic_arn] if self.sns_topic_arn else [],
                AlarmDescription=f"Alert when supplier {supplier_id} performance drops below {threshold_score}",
                Dimensions=[
                    {
                        "Name": "SupplierId",
                        "Value": supplier_id,
                    }
                ],
            )
            logger.info(f"Created alarm: {alarm_name}")
            return True
        except ClientError as e:
            logger.error(f"Failed to create alarm {alarm_name}: {str(e)}")
            return False

    def delete_alarm(self, alarm_name: str) -> bool:
        """Delete a CloudWatch alarm.
        
        Args:
            alarm_name: Name of the alarm to delete
        
        Returns:
            True if alarm deleted successfully, False otherwise
        """
        try:
            self.client.delete_alarms(AlarmNames=[alarm_name])
            logger.info(f"Deleted alarm: {alarm_name}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete alarm {alarm_name}: {str(e)}")
            return False

    def list_alarms(self) -> list:
        """List all CloudWatch alarms for this namespace.
        
        Returns:
            List of alarm names
        """
        try:
            response = self.client.describe_alarms()
            alarms = [alarm["AlarmName"] for alarm in response.get("MetricAlarms", [])]
            return alarms
        except ClientError as e:
            logger.error(f"Failed to list alarms: {str(e)}")
            return []
