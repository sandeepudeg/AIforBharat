"""Tests for Notification Service.

Feature: supply-chain-optimizer, Property 27-31: Alert and Notification System
Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5
"""

from datetime import datetime
from typing import List
from unittest.mock import MagicMock, patch
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck

from src.services.notification_service import NotificationService
from src.models.alert import Alert, AlertType, AlertSeverity, AlertStatus


@pytest.fixture
def notification_service():
    """Create a NotificationService instance."""
    with patch("src.services.notification_service.get_sns_client") as mock_sns, \
         patch("src.services.notification_service.get_dynamodb_resource") as mock_db:
        mock_sns.return_value = MagicMock()
        mock_db.return_value = MagicMock()
        service = NotificationService()
        service.sns_client.publish = MagicMock(return_value={"MessageId": "test-123"})
        service.dynamodb.Table = MagicMock(return_value=MagicMock())
        yield service


class TestCriticalInventoryAlert:
    """Test critical inventory alert functionality."""

    def test_send_critical_inventory_alert(self, notification_service):
        """Test sending critical inventory alert."""
        alert = notification_service.send_critical_inventory_alert(
            sku="PROD-001",
            warehouse_id="WH-001",
            current_inventory=50,
            reorder_point=100,
            recipients=["manager@example.com"],
        )

        assert alert is not None
        assert alert.alert_type == AlertType.CRITICAL_INVENTORY
        assert alert.severity == AlertSeverity.CRITICAL
        assert alert.status == AlertStatus.SENT
        assert alert.sku == "PROD-001"
        assert alert.warehouse_id == "WH-001"
        assert alert.current_value == 50
        assert alert.threshold_value == 100
        assert alert.sent_at is not None

    def test_send_critical_inventory_alert_invalid_sku(self, notification_service):
        """Test with invalid SKU."""
        with pytest.raises(ValueError):
            notification_service.send_critical_inventory_alert(
                sku="",
                warehouse_id="WH-001",
                current_inventory=50,
                reorder_point=100,
                recipients=["manager@example.com"],
            )

    def test_send_critical_inventory_alert_invalid_warehouse(self, notification_service):
        """Test with invalid warehouse ID."""
        with pytest.raises(ValueError):
            notification_service.send_critical_inventory_alert(
                sku="PROD-001",
                warehouse_id="",
                current_inventory=50,
                reorder_point=100,
                recipients=["manager@example.com"],
            )

    def test_send_critical_inventory_alert_negative_inventory(self, notification_service):
        """Test with negative inventory."""
        with pytest.raises(ValueError):
            notification_service.send_critical_inventory_alert(
                sku="PROD-001",
                warehouse_id="WH-001",
                current_inventory=-50,
                reorder_point=100,
                recipients=["manager@example.com"],
            )

    def test_send_critical_inventory_alert_no_recipients(self, notification_service):
        """Test with no recipients."""
        with pytest.raises(ValueError):
            notification_service.send_critical_inventory_alert(
                sku="PROD-001",
                warehouse_id="WH-001",
                current_inventory=50,
                reorder_point=100,
                recipients=[],
            )

    @given(
        sku=st.text(min_size=1, max_size=20).filter(lambda x: x.strip()),
        warehouse_id=st.text(min_size=1, max_size=20).filter(lambda x: x.strip()),
        current_inventory=st.integers(min_value=0, max_value=1000),
        reorder_point=st.integers(min_value=0, max_value=1000),
    )
    @settings(suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture], max_examples=50)
    def test_critical_inventory_alert_property(
        self, sku, warehouse_id, current_inventory, reorder_point
    ):
        """Property test: Critical inventory alert should always be sent with correct type and severity.
        
        Feature: supply-chain-optimizer, Property 27: Critical Inventory Alert
        Validates: Requirements 7.1
        """
        with patch("src.services.notification_service.get_sns_client") as mock_sns, \
             patch("src.services.notification_service.get_dynamodb_resource") as mock_db:
            mock_sns.return_value = MagicMock()
            mock_db.return_value = MagicMock()
            service = NotificationService()
            service.sns_client.publish = MagicMock(return_value={"MessageId": "test-123"})
            service.dynamodb.Table = MagicMock(return_value=MagicMock())
            
            recipients = ["manager@example.com"]
            alert = service.send_critical_inventory_alert(
                sku=sku,
                warehouse_id=warehouse_id,
                current_inventory=current_inventory,
                reorder_point=reorder_point,
                recipients=recipients,
            )

            # Property: Alert should always be sent with correct type and severity
            assert alert.alert_type == AlertType.CRITICAL_INVENTORY
            assert alert.severity == AlertSeverity.CRITICAL
            assert alert.status == AlertStatus.SENT
            assert alert.sent_at is not None
            assert alert.sku == sku
            assert alert.warehouse_id == warehouse_id
            assert alert.current_value == current_inventory
            assert alert.threshold_value == reorder_point


class TestDeliveryDelayAlert:
    """Test delivery delay alert functionality."""

    def test_send_delivery_delay_alert(self, notification_service):
        """Test sending delivery delay alert."""
        alert = notification_service.send_delivery_delay_alert(
            po_id="PO-001",
            sku="PROD-001",
            expected_delivery_date="2024-01-15",
            days_overdue=5,
            inventory_impact="5 days of inventory remaining",
            recipients=["manager@example.com"],
        )

        assert alert is not None
        assert alert.alert_type == AlertType.DELIVERY_DELAY
        assert alert.severity == AlertSeverity.MEDIUM
        assert alert.status == AlertStatus.SENT
        assert alert.po_id == "PO-001"
        assert alert.sku == "PROD-001"

    def test_send_delivery_delay_alert_high_severity(self, notification_service):
        """Test delivery delay alert with high severity (>7 days)."""
        alert = notification_service.send_delivery_delay_alert(
            po_id="PO-001",
            sku="PROD-001",
            expected_delivery_date="2024-01-15",
            days_overdue=10,
            inventory_impact="Critical inventory shortage",
            recipients=["manager@example.com"],
        )

        assert alert.severity == AlertSeverity.HIGH

    def test_send_delivery_delay_alert_invalid_po(self, notification_service):
        """Test with invalid PO ID."""
        with pytest.raises(ValueError):
            notification_service.send_delivery_delay_alert(
                po_id="",
                sku="PROD-001",
                expected_delivery_date="2024-01-15",
                days_overdue=5,
                inventory_impact="5 days of inventory remaining",
                recipients=["manager@example.com"],
            )

    def test_send_delivery_delay_alert_negative_days(self, notification_service):
        """Test with negative days overdue."""
        with pytest.raises(ValueError):
            notification_service.send_delivery_delay_alert(
                po_id="PO-001",
                sku="PROD-001",
                expected_delivery_date="2024-01-15",
                days_overdue=-5,
                inventory_impact="5 days of inventory remaining",
                recipients=["manager@example.com"],
            )

    @given(
        po_id=st.text(min_size=1, max_size=20).filter(lambda x: x.strip()),
        sku=st.text(min_size=1, max_size=20).filter(lambda x: x.strip()),
        days_overdue=st.integers(min_value=0, max_value=30),
    )
    @settings(suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture], max_examples=50)
    def test_delivery_delay_alert_property(
        self, po_id, sku, days_overdue
    ):
        """Property test: Delivery delay alert should always be sent with correct type.
        
        Feature: supply-chain-optimizer, Property 28: Delivery Delay Impact Notification
        Validates: Requirements 7.2
        """
        with patch("src.services.notification_service.get_sns_client") as mock_sns, \
             patch("src.services.notification_service.get_dynamodb_resource") as mock_db:
            mock_sns.return_value = MagicMock()
            mock_db.return_value = MagicMock()
            service = NotificationService()
            service.sns_client.publish = MagicMock(return_value={"MessageId": "test-123"})
            service.dynamodb.Table = MagicMock(return_value=MagicMock())
            
            alert = service.send_delivery_delay_alert(
                po_id=po_id,
                sku=sku,
                expected_delivery_date="2024-01-15",
                days_overdue=days_overdue,
                inventory_impact="Inventory impact",
                recipients=["manager@example.com"],
            )

            # Property: Alert should always be sent with correct type
            assert alert.alert_type == AlertType.DELIVERY_DELAY
            assert alert.status == AlertStatus.SENT
            assert alert.sent_at is not None
            assert alert.po_id == po_id
            assert alert.sku == sku


class TestAnomalyAlert:
    """Test anomaly alert functionality."""

    def test_send_anomaly_alert(self, notification_service):
        """Test sending anomaly alert."""
        alert = notification_service.send_anomaly_alert(
            anomaly_id="ANOM-001",
            anomaly_type="inventory_deviation",
            severity="high",
            description="Inventory deviation detected",
            sku="PROD-001",
            warehouse_id="WH-001",
            recommended_action="Investigate inventory discrepancy",
            recipients=["manager@example.com"],
        )

        assert alert is not None
        assert alert.alert_type == AlertType.ANOMALY
        assert alert.severity == AlertSeverity.HIGH
        assert alert.status == AlertStatus.SENT
        assert alert.anomaly_id == "ANOM-001"

    def test_send_anomaly_alert_critical_severity(self, notification_service):
        """Test anomaly alert with critical severity."""
        alert = notification_service.send_anomaly_alert(
            anomaly_id="ANOM-001",
            anomaly_type="inventory_shrinkage",
            severity="critical",
            description="Critical inventory shrinkage detected",
            sku="PROD-001",
            warehouse_id="WH-001",
            recommended_action="Immediate investigation required",
            recipients=["manager@example.com"],
        )

        assert alert.severity == AlertSeverity.CRITICAL

    def test_send_anomaly_alert_invalid_anomaly_id(self, notification_service):
        """Test with invalid anomaly ID."""
        with pytest.raises(ValueError):
            notification_service.send_anomaly_alert(
                anomaly_id="",
                anomaly_type="inventory_deviation",
                severity="high",
                description="Inventory deviation detected",
                sku="PROD-001",
                warehouse_id="WH-001",
                recommended_action="Investigate inventory discrepancy",
                recipients=["manager@example.com"],
            )

    def test_send_anomaly_alert_invalid_type(self, notification_service):
        """Test with invalid anomaly type."""
        with pytest.raises(ValueError):
            notification_service.send_anomaly_alert(
                anomaly_id="ANOM-001",
                anomaly_type="",
                severity="high",
                description="Inventory deviation detected",
                sku="PROD-001",
                warehouse_id="WH-001",
                recommended_action="Investigate inventory discrepancy",
                recipients=["manager@example.com"],
            )

    @given(
        anomaly_id=st.text(min_size=1, max_size=20).filter(lambda x: x.strip()),
        anomaly_type=st.sampled_from(["inventory_deviation", "supplier_delay", "demand_spike", "inventory_shrinkage"]),
        severity=st.sampled_from(["low", "medium", "high", "critical"]),
        description=st.text(min_size=10, max_size=200).filter(lambda x: x.strip()),
        recommended_action=st.text(min_size=10, max_size=200).filter(lambda x: x.strip()),
    )
    @settings(suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture], max_examples=50)
    def test_anomaly_alert_property(
        self, anomaly_id, anomaly_type, severity, description, recommended_action
    ):
        """Property test: Anomaly alert should always be sent with complete information.
        
        Feature: supply-chain-optimizer, Property 29: Anomaly Alert Completeness
        Validates: Requirements 7.3
        
        For any detected anomaly, the system should send alerts including:
        - Severity level (low/medium/high/critical)
        - Description of the anomaly
        - Recommended actions
        """
        with patch("src.services.notification_service.get_sns_client") as mock_sns, \
             patch("src.services.notification_service.get_dynamodb_resource") as mock_db:
            mock_sns.return_value = MagicMock()
            mock_db.return_value = MagicMock()
            service = NotificationService()
            service.sns_client.publish = MagicMock(return_value={"MessageId": "test-123"})
            service.dynamodb.Table = MagicMock(return_value=MagicMock())
            
            alert = service.send_anomaly_alert(
                anomaly_id=anomaly_id,
                anomaly_type=anomaly_type,
                severity=severity,
                description=description,
                sku="PROD-001",
                warehouse_id="WH-001",
                recommended_action=recommended_action,
                recipients=["manager@example.com"],
            )

            # Property: Alert should always be sent with complete information
            # 1. Verify alert type and status
            assert alert.alert_type == AlertType.ANOMALY
            assert alert.status == AlertStatus.SENT
            assert alert.sent_at is not None
            
            # 2. Verify anomaly identification
            assert alert.anomaly_id == anomaly_id
            assert len(alert.anomaly_id) > 0
            
            # 3. Verify severity level is correctly mapped
            severity_map = {
                "low": AlertSeverity.LOW,
                "medium": AlertSeverity.MEDIUM,
                "high": AlertSeverity.HIGH,
                "critical": AlertSeverity.CRITICAL,
            }
            assert alert.severity == severity_map[severity]
            assert alert.severity in [
                AlertSeverity.LOW,
                AlertSeverity.MEDIUM,
                AlertSeverity.HIGH,
                AlertSeverity.CRITICAL,
            ]
            
            # 4. Verify description is present and non-empty
            assert alert.description is not None
            assert len(alert.description) > 0
            assert alert.description == description
            
            # 5. Verify recommended action is present and non-empty
            assert alert.recommended_action is not None
            assert len(alert.recommended_action) > 0
            assert alert.recommended_action == recommended_action
            
            # 6. Verify all required fields for completeness
            assert alert.title is not None
            assert len(alert.title) > 0
            assert "Anomaly" in alert.title
            
            # 7. Verify recipients are set
            assert alert.recipients is not None
            assert len(alert.recipients) > 0


class TestPurchaseOrderStatusAlert:
    """Test purchase order status alert functionality."""

    def test_send_purchase_order_status_alert_approved(self, notification_service):
        """Test sending PO status alert for approved order."""
        alert = notification_service.send_purchase_order_status_alert(
            po_id="PO-001",
            sku="PROD-001",
            status="approved",
            reason="Order approved by procurement",
            recipients=["manager@example.com"],
        )

        assert alert is not None
        assert alert.alert_type == AlertType.PURCHASE_ORDER_STATUS
        assert alert.severity == AlertSeverity.LOW
        assert alert.status == AlertStatus.SENT
        assert alert.po_id == "PO-001"

    def test_send_purchase_order_status_alert_rejected(self, notification_service):
        """Test sending PO status alert for rejected order."""
        alert = notification_service.send_purchase_order_status_alert(
            po_id="PO-001",
            sku="PROD-001",
            status="rejected",
            reason="Supplier out of stock",
            recipients=["manager@example.com"],
        )

        assert alert.severity == AlertSeverity.HIGH

    def test_send_purchase_order_status_alert_invalid_po(self, notification_service):
        """Test with invalid PO ID."""
        with pytest.raises(ValueError):
            notification_service.send_purchase_order_status_alert(
                po_id="",
                sku="PROD-001",
                status="approved",
                reason="Order approved",
                recipients=["manager@example.com"],
            )

    def test_send_purchase_order_status_alert_invalid_status(self, notification_service):
        """Test with invalid status."""
        with pytest.raises(ValueError):
            notification_service.send_purchase_order_status_alert(
                po_id="PO-001",
                sku="PROD-001",
                status="",
                reason="Order approved",
                recipients=["manager@example.com"],
            )

    @given(
        po_id=st.text(min_size=1, max_size=20).filter(lambda x: x.strip()),
        sku=st.text(min_size=1, max_size=20).filter(lambda x: x.strip()),
        status=st.sampled_from(["approved", "rejected", "shipped", "delivered"]),
    )
    @settings(suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture], max_examples=50)
    def test_purchase_order_status_alert_property(
        self, po_id, sku, status
    ):
        """Property test: PO status alert should always be sent with correct type.
        
        Feature: supply-chain-optimizer, Property 30: Purchase Order Status Notification
        Validates: Requirements 7.4
        """
        with patch("src.services.notification_service.get_sns_client") as mock_sns, \
             patch("src.services.notification_service.get_dynamodb_resource") as mock_db:
            mock_sns.return_value = MagicMock()
            mock_db.return_value = MagicMock()
            service = NotificationService()
            service.sns_client.publish = MagicMock(return_value={"MessageId": "test-123"})
            service.dynamodb.Table = MagicMock(return_value=MagicMock())
            
            alert = service.send_purchase_order_status_alert(
                po_id=po_id,
                sku=sku,
                status=status,
                reason="Status update",
                recipients=["manager@example.com"],
            )

            # Property: Alert should always be sent with correct type
            assert alert.alert_type == AlertType.PURCHASE_ORDER_STATUS
            assert alert.status == AlertStatus.SENT
            assert alert.sent_at is not None
            assert alert.po_id == po_id
            assert alert.sku == sku


class TestForecastChangeAlert:
    """Test forecast change alert functionality."""

    def test_send_forecast_change_alert(self, notification_service):
        """Test sending forecast change alert."""
        alert = notification_service.send_forecast_change_alert(
            sku="PROD-001",
            old_forecast=1000,
            new_forecast=1300,
            variance_percentage=30.0,
            recipients=["manager@example.com"],
        )

        assert alert is not None
        assert alert.alert_type == AlertType.FORECAST_CHANGE
        assert alert.severity == AlertSeverity.HIGH
        assert alert.status == AlertStatus.SENT
        assert alert.sku == "PROD-001"
        assert alert.current_value == 1300
        assert alert.threshold_value == 1000

    def test_send_forecast_change_alert_small_variance(self, notification_service):
        """Test forecast change alert with small variance."""
        alert = notification_service.send_forecast_change_alert(
            sku="PROD-001",
            old_forecast=1000,
            new_forecast=1050,
            variance_percentage=5.0,
            recipients=["manager@example.com"],
        )

        assert alert.severity == AlertSeverity.MEDIUM

    def test_send_forecast_change_alert_invalid_sku(self, notification_service):
        """Test with invalid SKU."""
        with pytest.raises(ValueError):
            notification_service.send_forecast_change_alert(
                sku="",
                old_forecast=1000,
                new_forecast=1200,
                variance_percentage=20.0,
                recipients=["manager@example.com"],
            )

    def test_send_forecast_change_alert_negative_forecast(self, notification_service):
        """Test with negative forecast."""
        with pytest.raises(ValueError):
            notification_service.send_forecast_change_alert(
                sku="PROD-001",
                old_forecast=-1000,
                new_forecast=1200,
                variance_percentage=20.0,
                recipients=["manager@example.com"],
            )

    @given(
        sku=st.text(min_size=1, max_size=20).filter(lambda x: x.strip()),
        old_forecast=st.integers(min_value=0, max_value=10000),
        new_forecast=st.integers(min_value=0, max_value=10000),
    )
    @settings(suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture], max_examples=50)
    def test_forecast_change_alert_property(
        self, sku, old_forecast, new_forecast
    ):
        """Property test: Forecast change alert should always be sent with correct type.
        
        Feature: supply-chain-optimizer, Property 31: Forecast Change Notification
        Validates: Requirements 7.5
        """
        with patch("src.services.notification_service.get_sns_client") as mock_sns, \
             patch("src.services.notification_service.get_dynamodb_resource") as mock_db:
            mock_sns.return_value = MagicMock()
            mock_db.return_value = MagicMock()
            service = NotificationService()
            service.sns_client.publish = MagicMock(return_value={"MessageId": "test-123"})
            service.dynamodb.Table = MagicMock(return_value=MagicMock())
            
            variance = abs(new_forecast - old_forecast) / max(old_forecast, 1) * 100
            alert = service.send_forecast_change_alert(
                sku=sku,
                old_forecast=old_forecast,
                new_forecast=new_forecast,
                variance_percentage=variance,
                recipients=["manager@example.com"],
            )

            # Property: Alert should always be sent with correct type
            assert alert.alert_type == AlertType.FORECAST_CHANGE
            assert alert.status == AlertStatus.SENT
            assert alert.sent_at is not None
            assert alert.sku == sku
            assert alert.current_value == new_forecast
            assert alert.threshold_value == old_forecast


class TestAlertManagement:
    """Test alert management functionality."""

    def test_acknowledge_alert(self, notification_service):
        """Test acknowledging an alert."""
        # Create and send alert
        alert = notification_service.send_critical_inventory_alert(
            sku="PROD-001",
            warehouse_id="WH-001",
            current_inventory=50,
            reorder_point=100,
            recipients=["manager@example.com"],
        )

        # Mock get_alert to return the alert
        notification_service.get_alert = MagicMock(return_value=alert)

        # Acknowledge alert
        acknowledged_alert = notification_service.acknowledge_alert(alert.alert_id)

        assert acknowledged_alert.status == AlertStatus.ACKNOWLEDGED
        assert acknowledged_alert.acknowledged_at is not None

    def test_resolve_alert(self, notification_service):
        """Test resolving an alert."""
        # Create and send alert
        alert = notification_service.send_critical_inventory_alert(
            sku="PROD-001",
            warehouse_id="WH-001",
            current_inventory=50,
            reorder_point=100,
            recipients=["manager@example.com"],
        )

        # Mock get_alert to return the alert
        notification_service.get_alert = MagicMock(return_value=alert)

        # Resolve alert
        resolved_alert = notification_service.resolve_alert(alert.alert_id)

        assert resolved_alert.status == AlertStatus.RESOLVED
        assert resolved_alert.resolved_at is not None

    def test_acknowledge_nonexistent_alert(self, notification_service):
        """Test acknowledging a nonexistent alert."""
        notification_service.get_alert = MagicMock(return_value=None)

        with pytest.raises(ValueError):
            notification_service.acknowledge_alert("NONEXISTENT-ID")

    def test_resolve_nonexistent_alert(self, notification_service):
        """Test resolving a nonexistent alert."""
        notification_service.get_alert = MagicMock(return_value=None)

        with pytest.raises(ValueError):
            notification_service.resolve_alert("NONEXISTENT-ID")
