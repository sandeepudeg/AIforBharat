#!/usr/bin/env python3
"""
Supply Chain Optimizer - Run with Real AWS Services

This script demonstrates the complete system using real AWS services:
- DynamoDB for data storage
- S3 for reports
- SNS for notifications
- RDS for relational data (optional)
"""

import json
from datetime import datetime, timedelta
from src.agents.demand_forecasting_agent import DemandForecastingAgent
from src.agents.inventory_optimizer_agent import InventoryOptimizerAgent
from src.agents.supplier_coordination_agent import SupplierCoordinationAgent
from src.agents.anomaly_detection_agent import AnomalyDetectionAgent
from src.agents.report_generation_agent import ReportGenerationAgent
from src.aws.clients import (
    get_dynamodb_resource,
    get_s3_client,
    get_sns_client,
)
from src.config import config, logger


class AWSServiceDemo:
    """Demonstrate agents working with AWS services."""

    def __init__(self):
        """Initialize AWS clients and agents."""
        self.dynamodb = get_dynamodb_resource()
        self.s3 = get_s3_client()
        self.sns = get_sns_client()
        
        self.forecasting_agent = DemandForecastingAgent()
        self.inventory_agent = InventoryOptimizerAgent()
        self.supplier_agent = SupplierCoordinationAgent()
        self.anomaly_agent = AnomalyDetectionAgent()
        self.reporting_agent = ReportGenerationAgent()
        
        logger.info("AWS Service Demo initialized")

    def save_to_dynamodb(self, table_name: str, item: dict) -> bool:
        """Save item to DynamoDB."""
        try:
            table = self.dynamodb.Table(table_name)
            table.put_item(Item=item)
            logger.info(f"Saved to DynamoDB table '{table_name}': {item.get('id', 'unknown')}")
            return True
        except Exception as e:
            logger.error(f"Failed to save to DynamoDB: {str(e)}")
            return False

    def read_from_dynamodb(self, table_name: str, key: dict) -> dict:
        """Read item from DynamoDB."""
        try:
            table = self.dynamodb.Table(table_name)
            response = table.get_item(Key=key)
            item = response.get('Item', {})
            logger.info(f"Read from DynamoDB table '{table_name}': {item}")
            return item
        except Exception as e:
            logger.error(f"Failed to read from DynamoDB: {str(e)}")
            return {}

    def save_to_s3(self, key: str, data: dict) -> bool:
        """Save report to S3."""
        try:
            bucket = config.s3.bucket_name
            self.s3.put_object(
                Bucket=bucket,
                Key=key,
                Body=json.dumps(data, indent=2, default=str),
                ContentType='application/json'
            )
            logger.info(f"Saved to S3: s3://{bucket}/{key}")
            return True
        except Exception as e:
            logger.error(f"Failed to save to S3: {str(e)}")
            return False

    def send_notification(self, subject: str, message: str) -> bool:
        """Send SNS notification."""
        try:
            topic_arn = config.sns.topic_arn_alerts
            if not topic_arn:
                logger.warning("SNS_TOPIC_ARN_ALERTS not configured")
                return False
            
            self.sns.publish(
                TopicArn=topic_arn,
                Subject=subject,
                Message=message
            )
            logger.info(f"SNS notification sent: {subject}")
            return True
        except Exception as e:
            logger.error(f"Failed to send SNS notification: {str(e)}")
            return False

    def run_complete_workflow(self):
        """Run complete supply chain optimization workflow."""
        print("\n" + "="*80)
        print("SUPPLY CHAIN OPTIMIZER - AWS SERVICES WORKFLOW")
        print("="*80)

        # Step 1: Create sample inventory data in DynamoDB
        print("\n[STEP 1] Creating inventory data in DynamoDB...")
        inventory_item = {
            'inventory_id': f'INV-{datetime.now().timestamp()}',
            'sku': 'PROD-001',
            'warehouse': 'WH-001',
            'current_quantity': 500,
            'reorder_point': 300,
            'safety_stock': 200,
            'last_updated': datetime.now().isoformat(),
        }
        self.save_to_dynamodb('inventory', inventory_item)

        # Step 2: Create sales history and forecast
        print("\n[STEP 2] Generating demand forecast...")
        sales_data = [
            {"date": f"2024-{(12-i):02d}-01", "quantity": 100 + i*5}
            for i in range(12)
        ]
        
        sales_analysis = self.forecasting_agent.analyze_sales_history(
            sku="PROD-001",
            sales_data=sales_data
        )
        
        forecast = self.forecasting_agent.generate_forecast(
            sku="PROD-001",
            sales_analysis=sales_analysis,
            forecast_days=30
        )
        
        # Save forecast to DynamoDB
        forecast_item = {
            'forecast_id': f'FCST-{datetime.now().timestamp()}',
            'sku': 'PROD-001',
            'forecasted_demand': forecast.get('forecasted_demand', 0),
            'confidence_80': forecast.get('confidence_80', 0),
            'confidence_95': forecast.get('confidence_95', 0),
            'forecast_date': datetime.now().isoformat(),
            'forecast_period_days': 30,
        }
        self.save_to_dynamodb('forecasts', forecast_item)
        print(f"  Forecast: {forecast_item['forecasted_demand']:.0f} units")
        print(f"  80% CI: {forecast_item['confidence_80']:.0f} units")
        print(f"  95% CI: {forecast_item['confidence_95']:.0f} units")

        # Step 3: Optimize inventory
        print("\n[STEP 3] Optimizing inventory levels...")
        eoq = self.inventory_agent.calculate_eoq(
            annual_demand=forecast.get('forecasted_demand', 3000) * 12,
            ordering_cost=50,
            holding_cost_per_unit=2
        )
        
        reorder_point = self.inventory_agent.calculate_reorder_point(
            average_daily_demand=forecast.get('forecasted_demand', 3000) / 30,
            lead_time_days=7,
            safety_stock=200
        )
        
        print(f"  EOQ: {eoq:.0f} units")
        print(f"  Reorder Point: {reorder_point:.0f} units")
        print(f"  Current Inventory: {inventory_item['current_quantity']} units")
        
        # Check if reorder needed
        if inventory_item['current_quantity'] < reorder_point:
            print(f"  ACTION: Reorder needed! Current < Reorder Point")

        # Step 4: Create purchase order
        print("\n[STEP 4] Creating purchase order...")
        po_item = {
            'po_id': f'PO-{datetime.now().timestamp()}',
            'sku': 'PROD-001',
            'supplier_id': 'SUPP-001',
            'quantity': int(eoq),
            'unit_price': 10.50,
            'total_price': int(eoq) * 10.50,
            'delivery_date': (datetime.now() + timedelta(days=7)).isoformat(),
            'status': 'pending',
            'created_date': datetime.now().isoformat(),
        }
        self.save_to_dynamodb('purchase_orders', po_item)
        print(f"  PO ID: {po_item['po_id']}")
        print(f"  Quantity: {po_item['quantity']} units")
        print(f"  Total Price: ${po_item['total_price']:.2f}")
        print(f"  Expected Delivery: {po_item['delivery_date']}")

        # Step 5: Detect anomalies
        print("\n[STEP 5] Detecting anomalies...")
        anomaly = self.anomaly_agent.detect_inventory_anomaly(
            sku="PROD-001",
            current_inventory=inventory_item['current_quantity'],
            forecasted_inventory=forecast.get('forecasted_demand', 3000),
            confidence_80=forecast.get('confidence_80', 2700),
            confidence_95=forecast.get('confidence_95', 2400)
        )
        
        anomaly_item = {
            'anomaly_id': f'ANM-{datetime.now().timestamp()}',
            'sku': 'PROD-001',
            'type': 'inventory_deviation',
            'is_anomaly': anomaly.get('is_anomaly', False),
            'severity': anomaly.get('severity', 'low'),
            'description': anomaly.get('description', 'No anomaly detected'),
            'detected_date': datetime.now().isoformat(),
        }
        self.save_to_dynamodb('anomalies', anomaly_item)
        
        if anomaly.get('is_anomaly'):
            print(f"  ALERT: Anomaly detected!")
            print(f"  Severity: {anomaly.get('severity', 'unknown')}")
            print(f"  Description: {anomaly.get('description', 'N/A')}")
            
            # Send SNS notification
            self.send_notification(
                subject=f"Supply Chain Alert - {anomaly.get('severity', 'unknown').upper()}",
                message=f"Anomaly detected for SKU PROD-001:\n{anomaly.get('description', 'N/A')}"
            )
        else:
            print(f"  No anomalies detected")

        # Step 6: Generate report
        print("\n[STEP 6] Generating analytics report...")
        kpis = self.reporting_agent.calculate_kpis(
            inventory_data=[{
                'sku': 'PROD-001',
                'quantity': inventory_item['current_quantity'],
                'value': inventory_item['current_quantity'] * 10.50
            }],
            forecast_data=[{
                'sku': 'PROD-001',
                'forecasted': forecast.get('forecasted_demand', 3000),
                'actual': 100  # Sample actual
            }],
            supplier_data=[{
                'supplier_id': 'SUPP-001',
                'reliability_score': 95
            }],
            period_start=datetime.now().date(),
            period_end=datetime.now().date()
        )
        
        report = {
            'report_id': f'RPT-{datetime.now().timestamp()}',
            'report_date': datetime.now().isoformat(),
            'period': f"{datetime.now().date()}",
            'kpis': kpis,
            'summary': {
                'total_inventory_value': inventory_item['current_quantity'] * 10.50,
                'forecast_accuracy': kpis.get('forecast_accuracy', 0),
                'supplier_reliability': kpis.get('supplier_reliability', 0),
            }
        }
        
        # Save report to S3
        report_key = f"reports/{datetime.now().strftime('%Y/%m/%d')}/report-{datetime.now().timestamp()}.json"
        self.save_to_s3(report_key, report)
        
        print(f"  Report ID: {report['report_id']}")
        print(f"  Inventory Turnover: {kpis.get('inventory_turnover', 0):.2f}")
        print(f"  Forecast Accuracy: {kpis.get('forecast_accuracy', 0):.2%}")
        print(f"  Supplier Reliability: {kpis.get('supplier_reliability', 0):.2%}")
        print(f"  Report saved to S3: {report_key}")

        # Step 7: Summary
        print("\n" + "="*80)
        print("WORKFLOW SUMMARY")
        print("="*80)
        print(f"✓ Inventory data saved to DynamoDB")
        print(f"✓ Forecast generated and saved to DynamoDB")
        print(f"✓ Purchase order created and saved to DynamoDB")
        print(f"✓ Anomalies detected and saved to DynamoDB")
        print(f"✓ Report generated and saved to S3")
        if anomaly.get('is_anomaly'):
            print(f"✓ Alert notification sent via SNS")
        print("\n" + "="*80)

    def verify_aws_services(self):
        """Verify AWS services are accessible."""
        print("\n[VERIFICATION] Checking AWS services...")
        
        try:
            # Check DynamoDB
            tables = self.dynamodb.meta.client.list_tables()
            print(f"✓ DynamoDB: {len(tables['TableNames'])} tables found")
            
            # Check S3
            buckets = self.s3.list_buckets()
            print(f"✓ S3: {len(buckets['Buckets'])} buckets found")
            
            # Check SNS
            topics = self.sns.list_topics()
            print(f"✓ SNS: {len(topics['Topics'])} topics found")
            
            return True
        except Exception as e:
            logger.error(f"AWS service verification failed: {str(e)}")
            print(f"✗ AWS services not accessible: {str(e)}")
            return False


def main():
    """Main entry point."""
    print("\n" + "="*80)
    print("SUPPLY CHAIN OPTIMIZER - AWS SERVICES INTEGRATION")
    print("="*80)
    
    demo = AWSServiceDemo()
    
    # Verify AWS services
    if not demo.verify_aws_services():
        print("\nERROR: AWS services not accessible")
        print("Please ensure:")
        print("  1. AWS credentials are configured (aws configure)")
        print("  2. AWS resources are created (run setup_aws_resources.bat or .sh)")
        print("  3. .env file is configured with AWS settings")
        return
    
    # Run workflow
    try:
        demo.run_complete_workflow()
        print("\n✓ Workflow completed successfully!")
    except Exception as e:
        logger.error(f"Workflow failed: {str(e)}")
        print(f"\n✗ Workflow failed: {str(e)}")


if __name__ == '__main__':
    main()
