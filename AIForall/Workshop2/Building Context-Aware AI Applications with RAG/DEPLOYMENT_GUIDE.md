# Bedrock RAG Retrieval System - Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Bedrock RAG Retrieval System in your AWS environment.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [AWS Account Setup](#aws-account-setup)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Deployment Steps](#deployment-steps)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)
8. [Cleanup](#cleanup)

---

## Prerequisites

### Required Software

- Python 3.8 or higher
- pip (Python package manager)
- AWS CLI v2
- Git

### AWS Requirements

- AWS Account with appropriate permissions
- AWS credentials configured locally
- Access to the following AWS services:
  - AWS Bedrock
  - Amazon OpenSearch Serverless
  - Amazon S3
  - AWS IAM
  - AWS Secrets Manager
  - AWS CloudWatch

### Permissions Required

The IAM user or role must have permissions for:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:*",
        "bedrock-agent:*",
        "aoss:*",
        "s3:*",
        "iam:*",
        "secretsmanager:*",
        "logs:*"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## AWS Account Setup

### Step 1: Enable Bedrock Models

1. Go to AWS Bedrock console
2. Navigate to "Model access"
3. Click "Manage model access"
4. Enable the following models:
   - Anthropic Claude 3 Sonnet
   - Amazon Titan Embeddings
   - Cohere Rerank (optional)

### Step 2: Create S3 Bucket for Documents

```bash
aws s3 mb s3://my-bedrock-documents --region us-east-1
```

### Step 3: Create S3 Bucket for Logs (Optional)

```bash
aws s3 mb s3://my-bedrock-logs --region us-east-1
```

### Step 4: Configure AWS CLI

```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter your default region (e.g., us-east-1)
# Enter your default output format (json)
```

---

## Installation

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd bedrock-rag-retrieval
```

### Step 2: Create Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Verify Installation

```bash
python -c "import boto3; print(f'boto3 version: {boto3.__version__}')"
python -c "import hypothesis; print(f'hypothesis version: {hypothesis.__version__}')"
```

---

## Configuration

### Step 1: Create Environment File

Copy the example environment file:

```bash
cp .env.example .env
```

### Step 2: Configure Environment Variables

Edit `.env` with your settings:

```env
# AWS Configuration
AWS_REGION=us-east-1
AWS_PROFILE=default

# S3 Configuration
DOCUMENTS_BUCKET=my-bedrock-documents
LOGS_BUCKET=my-bedrock-logs

# Knowledge Base Configuration
KB_NAME=my-knowledge-base
KB_DESCRIPTION=My RAG knowledge base

# Embedding Model
EMBEDDING_MODEL=amazon.titan-embed-text-v2:0

# Generation Model
GENERATION_MODEL=anthropic.claude-3-sonnet-20240229-v1:0

# Retrieval Configuration
MAX_RETRIEVAL_RESULTS=5
MIN_RELEVANCE_SCORE=0.5

# Ingestion Configuration
CHUNK_SIZE=1024
CHUNK_OVERLAP=20
```

### Step 3: Configure AWS Credentials

Option 1: Using AWS CLI (Recommended)

```bash
aws configure
```

Option 2: Using Environment Variables

```bash
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_DEFAULT_REGION=us-east-1
```

Option 3: Using AWS Credentials File

Create `~/.aws/credentials`:

```ini
[default]
aws_access_key_id = your-access-key
aws_secret_access_key = your-secret-key

[profile-name]
aws_access_key_id = your-access-key
aws_secret_access_key = your-secret-key
```

---

## Deployment Steps

### Step 1: Initialize AWS Configuration

```python
from config.aws_config import AWSConfig

config = AWSConfig(region='us-east-1')
config.validate_credentials()
print("AWS credentials validated successfully")
```

### Step 2: Create IAM Resources

```python
from src.iam_manager import IAMManager

iam_manager = IAMManager(config)

# Create Knowledge Base execution role
kb_role = iam_manager.create_knowledge_base_execution_role('bedrock-kb-role')
print(f"Created KB role: {kb_role['role_arn']}")

# Create foundation model policy
fm_policy = iam_manager.create_foundation_model_policy('bedrock-models-policy')
print(f"Created FM policy: {fm_policy['policy_arn']}")

# Create S3 bucket policy
s3_policy = iam_manager.create_s3_bucket_policy(
    'bedrock-s3-policy',
    ['my-bedrock-documents']
)
print(f"Created S3 policy: {s3_policy['policy_arn']}")

# Attach policies to role
iam_manager.attach_policy_to_role('bedrock-kb-role', fm_policy['policy_arn'])
iam_manager.attach_policy_to_role('bedrock-kb-role', s3_policy['policy_arn'])
```

### Step 3: Create OpenSearch Serverless Resources

```python
from src.oss_security import OSSSecurityManager

oss_manager = OSSSecurityManager(config)

# Create encryption policy
enc_policy = oss_manager.create_encryption_policy('bedrock-encryption-policy')
print(f"Created encryption policy: {enc_policy['policy_name']}")

# Create network policy
net_policy = oss_manager.create_network_policy(
    'bedrock-network-policy',
    ['bedrock-collection'],
    allow_public_access=False
)
print(f"Created network policy: {net_policy['policy_name']}")

# Create data access policy
kb_role_arn = 'arn:aws:iam::123456789012:role/bedrock-kb-role'
data_policy = oss_manager.create_data_access_policy(
    'bedrock-data-access-policy',
    ['bedrock-collection'],
    [kb_role_arn]
)
print(f"Created data access policy: {data_policy['policy_name']}")
```

### Step 4: Create S3 Bucket

```python
from src.s3_manager import S3Manager

s3_manager = S3Manager(config)

# Create bucket
bucket = s3_manager.create_bucket('my-bedrock-documents')
print(f"Created S3 bucket: {bucket['bucket_name']}")
```

### Step 5: Create Vector Index

```python
from src.vector_store import VectorIndexManager

vector_manager = VectorIndexManager(config)

# Create vector index
index = vector_manager.create_vector_index(
    'bedrock-vectors',
    dimension=1536,
    similarity_metric='cosine'
)
print(f"Created vector index: {index['index_name']}")
```

### Step 6: Create Knowledge Base

```python
from src.knowledge_base_manager import BedrockKnowledgeBase

kb_manager = BedrockKnowledgeBase(config)

# Create knowledge base
kb = kb_manager.create_knowledge_base(
    kb_name='my-knowledge-base',
    kb_description='My RAG knowledge base',
    embedding_model='amazon.titan-embed-text-v2:0',
    generation_model='anthropic.claude-3-sonnet-20240229-v1:0'
)
print(f"Created knowledge base: {kb['kb_id']}")
```

### Step 7: Create Data Source

```python
# Create S3 data source
data_source = kb_manager.create_data_source(
    kb_id=kb['kb_id'],
    source_name='my-s3-source',
    source_type='S3',
    source_config={'bucket_name': 'my-bedrock-documents'}
)
print(f"Created data source: {data_source['data_source_id']}")
```

### Step 8: Upload Documents

```python
# Upload documents to S3
s3_manager.upload_document(
    'my-bedrock-documents',
    '/path/to/document1.pdf'
)
s3_manager.upload_document(
    'my-bedrock-documents',
    '/path/to/document2.pdf'
)
print("Documents uploaded successfully")
```

### Step 9: Start Ingestion

```python
from src.ingestion_manager import IngestionJobManager

ingestion_manager = IngestionJobManager(config)

# Start ingestion job
job = ingestion_manager.start_ingestion_job(
    kb_id=kb['kb_id'],
    data_source_id=data_source['data_source_id']
)
print(f"Started ingestion job: {job['ingestion_job_id']}")

# Wait for ingestion to complete
ingestion_manager.wait_for_ingestion_job_complete(
    kb_id=kb['kb_id'],
    data_source_id=data_source['data_source_id'],
    ingestion_job_id=job['ingestion_job_id'],
    max_wait_seconds=3600
)
print("Ingestion completed successfully")
```

### Step 10: Test Retrieval

```python
from src.retrieval_api import RetrieveAPI
from src.retrieval_config import RetrievalConfiguration, RetrievalType

retrieval_api = RetrieveAPI(config)

# Create retrieval configuration
retrieval_config = RetrievalConfiguration(
    retrieval_type=RetrievalType.SEMANTIC,
    max_results=5
)

# Test retrieval
response = retrieval_api.retrieve(
    kb_id=kb['kb_id'],
    query='test query',
    retrieval_config=retrieval_config
)

print(f"Retrieved {len(response.results)} documents")
for result in response.results:
    print(f"  - Score: {result.relevance_score}, Content: {result.content[:100]}")
```

### Step 11: Test Retrieve and Generate

```python
from src.retrieve_and_generate_api import RetrieveAndGenerateAPI, GenerationConfig

rag_api = RetrieveAndGenerateAPI(config)

# Create generation configuration
gen_config = GenerationConfig(
    max_tokens=512,
    temperature=0.7
)

# Test retrieve and generate
response = rag_api.retrieve_and_generate(
    kb_id=kb['kb_id'],
    query='What is the main topic?',
    generation_config=gen_config
)

print(f"Generated response: {response.generated_text}")
print(f"Citations: {len(response.citations)}")
```

---

## Verification

### Step 1: Verify AWS Credentials

```bash
aws sts get-caller-identity
```

Expected output:
```json
{
    "UserId": "AIDAI...",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/username"
}
```

### Step 2: Verify Bedrock Access

```bash
aws bedrock list-foundation-models --region us-east-1
```

### Step 3: Verify S3 Bucket

```bash
aws s3 ls s3://my-bedrock-documents/
```

### Step 4: Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_knowledge_base_manager.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Step 5: Run Example Scripts

```bash
python examples/basic_retrieval.py
python examples/retrieve_and_generate.py
python examples/multi_source_ingestion.py
```

---

## Troubleshooting

### Issue: "Access Denied" Error

**Cause:** IAM permissions are insufficient

**Solution:**
1. Verify IAM user/role has required permissions
2. Check AWS credentials are correctly configured
3. Ensure Bedrock models are enabled in your account

```bash
aws iam get-user
aws bedrock list-foundation-models --region us-east-1
```

### Issue: "Knowledge Base Not Found" Error

**Cause:** Knowledge base ID is incorrect or doesn't exist

**Solution:**
1. Verify knowledge base was created successfully
2. Check knowledge base ID is correct
3. Ensure you're using the correct AWS region

```bash
aws bedrock-agent list-knowledge-bases --region us-east-1
```

### Issue: "Ingestion Job Failed" Error

**Cause:** Documents are malformed or incompatible

**Solution:**
1. Check document format (PDF, TXT, DOCX supported)
2. Verify document is not corrupted
3. Check document size is within limits
4. Review error logs for specific issues

```python
from src.error_handler import ErrorHandler
handler = ErrorHandler()
logs = handler.get_error_logs()
for log in logs:
    print(f"{log.timestamp}: {log.message}")
```

### Issue: "Rate Limit Exceeded" Error

**Cause:** Too many API requests

**Solution:**
1. Implement retry logic with exponential backoff
2. Reduce batch size for ingestion
3. Add delays between API calls
4. Contact AWS support to increase limits

```python
from src.retry_utils import retry_with_backoff

@retry_with_backoff(max_attempts=5, initial_delay=1, max_delay=30)
def call_api():
    # API call
    pass
```

### Issue: "OpenSearch Serverless Collection Not Found" Error

**Cause:** Collection doesn't exist or policies not applied

**Solution:**
1. Verify collection was created
2. Check security policies are properly configured
3. Ensure data access policy includes your role

```bash
aws aoss list-collections --region us-east-1
```

### Issue: "Timeout" Error During Ingestion

**Cause:** Large documents or slow network

**Solution:**
1. Increase timeout value
2. Reduce chunk size
3. Upload documents in smaller batches
4. Check network connectivity

```python
ingestion_manager.wait_for_ingestion_job_complete(
    kb_id=kb['kb_id'],
    data_source_id=data_source['data_source_id'],
    ingestion_job_id=job['ingestion_job_id'],
    max_wait_seconds=7200  # Increase timeout
)
```

### Issue: "Invalid Credentials" Error

**Cause:** AWS credentials are expired or incorrect

**Solution:**
1. Refresh AWS credentials
2. Verify credentials in ~/.aws/credentials
3. Check environment variables
4. Re-run `aws configure`

```bash
aws configure
aws sts get-caller-identity
```

---

## Cleanup

### Remove All Resources

```python
from src.knowledge_base_manager import BedrockKnowledgeBase
from src.s3_manager import S3Manager
from src.iam_manager import IAMManager
from src.oss_security import OSSSecurityManager

# Clean up knowledge base
kb_manager = BedrockKnowledgeBase(config)
kb_manager.cleanup_knowledge_base(kb_id, delete_s3_bucket=True, delete_iam_roles_and_policies=True)

# Clean up S3 bucket
s3_manager = S3Manager(config)
s3_manager.delete_bucket('my-bedrock-documents', force=True)

# Clean up IAM resources
iam_manager = IAMManager(config)
iam_manager.delete_role('bedrock-kb-role')

# Clean up OSS policies
oss_manager = OSSSecurityManager(config)
oss_manager.delete_encryption_policy('bedrock-encryption-policy')
oss_manager.delete_network_policy('bedrock-network-policy')
oss_manager.delete_data_access_policy('bedrock-data-access-policy')
```

### Using AWS CLI

```bash
# Delete S3 bucket
aws s3 rm s3://my-bedrock-documents --recursive
aws s3 rb s3://my-bedrock-documents

# Delete IAM role
aws iam delete-role --role-name bedrock-kb-role

# Delete policies
aws iam delete-policy --policy-arn arn:aws:iam::123456789012:policy/bedrock-models-policy
```

---

## Performance Optimization

### Document Ingestion

1. **Batch Upload:** Upload multiple documents at once
2. **Chunk Size:** Use 1024 tokens for optimal performance
3. **Parallel Processing:** Process multiple data sources simultaneously

### Retrieval

1. **Result Limit:** Set appropriate max_results (5-10 recommended)
2. **Relevance Threshold:** Filter by minimum relevance score
3. **Caching:** Cache frequently accessed configurations

### Generation

1. **Token Limit:** Set appropriate max_tokens (256-1024 recommended)
2. **Temperature:** Use 0.7 for balanced creativity and consistency
3. **Streaming:** Use streaming for long responses

---

## Security Best Practices

1. **Credentials:** Store in AWS Secrets Manager, never in code
2. **IAM Roles:** Use least privilege principle
3. **Encryption:** Enable encryption at rest and in transit
4. **Logging:** Enable CloudWatch logging for audit trails
5. **Network:** Use VPC endpoints for private connectivity
6. **Validation:** Validate all user inputs
7. **Monitoring:** Set up CloudWatch alarms for errors

---

## Monitoring and Logging

### CloudWatch Logs

```bash
# View logs
aws logs tail /aws/bedrock/knowledge-bases --follow

# Create log group
aws logs create-log-group --log-group-name /aws/bedrock/rag-system
```

### Metrics

Monitor these key metrics:

- Ingestion job success rate
- Average retrieval latency
- Generation latency
- Error rate
- API throttling events

### Alarms

Set up CloudWatch alarms for:

- Ingestion job failures
- High error rates
- API throttling
- Knowledge base unavailability

---

## Support and Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Amazon OpenSearch Serverless](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless.html)
- [AWS IAM Documentation](https://docs.aws.amazon.com/iam/)
- [GitHub Repository](https://github.com/your-repo)
- [Issue Tracker](https://github.com/your-repo/issues)

