"""
Supply Chain Optimizer Agents as Tools

Wraps all agents as tools that can be used by a Strands Agent.
These tools read from and write to DynamoDB for data persistence.
Integrates with Bedrock Knowledge Base for data ingestion.
"""

import os
from strands import tool
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
import json

from src.agents.demand_forecasting_agent import DemandForecastingAgent
from src.agents.inventory_optimizer_agent import InventoryOptimizerAgent
from src.agents.supplier_coordination_agent import SupplierCoordinationAgent
from src.agents.anomaly_detection_agent import AnomalyDetectionAgent
from src.agents.report_generation_agent import ReportGenerationAgent
from src.agents.knowledge_base_manager import KnowledgeBaseManager
from src.aws.clients import get_dynamodb_resource, get_s3_client, get_sns_client
from src.config import logger, config

# Suppress warnings
import warnings
warnings.filterwarnings("ignore")


# Initialize agents
forecasting_agent = DemandForecastingAgent()
inventory_agent = InventoryOptimizerAgent()
supplier_agent = SupplierCoordinationAgent()
anomaly_agent = AnomalyDetectionAgent()
reporting_agent = ReportGenerationAgent()

# Initialize AWS clients
dynamodb = get_dynamodb_resource()
s3_client = get_s3_client()
sns_client = get_sns_client()

# Initialize Knowledge Base Manager (if KB ID is provided)
kb_manager = None
kb_id = os.getenv("BEDROCK_KB_ID")
if kb_id:
    try:
        kb_manager = KnowledgeBaseManager(kb_id)
        logger.info(f"Knowledge Base Manager initialized with KB ID: {kb_id}")
    except Exception as e:
        logger.warning(f"Could not initialize Knowledge Base Manager: {str(e)}")
else:
    logger.info("No BEDROCK_KB_ID provided, Knowledge Base features disabled")


# ============================================================================
# DynamoDB Helper Functions
# ============================================================================

def get_inventory_from_dynamodb(sku: str) -> Optional[Dict[str, Any]]:
    """Get inventory data from DynamoDB."""
    try:
        table = dynamodb.Table('inventory')
        response = table.scan(
            FilterExpression='#s = :sku',
            ExpressionAttributeNames={'#s': 'sku'},
            ExpressionAttributeValues={':sku': sku}
        )
        items = response.get('Items', [])
        return items[0] if items else None
    except Exception as e:
        logger.warning(f"Could not get inventory from DynamoDB for {sku}: {str(e)}")
        return None


def get_sales_history_from_dynamodb(sku: str) -> List[Dict[str, Any]]:
    """Get sales history from DynamoDB."""
    try:
        table = dynamodb.Table('sales_history')
        response = table.scan(
            FilterExpression='#s = :sku',
            ExpressionAttributeNames={'#s': 'sku'},
            ExpressionAttributeValues={':sku': sku}
        )
        items = response.get('Items', [])
        # Sort by date
        items.sort(key=lambda x: x.get('date', ''))
        return items
    except Exception as e:
        logger.warning(f"Could not get sales history from DynamoDB for {sku}: {str(e)}")
        return []


def get_supplier_from_dynamodb(supplier_id: str) -> Optional[Dict[str, Any]]:
    """Get supplier data from DynamoDB."""
    try:
        table = dynamodb.Table('suppliers')
        response = table.get_item(Key={'supplier_id': supplier_id})
        return response.get('Item')
    except Exception as e:
        logger.warning(f"Could not get supplier from DynamoDB: {str(e)}")
        return None


def save_to_dynamodb(table_name: str, item: Dict[str, Any]) -> bool:
    """Save item to DynamoDB."""
    try:
        table = dynamodb.Table(table_name)
        table.put_item(Item=item)
        logger.info(f"Saved to DynamoDB table '{table_name}'")
        return True
    except Exception as e:
        logger.warning(f"Could not save to DynamoDB table '{table_name}': {str(e)}")
        return False


def query_dynamodb(table_name: str, key_condition: str, expression_values: Dict) -> List[Dict[str, Any]]:
    """Query DynamoDB table."""
    try:
        table = dynamodb.Table(table_name)
        response = table.scan(
            FilterExpression=key_condition,
            ExpressionAttributeValues=expression_values
        )
        return response.get('Items', [])
    except Exception as e:
        logger.warning(f"Could not query DynamoDB table '{table_name}': {str(e)}")
        return []


@tool
def forecast_demand(sku: str, forecast_days: int = 30) -> Dict[str, Any]:
    """
    Generate demand forecast for a product using sales history from DynamoDB.
    
    Args:
        sku: Product SKU (e.g., 'PROD-001')
        forecast_days: Number of days to forecast (default: 30)
    
    Returns:
        Forecast with forecasted_demand, confidence_80, confidence_95
    
    Example:
        forecast_demand(sku='PROD-001', forecast_days=30)
    """
    try:
        logger.info(f"Forecasting demand for SKU: {sku}")
        
        # Get sales history from DynamoDB
        sales_data = get_sales_history_from_dynamodb(sku)
        
        if not sales_data:
            logger.warning(f"No sales history found for SKU: {sku}, using default forecast")
            return {
                'status': 'success',
                'sku': sku,
                'forecasted_demand': 1000,
                'confidence_80': 950,
                'confidence_95': 900,
                'message': f'Default forecast generated for {sku} (no historical data)'
            }
        
        # Analyze sales history
        analysis = forecasting_agent.analyze_sales_history(
            sku=sku,
            sales_data=sales_data
        )
        
        # Generate forecast
        forecast = forecasting_agent.generate_forecast(
            sku=sku,
            sales_analysis=analysis,
            forecast_period=forecast_days
        )
        
        # Save to DynamoDB
        forecast_item = {
            'forecast_id': f'FCST-{datetime.now().timestamp()}',
            'sku': sku,
            'forecasted_demand': forecast.get('forecasted_demand', 0),
            'confidence_80': forecast.get('confidence_80', 0),
            'confidence_95': forecast.get('confidence_95', 0),
            'forecast_date': datetime.now().isoformat(),
            'forecast_period_days': forecast_days,
        }
        
        save_to_dynamodb('forecasts', forecast_item)
        
        return {
            'status': 'success',
            'forecast_id': forecast_item['forecast_id'],
            'sku': sku,
            'forecasted_demand': forecast.get('forecasted_demand', 0),
            'confidence_80': forecast.get('confidence_80', 0),
            'confidence_95': forecast.get('confidence_95', 0),
            'message': f'Forecast generated for {sku}: {forecast.get("forecasted_demand", 0):.0f} units'
        }
    except Exception as e:
        logger.error(f"Forecast demand failed: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@tool
def optimize_inventory(sku: str) -> Dict[str, Any]:
    """
    Optimize inventory levels for a product using data from DynamoDB.
    
    Args:
        sku: Product SKU
    
    Returns:
        EOQ, reorder point, and optimization recommendations
    
    Example:
        optimize_inventory(sku='PROD-001')
    """
    try:
        logger.info(f"Optimizing inventory for SKU: {sku}")
        
        # Get inventory data from DynamoDB
        inventory = get_inventory_from_dynamodb(sku)
        if not inventory:
            logger.warning(f"No inventory found for SKU: {sku}, using defaults")
            return {
                'status': 'success',
                'sku': sku,
                'eoq': 500,
                'reorder_point': 200,
                'annual_demand': 6000,
                'current_inventory': 0,
                'ordering_cost': 50,
                'holding_cost_per_unit': 2,
                'message': f'Default optimization for {sku} (no inventory data)'
            }
        
        # Get sales history to calculate annual demand
        sales_data = get_sales_history_from_dynamodb(sku)
        if not sales_data:
            logger.warning(f"No sales history found for SKU: {sku}, using default demand")
            annual_demand = 6000
        else:
            # Calculate annual demand from sales data
            total_quantity = sum(item.get('quantity', 0) for item in sales_data)
            annual_demand = total_quantity * (365 / len(sales_data)) if sales_data else 6000
        
        # Default costs (can be stored in DynamoDB too)
        ordering_cost = inventory.get('ordering_cost', 50)
        holding_cost_per_unit = inventory.get('holding_cost_per_unit', 2)
        
        # Calculate EOQ
        eoq = inventory_agent.calculate_eoq(
            annual_demand=annual_demand,
            ordering_cost=ordering_cost,
            holding_cost_per_unit=holding_cost_per_unit
        )
        
        # Calculate reorder point
        avg_daily_demand = annual_demand / 365
        reorder_point = inventory_agent.calculate_reorder_point(
            average_daily_demand=avg_daily_demand,
            lead_time_days=inventory.get('lead_time_days', 7),
            safety_stock=inventory.get('safety_stock', 200)
        )
        
        return {
            'status': 'success',
            'sku': sku,
            'eoq': round(eoq, 2),
            'reorder_point': round(reorder_point, 2),
            'annual_demand': round(annual_demand, 2),
            'current_inventory': inventory.get('current_quantity', 0),
            'ordering_cost': ordering_cost,
            'holding_cost_per_unit': holding_cost_per_unit,
            'message': f'Optimal order quantity: {eoq:.0f} units, Reorder at: {reorder_point:.0f} units'
        }
    except Exception as e:
        logger.error(f"Optimize inventory failed: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@tool
def create_purchase_order(sku: str, supplier_id: str, quantity: int, delivery_days: int = 7) -> Dict[str, Any]:
    """
    Create a purchase order with a supplier using data from DynamoDB.
    
    Args:
        sku: Product SKU
        supplier_id: Supplier ID
        quantity: Order quantity
        delivery_days: Expected delivery in days (default: 7)
    
    Returns:
        Purchase order details
    
    Example:
        create_purchase_order(
            sku='PROD-001',
            supplier_id='SUPP-001',
            quantity=1500,
            delivery_days=7
        )
    """
    try:
        logger.info(f"Creating purchase order for SKU: {sku}")
        
        # Get supplier data from DynamoDB
        supplier = get_supplier_from_dynamodb(supplier_id)
        if not supplier:
            logger.warning(f"Supplier not found: {supplier_id}, using default price")
            unit_price = 10.50
            supplier_name = "Unknown Supplier"
        else:
            unit_price = supplier.get('unit_price', 10.50)
            supplier_name = supplier.get('name', 'Unknown')
        
        po_item = {
            'po_id': f'PO-{datetime.now().timestamp()}',
            'sku': sku,
            'supplier_id': supplier_id,
            'quantity': quantity,
            'unit_price': unit_price,
            'total_price': quantity * unit_price,
            'delivery_date': (datetime.now() + timedelta(days=delivery_days)).isoformat(),
            'status': 'pending',
            'created_date': datetime.now().isoformat(),
        }
        
        # Save to DynamoDB
        save_to_dynamodb('purchase_orders', po_item)
        
        return {
            'status': 'success',
            'po_id': po_item['po_id'],
            'sku': sku,
            'supplier_id': supplier_id,
            'supplier_name': supplier_name,
            'quantity': quantity,
            'unit_price': unit_price,
            'total_price': po_item['total_price'],
            'delivery_date': po_item['delivery_date'],
            'message': f'Purchase order created: {po_item["po_id"]} for {quantity} units'
        }
    except Exception as e:
        logger.error(f"Create purchase order failed: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@tool
def detect_anomalies(sku: str) -> Dict[str, Any]:
    """
    Detect anomalies in inventory or supply chain using data from DynamoDB.
    
    Args:
        sku: Product SKU
    
    Returns:
        Anomaly detection results with severity and recommendations
    
    Example:
        detect_anomalies(sku='PROD-001')
    """
    try:
        logger.info(f"Detecting anomalies for SKU: {sku}")
        
        # Get inventory data from DynamoDB
        inventory = get_inventory_from_dynamodb(sku)
        if not inventory:
            logger.warning(f"No inventory found for SKU: {sku}, skipping anomaly detection")
            return {
                'status': 'success',
                'sku': sku,
                'is_anomaly': False,
                'severity': 'low',
                'description': 'No inventory data available for anomaly detection',
                'message': f'No anomaly detected for {sku} (no data)'
            }
        
        # Get latest forecast from DynamoDB
        forecasts = query_dynamodb(
            'forecasts',
            '#s = :sku',
            {':sku': sku}
        )
        
        if not forecasts:
            logger.warning(f"No forecast found for SKU: {sku}, using default")
            latest_forecast = {
                'forecasted_demand': 1000,
                'confidence_80': 950,
                'confidence_95': 900
            }
        else:
            # Use latest forecast
            latest_forecast = sorted(forecasts, key=lambda x: x.get('forecast_date', ''))[-1]
        
        # Detect anomaly
        anomaly = anomaly_agent.detect_inventory_anomaly(
            sku=sku,
            current_inventory=inventory.get('current_quantity', 0),
            forecasted_inventory=latest_forecast.get('forecasted_demand', 0),
            confidence_80=latest_forecast.get('confidence_80', 0),
            confidence_95=latest_forecast.get('confidence_95', 0)
        )
        
        # Save to DynamoDB
        anomaly_item = {
            'anomaly_id': f'ANM-{datetime.now().timestamp()}',
            'sku': sku,
            'type': 'inventory_deviation',
            'is_anomaly': anomaly.get('is_anomaly', False),
            'severity': anomaly.get('severity', 'low'),
            'description': anomaly.get('description', 'No anomaly detected'),
            'detected_date': datetime.now().isoformat(),
        }
        
        save_to_dynamodb('anomalies', anomaly_item)
        
        # Send SNS alert if anomaly detected
        if anomaly.get('is_anomaly'):
            try:
                sns_client.publish(
                    TopicArn=config.sns.topic_arn_alerts,
                    Subject=f"Supply Chain Alert - {anomaly.get('severity', 'unknown').upper()}",
                    Message=f"Anomaly detected for SKU {sku}:\n{anomaly.get('description', 'N/A')}"
                )
            except Exception as e:
                logger.warning(f"Failed to send SNS alert: {str(e)}")
        
        return {
            'status': 'success',
            'anomaly_id': anomaly_item['anomaly_id'],
            'sku': sku,
            'is_anomaly': anomaly.get('is_anomaly', False),
            'severity': anomaly.get('severity', 'low'),
            'description': anomaly.get('description', 'No anomaly detected'),
            'message': f'Anomaly detection complete for {sku}: {anomaly.get("description", "No anomaly")}'
        }
    except Exception as e:
        logger.error(f"Detect anomalies failed: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@tool
def generate_report(sku: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate analytics report with KPIs using data from DynamoDB.
    
    Args:
        sku: Optional product SKU. If provided, generates report for that product.
             If not provided, generates report for all products.
    
    Returns:
        Report with KPIs and recommendations
    
    Example:
        generate_report(sku='PROD-001')
        generate_report()  # All products
    """
    try:
        logger.info("Generating analytics report")
        
        # Get inventory data from DynamoDB
        if sku:
            inventory_item = get_inventory_from_dynamodb(sku)
            inventory_data = [inventory_item] if inventory_item else []
        else:
            inventory_data = query_dynamodb('inventory', 'attribute_exists(sku)', {})
        
        if not inventory_data:
            logger.warning("No inventory data found, generating default report")
            inventory_data = []
        
        # Get forecast data from DynamoDB
        forecast_data = query_dynamodb('forecasts', 'attribute_exists(sku)', {})
        
        # Get supplier data from DynamoDB
        supplier_data = query_dynamodb('suppliers', 'attribute_exists(supplier_id)', {})
        
        # Calculate KPIs
        kpis = reporting_agent.calculate_kpis(
            inventory_data=inventory_data,
            forecast_data=forecast_data,
            supplier_data=supplier_data,
            period_start=date.today(),
            period_end=date.today()
        )
        
        # Create report
        report = {
            'report_id': f'RPT-{datetime.now().timestamp()}',
            'report_date': datetime.now().isoformat(),
            'period': str(date.today()),
            'sku_filter': sku or 'all',
            'kpis': kpis,
            'summary': {
                'total_inventory_value': sum(item.get('value', 0) for item in inventory_data),
                'total_items': len(inventory_data),
                'forecast_accuracy': kpis.get('forecast_accuracy', 0),
                'supplier_reliability': kpis.get('supplier_reliability', 0),
            }
        }
        
        # Save to S3
        try:
            report_key = f"reports/{datetime.now().strftime('%Y/%m/%d')}/report-{datetime.now().timestamp()}.json"
            s3_client.put_object(
                Bucket=config.s3.bucket_name,
                Key=report_key,
                Body=json.dumps(report, indent=2, default=str),
                ContentType='application/json'
            )
            report_location = f's3://{config.s3.bucket_name}/{report_key}'
        except Exception as e:
            logger.warning(f"Could not save report to S3: {str(e)}")
            report_location = "S3 save failed"
        
        return {
            'status': 'success',
            'report_id': report['report_id'],
            'kpis': kpis,
            'inventory_turnover': kpis.get('inventory_turnover', 0),
            'forecast_accuracy': kpis.get('forecast_accuracy', 0),
            'supplier_reliability': kpis.get('supplier_reliability', 0),
            'report_location': report_location,
            'message': f'Report generated: {report["report_id"]}'
        }
    except Exception as e:
        logger.error(f"Generate report failed: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@tool
def get_inventory_status(sku: str) -> Dict[str, Any]:
    """
    Get current inventory status for a product.
    
    Args:
        sku: Product SKU
    
    Returns:
        Current inventory details
    
    Example:
        get_inventory_status(sku='PROD-001')
    """
    try:
        logger.info(f"Getting inventory status for SKU: {sku}")
        
        table = dynamodb.Table('inventory')
        response = table.scan(
            FilterExpression='sku = :sku',
            ExpressionAttributeValues={':sku': sku}
        )
        
        items = response.get('Items', [])
        
        if items:
            item = items[0]
            return {
                'status': 'success',
                'sku': sku,
                'current_quantity': item.get('current_quantity', 0),
                'reorder_point': item.get('reorder_point', 0),
                'safety_stock': item.get('safety_stock', 0),
                'warehouse': item.get('warehouse', 'N/A'),
                'message': f'Inventory for {sku}: {item.get("current_quantity", 0)} units'
            }
        else:
            return {
                'status': 'not_found',
                'sku': sku,
                'message': f'No inventory found for SKU: {sku}'
            }
    except Exception as e:
        logger.error(f"Get inventory status failed: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@tool
def sync_data_from_knowledge_base() -> Dict[str, Any]:
    """
    Sync all data from Bedrock Knowledge Base to DynamoDB.
    
    This tool retrieves data from the knowledge base and stores it in DynamoDB
    for use by other tools.
    
    Returns:
        Sync status for each data type
    
    Example:
        sync_data_from_knowledge_base()
    """
    try:
        if not kb_manager:
            return {
                'status': 'error',
                'message': 'Knowledge Base not configured. Set BEDROCK_KB_ID environment variable.'
            }
        
        logger.info("Syncing data from knowledge base to DynamoDB")
        
        # Sync all data types
        results = kb_manager.sync_all_data()
        
        return {
            'status': 'success',
            'inventory_synced': results.get('inventory', False),
            'sales_history_synced': results.get('sales_history', False),
            'suppliers_synced': results.get('suppliers', False),
            'message': f'Data sync complete: {results}'
        }
    except Exception as e:
        logger.error(f"Sync data from knowledge base failed: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@tool
def retrieve_from_knowledge_base(query: str, data_type: str = "inventory") -> Dict[str, Any]:
    """
    Retrieve specific data from Bedrock Knowledge Base.
    
    Args:
        query: Search query
        data_type: Type of data to retrieve (inventory, sales_history, suppliers)
    
    Returns:
        Retrieved data and storage status
    
    Example:
        retrieve_from_knowledge_base(query="PROD-001", data_type="inventory")
    """
    try:
        if not kb_manager:
            return {
                'status': 'error',
                'message': 'Knowledge Base not configured. Set BEDROCK_KB_ID environment variable.'
            }
        
        logger.info(f"Retrieving {data_type} from knowledge base: {query}")
        
        # Retrieve from knowledge base
        results = kb_manager.retrieve_from_knowledge_base(query, max_results=5)
        
        if not results:
            return {
                'status': 'not_found',
                'query': query,
                'data_type': data_type,
                'message': f'No {data_type} found for query: {query}'
            }
        
        # Store retrieved data
        stored_count = 0
        if data_type == "inventory":
            stored_count = len([r for r in results if kb_manager.ingest_inventory_data([json.loads(r.get('content', '{}'))])])
        elif data_type == "sales_history":
            stored_count = len([r for r in results if kb_manager.ingest_sales_history([json.loads(r.get('content', '{}'))])])
        elif data_type == "suppliers":
            stored_count = len([r for r in results if kb_manager.ingest_supplier_data([json.loads(r.get('content', '{}'))])])
        
        return {
            'status': 'success',
            'query': query,
            'data_type': data_type,
            'results_found': len(results),
            'results_stored': stored_count,
            'message': f'Retrieved and stored {stored_count} {data_type} records'
        }
    except Exception as e:
        logger.error(f"Retrieve from knowledge base failed: {str(e)}")
        return {'status': 'error', 'message': str(e)}


# Export all tools
__all__ = [
    'forecast_demand',
    'optimize_inventory',
    'create_purchase_order',
    'detect_anomalies',
    'generate_report',
    'get_inventory_status',
    'sync_data_from_knowledge_base',
    'retrieve_from_knowledge_base',
]
