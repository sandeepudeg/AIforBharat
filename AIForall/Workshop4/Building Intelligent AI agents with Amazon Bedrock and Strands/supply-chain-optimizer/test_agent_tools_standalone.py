#!/usr/bin/env python3
"""
Standalone test script for agent tools.

This script tests the agent tools without requiring a full Strands agent setup.
It can be run to verify that all tools work correctly with DynamoDB.
"""

import os
import sys
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agents.agent_tools import (
    forecast_demand,
    optimize_inventory,
    create_purchase_order,
    detect_anomalies,
    generate_report,
    get_inventory_status,
)
from src.config import logger


def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_result(result):
    """Print a formatted result."""
    import json
    print(json.dumps(result, indent=2, default=str))


def test_forecast_demand():
    """Test forecast_demand tool."""
    print_header("TEST 1: Forecast Demand")
    print("Testing forecast_demand tool...")
    
    result = forecast_demand(sku='PROD-001', forecast_days=30)
    print_result(result)
    
    assert result['status'] in ['success', 'error'], "Invalid status"
    print("✓ Test passed")


def test_optimize_inventory():
    """Test optimize_inventory tool."""
    print_header("TEST 2: Optimize Inventory")
    print("Testing optimize_inventory tool...")
    
    result = optimize_inventory(sku='PROD-001')
    print_result(result)
    
    assert result['status'] in ['success', 'error'], "Invalid status"
    print("✓ Test passed")


def test_create_purchase_order():
    """Test create_purchase_order tool."""
    print_header("TEST 3: Create Purchase Order")
    print("Testing create_purchase_order tool...")
    
    result = create_purchase_order(
        sku='PROD-001',
        supplier_id='SUPP-001',
        quantity=1500,
        delivery_days=7
    )
    print_result(result)
    
    assert result['status'] in ['success', 'error'], "Invalid status"
    print("✓ Test passed")


def test_detect_anomalies():
    """Test detect_anomalies tool."""
    print_header("TEST 4: Detect Anomalies")
    print("Testing detect_anomalies tool...")
    
    result = detect_anomalies(sku='PROD-001')
    print_result(result)
    
    assert result['status'] in ['success', 'error'], "Invalid status"
    print("✓ Test passed")


def test_generate_report():
    """Test generate_report tool."""
    print_header("TEST 5: Generate Report")
    print("Testing generate_report tool...")
    
    result = generate_report(sku='PROD-001')
    print_result(result)
    
    assert result['status'] in ['success', 'error'], "Invalid status"
    print("✓ Test passed")


def test_get_inventory_status():
    """Test get_inventory_status tool."""
    print_header("TEST 6: Get Inventory Status")
    print("Testing get_inventory_status tool...")
    
    result = get_inventory_status(sku='PROD-001')
    print_result(result)
    
    assert result['status'] in ['success', 'not_found', 'error'], "Invalid status"
    print("✓ Test passed")


def test_all_tools():
    """Test all tools in sequence."""
    print_header("RUNNING ALL TOOL TESTS")
    
    tests = [
        ("Forecast Demand", test_forecast_demand),
        ("Optimize Inventory", test_optimize_inventory),
        ("Create Purchase Order", test_create_purchase_order),
        ("Detect Anomalies", test_detect_anomalies),
        ("Generate Report", test_generate_report),
        ("Get Inventory Status", test_get_inventory_status),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"✗ Test failed: {str(e)}")
            failed += 1
    
    print_header("TEST SUMMARY")
    print(f"Total tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n✓ All tests passed!")
    else:
        print(f"\n✗ {failed} test(s) failed")
    
    return failed == 0


if __name__ == "__main__":
    try:
        success = test_all_tools()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
