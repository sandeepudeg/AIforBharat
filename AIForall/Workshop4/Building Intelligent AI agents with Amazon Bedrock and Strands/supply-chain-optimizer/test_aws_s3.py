"""Test S3 connection and basic operations."""

import json
from datetime import datetime
from src.aws.clients import get_s3_client
from src.config import config, logger


def test_s3_connection():
    """Test S3 connection."""
    try:
        s3 = get_s3_client()
        logger.info("S3 client obtained successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to get S3 client: {str(e)}")
        return False


def test_s3_list_buckets():
    """Test S3 list buckets operation."""
    try:
        s3 = get_s3_client()
        response = s3.list_buckets()
        
        buckets = response.get('Buckets', [])
        logger.info(f"Found {len(buckets)} S3 buckets")
        
        for bucket in buckets:
            logger.info(f"  - {bucket['Name']}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to list S3 buckets: {str(e)}")
        return False


def test_s3_write_read():
    """Test S3 write and read operations."""
    try:
        s3 = get_s3_client()
        bucket = config.s3.bucket
        
        if not bucket:
            logger.error("S3_BUCKET not configured in environment")
            return False
        
        # Prepare test data
        test_key = f"test/test-{datetime.now().timestamp()}.json"
        test_data = {
            'test': 'data',
            'timestamp': datetime.now().isoformat(),
            'message': 'This is a test file from Supply Chain Optimizer',
        }
        
        # Write test file
        logger.info(f"Writing test file to s3://{bucket}/{test_key}")
        s3.put_object(
            Bucket=bucket,
            Key=test_key,
            Body=json.dumps(test_data),
            ContentType='application/json',
        )
        logger.info("Write successful")
        
        # Read test file
        response = s3.get_object(Bucket=bucket, Key=test_key)
        retrieved_data = json.loads(response['Body'].read().decode())
        
        logger.info(f"Read successful: {retrieved_data}")
        
        # Verify data
        if retrieved_data == test_data:
            logger.info("Data verification successful")
            
            # Clean up
            s3.delete_object(Bucket=bucket, Key=test_key)
            logger.info("Test file cleaned up")
            
            return True
        else:
            logger.error("Retrieved data doesn't match original")
            return False
            
    except Exception as e:
        logger.error(f"S3 write/read test failed: {str(e)}")
        return False


def test_s3_list_objects():
    """Test S3 list objects operation."""
    try:
        s3 = get_s3_client()
        bucket = config.s3.bucket
        
        if not bucket:
            logger.error("S3_BUCKET not configured in environment")
            return False
        
        logger.info(f"Listing objects in s3://{bucket}...")
        response = s3.list_objects_v2(Bucket=bucket, MaxKeys=10)
        
        objects = response.get('Contents', [])
        logger.info(f"Found {len(objects)} objects (showing up to 10)")
        
        for obj in objects[:5]:
            logger.info(f"  - {obj['Key']} ({obj['Size']} bytes)")
        
        return True
        
    except Exception as e:
        logger.error(f"S3 list objects test failed: {str(e)}")
        return False


def test_s3_bucket_versioning():
    """Test S3 bucket versioning status."""
    try:
        s3 = get_s3_client()
        bucket = config.s3.bucket
        
        if not bucket:
            logger.error("S3_BUCKET not configured in environment")
            return False
        
        response = s3.get_bucket_versioning(Bucket=bucket)
        status = response.get('Status', 'Not set')
        
        logger.info(f"Bucket versioning status: {status}")
        
        if status == 'Enabled':
            logger.info("Versioning is enabled (good for data protection)")
        else:
            logger.warning("Versioning is not enabled (consider enabling for production)")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to check bucket versioning: {str(e)}")
        return False


if __name__ == '__main__':
    print("\n" + "="*60)
    print("S3 Connection Tests")
    print("="*60 + "\n")
    
    # Test 1: Connection
    print("[1/5] Testing S3 connection...")
    if test_s3_connection():
        print("PASS: S3 connection successful\n")
    else:
        print("FAIL: S3 connection failed\n")
        exit(1)
    
    # Test 2: List buckets
    print("[2/5] Testing S3 list buckets...")
    if test_s3_list_buckets():
        print("PASS: S3 list buckets successful\n")
    else:
        print("FAIL: S3 list buckets failed\n")
        exit(1)
    
    # Test 3: Write/Read
    print("[3/5] Testing S3 write/read operations...")
    if test_s3_write_read():
        print("PASS: S3 write/read successful\n")
    else:
        print("FAIL: S3 write/read failed\n")
        print("Make sure:")
        print("  - S3_BUCKET is set in .env")
        print("  - AWS credentials have S3 permissions\n")
        exit(1)
    
    # Test 4: List objects
    print("[4/5] Testing S3 list objects...")
    if test_s3_list_objects():
        print("PASS: S3 list objects successful\n")
    else:
        print("FAIL: S3 list objects failed\n")
        exit(1)
    
    # Test 5: Bucket versioning
    print("[5/5] Checking S3 bucket versioning...")
    if test_s3_bucket_versioning():
        print("PASS: S3 bucket versioning check successful\n")
    else:
        print("FAIL: S3 bucket versioning check failed\n")
        exit(1)
    
    print("="*60)
    print("All S3 tests PASSED!")
    print("="*60)
