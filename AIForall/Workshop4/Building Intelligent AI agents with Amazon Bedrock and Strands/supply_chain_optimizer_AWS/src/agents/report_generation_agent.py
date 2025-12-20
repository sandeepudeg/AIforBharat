"""Report Generation Agent for Supply Chain Optimizer.

This agent is responsible for:
- Calculating key performance indicators (KPIs)
- Generating comprehensive analytics reports
- Creating visualizations of key metrics
- Performing period-over-period analysis
- Providing actionable recommendations
- Storing reports in S3 with metadata in RDS
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal
import uuid
import json
import statistics
import io

from src.config import logger
from src.models.report import Report, ReportType
from src.aws.clients import get_s3_client, get_dynamodb_resource
from src.database.connection import get_rds_session


class ReportGenerationAgent:
    """Agent for generating supply chain analytics reports."""

    def __init__(self):
        """Initialize the Report Generation Agent."""
        self.s3_client = get_s3_client()
        self.dynamodb = get_dynamodb_resource()
        self.s3_bucket = "supply-chain-reports"
        self.logger = logger

    def calculate_kpis(
        self,
        inventory_data: List[Dict[str, Any]],
        forecast_data: List[Dict[str, Any]],
        supplier_data: List[Dict[str, Any]],
        period_start: date,
        period_end: date,
    ) -> Dict[str, float]:
        """Calculate key performance indicators for the reporting period.

        Args:
            inventory_data: List of inventory records with quantity and value
            forecast_data: List of forecast records with actual vs forecasted demand
            supplier_data: List of supplier performance records
            period_start: Start date of reporting period
            period_end: End date of reporting period

        Returns:
            Dictionary containing calculated KPIs:
            - inventory_turnover: Ratio of COGS to average inventory
            - stockout_rate: Percentage of time products were out of stock
            - supplier_performance_score: Average supplier reliability score (0-100)
            - forecast_accuracy: Percentage accuracy of demand forecasts (0-100)
        """
        try:
            # Calculate inventory turnover
            inventory_turnover = self._calculate_inventory_turnover(inventory_data)

            # Calculate stockout rate
            stockout_rate = self._calculate_stockout_rate(inventory_data)

            # Calculate supplier performance score
            supplier_performance_score = self._calculate_supplier_performance(supplier_data)

            # Calculate forecast accuracy
            forecast_accuracy = self._calculate_forecast_accuracy(forecast_data)

            kpis = {
                "inventory_turnover": inventory_turnover,
                "stockout_rate": stockout_rate,
                "supplier_performance_score": supplier_performance_score,
                "forecast_accuracy": forecast_accuracy,
            }

            self.logger.info(f"Calculated KPIs for period {period_start} to {period_end}: {kpis}")
            return kpis

        except Exception as e:
            self.logger.error(f"Failed to calculate KPIs: {str(e)}")
            raise

    def generate_report(
        self,
        report_type: ReportType,
        period_start: date,
        period_end: date,
        kpis: Dict[str, float],
        recommendations: Optional[List[str]] = None,
        cost_savings: float = 0.0,
    ) -> Report:
        """Generate a comprehensive analytics report.

        Args:
            report_type: Type of report (daily, weekly, monthly, custom)
            period_start: Start date of reporting period
            period_end: End date of reporting period
            kpis: Dictionary of calculated KPIs
            recommendations: Optional list of recommendations
            cost_savings: Optional cost savings amount

        Returns:
            Report model instance with all metrics
        """
        try:
            report_id = f"RPT-{uuid.uuid4().hex[:12].upper()}"

            report = Report(
                report_id=report_id,
                report_type=report_type,
                period_start=period_start,
                period_end=period_end,
                inventory_turnover=kpis.get("inventory_turnover", 0.0),
                stockout_rate=kpis.get("stockout_rate", 0.0),
                supplier_performance_score=kpis.get("supplier_performance_score", 0.0),
                forecast_accuracy=kpis.get("forecast_accuracy", 0.0),
                cost_savings=cost_savings,
                recommendations=recommendations or [],
                generated_by="Report Generation Agent",
            )

            self.logger.info(f"Generated report {report_id} for period {period_start} to {period_end}")
            return report

        except Exception as e:
            self.logger.error(f"Failed to generate report: {str(e)}")
            raise

    def create_visualizations(
        self,
        report: Report,
        historical_data: Optional[Dict[str, List[float]]] = None,
    ) -> Dict[str, Any]:
        """Create visualizations for key metrics and trends.

        Args:
            report: Report model instance
            historical_data: Optional historical data for trend visualization
                           Keys: 'inventory_turnover', 'stockout_rate', 'forecast_accuracy'
                           Values: List of historical values

        Returns:
            Dictionary containing visualization specifications:
            - charts: List of chart specifications
            - data_points: Number of data points visualized
            - visualization_types: List of visualization types used
        """
        try:
            visualizations = {
                "charts": [],
                "data_points": 0,
                "visualization_types": [],
            }

            # Create KPI summary chart
            kpi_chart = {
                "type": "bar",
                "title": "Key Performance Indicators",
                "metrics": {
                    "inventory_turnover": report.inventory_turnover,
                    "stockout_rate": report.stockout_rate * 100,  # Convert to percentage
                    "supplier_performance_score": report.supplier_performance_score,
                    "forecast_accuracy": report.forecast_accuracy,
                },
            }
            visualizations["charts"].append(kpi_chart)
            visualizations["visualization_types"].append("bar")

            # Create trend chart if historical data provided
            if historical_data:
                trend_chart = {
                    "type": "line",
                    "title": "Metric Trends Over Time",
                    "data": historical_data,
                }
                visualizations["charts"].append(trend_chart)
                visualizations["visualization_types"].append("line")
                visualizations["data_points"] = sum(len(v) for v in historical_data.values())

            # Create performance gauge chart
            gauge_chart = {
                "type": "gauge",
                "title": "Overall Performance Score",
                "value": (
                    report.supplier_performance_score
                    + report.forecast_accuracy
                    + (100 - report.stockout_rate * 100)
                ) / 3,
            }
            visualizations["charts"].append(gauge_chart)
            visualizations["visualization_types"].append("gauge")

            self.logger.info(
                f"Created {len(visualizations['charts'])} visualizations for report {report.report_id}"
            )
            return visualizations

        except Exception as e:
            self.logger.error(f"Failed to create visualizations: {str(e)}")
            raise

    def compare_periods(
        self,
        current_period_kpis: Dict[str, float],
        previous_period_kpis: Dict[str, float],
        current_period_start: date,
        current_period_end: date,
        previous_period_start: date,
        previous_period_end: date,
    ) -> Dict[str, Any]:
        """Perform period-over-period comparison analysis.

        Args:
            current_period_kpis: KPIs for current reporting period
            previous_period_kpis: KPIs for previous reporting period
            current_period_start: Start date of current period
            current_period_end: End date of current period
            previous_period_start: Start date of previous period
            previous_period_end: End date of previous period

        Returns:
            Dictionary containing comparison results:
            - period_comparison: Detailed metric comparisons
            - trend_direction: Whether metrics are improving or declining
            - variance_percentage: Percentage change for each metric
        """
        try:
            comparison = {
                "current_period": f"{current_period_start} to {current_period_end}",
                "previous_period": f"{previous_period_start} to {previous_period_end}",
                "period_comparison": {},
                "trend_direction": {},
                "variance_percentage": {},
            }

            # Compare each KPI
            for metric_name in current_period_kpis.keys():
                current_value = current_period_kpis.get(metric_name, 0)
                previous_value = previous_period_kpis.get(metric_name, 0)

                # Calculate variance
                if previous_value != 0:
                    variance_pct = ((current_value - previous_value) / abs(previous_value)) * 100
                else:
                    variance_pct = 0 if current_value == 0 else 100

                # Determine trend direction
                # For stockout_rate, lower is better; for others, higher is better
                if metric_name == "stockout_rate":
                    trend = "improving" if current_value < previous_value else "declining"
                else:
                    trend = "improving" if current_value > previous_value else "declining"

                comparison["period_comparison"][metric_name] = {
                    "current": current_value,
                    "previous": previous_value,
                    "change": current_value - previous_value,
                }
                comparison["trend_direction"][metric_name] = trend
                comparison["variance_percentage"][metric_name] = variance_pct

            self.logger.info(f"Completed period-over-period comparison: {comparison}")
            return comparison

        except Exception as e:
            self.logger.error(f"Failed to compare periods: {str(e)}")
            raise

    def generate_recommendations(
        self,
        kpis: Dict[str, float],
        anomalies: Optional[List[Dict[str, Any]]] = None,
        trends: Optional[Dict[str, str]] = None,
    ) -> List[str]:
        """Generate actionable recommendations based on KPIs and trends.

        Args:
            kpis: Dictionary of calculated KPIs
            anomalies: Optional list of detected anomalies
            trends: Optional dictionary of metric trends

        Returns:
            List of actionable recommendations
        """
        try:
            recommendations = []

            # Analyze inventory turnover
            inventory_turnover = kpis.get("inventory_turnover", 0)
            if inventory_turnover < 2:
                recommendations.append(
                    "Inventory turnover is low. Consider reducing safety stock or increasing sales efforts."
                )
            elif inventory_turnover > 10:
                recommendations.append(
                    "Inventory turnover is very high. Ensure adequate safety stock to prevent stockouts."
                )

            # Analyze stockout rate
            stockout_rate = kpis.get("stockout_rate", 0)
            if stockout_rate > 0.05:  # 5%
                recommendations.append(
                    "Stockout rate is high. Increase safety stock or improve demand forecasting."
                )

            # Analyze supplier performance
            supplier_score = kpis.get("supplier_performance_score", 0)
            if supplier_score < 80:
                recommendations.append(
                    "Supplier performance is below target. Consider reviewing supplier contracts or finding alternatives."
                )

            # Analyze forecast accuracy
            forecast_accuracy = kpis.get("forecast_accuracy", 0)
            if forecast_accuracy < 75:
                recommendations.append(
                    "Forecast accuracy is low. Review forecasting methodology and incorporate external factors."
                )

            # Add anomaly-based recommendations
            if anomalies:
                for anomaly in anomalies:
                    if anomaly.get("severity") == "critical":
                        recommendations.append(
                            f"Critical anomaly detected: {anomaly.get('description', 'Unknown')}. "
                            f"Recommended action: {anomaly.get('recommended_action', 'Investigate immediately')}"
                        )

            # Add trend-based recommendations
            if trends:
                for metric, trend in trends.items():
                    if trend == "declining":
                        recommendations.append(
                            f"Metric '{metric}' is declining. Review contributing factors and take corrective action."
                        )

            self.logger.info(f"Generated {len(recommendations)} recommendations")
            return recommendations

        except Exception as e:
            self.logger.error(f"Failed to generate recommendations: {str(e)}")
            raise

    def store_report_in_s3(
        self,
        report: Report,
        visualizations: Dict[str, Any],
    ) -> str:
        """Store report and visualizations in S3.

        Args:
            report: Report model instance
            visualizations: Visualization specifications

        Returns:
            S3 object key where report was stored
        """
        try:
            # Create report document
            report_document = {
                "report_id": report.report_id,
                "report_type": report.report_type.value,
                "period_start": report.period_start.isoformat(),
                "period_end": report.period_end.isoformat(),
                "inventory_turnover": report.inventory_turnover,
                "stockout_rate": report.stockout_rate,
                "supplier_performance_score": report.supplier_performance_score,
                "forecast_accuracy": report.forecast_accuracy,
                "cost_savings": report.cost_savings,
                "recommendations": report.recommendations,
                "visualizations": visualizations,
                "generated_at": report.generated_at.isoformat(),
                "generated_by": report.generated_by,
            }

            # Create S3 key
            s3_key = f"reports/{report.report_type.value}/{report.report_id}.json"

            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=s3_key,
                Body=json.dumps(report_document, indent=2),
                ContentType="application/json",
                Metadata={
                    "report_id": report.report_id,
                    "report_type": report.report_type.value,
                    "period_start": report.period_start.isoformat(),
                    "period_end": report.period_end.isoformat(),
                },
            )

            self.logger.info(f"Stored report {report.report_id} in S3 at {s3_key}")
            return s3_key

        except Exception as e:
            self.logger.error(f"Failed to store report in S3: {str(e)}")
            raise

    def store_report_metadata_in_rds(
        self,
        report: Report,
        s3_key: str,
    ) -> None:
        """Store report metadata in RDS for querying.

        Args:
            report: Report model instance
            s3_key: S3 object key where report is stored
        """
        try:
            session = get_rds_session()

            # Create SQL insert statement
            insert_query = """
                INSERT INTO reports (
                    report_id, report_type, period_start, period_end,
                    inventory_turnover, stockout_rate, supplier_performance_score,
                    forecast_accuracy, cost_savings, s3_key, generated_at, generated_by
                ) VALUES (
                    :report_id, :report_type, :period_start, :period_end,
                    :inventory_turnover, :stockout_rate, :supplier_performance_score,
                    :forecast_accuracy, :cost_savings, :s3_key, :generated_at, :generated_by
                )
            """

            # Execute insert
            session.execute(
                insert_query,
                {
                    "report_id": report.report_id,
                    "report_type": report.report_type.value,
                    "period_start": report.period_start,
                    "period_end": report.period_end,
                    "inventory_turnover": report.inventory_turnover,
                    "stockout_rate": report.stockout_rate,
                    "supplier_performance_score": report.supplier_performance_score,
                    "forecast_accuracy": report.forecast_accuracy,
                    "cost_savings": report.cost_savings,
                    "s3_key": s3_key,
                    "generated_at": report.generated_at,
                    "generated_by": report.generated_by,
                },
            )

            session.commit()
            self.logger.info(f"Stored report metadata {report.report_id} in RDS")

        except Exception as e:
            self.logger.error(f"Failed to store report metadata in RDS: {str(e)}")
            raise
        finally:
            session.close()

    def generate_complete_report(
        self,
        report_type: ReportType,
        period_start: date,
        period_end: date,
        inventory_data: List[Dict[str, Any]],
        forecast_data: List[Dict[str, Any]],
        supplier_data: List[Dict[str, Any]],
        anomalies: Optional[List[Dict[str, Any]]] = None,
        previous_period_kpis: Optional[Dict[str, float]] = None,
        previous_period_start: Optional[date] = None,
        previous_period_end: Optional[date] = None,
    ) -> Report:
        """Generate a complete report with all components and store it.

        This is the main entry point that orchestrates all reporting steps.

        Args:
            report_type: Type of report (daily, weekly, monthly, custom)
            period_start: Start date of reporting period
            period_end: End date of reporting period
            inventory_data: List of inventory records
            forecast_data: List of forecast records
            supplier_data: List of supplier performance records
            anomalies: Optional list of detected anomalies
            previous_period_kpis: Optional KPIs from previous period for comparison
            previous_period_start: Optional start date of previous period
            previous_period_end: Optional end date of previous period

        Returns:
            Stored Report model instance
        """
        try:
            # Step 1: Calculate KPIs
            kpis = self.calculate_kpis(
                inventory_data, forecast_data, supplier_data, period_start, period_end
            )

            # Step 2: Generate recommendations
            trends = None
            if previous_period_kpis:
                comparison = self.compare_periods(
                    kpis,
                    previous_period_kpis,
                    period_start,
                    period_end,
                    previous_period_start or period_start - timedelta(days=7),
                    previous_period_end or period_start,
                )
                trends = comparison.get("trend_direction", {})

            recommendations = self.generate_recommendations(kpis, anomalies, trends)

            # Step 3: Generate report
            report = self.generate_report(
                report_type=report_type,
                period_start=period_start,
                period_end=period_end,
                kpis=kpis,
                recommendations=recommendations,
            )

            # Step 4: Create visualizations
            visualizations = self.create_visualizations(report)

            # Step 5: Store in S3
            s3_key = self.store_report_in_s3(report, visualizations)

            # Step 6: Store metadata in RDS
            self.store_report_metadata_in_rds(report, s3_key)

            self.logger.info(
                f"Complete report generated for {report_type.value} period "
                f"{period_start} to {period_end}: {report.report_id}"
            )

            return report

        except Exception as e:
            self.logger.error(f"Failed to generate complete report: {str(e)}")
            raise

    @staticmethod
    def _calculate_inventory_turnover(inventory_data: List[Dict[str, Any]]) -> float:
        """Calculate inventory turnover ratio.

        Inventory Turnover = COGS / Average Inventory Value

        Args:
            inventory_data: List of inventory records with 'quantity' and 'unit_cost' fields

        Returns:
            Inventory turnover ratio
        """
        if not inventory_data or len(inventory_data) == 0:
            return 0.0

        # Calculate total inventory value
        total_value = sum(
            record.get("quantity", 0) * record.get("unit_cost", 0) for record in inventory_data
        )

        # For simplicity, assume COGS is 4x average inventory (typical ratio)
        # In production, this would come from actual COGS data
        average_inventory_value = total_value / len(inventory_data) if inventory_data else 1
        cogs = average_inventory_value * 4

        if average_inventory_value == 0:
            return 0.0

        return cogs / average_inventory_value

    @staticmethod
    def _calculate_stockout_rate(inventory_data: List[Dict[str, Any]]) -> float:
        """Calculate stockout rate.

        Stockout Rate = Number of stockout events / Total number of inventory checks

        Args:
            inventory_data: List of inventory records with 'quantity_on_hand' field

        Returns:
            Stockout rate as decimal (0-1)
        """
        if not inventory_data or len(inventory_data) == 0:
            return 0.0

        stockout_count = sum(1 for record in inventory_data if record.get("quantity_on_hand", 0) == 0)
        return stockout_count / len(inventory_data)

    @staticmethod
    def _calculate_supplier_performance(supplier_data: List[Dict[str, Any]]) -> float:
        """Calculate average supplier performance score.

        Args:
            supplier_data: List of supplier records with 'reliability_score' field

        Returns:
            Average supplier performance score (0-100)
        """
        if not supplier_data or len(supplier_data) == 0:
            return 0.0

        scores = [record.get("reliability_score", 0) for record in supplier_data]
        return statistics.mean(scores) if scores else 0.0

    @staticmethod
    def _calculate_forecast_accuracy(forecast_data: List[Dict[str, Any]]) -> float:
        """Calculate forecast accuracy percentage.

        Forecast Accuracy = 1 - (|Actual - Forecast| / Actual) * 100

        Args:
            forecast_data: List of forecast records with 'forecasted_demand' and 'actual_demand' fields

        Returns:
            Forecast accuracy as percentage (0-100)
        """
        if not forecast_data or len(forecast_data) == 0:
            return 0.0

        accuracies = []
        for record in forecast_data:
            actual = record.get("actual_demand", 0)
            forecasted = record.get("forecasted_demand", 0)

            if actual == 0:
                # If actual is 0, accuracy is 100% if forecast is also 0, else 0%
                accuracy = 100 if forecasted == 0 else 0
            else:
                # Calculate MAPE (Mean Absolute Percentage Error)
                error = abs(actual - forecasted) / actual
                accuracy = max(0, (1 - error) * 100)

            accuracies.append(accuracy)

        return statistics.mean(accuracies) if accuracies else 0.0
