"""Notification service for Supply Chain Optimizer.

This service handles sending alerts and notifications through SNS.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
import json

from src.config import logger, config
from src.aws.clients import get_sns_client, get_dynamodb_resource
from src.models.alert import Alert, AlertType, AlertSeverity, AlertStatus


class NotificationService:
    """Service for managing alerts and notifications."""

    def __init__(self):
        """Initialize the Notification Service."""
        self.sns_client = get_sns_client()
        self.dynamodb = get_dynamodb_resource()
        self.alerts_table_name = "alerts"
        self.logger = logger

    def send_critical_inventory_alert(
        self,
        sku: str,
        warehouse_id: str,
        current_inventory: int,
        reorder_point: int,
        recipients: List[str],
    ) -> Alert:
        """Send critical inventory alert.

        Args:
            sku: Stock Keeping Unit
            warehouse_id: Warehouse identifier
            current_inventory: Current inventory level
            reorder_point: Reorder point threshold
            recipients: List of email addresses to notify

        Returns:
            Alert object with sent status

        Raises:
            ValueError: If any parameter is invalid
        """
        if not sku or len(sku.strip()) == 0:
            raise ValueError("SKU cannot be empty")
        if not warehouse_id or len(warehouse_id.strip()) == 0:
            raise ValueError("Warehouse ID cannot be empty")
        if current_inventory < 0:
            raise ValueError("Current inventory cannot be negative")
        if reorder_point < 0:
            raise ValueError("Reorder point cannot be negative")
        if not recipients or len(recipients) == 0:
            raise ValueError("Recipients list cannot be empty")

        alert = Alert(
            alert_type=AlertType.CRITICAL_INVENTORY,
            severity=AlertSeverity.CRITICAL,
            title=f"Critical Inventory Alert: {sku}",
            description=f"Inventory for SKU {sku} at warehouse {warehouse_id} has reached critical level",
            sku=sku,
            warehouse_id=warehouse_id,
            current_value=current_inventory,
            threshold_value=reorder_point,
            recommended_action=f"Immediately place purchase order for {sku}. Current inventory: {current_inventory}, Reorder point: {reorder_point}",
            recipients=recipients,
        )

        return self._send_alert(alert)

    def send_delivery_delay_alert(
        self,
        po_id: str,
        sku: str,
        expected_delivery_date: str,
        days_overdue: int,
        inventory_impact: str,
        recipients: List[str],
    ) -> Alert:
        """Send delivery delay alert.

        Args:
            po_id: Purchase order ID
            sku: Stock Keeping Unit
            expected_delivery_date: Expected delivery date
            days_overdue: Number of days overdue
            inventory_impact: Description of inventory impact
            recipients: List of email addresses to notify

        Returns:
            Alert object with sent status

        Raises:
            ValueError: If any parameter is invalid
        """
        if not po_id or len(po_id.strip()) == 0:
            raise ValueError("PO ID cannot be empty")
        if not sku or len(sku.strip()) == 0:
            raise ValueError("SKU cannot be empty")
        if days_overdue < 0:
            raise ValueError("Days overdue cannot be negative")
        if not recipients or len(recipients) == 0:
            raise ValueError("Recipients list cannot be empty")

        alert = Alert(
            alert_type=AlertType.DELIVERY_DELAY,
            severity=AlertSeverity.HIGH if days_overdue > 7 else AlertSeverity.MEDIUM,
            title=f"Delivery Delay Alert: {po_id}",
            description=f"Purchase order {po_id} for SKU {sku} is {days_overdue} days overdue. Expected delivery: {expected_delivery_date}",
            sku=sku,
            po_id=po_id,
            recommended_action=f"Contact supplier immediately. {inventory_impact}. Consider alternative suppliers.",
            recipients=recipients,
        )

        return self._send_alert(alert)

    def send_anomaly_alert(
        self,
        anomaly_id: str,
        anomaly_type: str,
        severity: str,
        description: str,
        sku: Optional[str],
        warehouse_id: Optional[str],
        recommended_action: str,
        recipients: List[str],
    ) -> Alert:
        """Send anomaly alert.

        Args:
            anomaly_id: Anomaly identifier
            anomaly_type: Type of anomaly
            severity: Severity level (low, medium, high, critical)
            description: Anomaly description
            sku: Stock Keeping Unit (optional)
            warehouse_id: Warehouse identifier (optional)
            recommended_action: Recommended action
            recipients: List of email addresses to notify

        Returns:
            Alert object with sent status

        Raises:
            ValueError: If any parameter is invalid
        """
        if not anomaly_id or len(anomaly_id.strip()) == 0:
            raise ValueError("Anomaly ID cannot be empty")
        if not anomaly_type or len(anomaly_type.strip()) == 0:
            raise ValueError("Anomaly type cannot be empty")
        if not recipients or len(recipients) == 0:
            raise ValueError("Recipients list cannot be empty")

        severity_map = {
            "low": AlertSeverity.LOW,
            "medium": AlertSeverity.MEDIUM,
            "high": AlertSeverity.HIGH,
            "critical": AlertSeverity.CRITICAL,
        }

        alert = Alert(
            alert_type=AlertType.ANOMALY,
            severity=severity_map.get(severity.lower(), AlertSeverity.MEDIUM),
            title=f"Anomaly Alert: {anomaly_type}",
            description=description,
            sku=sku,
            warehouse_id=warehouse_id,
            anomaly_id=anomaly_id,
            recommended_action=recommended_action,
            recipients=recipients,
        )

        return self._send_alert(alert)

    def send_purchase_order_status_alert(
        self,
        po_id: str,
        sku: str,
        status: str,
        reason: Optional[str],
        recipients: List[str],
    ) -> Alert:
        """Send purchase order status alert.

        Args:
            po_id: Purchase order ID
            sku: Stock Keeping Unit
            status: Order status (approved, rejected, shipped, delivered)
            reason: Reason for status change (optional)
            recipients: List of email addresses to notify

        Returns:
            Alert object with sent status

        Raises:
            ValueError: If any parameter is invalid
        """
        if not po_id or len(po_id.strip()) == 0:
            raise ValueError("PO ID cannot be empty")
        if not sku or len(sku.strip()) == 0:
            raise ValueError("SKU cannot be empty")
        if not status or len(status.strip()) == 0:
            raise ValueError("Status cannot be empty")
        if not recipients or len(recipients) == 0:
            raise ValueError("Recipients list cannot be empty")

        severity_map = {
            "approved": AlertSeverity.LOW,
            "rejected": AlertSeverity.HIGH,
            "shipped": AlertSeverity.LOW,
            "delivered": AlertSeverity.LOW,
        }

        alert = Alert(
            alert_type=AlertType.PURCHASE_ORDER_STATUS,
            severity=severity_map.get(status.lower(), AlertSeverity.MEDIUM),
            title=f"Purchase Order Status Update: {po_id}",
            description=f"Purchase order {po_id} for SKU {sku} status changed to {status}",
            sku=sku,
            po_id=po_id,
            recommended_action=reason or f"Purchase order {po_id} has been {status}",
            recipients=recipients,
        )

        return self._send_alert(alert)

    def send_forecast_change_alert(
        self,
        sku: str,
        old_forecast: int,
        new_forecast: int,
        variance_percentage: float,
        recipients: List[str],
    ) -> Alert:
        """Send forecast change alert.

        Args:
            sku: Stock Keeping Unit
            old_forecast: Previous forecast value
            new_forecast: New forecast value
            variance_percentage: Percentage change in forecast
            recipients: List of email addresses to notify

        Returns:
            Alert object with sent status

        Raises:
            ValueError: If any parameter is invalid
        """
        if not sku or len(sku.strip()) == 0:
            raise ValueError("SKU cannot be empty")
        if old_forecast < 0:
            raise ValueError("Old forecast cannot be negative")
        if new_forecast < 0:
            raise ValueError("New forecast cannot be negative")
        if not recipients or len(recipients) == 0:
            raise ValueError("Recipients list cannot be empty")

        severity = (
            AlertSeverity.HIGH
            if abs(variance_percentage) > 20
            else AlertSeverity.MEDIUM
        )

        alert = Alert(
            alert_type=AlertType.FORECAST_CHANGE,
            severity=severity,
            title=f"Forecast Change Alert: {sku}",
            description=f"Demand forecast for SKU {sku} has changed by {variance_percentage:.1f}%",
            sku=sku,
            current_value=new_forecast,
            threshold_value=old_forecast,
            recommended_action=f"Review inventory levels. Old forecast: {old_forecast}, New forecast: {new_forecast}",
            recipients=recipients,
        )

        return self._send_alert(alert)

    def _send_alert(self, alert: Alert) -> Alert:
        """Send alert through SNS and store in DynamoDB.

        Args:
            alert: Alert object to send

        Returns:
            Alert object with updated status

        Raises:
            Exception: If SNS publish fails
        """
        try:
            # Prepare message
            message = self._format_alert_message(alert)

            # Publish to SNS
            topic_arn = config.sns.topic_arn_alerts
            if not topic_arn:
                self.logger.warning("SNS topic ARN not configured, skipping SNS publish")
            else:
                response = self.sns_client.publish(
                    TopicArn=topic_arn,
                    Subject=alert.title,
                    Message=message,
                )
                self.logger.info(f"Alert published to SNS: {response['MessageId']}")

            # Update alert status
            alert.status = AlertStatus.SENT
            alert.sent_at = datetime.utcnow()

            # Store in DynamoDB
            self._store_alert(alert)

            return alert

        except Exception as e:
            self.logger.error(f"Failed to send alert: {str(e)}")
            raise

    def _format_alert_message(self, alert: Alert) -> str:
        """Format alert message for SNS.

        Args:
            alert: Alert object

        Returns:
            Formatted message string
        """
        message = f"""
Supply Chain Alert Notification
================================

Alert Type: {alert.alert_type.value}
Severity: {alert.severity.value}
Title: {alert.title}

Description:
{alert.description}

Details:
- SKU: {alert.sku or 'N/A'}
- Warehouse: {alert.warehouse_id or 'N/A'}
- Purchase Order: {alert.po_id or 'N/A'}
- Current Value: {alert.current_value or 'N/A'}
- Threshold Value: {alert.threshold_value or 'N/A'}

Recommended Action:
{alert.recommended_action}

Alert ID: {alert.alert_id}
Created: {alert.created_at.isoformat()}
"""
        return message

    def _store_alert(self, alert: Alert) -> None:
        """Store alert in DynamoDB.

        Args:
            alert: Alert object to store
        """
        try:
            table = self.dynamodb.Table(self.alerts_table_name)
            table.put_item(Item=alert.to_dict())
            self.logger.info(f"Alert stored in DynamoDB: {alert.alert_id}")
        except Exception as e:
            self.logger.error(f"Failed to store alert in DynamoDB: {str(e)}")
            raise

    def get_alert(self, alert_id: str) -> Optional[Alert]:
        """Retrieve alert from DynamoDB.

        Args:
            alert_id: Alert identifier

        Returns:
            Alert object or None if not found
        """
        try:
            table = self.dynamodb.Table(self.alerts_table_name)
            response = table.get_item(Key={"alert_id": alert_id})
            if "Item" in response:
                return Alert.from_dict(response["Item"])
            return None
        except Exception as e:
            self.logger.error(f"Failed to retrieve alert: {str(e)}")
            raise

    def acknowledge_alert(self, alert_id: str) -> Alert:
        """Acknowledge an alert.

        Args:
            alert_id: Alert identifier

        Returns:
            Updated alert object

        Raises:
            ValueError: If alert not found
        """
        alert = self.get_alert(alert_id)
        if not alert:
            raise ValueError(f"Alert not found: {alert_id}")

        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_at = datetime.utcnow()

        try:
            table = self.dynamodb.Table(self.alerts_table_name)
            table.put_item(Item=alert.to_dict())
            self.logger.info(f"Alert acknowledged: {alert_id}")
            return alert
        except Exception as e:
            self.logger.error(f"Failed to acknowledge alert: {str(e)}")
            raise

    def resolve_alert(self, alert_id: str) -> Alert:
        """Resolve an alert.

        Args:
            alert_id: Alert identifier

        Returns:
            Updated alert object

        Raises:
            ValueError: If alert not found
        """
        alert = self.get_alert(alert_id)
        if not alert:
            raise ValueError(f"Alert not found: {alert_id}")

        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.utcnow()

        try:
            table = self.dynamodb.Table(self.alerts_table_name)
            table.put_item(Item=alert.to_dict())
            self.logger.info(f"Alert resolved: {alert_id}")
            return alert
        except Exception as e:
            self.logger.error(f"Failed to resolve alert: {str(e)}")
            raise
