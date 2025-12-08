# Resource Cleanup Procedures

This document describes how to clean up AWS resources created by the Bedrock RAG Retrieval System.

## Table of Contents

1. [Overview](#overview)
2. [Cleanup Methods](#cleanup-methods)
3. [Programmatic Cleanup](#programmatic-cleanup)
4. [Script-Based Cleanup](#script-based-cleanup)
5. [Manual Cleanup](#manual-cleanup)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## Overview

The Bedrock RAG Retrieval System creates several AWS resources that should be cleaned up when no longer needed to avoid unnecessary costs:

- **Knowledge Bases**: AWS Bedrock Knowledge Base instances
- **Data Sources**: Data source configurations within knowledge bases
- **Vector Store**: OpenSearch Serverless collections and indices
- **S3 Buckets**: Document storage buckets
- **IAM Roles and Policies**: Execution roles and access policies

### Resource Cleanup Hierarchy

Resources should be cleaned up in the following order to avoid dependency issues:

1. **Knowledge Base** (deletes data sources automatically)
2. **Vector Store** (indices and collections)
3. **S3 Buckets** (document storage)
4. **IAM Roles and Policies** (execution roles)

## Cleanup Methods

### Method 1: Programmatic Cleanup (Recommended)

Use the `ResourceCleanupManager` class to programmatically clean up resources.

#### Basic Cleanup

```python
from config.aws_config import AWSConfig
from src.cleanup_manager import ResourceCleanupManager
from src.knowledge_base_manager import BedrockKnowledgeBase

# Initialize AWS config
aws_config = AWSConfig()

# Initialize managers
kb_manager = BedrockKnowledgeBase(aws_config)
cleanup_manager = ResourceCleanupManager(aws_config)

# Clean up a specific knowledge base
cleanup_results = cleanup_manager.cleanup_knowledge_base_resources(
    kb_id="kb-12345",
    kb_manager=kb_manager,
    confirm=True  # Required for actual deletion
)

# Print cleanup report
report = cleanup_manager.generate_cleanup_report(cleanup_results)
print(report)
```

#### Comprehensive Cleanup

```python
from config.aws_config import AWSConfig
from src.cleanup_manager import ResourceCleanupManager
from src.knowledge_base_manager import BedrockKnowledgeBase
from src.s3_manager import S3Manager
from src.iam_manager import IAMManager
from src.vector_store import VectorIndexManager

# Initialize AWS config
aws_config = AWSConfig()

# Initialize all managers
kb_manager = BedrockKnowledgeBase(aws_config)
s3_manager = S3Manager(aws_config)
iam_manager = IAMManager(aws_config)
vector_store_manager = VectorIndexManager(aws_config)
cleanup_manager = ResourceCleanupManager(aws_config)

# Comprehensive cleanup with all resources
cleanup_results = cleanup_manager.cleanup_knowledge_base_resources(
    kb_id="kb-12345",
    kb_manager=kb_manager,
    vector_store_manager=vector_store_manager,
    s3_manager=s3_manager,
    iam_manager=iam_manager,
    delete_s3_buckets=True,
    delete_iam_roles=True,
    confirm=True
)

# Print cleanup report
report = cleanup_manager.generate_cleanup_report(cleanup_results)
print(report)
```

#### Test Resource Cleanup

```python
# Clean up all test resources with a specific prefix
cleanup_results = cleanup_manager.cleanup_test_resources(
    test_prefix="test-",
    kb_manager=kb_manager,
    s3_manager=s3_manager,
    iam_manager=iam_manager,
    confirm=True
)
```

#### Orphaned Resource Cleanup

```python
# Clean up orphaned resources (failed KBs, etc.)
cleanup_results = cleanup_manager.cleanup_orphaned_resources(
    kb_manager=kb_manager,
    s3_manager=s3_manager,
    iam_manager=iam_manager,
    confirm=True
)
```

### Method 2: Script-Based Cleanup

Use provided cleanup scripts for command-line cleanup operations.

#### Clean Up Test Resources

```bash
# List test resources without deleting (dry-run)
python scripts/cleanup_test_resources.py --prefix test- --dry-run

# Clean up test resources with default prefix
python scripts/cleanup_test_resources.py --confirm

# Clean up test resources with custom prefix
python scripts/cleanup_test_resources.py --prefix my-test- --confirm

# Clean up test resources and delete S3 buckets
python scripts/cleanup_test_resources.py --confirm --delete-s3

# Clean up test resources and delete IAM roles
python scripts/cleanup_test_resources.py --confirm --delete-iam

# Use specific AWS profile
python scripts/cleanup_test_resources.py --confirm --profile my-profile

# Enable verbose logging
python scripts/cleanup_test_resources.py --confirm --verbose
```

#### Clean Up Orphaned Resources

```bash
# List orphaned resources without deleting (dry-run)
python scripts/cleanup_orphaned_resources.py --dry-run

# Clean up orphaned resources
python scripts/cleanup_orphaned_resources.py --confirm

# Use specific AWS profile
python scripts/cleanup_orphaned_resources.py --confirm --profile my-profile

# Enable verbose logging
python scripts/cleanup_orphaned_resources.py --confirm --verbose
```

### Method 3: Manual Cleanup

If programmatic cleanup is not available, resources can be cleaned up manually through the AWS Console.

#### AWS Console Cleanup

1. **Knowledge Bases**
   - Navigate to AWS Bedrock → Knowledge Bases
   - Select the knowledge base to delete
   - Click "Delete" and confirm

2. **OpenSearch Serverless Collections**
   - Navigate to OpenSearch Serverless → Collections
   - Select the collection to delete
   - Click "Delete" and confirm

3. **S3 Buckets**
   - Navigate to S3 → Buckets
   - Select the bucket to delete
   - Click "Delete" and confirm (may need to empty bucket first)

4. **IAM Roles and Policies**
   - Navigate to IAM → Roles
   - Select the role to delete
   - Detach all policies first
   - Click "Delete" and confirm
   - Navigate to IAM → Policies
   - Select the policy to delete
   - Click "Delete" and confirm

#### AWS CLI Cleanup

```bash
# Delete a knowledge base
aws bedrock-agent delete-knowledge-base --knowledge-base-id kb-12345

# List knowledge bases
aws bedrock-agent list-knowledge-bases

# Delete an S3 bucket (must be empty)
aws s3 rb s3://my-bucket

# Delete an S3 bucket and all contents
aws s3 rb s3://my-bucket --force

# Delete an IAM role
aws iam delete-role --role-name my-role

# Delete an IAM policy
aws iam delete-policy --policy-arn arn:aws:iam::123456789012:policy/my-policy
```

## Best Practices

### 1. Always Use Confirmation Flags

Always use the `--confirm` flag or `confirm=True` parameter to prevent accidental deletion:

```python
# This will fail without confirmation
cleanup_manager.cleanup_knowledge_base_resources(
    kb_id="kb-12345",
    kb_manager=kb_manager,
    confirm=False  # Raises ValueError
)
```

### 2. Use Dry-Run Mode First

Always preview resources before deletion:

```bash
# Preview what will be deleted
python scripts/cleanup_test_resources.py --prefix test- --dry-run

# Then delete if satisfied
python scripts/cleanup_test_resources.py --prefix test- --confirm
```

### 3. Clean Up in Order

Follow the resource cleanup hierarchy to avoid dependency issues:

1. Delete knowledge bases first (automatically deletes data sources)
2. Delete vector store collections
3. Delete S3 buckets
4. Delete IAM roles and policies

### 4. Monitor Cleanup Progress

Enable verbose logging to monitor cleanup progress:

```bash
python scripts/cleanup_test_resources.py --confirm --verbose
```

### 5. Check for Errors

Always check cleanup results for errors:

```python
cleanup_results = cleanup_manager.cleanup_knowledge_base_resources(...)

if cleanup_results.get("errors"):
    print(f"Cleanup completed with {len(cleanup_results['errors'])} errors:")
    for error in cleanup_results["errors"]:
        print(f"  - {error}")
else:
    print("Cleanup completed successfully")
```

### 6. Document Resource Naming

Use consistent naming conventions for resources to make cleanup easier:

- Knowledge bases: `{project}-kb-{environment}`
- S3 buckets: `{project}-documents-{environment}`
- IAM roles: `{project}-kb-execution-role-{environment}`
- Test resources: `test-{resource-type}-{timestamp}`

### 7. Regular Cleanup Schedule

Implement a regular cleanup schedule to remove test and orphaned resources:

```bash
# Weekly cleanup of test resources
0 2 * * 0 python /path/to/scripts/cleanup_test_resources.py --confirm

# Daily cleanup of orphaned resources
0 3 * * * python /path/to/scripts/cleanup_orphaned_resources.py --confirm
```

## Troubleshooting

### Issue: "Cleanup confirmation required"

**Problem**: Cleanup fails with "Cleanup confirmation required" error.

**Solution**: Add the `--confirm` flag or set `confirm=True`:

```bash
python scripts/cleanup_test_resources.py --confirm
```

### Issue: "Knowledge base ID cannot be empty"

**Problem**: Cleanup fails with "Knowledge base ID cannot be empty" error.

**Solution**: Ensure you're providing a valid knowledge base ID:

```python
cleanup_manager.cleanup_knowledge_base_resources(
    kb_id="kb-12345",  # Must be non-empty
    kb_manager=kb_manager,
    confirm=True
)
```

### Issue: "Failed to delete knowledge base"

**Problem**: Knowledge base deletion fails.

**Possible causes**:
- Knowledge base is still processing
- Knowledge base has active data sources
- Insufficient IAM permissions

**Solution**:
1. Wait for knowledge base to finish processing
2. Ensure all data sources are deleted first
3. Check IAM permissions

### Issue: "S3 bucket is not empty"

**Problem**: S3 bucket deletion fails because bucket is not empty.

**Solution**: Use the `--delete-s3` flag to force deletion of bucket contents:

```bash
python scripts/cleanup_test_resources.py --confirm --delete-s3
```

Or manually delete bucket contents first:

```bash
aws s3 rm s3://my-bucket --recursive
aws s3 rb s3://my-bucket
```

### Issue: "Access denied" errors

**Problem**: Cleanup fails with access denied errors.

**Solution**:
1. Check IAM permissions for the AWS user/role
2. Ensure the user has permissions for:
   - `bedrock-agent:DeleteKnowledgeBase`
   - `bedrock-agent:DeleteDataSource`
   - `s3:DeleteBucket`
   - `s3:DeleteObject`
   - `iam:DeleteRole`
   - `iam:DeletePolicy`

### Issue: Cleanup hangs or times out

**Problem**: Cleanup script hangs or times out.

**Solution**:
1. Check AWS service status
2. Verify network connectivity
3. Increase timeout values if needed
4. Try cleanup again later

### Issue: Partial cleanup (some resources deleted, others failed)

**Problem**: Cleanup partially succeeds, leaving some resources behind.

**Solution**:
1. Check the cleanup report for specific errors
2. Address the errors (e.g., delete dependencies first)
3. Run cleanup again for remaining resources

## Cleanup Report Example

```
============================================================
RESOURCE CLEANUP REPORT
============================================================

Knowledge Base Cleanup:
  - KB Deleted: True
  - Data Sources Deleted: 2

Vector Store Cleanup:
  - Collections Deleted: 1

S3 Cleanup:
  - Buckets Deleted: 1

IAM Cleanup:
  - Roles Deleted: 1
  - Policies Deleted: 3

------------------------------------------------------------
Total Resources Deleted: 9

No errors encountered.
============================================================
```

## Cost Optimization

### Estimated Costs

- **Knowledge Base**: $0.30 per KB per day
- **OpenSearch Serverless**: $0.30 per OCU per hour
- **S3 Storage**: $0.023 per GB per month
- **Data Transfer**: $0.02 per GB (out of region)

### Cost Reduction Tips

1. Delete unused knowledge bases immediately
2. Clean up test resources after testing
3. Use lifecycle policies for S3 buckets
4. Monitor resource usage regularly
5. Set up cost alerts in AWS Billing

## Additional Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [OpenSearch Serverless Documentation](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless.html)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [AWS IAM Documentation](https://docs.aws.amazon.com/iam/)
- [AWS CLI Reference](https://docs.aws.amazon.com/cli/latest/reference/)
