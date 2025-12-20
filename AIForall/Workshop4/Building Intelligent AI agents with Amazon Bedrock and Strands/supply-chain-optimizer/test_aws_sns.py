"""Test SNS connection and basic operations."""

from datetime import datetime
from src.aws.clients import get_sns_client
from src.config import config, logger


def test_sns_connection():
    """Test SNS connection."""
    try:
        sns = get_sns_client()
        logger.info("SNS client obtained successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to get SNS client: {str(e)}")
        return False


def test_sns_list_topics():
    """Test SNS list topics operation."""
    try:
        sns = get_sns_client()
        response = sns.list_topics()
        
        topics = response.get('Topics', [])
        logger.info(f"Found {len(topics)} SNS topics")
        
        for topic in topics[:10]:
            logger.info(f"  - {topic['TopicArn']}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to list SNS topics: {str(e)}")
        return False


def test_sns_publish():
    """Test SNS publish operation."""
    try:
        sns = get_sns_client()
        topic_arn = config.sns.topic_arn
        
        if not topic_arn:
            logger.error("SNS_TOPIC_ARN not configured in environment")
            return False
        
        # Publish test message
        message = {
            'test': 'message',
            'timestamp': datetime.now().isoformat(),
            'source': 'Supply Chain Optimizer - Test',
        }
        
        logger.info(f"Publishing test message to {topic_arn}")
        response = sns.publish(
            TopicArn=topic_arn,
            Subject='Supply Chain Optimizer - Test Alert',
            Message=f"Test message from Supply Chain Optimizer\n\nTimestamp: {datetime.now().isoformat()}\n\nThis is a test to verify SNS connectivity.",
        )
        
        message_id = response['MessageId']
        logger.info(f"Message published successfully. Message ID: {message_id}")
        
        return True
        
    except Exception as e:
        logger.error(f"SNS publish test failed: {str(e)}")
        return False


def test_sns_topic_attributes():
    """Test SNS topic attributes."""
    try:
        sns = get_sns_client()
        topic_arn = config.sns.topic_arn
        
        if not topic_arn:
            logger.error("SNS_TOPIC_ARN not configured in environment")
            return False
        
        response = sns.get_topic_attributes(TopicArn=topic_arn)
        attributes = response.get('Attributes', {})
        
        logger.info(f"Topic ARN: {topic_arn}")
        logger.info(f"Display Name: {attributes.get('DisplayName', 'Not set')}")
        logger.info(f"Subscriptions Count: {attributes.get('SubscriptionsConfirmed', 0)}")
        logger.info(f"Pending Subscriptions: {attributes.get('SubscriptionsPending', 0)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to get SNS topic attributes: {str(e)}")
        return False


def test_sns_list_subscriptions():
    """Test SNS list subscriptions."""
    try:
        sns = get_sns_client()
        topic_arn = config.sns.topic_arn
        
        if not topic_arn:
            logger.error("SNS_TOPIC_ARN not configured in environment")
            return False
        
        response = sns.list_subscriptions_by_topic(TopicArn=topic_arn)
        subscriptions = response.get('Subscriptions', [])
        
        logger.info(f"Found {len(subscriptions)} subscriptions for topic")
        
        for sub in subscriptions:
            logger.info(f"  - {sub['Protocol']}: {sub['Endpoint']} ({sub['SubscriptionArn']})")
        
        if len(subscriptions) == 0:
            logger.warning("No subscriptions found. Subscribe an email to receive alerts.")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to list SNS subscriptions: {str(e)}")
        return False


if __name__ == '__main__':
    print("\n" + "="*60)
    print("SNS Connection Tests")
    print("="*60 + "\n")
    
    # Test 1: Connection
    print("[1/5] Testing SNS connection...")
    if test_sns_connection():
        print("PASS: SNS connection successful\n")
    else:
        print("FAIL: SNS connection failed\n")
        exit(1)
    
    # Test 2: List topics
    print("[2/5] Testing SNS list topics...")
    if test_sns_list_topics():
        print("PASS: SNS list topics successful\n")
    else:
        print("FAIL: SNS list topics failed\n")
        exit(1)
    
    # Test 3: Topic attributes
    print("[3/5] Checking SNS topic attributes...")
    if test_sns_topic_attributes():
        print("PASS: SNS topic attributes retrieved\n")
    else:
        print("FAIL: SNS topic attributes retrieval failed\n")
        print("Make sure:")
        print("  - SNS_TOPIC_ARN is set in .env\n")
        exit(1)
    
    # Test 4: List subscriptions
    print("[4/5] Listing SNS subscriptions...")
    if test_sns_list_subscriptions():
        print("PASS: SNS subscriptions listed\n")
    else:
        print("FAIL: SNS subscriptions listing failed\n")
        exit(1)
    
    # Test 5: Publish message
    print("[5/5] Testing SNS publish operation...")
    if test_sns_publish():
        print("PASS: SNS publish successful\n")
        print("Check your email for the test message (may take a few seconds)\n")
    else:
        print("FAIL: SNS publish failed\n")
        exit(1)
    
    print("="*60)
    print("All SNS tests PASSED!")
    print("="*60)
