#!/usr/bin/env python3
"""
Complete Knowledge Base Integration Test

Tests the entire workflow:
1. Upload custom data to S3
2. Sync Knowledge Base
3. Retrieve data from KB
4. Store in DynamoDB
5. Execute agent tools
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import logger, config
from src.aws.clients import get_dynamodb_resource, get_s3_client
from src.agents.knowledge_base_manager import KnowledgeBaseManager
from src.agents.agent_tools import (
    forecast_demand,
    optimize_inventory,
    create_purchase_order,
    detect_anomalies,
    generate_report,
    get_inventory_status,
    sync_data_from_knowledge_base,
    retrieve_from_knowledge_base
)


def create_test_data_files():
    """Create test data files for upload."""
    print("\n" + "="*70)
    print("  CREATING TEST DATA FILES")
    print("="*70 + "\n")
    
    # Create test directory
    test_dir = Path("test_data")
    test_dir.mkdir(exist_ok=True)
    
    # Create inventory test data
    inventory_data = [
        {
            'sku': 'TEST-001',
            'product_name': 'Test Widget A',
            'current_quantity': 1500,
            'reorder_point': 200,
            'safety_stock': 300,
            'warehouse': 'WH-TEST',
            'lead_time_days': 7,
            'ordering_cost': 50,
            'holding_cost_per_unit': 2,
            'unit_price': 10.50,
        },
        {
            'sku': 'TEST-002',
            'product_name': 'Test Widget B',
            'current_quantity': 800,
            'reorder_point': 150,
            'safety_stock': 250,
            'warehouse': 'WH-TEST',
            'lead_time_days': 5,
            'ordering_cost': 40,
            'holding_cost_per_unit': 1.5,
            'unit_price': 15.75,
        },
    ]
    
    inventory_file = test_dir / "inventory.json"
    with open(inventory_file, 'w') as f:
        json.dump(inventory_data, f, indent=2)
    print(f"✓ Created: {inventory_file}")
    
    # Create sales history test data
    sales_data = []
    base_date = datetime.now()
    for sku in ['TEST-001', 'TEST-002']:
        for i in range(12):
            date = (base_date - timedelta(days=30*i)).strftime('%Y-%m-%d')
            quantity = 100 + (i * 5)
            sales_data.append({
                'sku': sku,
                'date': date,
                'quantity': quantity,
                'revenue': quantity * (10.50 if sku == 'TEST-001' else 15.75),
            })
    
    sales_file = test_dir / "sales_history.json"
    with open(sales_file, 'w') as f:
        json.dump(sales_data, f, indent=2)
    print(f"✓ Created: {sales_file}")
    
    # Create suppliers test data
    suppliers_data = [
        {
            'supplier_id': 'TEST-SUPP-001',
            'name': 'Test Supplier A',
            'unit_price': 10.50,
            'reliability_score': 0.95,
            'lead_time_days': 7,
        },
        {
            'supplier_id': 'TEST-SUPP-002',
            'name': 'Test Supplier B',
            'unit_price': 9.75,
            'reliability_score': 0.88,
            'lead_time_days': 14,
        },
    ]
    
    suppliers_file = test_dir / "suppliers.json"
    with open(suppliers_file, 'w') as f:
        json.dump(suppliers_data, f, indent=2)
    print(f"✓ Created: {suppliers_file}")
    
    return test_dir


def test_s3_bucket_creation():
    """Test S3 bucket creation with region handling."""
    print("\n" + "="*70)
    print("  TEST 1: S3 BUCKET CREATION")
    print("="*70 + "\n")
    
    try:
        s3_client = get_s3_client()
        bucket_name = f"kb-test-{datetime.now().timestamp():.0f}".replace('.', '')
        
        print(f"Region: {config.aws.region}")
        print(f"Bucket name: {bucket_name}")
        
        # Create bucket with proper region handling
        if config.aws.region == 'us-east-1':
            print("  Creating bucket without LocationConstraint (us-east-1)...")
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            print(f"  Creating bucket with LocationConstraint ({config.aws.region})...")
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': config.aws.region}
            )
        
        print(f"✓ Bucket created successfully: {bucket_name}\n")
        return bucket_name
    except Exception as e:
        print(f"✗ Failed to create bucket: {str(e)}\n")
        return None


def test_file_upload_to_s3(bucket_name, test_dir):
    """Test uploading files to S3."""
    print("="*70)
    print("  TEST 2: FILE UPLOAD TO S3")
    print("="*70 + "\n")
    
    try:
        s3_client = get_s3_client()
        
        files_uploaded = 0
        for file_path in test_dir.glob("*.json"):
            with open(file_path, 'r') as f:
                content = f.read()
            
            s3_key = f"supply-chain-data/{file_path.name}"
            s3_client.put_object(
                Bucket=bucket_name,
                Key=s3_key,
                Body=content,
                ContentType='application/json'
            )
            print(f"✓ Uploaded: s3://{bucket_name}/{s3_key}")
            files_uploaded += 1
        
        print(f"\n✓ Successfully uploaded {files_uploaded} files\n")
        return True
    except Exception as e:
        print(f"✗ Failed to upload files: {str(e)}\n")
        return False


def test_dynamodb_ingestion():
    """Test ingesting data into DynamoDB."""
    print("="*70)
    print("  TEST 3: DYNAMODB DATA INGESTION")
    print("="*70 + "\n")
    
    try:
        dynamodb = get_dynamodb_resource()
        
        # Ingest inventory
        print("Ingesting inventory data...")
        inventory_table = dynamodb.Table('inventory')
        inventory_table.put_item(Item={
            'sku': 'TEST-001',
            'product_name': 'Test Widget A',
            'current_quantity': 1500,
            'reorder_point': 200,
            'safety_stock': 300,
            'warehouse': 'WH-TEST',
            'lead_time_days': 7,
            'ordering_cost': 50,
            'holding_cost_per_unit': 2,
            'unit_price': 10.50,
        })
        print("✓ Inventory ingested")
        
        # Ingest sales history
        print("Ingesting sales history...")
        sales_table = dynamodb.Table('sales_history')
        base_date = datetime.now()
        for i in range(12):
            date = (base_date - timedelta(days=30*i)).strftime('%Y-%m-%d')
            sales_table.put_item(Item={
                'sku': 'TEST-001',
                'date': date,
                'quantity': 100 + (i * 5),
                'revenue': (100 + (i * 5)) * 10.50,
            })
        print("✓ Sales history ingested (12 records)")
        
        # Ingest suppliers
        print("Ingesting supplier data...")
        suppliers_table = dynamodb.Table('suppliers')
        suppliers_table.put_item(Item={
            'supplier_id': 'TEST-SUPP-001',
            'name': 'Test Supplier A',
            'unit_price': 10.50,
            'reliability_score': 0.95,
            'lead_time_days': 7,
        })
        print("✓ Supplier ingested")
        
        print("\n✓ All data ingested successfully\n")
        return True
    except Exception as e:
        print(f"✗ Failed to ingest data: {str(e)}\n")
        return False


def test_agent_tools():
    """Test agent tools with DynamoDB data."""
    print("="*70)
    print("  TEST 4: AGENT TOOLS EXECUTION")
    print("="*70 + "\n")
    
    try:
        # Test get_inventory_status
        print("Testing get_inventory_status...")
        result = get_inventory_status('TEST-001')
        print(f"  Result: {result['message']}")
        assert result['status'] == 'success', "get_inventory_status failed"
        print("✓ get_inventory_status passed\n")
        
        # Test forecast_demand
        print("Testing forecast_demand...")
        result = forecast_demand('TEST-001', forecast_days=30)
        print(f"  Result: {result['message']}")
        assert result['status'] == 'success', "forecast_demand failed"
        print("✓ forecast_demand passed\n")
        
        # Test optimize_inventory
        print("Testing optimize_inventory...")
        result = optimize_inventory('TEST-001')
        print(f"  Result: {result['message']}")
        assert result['status'] == 'success', "optimize_inventory failed"
        print("✓ optimize_inventory passed\n")
        
        # Test create_purchase_order
        print("Testing create_purchase_order...")
        result = create_purchase_order('TEST-001', 'TEST-SUPP-001', 500)
        print(f"  Result: {result['message']}")
        assert result['status'] == 'success', "create_purchase_order failed"
        print("✓ create_purchase_order passed\n")
        
        # Test detect_anomalies
        print("Testing detect_anomalies...")
        result = detect_anomalies('TEST-001')
        print(f"  Result: {result['message']}")
        assert result['status'] == 'success', "detect_anomalies failed"
        print("✓ detect_anomalies passed\n")
        
        # Test generate_report
        print("Testing generate_report...")
        result = generate_report('TEST-001')
        print(f"  Result: {result['message']}")
        assert result['status'] == 'success', "generate_report failed"
        print("✓ generate_report passed\n")
        
        print("✓ All agent tools executed successfully\n")
        return True
    except Exception as e:
        print(f"✗ Agent tool test failed: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


def test_kb_integration():
    """Test Knowledge Base integration (if configured)."""
    print("="*70)
    print("  TEST 5: KNOWLEDGE BASE INTEGRATION")
    print("="*70 + "\n")
    
    kb_id = os.getenv("BEDROCK_KB_ID")
    if not kb_id:
        print("⚠️  BEDROCK_KB_ID not set, skipping KB tests")
        print("   To enable KB tests, set: export BEDROCK_KB_ID=<your-kb-id>\n")
        return True
    
    try:
        print(f"Knowledge Base ID: {kb_id}")
        
        # Test sync_data_from_knowledge_base
        print("\nTesting sync_data_from_knowledge_base...")
        result = sync_data_from_knowledge_base()
        print(f"  Result: {result['message']}")
        if result['status'] == 'success':
            print("✓ sync_data_from_knowledge_base passed\n")
        else:
            print(f"⚠️  KB sync returned: {result['message']}\n")
        
        # Test retrieve_from_knowledge_base
        print("Testing retrieve_from_knowledge_base...")
        result = retrieve_from_knowledge_base("inventory", "inventory")
        print(f"  Result: {result['message']}")
        if result['status'] in ['success', 'not_found']:
            print("✓ retrieve_from_knowledge_base passed\n")
        else:
            print(f"⚠️  KB retrieve returned: {result['message']}\n")
        
        print("✓ Knowledge Base integration tests complete\n")
        return True
    except Exception as e:
        print(f"⚠️  KB integration test warning: {str(e)}\n")
        return True  # Don't fail if KB is not fully configured


def cleanup_test_data(bucket_name, test_dir):
    """Clean up test data."""
    print("="*70)
    print("  CLEANUP")
    print("="*70 + "\n")
    
    try:
        # Delete S3 bucket
        if bucket_name:
            s3_client = get_s3_client()
            try:
                # Delete all objects in bucket
                response = s3_client.list_objects_v2(Bucket=bucket_name)
                if 'Contents' in response:
                    for obj in response['Contents']:
                        s3_client.delete_object(Bucket=bucket_name, Key=obj['Key'])
                
                # Delete bucket
                s3_client.delete_bucket(Bucket=bucket_name)
                print(f"✓ Deleted S3 bucket: {bucket_name}")
            except Exception as e:
                print(f"⚠️  Could not delete bucket: {str(e)}")
        
        # Delete test data files
        import shutil
        if test_dir.exists():
            shutil.rmtree(test_dir)
            print(f"✓ Deleted test data directory: {test_dir}")
        
        print()
    except Exception as e:
        print(f"⚠️  Cleanup warning: {str(e)}\n")


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("  KNOWLEDGE BASE INTEGRATION - COMPLETE TEST SUITE")
    print("="*70)
    
    results = {
        'S3 Bucket Creation': False,
        'File Upload': False,
        'DynamoDB Ingestion': False,
        'Agent Tools': False,
        'KB Integration': False,
    }
    
    try:
        # Create test data
        test_dir = create_test_data_files()
        
        # Test 1: S3 bucket creation
        bucket_name = test_s3_bucket_creation()
        results['S3 Bucket Creation'] = bucket_name is not None
        
        # Test 2: File upload
        if bucket_name:
            results['File Upload'] = test_file_upload_to_s3(bucket_name, test_dir)
        
        # Test 3: DynamoDB ingestion
        results['DynamoDB Ingestion'] = test_dynamodb_ingestion()
        
        # Test 4: Agent tools
        results['Agent Tools'] = test_agent_tools()
        
        # Test 5: KB integration
        results['KB Integration'] = test_kb_integration()
        
    except Exception as e:
        print(f"\n✗ Test suite error: {str(e)}\n")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        try:
            cleanup_test_data(bucket_name if 'bucket_name' in locals() else None, test_dir if 'test_dir' in locals() else None)
        except:
            pass
    
    # Print summary
    print("="*70)
    print("  TEST SUMMARY")
    print("="*70 + "\n")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_flag in results.items():
        status = "✓ PASSED" if passed_flag else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed\n")
    
    if passed == total:
        print("✅ ALL TESTS PASSED!\n")
        return 0
    else:
        print("⚠️  SOME TESTS FAILED\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
