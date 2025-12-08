#!/usr/bin/env python
"""Test runner that manually runs tests without pytest to avoid Windows hanging"""

import sys
import os
import traceback
from datetime import datetime
from unittest.mock import MagicMock, patch

# Add current directory to path
sys.path.insert(0, '.')

# Disable hypothesis database
os.environ['HYPOTHESIS_DATABASE_DIRECTORY'] = 'none'

# Import test classes
from tests.test_aws_config import (
    TestAWSConfigInitialization,
    TestAWSConfigCredentialValidation,
    TestAWSConfigAccountIDDetection,
    TestAWSConfigClientManagement,
    TestAWSConfigServiceValidation,
    TestAWSConfigPropertyBased
)

def create_mock_bedrock_client():
    """Create a mock Bedrock client"""
    with patch('boto3.client') as mock_client:
        client = MagicMock()
        mock_client.return_value = client
        return client

def run_test_method(test_class, method_name):
    """Run a single test method"""
    try:
        test_instance = test_class()
        method = getattr(test_instance, method_name)
        
        # Check if method has parameters (fixtures)
        import inspect
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())
        
        if len(params) == 0:
            # No parameters, just call it
            method()
        else:
            # Has parameters, skip it (requires pytest fixtures)
            return None, "Requires pytest fixtures"
        
        return True, None
    except Exception as e:
        return False, traceback.format_exc()

def run_all_tests():
    """Run all tests"""
    test_classes = [
        TestAWSConfigInitialization,
        TestAWSConfigCredentialValidation,
        TestAWSConfigAccountIDDetection,
        TestAWSConfigClientManagement,
        TestAWSConfigServiceValidation,
        TestAWSConfigPropertyBased
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    skipped_tests = 0
    failed_test_details = []
    
    print("=" * 80)
    print(f"Running tests at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    for test_class in test_classes:
        print(f"\n{test_class.__name__}:")
        
        # Get all test methods
        test_methods = [m for m in dir(test_class) if m.startswith('test_')]
        
        for method_name in test_methods:
            total_tests += 1
            success, error = run_test_method(test_class, method_name)
            
            if success is None:
                skipped_tests += 1
                print(f"  ⊘ {method_name} (skipped - requires fixtures)")
            elif success:
                passed_tests += 1
                print(f"  ✓ {method_name}")
            else:
                failed_tests += 1
                print(f"  ✗ {method_name}")
                failed_test_details.append((test_class.__name__, method_name, error))
                if error:
                    print(f"    Error: {error[:200]}")
    
    print("\n" + "=" * 80)
    print(f"Test Results: {passed_tests} passed, {failed_tests} failed, {skipped_tests} skipped, {total_tests} total")
    print("=" * 80)
    
    if failed_test_details:
        print("\nFailed Test Details:")
        for class_name, method_name, error in failed_test_details:
            print(f"\n{class_name}.{method_name}:")
            print(error[:500])
    
    return failed_tests == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
