"""Alert model for Supply Chain Optimizer."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List
import uuid


class AlertType(str, Enum):
    """Alert type enumeration."""

    CRITICAL_INVENTORY = "critical_inventory"
    DELIVERY_DELAY = "delivery_delay"
    ANOMALY = "anomaly"
    PURCHASE_ORDER_STATUS = "purchase_order_status"
    FORECAST_CHANGE = "forecast_change"


class AlertSeverity(str, Enum):
    """Alert severity enumeration."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    """Alert status enumeration."""

    PENDING = "pending"
    SENT = "sent"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


@dataclass
class Alert:
    """Alert model."""

    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    alert_type: AlertType = AlertType.CRITICAL_INVENTORY
    severity: AlertSeverity = AlertSeverity.MEDIUM
    status: AlertStatus = AlertStatus.PENDING
    title: str = ""
    description: str = ""
    sku: Optional[str] = None
    warehouse_id: Optional[str] = None
    po_id: Optional[str] = None
    anomaly_id: Optional[str] = None
    current_value: Optional[float] = None
    threshold_value: Optional[float] = None
    recommended_action: str = ""
    recipients: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convert alert to dictionary."""
        return {
            "alert_id": self.alert_id,
            "alert_type": self.alert_type.value,
            "severity": self.severity.value,
            "status": self.status.value,
            "title": self.title,
            "description": self.description,
            "sku": self.sku,
            "warehouse_id": self.warehouse_id,
            "po_id": self.po_id,
            "anomaly_id": self.anomaly_id,
            "current_value": self.current_value,
            "threshold_value": self.threshold_value,
            "recommended_action": self.recommended_action,
            "recipients": self.recipients,
            "created_at": self.created_at.isoformat(),
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }

    @staticmethod
    def from_dict(data: dict) -> "Alert":
        """Create alert from dictionary."""
        return Alert(
            alert_id=data.get("alert_id", str(uuid.uuid4())),
            alert_type=AlertType(data.get("alert_type", "critical_inventory")),
            severity=AlertSeverity(data.get("severity", "medium")),
            status=AlertStatus(data.get("status", "pending")),
            title=data.get("title", ""),
            description=data.get("description", ""),
            sku=data.get("sku"),
            warehouse_id=data.get("warehouse_id"),
            po_id=data.get("po_id"),
            anomaly_id=data.get("anomaly_id"),
            current_value=data.get("current_value"),
            threshold_value=data.get("threshold_value"),
            recommended_action=data.get("recommended_action", ""),
            recipients=data.get("recipients", []),
            created_at=datetime.fromisoformat(data["created_at"]) if isinstance(data.get("created_at"), str) else data.get("created_at", datetime.utcnow()),
            sent_at=datetime.fromisoformat(data["sent_at"]) if isinstance(data.get("sent_at"), str) else data.get("sent_at"),
            acknowledged_at=datetime.fromisoformat(data["acknowledged_at"]) if isinstance(data.get("acknowledged_at"), str) else data.get("acknowledged_at"),
            resolved_at=datetime.fromisoformat(data["resolved_at"]) if isinstance(data.get("resolved_at"), str) else data.get("resolved_at"),
        )
