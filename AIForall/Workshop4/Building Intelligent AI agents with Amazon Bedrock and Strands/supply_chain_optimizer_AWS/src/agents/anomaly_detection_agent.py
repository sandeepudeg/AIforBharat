"""Anomaly Detection Agent for Supply Chain Optimizer.

This agent is responsible for:
- Detecting unusual inventory levels
- Flagging supplier performance issues
- Identifying unexpected demand changes
- Analyzing root causes of anomalies
- Generating recommendations for corrective actions
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
import uuid
import statistics

from src.config import logger
from src.models.anomaly import Anomaly, AnomalyType, SeverityLevel, AnomalyStatus
from src.aws.clients import get_dynamodb_resource


class AnomalyDetectionAgent:
    """Agent for anomaly detection and analysis."""

    def __init__(self):
        """Initialize the Anomaly Detection Agent."""
        self.dynamodb = get_dynamodb_resource()
        self.anomalies_table_name = "anomalies"
        self.logger = logger

    def detect_inventory_anomaly(
        self,
        sku: str,
        current_inventory: int,
        forecasted_inventory: int,
        confidence_80: float,
        confidence_95: float,
        warehouse_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Detect unusual inventory levels.

        Detects when actual inventory deviates significantly from forecasted levels
        beyond the confidence intervals.

        Args:
            sku: Stock Keeping Unit
            current_inventory: Current inventory level
            forecasted_inventory: Forecasted inventory level
            confidence_80: 80% confidence interval
            confidence_95: 95% confidence interval
            warehouse_id: Optional warehouse identifier

        Returns:
            Dictionary with anomaly details if detected, None otherwise:
            - anomaly_id: Unique anomaly identifier
            - anomaly_type: Type of anomaly (inventory_deviation)
            - sku: Stock Keeping Unit
            - warehouse_id: Warehouse identifier (if provided)
            - severity: Severity level (low, medium, high, critical)
            - confidence_score: Confidence score (0-1)
            - description: Anomaly description
            - root_cause: Root cause analysis
            - recommended_action: Recommended action

        Raises:
            ValueError: If any parameter is invalid
        """
        if not sku or len(sku.strip()) == 0:
            raise ValueError("SKU cannot be empty")
        if current_inventory < 0:
            raise ValueError("Current inventory cannot be negative")
        if forecasted_inventory < 0:
            raise ValueError("Forecasted inventory cannot be negative")
        if confidence_80 < 0 or confidence_95 < 0:
            raise ValueError("Confidence intervals cannot be negative")

        # Calculate deviation from forecast
        deviation = current_inventory - forecasted_inventory
        deviation_percentage = (
            (abs(deviation) / forecasted_inventory * 100)
            if forecasted_inventory > 0
            else 0
        )

        # Determine if anomaly exists based on confidence intervals
        # If current inventory is outside 95% confidence interval, it's an anomaly
        lower_bound_95 = forecasted_inventory - confidence_95
        upper_bound_95 = forecasted_inventory + confidence_95

        is_anomaly = current_inventory < lower_bound_95 or current_inventory > upper_bound_95

        if not is_anomaly:
            return None

        # Determine severity based on deviation percentage
        if deviation_percentage > 50:
            severity = SeverityLevel.CRITICAL
            confidence_score = 0.95
        elif deviation_percentage > 30:
            severity = SeverityLevel.HIGH
            confidence_score = 0.85
        elif deviation_percentage > 15:
            severity = SeverityLevel.MEDIUM
            confidence_score = 0.75
        else:
            severity = SeverityLevel.LOW
            confidence_score = 0.65

        # Generate description
        if deviation > 0:
            description = (
                f"Inventory level {deviation_percentage:.1f}% ABOVE forecast. "
                f"Current: {current_inventory}, Forecasted: {forecasted_inventory}"
            )
            root_cause = "Possible causes: Demand lower than expected, Excess stock received"
        else:
            description = (
                f"Inventory level {deviation_percentage:.1f}% BELOW forecast. "
                f"Current: {current_inventory}, Forecasted: {forecasted_inventory}"
            )
            root_cause = "Possible causes: Demand higher than expected, Supply shortage, Inventory shrinkage"

        # Generate recommendation
        if deviation > 0:
            recommended_action = (
                "Review demand forecast. Consider promotional activities to increase sales. "
                "Evaluate storage capacity and holding costs."
            )
        else:
            recommended_action = (
                "Initiate emergency procurement. Review demand forecast accuracy. "
                "Investigate potential inventory shrinkage or data entry errors."
            )

        anomaly = {
            "anomaly_id": f"ANM-{uuid.uuid4().hex[:8].upper()}",
            "anomaly_type": AnomalyType.INVENTORY_DEVIATION.value,
            "sku": sku,
            "warehouse_id": warehouse_id,
            "severity": severity.value,
            "confidence_score": confidence_score,
            "description": description,
            "root_cause": root_cause,
            "recommended_action": recommended_action,
            "status": AnomalyStatus.OPEN.value,
            "created_at": datetime.utcnow().isoformat(),
        }

        self.logger.warning(
            f"Inventory anomaly detected for SKU {sku}: "
            f"deviation={deviation_percentage:.1f}%, severity={severity.value}"
        )

        return anomaly

    def detect_supplier_anomaly(
        self,
        supplier_id: str,
        on_time_delivery_rate: float,
        average_delivery_days: float,
        expected_lead_time: float,
        historical_on_time_rate: float,
    ) -> Optional[Dict[str, Any]]:
        """Detect supplier performance degradation.

        Detects when a supplier's performance metrics decline significantly.

        Args:
            supplier_id: Supplier identifier
            on_time_delivery_rate: Current on-time delivery rate (0-1)
            average_delivery_days: Current average delivery time
            expected_lead_time: Expected lead time
            historical_on_time_rate: Historical on-time delivery rate

        Returns:
            Dictionary with anomaly details if detected, None otherwise:
            - anomaly_id: Unique anomaly identifier
            - anomaly_type: Type of anomaly (supplier_delay)
            - sku: Supplier ID (used as identifier)
            - severity: Severity level
            - confidence_score: Confidence score (0-1)
            - description: Anomaly description
            - root_cause: Root cause analysis
            - recommended_action: Recommended action

        Raises:
            ValueError: If any parameter is invalid
        """
        if not supplier_id or len(supplier_id.strip()) == 0:
            raise ValueError("Supplier ID cannot be empty")
        if not (0 <= on_time_delivery_rate <= 1):
            raise ValueError("On-time delivery rate must be between 0 and 1")
        if not (0 <= historical_on_time_rate <= 1):
            raise ValueError("Historical on-time rate must be between 0 and 1")
        if average_delivery_days < 0 or expected_lead_time < 0:
            raise ValueError("Delivery times cannot be negative")

        # Calculate performance degradation
        rate_decline = historical_on_time_rate - on_time_delivery_rate
        delivery_delay = average_delivery_days - expected_lead_time

        # Determine if anomaly exists
        is_anomaly = rate_decline > 0.1 or delivery_delay > 2

        if not is_anomaly:
            return None

        # Determine severity
        if rate_decline > 0.3 or delivery_delay > 5:
            severity = SeverityLevel.CRITICAL
            confidence_score = 0.95
        elif rate_decline > 0.2 or delivery_delay > 3:
            severity = SeverityLevel.HIGH
            confidence_score = 0.85
        elif rate_decline > 0.1 or delivery_delay > 1:
            severity = SeverityLevel.MEDIUM
            confidence_score = 0.75
        else:
            severity = SeverityLevel.LOW
            confidence_score = 0.65

        # Generate description
        description = (
            f"Supplier performance degradation detected. "
            f"On-time rate: {on_time_delivery_rate:.1%} (was {historical_on_time_rate:.1%}). "
            f"Avg delivery: {average_delivery_days:.1f} days (expected: {expected_lead_time:.1f})"
        )

        root_cause = (
            "Possible causes: Supplier capacity issues, Supply chain disruptions, "
            "Quality control delays, Logistics problems"
        )

        recommended_action = (
            "Contact supplier to discuss performance issues. "
            "Evaluate alternative suppliers. "
            "Adjust safety stock and reorder points. "
            "Consider diversifying supplier base."
        )

        anomaly = {
            "anomaly_id": f"ANM-{uuid.uuid4().hex[:8].upper()}",
            "anomaly_type": AnomalyType.SUPPLIER_DELAY.value,
            "sku": supplier_id,  # Using SKU field to store supplier ID
            "warehouse_id": None,
            "severity": severity.value,
            "confidence_score": confidence_score,
            "description": description,
            "root_cause": root_cause,
            "recommended_action": recommended_action,
            "status": AnomalyStatus.OPEN.value,
            "created_at": datetime.utcnow().isoformat(),
        }

        self.logger.warning(
            f"Supplier anomaly detected for supplier {supplier_id}: "
            f"rate_decline={rate_decline:.1%}, delivery_delay={delivery_delay:.1f} days"
        )

        return anomaly

    def detect_demand_spike(
        self,
        sku: str,
        current_demand: int,
        forecasted_demand: int,
        confidence_95: float,
    ) -> Optional[Dict[str, Any]]:
        """Detect unexpected demand spikes.

        Detects when demand exceeds the 95% confidence interval of the forecast.

        Args:
            sku: Stock Keeping Unit
            current_demand: Current demand
            forecasted_demand: Forecasted demand
            confidence_95: 95% confidence interval

        Returns:
            Dictionary with anomaly details if detected, None otherwise:
            - anomaly_id: Unique anomaly identifier
            - anomaly_type: Type of anomaly (demand_spike)
            - sku: Stock Keeping Unit
            - severity: Severity level
            - confidence_score: Confidence score (0-1)
            - description: Anomaly description
            - root_cause: Root cause analysis
            - recommended_action: Recommended action

        Raises:
            ValueError: If any parameter is invalid
        """
        if not sku or len(sku.strip()) == 0:
            raise ValueError("SKU cannot be empty")
        if current_demand < 0 or forecasted_demand < 0:
            raise ValueError("Demand cannot be negative")
        if confidence_95 < 0:
            raise ValueError("Confidence interval cannot be negative")

        # Calculate upper bound of 95% confidence interval
        upper_bound_95 = forecasted_demand + confidence_95

        # Check if current demand exceeds upper bound
        is_spike = current_demand > upper_bound_95

        if not is_spike:
            return None

        # Calculate spike magnitude
        spike_percentage = (
            ((current_demand - forecasted_demand) / forecasted_demand * 100)
            if forecasted_demand > 0
            else 0
        )

        # Determine severity based on spike magnitude
        if spike_percentage > 100:
            severity = SeverityLevel.CRITICAL
            confidence_score = 0.95
        elif spike_percentage > 50:
            severity = SeverityLevel.HIGH
            confidence_score = 0.85
        elif spike_percentage > 25:
            severity = SeverityLevel.MEDIUM
            confidence_score = 0.75
        else:
            severity = SeverityLevel.LOW
            confidence_score = 0.65

        # Generate description
        description = (
            f"Demand spike detected for SKU {sku}. "
            f"Current demand: {current_demand}, Forecasted: {forecasted_demand}, "
            f"Spike magnitude: {spike_percentage:.1f}%"
        )

        root_cause = (
            "Possible causes: Viral marketing, Competitor stockout, "
            "Seasonal event, Promotional campaign, Supply shortage elsewhere"
        )

        recommended_action = (
            "Initiate emergency procurement immediately. "
            "Increase production if applicable. "
            "Communicate with suppliers for expedited delivery. "
            "Monitor inventory levels closely. "
            "Update demand forecast."
        )

        anomaly = {
            "anomaly_id": f"ANM-{uuid.uuid4().hex[:8].upper()}",
            "anomaly_type": AnomalyType.DEMAND_SPIKE.value,
            "sku": sku,
            "warehouse_id": None,
            "severity": severity.value,
            "confidence_score": confidence_score,
            "description": description,
            "root_cause": root_cause,
            "recommended_action": recommended_action,
            "status": AnomalyStatus.OPEN.value,
            "created_at": datetime.utcnow().isoformat(),
        }

        self.logger.warning(
            f"Demand spike detected for SKU {sku}: "
            f"spike_magnitude={spike_percentage:.1f}%, severity={severity.value}"
        )

        return anomaly

    def analyze_root_cause(
        self,
        anomaly_type: str,
        sku: str,
        current_value: float,
        expected_value: float,
        historical_data: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """Analyze root cause of an anomaly.

        Provides detailed root cause analysis based on anomaly type and data.

        Args:
            anomaly_type: Type of anomaly (inventory_deviation, supplier_delay, demand_spike, inventory_shrinkage)
            sku: Stock Keeping Unit or identifier
            current_value: Current value
            expected_value: Expected value
            historical_data: Optional historical data for trend analysis

        Returns:
            Dictionary with root cause analysis:
            - anomaly_type: Type of anomaly
            - sku: Stock Keeping Unit
            - deviation: Deviation from expected
            - deviation_percentage: Deviation percentage
            - possible_causes: List of possible causes
            - trend_analysis: Trend analysis if historical data provided
            - confidence_level: Confidence in analysis (0-1)

        Raises:
            ValueError: If parameters are invalid
        """
        if not anomaly_type or len(anomaly_type.strip()) == 0:
            raise ValueError("Anomaly type cannot be empty")
        if not sku or len(sku.strip()) == 0:
            raise ValueError("SKU cannot be empty")

        # Calculate deviation
        deviation = current_value - expected_value
        deviation_percentage = (
            (deviation / expected_value * 100) if expected_value != 0 else 0
        )

        # Determine possible causes based on anomaly type
        possible_causes = []
        confidence_level = 0.7

        if anomaly_type == AnomalyType.INVENTORY_DEVIATION.value:
            if deviation > 0:
                possible_causes = [
                    "Demand lower than forecasted",
                    "Excess stock received from supplier",
                    "Inventory counting error",
                    "Delayed sales processing",
                ]
            else:
                possible_causes = [
                    "Demand higher than forecasted",
                    "Supply shortage or delay",
                    "Inventory shrinkage or theft",
                    "Data entry error",
                    "Unrecorded sales",
                ]

        elif anomaly_type == AnomalyType.SUPPLIER_DELAY.value:
            possible_causes = [
                "Supplier capacity constraints",
                "Supply chain disruptions",
                "Quality control delays",
                "Logistics/transportation issues",
                "Customs or regulatory delays",
                "Supplier financial difficulties",
            ]

        elif anomaly_type == AnomalyType.DEMAND_SPIKE.value:
            possible_causes = [
                "Viral marketing or social media trend",
                "Competitor stockout",
                "Seasonal event or holiday",
                "Promotional campaign",
                "Supply shortage in market",
                "Price reduction or discount",
            ]

        elif anomaly_type == AnomalyType.INVENTORY_SHRINKAGE.value:
            possible_causes = [
                "Theft or loss",
                "Damage or spoilage",
                "Inventory counting error",
                "Unrecorded transfers",
                "Supplier short shipment",
                "Data entry error",
            ]

        # Analyze trend if historical data provided
        trend_analysis = None
        if historical_data and len(historical_data) > 1:
            try:
                mean = statistics.mean(historical_data)
                stdev = statistics.stdev(historical_data) if len(historical_data) > 1 else 0
                z_score = (current_value - mean) / stdev if stdev > 0 else 0

                trend_analysis = {
                    "mean": round(mean, 2),
                    "stdev": round(stdev, 2),
                    "z_score": round(z_score, 2),
                    "is_outlier": abs(z_score) > 2,
                }

                # Increase confidence if z-score indicates outlier
                if abs(z_score) > 2:
                    confidence_level = 0.9
            except Exception as e:
                self.logger.warning(f"Failed to analyze trend: {str(e)}")

        analysis = {
            "anomaly_type": anomaly_type,
            "sku": sku,
            "deviation": round(deviation, 2),
            "deviation_percentage": round(deviation_percentage, 2),
            "possible_causes": possible_causes,
            "trend_analysis": trend_analysis,
            "confidence_level": confidence_level,
        }

        self.logger.info(
            f"Root cause analysis for {anomaly_type} on {sku}: "
            f"deviation={deviation_percentage:.1f}%, confidence={confidence_level:.1%}"
        )

        return analysis

    def generate_recommendations(
        self,
        anomaly_type: str,
        severity: str,
        current_value: float,
        expected_value: float,
    ) -> Dict[str, Any]:
        """Generate recommendations for corrective actions.

        Args:
            anomaly_type: Type of anomaly
            severity: Severity level (low, medium, high, critical)
            current_value: Current value
            expected_value: Expected value

        Returns:
            Dictionary with recommendations:
            - immediate_actions: List of immediate actions
            - short_term_actions: List of short-term actions (1-7 days)
            - long_term_actions: List of long-term actions (1+ weeks)
            - priority_level: Priority level (1-5, 5 being highest)

        Raises:
            ValueError: If parameters are invalid
        """
        if not anomaly_type or len(anomaly_type.strip()) == 0:
            raise ValueError("Anomaly type cannot be empty")
        if not severity or len(severity.strip()) == 0:
            raise ValueError("Severity cannot be empty")

        # Determine priority based on severity
        priority_map = {
            SeverityLevel.LOW.value: 1,
            SeverityLevel.MEDIUM.value: 2,
            SeverityLevel.HIGH.value: 3,
            SeverityLevel.CRITICAL.value: 5,
        }
        priority_level = priority_map.get(severity, 2)

        immediate_actions = []
        short_term_actions = []
        long_term_actions = []

        # Generate recommendations based on anomaly type
        if anomaly_type == AnomalyType.INVENTORY_DEVIATION.value:
            if current_value < expected_value:
                # Low inventory
                immediate_actions = [
                    "Alert procurement team",
                    "Check supplier status",
                    "Review recent sales data",
                ]
                short_term_actions = [
                    "Initiate emergency procurement",
                    "Communicate with customers about potential delays",
                    "Investigate inventory discrepancies",
                ]
                long_term_actions = [
                    "Increase safety stock levels",
                    "Diversify supplier base",
                    "Improve demand forecasting",
                ]
            else:
                # High inventory
                immediate_actions = [
                    "Review demand forecast",
                    "Assess storage capacity",
                ]
                short_term_actions = [
                    "Plan promotional activities",
                    "Evaluate holding costs",
                    "Consider inventory transfers",
                ]
                long_term_actions = [
                    "Improve demand forecasting accuracy",
                    "Optimize reorder points",
                    "Review supplier agreements",
                ]

        elif anomaly_type == AnomalyType.SUPPLIER_DELAY.value:
            immediate_actions = [
                "Contact supplier for status update",
                "Identify alternative suppliers",
                "Assess inventory impact",
            ]
            short_term_actions = [
                "Negotiate expedited delivery",
                "Activate backup suppliers",
                "Adjust inventory forecasts",
            ]
            long_term_actions = [
                "Diversify supplier base",
                "Implement supplier performance monitoring",
                "Renegotiate supplier contracts",
            ]

        elif anomaly_type == AnomalyType.DEMAND_SPIKE.value:
            immediate_actions = [
                "Alert procurement team",
                "Initiate emergency procurement",
                "Increase production if applicable",
            ]
            short_term_actions = [
                "Expedite supplier deliveries",
                "Allocate inventory strategically",
                "Monitor inventory levels closely",
            ]
            long_term_actions = [
                "Increase safety stock",
                "Improve demand forecasting",
                "Build supplier relationships for flexibility",
            ]

        elif anomaly_type == AnomalyType.INVENTORY_SHRINKAGE.value:
            immediate_actions = [
                "Conduct physical inventory count",
                "Investigate discrepancies",
                "Review access logs",
            ]
            short_term_actions = [
                "Implement corrective measures",
                "Enhance security controls",
                "Audit inventory records",
            ]
            long_term_actions = [
                "Implement RFID tracking",
                "Improve inventory management processes",
                "Enhance staff training",
            ]

        recommendations = {
            "anomaly_type": anomaly_type,
            "severity": severity,
            "priority_level": priority_level,
            "immediate_actions": immediate_actions,
            "short_term_actions": short_term_actions,
            "long_term_actions": long_term_actions,
        }

        self.logger.info(
            f"Generated recommendations for {anomaly_type} "
            f"(severity={severity}, priority={priority_level})"
        )

        return recommendations

    def store_anomaly(
        self,
        anomaly_data: Dict[str, Any],
    ) -> None:
        """Store anomaly in the database.

        Args:
            anomaly_data: Anomaly data to store

        Raises:
            Exception: If database operation fails
        """
        try:
            table = self.dynamodb.Table(self.anomalies_table_name)

            # Add metadata if not present
            if "created_at" not in anomaly_data:
                anomaly_data["created_at"] = datetime.utcnow().isoformat()

            # Store in database
            table.put_item(Item=anomaly_data)

            self.logger.info(
                f"Stored anomaly {anomaly_data.get('anomaly_id')} in database"
            )

        except Exception as e:
            self.logger.error(
                f"Failed to store anomaly: {str(e)}"
            )
            raise

    def retrieve_anomaly(
        self,
        anomaly_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Retrieve an anomaly from the database.

        Args:
            anomaly_id: Anomaly identifier

        Returns:
            Anomaly data if found, None otherwise

        Raises:
            Exception: If database operation fails
        """
        try:
            table = self.dynamodb.Table(self.anomalies_table_name)

            response = table.get_item(Key={"anomaly_id": anomaly_id})

            if "Item" in response:
                self.logger.info(f"Retrieved anomaly {anomaly_id} from database")
                return response["Item"]

            self.logger.warning(f"Anomaly {anomaly_id} not found in database")
            return None

        except Exception as e:
            self.logger.error(
                f"Failed to retrieve anomaly {anomaly_id}: {str(e)}"
            )
            raise

    def retrieve_anomalies_by_sku(
        self,
        sku: str,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve anomalies for a specific SKU.

        Args:
            sku: Stock Keeping Unit
            status: Optional status filter (open, investigating, resolved)

        Returns:
            List of anomalies for the SKU

        Raises:
            Exception: If database operation fails
        """
        try:
            table = self.dynamodb.Table(self.anomalies_table_name)

            # Query anomalies by SKU
            response = table.query(
                KeyConditionExpression="sku = :sku",
                ExpressionAttributeValues={":sku": sku},
            )

            anomalies = response.get("Items", [])

            # Filter by status if provided
            if status:
                anomalies = [a for a in anomalies if a.get("status") == status]

            self.logger.info(
                f"Retrieved {len(anomalies)} anomalies for SKU {sku}"
            )

            return anomalies

        except Exception as e:
            self.logger.error(
                f"Failed to retrieve anomalies for SKU {sku}: {str(e)}"
            )
            raise
