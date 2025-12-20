"""Test DynamoDB connection and basic operations."""

import json
from datetime import datetime
from src.aws.clients import get_dynamodb_resource
from src.config import logger


def test_dynamodb_connection():
    """Test DynamoDB connection."""
    try:
        dynamodb = get_dynamodb_resource()
        logger.info("DynamoDB resource obtained successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to get DynamoDB resource: {str(e)}")
        return False


def test_dynamodb_write_read():
    """Test DynamoDB write and read operations."""
    try:
        dynamodb = get_dynamodb_resource()
        
        # Test with forecasts table
        table_name = 'forecasts'
        table = dynamodb.Table(table_name)
        
        # Write test item
        test_item = {
            'forecast_id': f'TEST-{datetime.now().timestamp()}',
            'sku': 'PROD-TEST-001',
            'forecasted_demand': 1000,
            'confidence_80': 950,
            'confidence_95': 900,
            'forecast_date': datetime.now().isoformat(),
            'forecast_period_days': 30,
        }
        
        logger.info(f"Writing test item to {table_name}: {test_item['forecast_id']}")
        table.put_item(Item=test_item)
        logger.info("Write successful")
        
        # Read test item
        response = table.get_item(Key={'forecast_id': test_item['forecast_id']})
        
        if 'Item' in response:
            logger.info(f"Read successful: {response['Item']}")
            return True
        else:
            logger.error("Item not found after write")
            return False
            
    except Exception as e:
        logger.error(f"DynamoDB write/read test failed: {str(e)}")
        return False


def test_dynamodb_scan():
    """Test DynamoDB scan operation."""
    try:
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table('forecasts')
        
        logger.info("Scanning forecasts table...")
        response = table.scan(Limit=5)
        
        item_count = len(response.get('Items', []))
        logger.info(f"Scan successful. Found {item_count} items")
        
        if item_count > 0:
            logger.info(f"Sample item: {response['Items'][0]}")
        
        return True
        
    except Exception as e:
        logger.error(f"DynamoDB scan test failed: {str(e)}")
        return False


def test_all_dynamodb_tables():
    """Test connection to all DynamoDB tables."""
    try:
        dynamodb = get_dynamodb_resource()
        
        tables = [
            'forecasts',
            'inventory',
            'anomalies',
            'purchase_orders',
            'suppliers',
        ]
        
        results = {}
        for table_name in tables:
            try:
                table = dynamodb.Table(table_name)
                # Try to get table description
                table.load()
                results[table_name] = 'OK'
                logger.info(f"Table {table_name}: OK")
            except Exception as e:
                results[table_name] = f'FAILED: {str(e)}'
                logger.error(f"Table {table_name}: FAILED - {str(e)}")
        
        all_ok = all(v == 'OK' for v in results.values())
        return all_ok, results
        
    except Exception as e:
        logger.error(f"Failed to test DynamoDB tables: {str(e)}")
        return False, {}


if __name__ == '__main__':
    print("\n" + "="*60)
    print("DynamoDB Connection Tests")
    print("="*60 + "\n")
    
    # Test 1: Connection
    print("[1/4] Testing DynamoDB connection...")
    if test_dynamodb_connection():
        print("PASS: DynamoDB connection successful\n")
    else:
        print("FAIL: DynamoDB connection failed\n")
        exit(1)
    
    # Test 2: Write/Read
    print("[2/4] Testing DynamoDB write/read operations...")
    if test_dynamodb_write_read():
        print("PASS: DynamoDB write/read successful\n")
    else:
        print("FAIL: DynamoDB write/read failed\n")
        exit(1)
    
    # Test 3: Scan
    print("[3/4] Testing DynamoDB scan operation...")
    if test_dynamodb_scan():
        print("PASS: DynamoDB scan successful\n")
    else:
        print("FAIL: DynamoDB scan failed\n")
        exit(1)
    
    # Test 4: All tables
    print("[4/4] Testing all DynamoDB tables...")
    all_ok, results = test_all_dynamodb_tables()
    print("\nTable Status:")
    for table, status in results.items():
        print(f"  {table}: {status}")
    
    if all_ok:
        print("\nPASS: All DynamoDB tables accessible\n")
    else:
        print("\nFAIL: Some DynamoDB tables not accessible\n")
        exit(1)
    
    print("="*60)
    print("All DynamoDB tests PASSED!")
    print("="*60)
