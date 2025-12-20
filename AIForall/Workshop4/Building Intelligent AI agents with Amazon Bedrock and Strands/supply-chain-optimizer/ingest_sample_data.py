#!/usr/bin/env python3
"""
Sample Data Ingestion Script

This script ingests sample supply chain data into DynamoDB.
Run this to populate the database with test data.
"""

import json
from datetime import datetime, timedelta
from src.aws.clients import get_dynamodb_resource
from src.config import logger


def create_sample_inventory():
    """Create sample inventory data."""
    return [
        {
            'sku': 'PROD-001',
            'product_name': 'Widget A',
            'current_quantity': 1500,
            'reorder_point': 200,
            'safety_stock': 300,
            'warehouse': 'WH-001',
            'lead_time_days': 7,
            'ordering_cost': 50,
            'holding_cost_per_unit': 2,
            'unit_price': 10.50,
            'category': 'Electronics',
            'last_updated': datetime.now().isoformat(),
        },
        {
            'sku': 'PROD-002',
            'product_name': 'Widget B',
            'current_quantity': 800,
            'reorder_point': 150,
            'safety_stock': 250,
            'warehouse': 'WH-002',
            'lead_time_days': 5,
            'ordering_cost': 40,
            'holding_cost_per_unit': 1.5,
            'unit_price': 15.75,
            'category': 'Electronics',
            'last_updated': datetime.now().isoformat(),
        },
        {
            'sku': 'PROD-003',
            'product_name': 'Gadget X',
            'current_quantity': 2000,
            'reorder_point': 300,
            'safety_stock': 400,
            'warehouse': 'WH-001',
            'lead_time_days': 10,
            'ordering_cost': 60,
            'holding_cost_per_unit': 3,
            'unit_price': 25.00,
            'category': 'Hardware',
            'last_updated': datetime.now().isoformat(),
        },
    ]


def create_sample_sales_history():
    """Create sample sales history data."""
    sales_data = []
    base_date = datetime.now()
    
    for sku in ['PROD-001', 'PROD-002', 'PROD-003']:
        for i in range(12):
            date = (base_date - timedelta(days=30*i)).strftime('%Y-%m-%d')
            quantity = 100 + (i * 5) + (hash(sku) % 50)
            
            sales_data.append({
                'sku': sku,
                'date': date,
                'quantity': quantity,
                'revenue': quantity * (10.50 if sku == 'PROD-001' else 15.75 if sku == 'PROD-002' else 25.00),
                'warehouse': 'WH-001' if sku in ['PROD-001', 'PROD-003'] else 'WH-002',
            })
    
    return sales_data


def create_sample_suppliers():
    """Create sample supplier data."""
    return [
        {
            'supplier_id': 'SUPP-001',
            'name': 'Global Supplies Inc',
            'contact_email': 'contact@globalsupplies.com',
            'contact_phone': '+1-555-0101',
            'unit_price': 10.50,
            'reliability_score': 0.95,
            'lead_time_days': 7,
            'min_order_quantity': 100,
            'payment_terms': 'Net 30',
            'location': 'USA',
            'rating': 4.8,
        },
        {
            'supplier_id': 'SUPP-002',
            'name': 'Asia Trade Partners',
            'contact_email': 'sales@asiatrade.com',
            'contact_phone': '+86-10-1234-5678',
            'unit_price': 9.75,
            'reliability_score': 0.88,
            'lead_time_days': 14,
            'min_order_quantity': 500,
            'payment_terms': 'Net 45',
            'location': 'China',
            'rating': 4.5,
        },
        {
            'supplier_id': 'SUPP-003',
            'name': 'European Distributors',
            'contact_email': 'info@eudist.eu',
            'contact_phone': '+49-30-1234-5678',
            'unit_price': 11.25,
            'reliability_score': 0.92,
            'lead_time_days': 5,
            'min_order_quantity': 200,
            'payment_terms': 'Net 30',
            'location': 'Germany',
            'rating': 4.7,
        },
    ]


def ingest_data_to_dynamodb():
    """Ingest all sample data to DynamoDB."""
    try:
        dynamodb = get_dynamodb_resource()
        
        print("\n" + "="*70)
        print("  INGESTING SAMPLE DATA TO DYNAMODB")
        print("="*70 + "\n")
        
        # Ingest inventory
        print("📦 Ingesting inventory data...")
        inventory_table = dynamodb.Table('inventory')
        inventory_data = create_sample_inventory()
        
        for item in inventory_data:
            inventory_table.put_item(Item=item)
            print(f"   ✓ Ingested: {item['sku']} - {item['product_name']}")
        
        print(f"   Total: {len(inventory_data)} items\n")
        
        # Ingest sales history
        print("📊 Ingesting sales history...")
        sales_table = dynamodb.Table('sales_history')
        sales_data = create_sample_sales_history()
        
        for item in sales_data:
            sales_table.put_item(Item=item)
        
        print(f"   ✓ Ingested {len(sales_data)} sales records")
        print(f"   SKUs: PROD-001, PROD-002, PROD-003")
        print(f"   Period: Last 12 months\n")
        
        # Ingest suppliers
        print("🏭 Ingesting supplier data...")
        suppliers_table = dynamodb.Table('suppliers')
        supplier_data = create_sample_suppliers()
        
        for item in supplier_data:
            suppliers_table.put_item(Item=item)
            print(f"   ✓ Ingested: {item['supplier_id']} - {item['name']}")
        
        print(f"   Total: {len(supplier_data)} suppliers\n")
        
        print("="*70)
        print("✓ DATA INGESTION COMPLETE")
        print("="*70)
        print("\nSummary:")
        print(f"  • Inventory items: {len(inventory_data)}")
        print(f"  • Sales records: {len(sales_data)}")
        print(f"  • Suppliers: {len(supplier_data)}")
        print("\nYou can now use the agent tools with this data!")
        print("="*70 + "\n")
        
        return True
    except Exception as e:
        logger.error(f"Failed to ingest data: {str(e)}")
        print(f"\n✗ Error: {str(e)}\n")
        return False


def verify_data_in_dynamodb():
    """Verify that data was ingested correctly."""
    try:
        dynamodb = get_dynamodb_resource()
        
        print("\n" + "="*70)
        print("  VERIFYING DATA IN DYNAMODB")
        print("="*70 + "\n")
        
        # Check inventory
        print("📦 Checking inventory table...")
        inventory_table = dynamodb.Table('inventory')
        response = inventory_table.scan()
        inventory_count = response['Count']
        print(f"   ✓ Found {inventory_count} inventory items")
        
        # Check sales history
        print("📊 Checking sales_history table...")
        sales_table = dynamodb.Table('sales_history')
        response = sales_table.scan()
        sales_count = response['Count']
        print(f"   ✓ Found {sales_count} sales records")
        
        # Check suppliers
        print("🏭 Checking suppliers table...")
        suppliers_table = dynamodb.Table('suppliers')
        response = suppliers_table.scan()
        suppliers_count = response['Count']
        print(f"   ✓ Found {suppliers_count} suppliers")
        
        print("\n" + "="*70)
        print("✓ VERIFICATION COMPLETE")
        print("="*70 + "\n")
        
        return True
    except Exception as e:
        logger.error(f"Failed to verify data: {str(e)}")
        print(f"\n✗ Error: {str(e)}\n")
        return False


if __name__ == "__main__":
    import sys
    
    print("\n" + "="*70)
    print("  SUPPLY CHAIN OPTIMIZER - DATA INGESTION")
    print("="*70)
    
    # Ingest data
    success = ingest_data_to_dynamodb()
    
    if success:
        # Verify data
        verify_data_in_dynamodb()
        sys.exit(0)
    else:
        print("\n✗ Data ingestion failed")
        sys.exit(1)
