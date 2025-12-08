# Bedrock RAG Retrieval System - API Documentation

## Overview

This document provides comprehensive API documentation for the Bedrock RAG Retrieval System. The system enables document ingestion, semantic search, and retrieval-augmented generation using AWS Bedrock and Knowledge Bases.

---

## Table of Contents

1. [AWS Configuration](#aws-configuration)
2. [IAM Management](#iam-management)
3. [Secrets Management](#secrets-management)
4. [OpenSearch Serverless Security](#opensearch-serverless-security)
5. [Vector Store Management](#vector-store-management)
6. [S3 Management](#s3-management)
7. [Data Source Connector](#data-source-connector)
8. [Knowledge Base Management](#knowledge-base-management)
9. [Document Chunking](#document-chunking)
10. [Ingestion Management](#ingestion-management)
11. [Retrieval API](#retrieval-api)
12. [Retrieve and Generate API](#retrieve-and-generate-api)
13. [Error Handling](#error-handling)
14. [Retry Utilities](#retry-utilities)
15. [Response Formatting](#response-formatting)

---

## AWS Configuration

### Class: `AWSConfig`

Manages AWS client initialization, credential validation, and service access.

**Location:** `config/aws_config.py`

### Methods

#### `__init__(region: str = None, profile: str = None)`

Initialize AWS configuration with optional region and profile.

**Parameters:**
- `region` (str, optional): AWS region (default: us-east-1)
- `profile` (str, optional): AWS profile name for credentials

**Example:**
```python
from config.aws_config import AWSConfig

config = AWSConfig(region='us-west-2', profile='my-profile')
```

#### `get_client(service_name: str) -> boto3.client`

Get or create a boto3 client for the specified service.

**Parameters:**
- `service_name` (str): AWS service name (e.g., 'bedrock-agent', 's3', 'iam')

**Returns:**
- boto3 client instance

**Example:**
```python
bedrock_client = config.get_client('bedrock-agent')
s3_client = config.get_client('s3')
```

#### `get_account_id() -> str`

Get the AWS account ID.

**Returns:**
- Account ID string

**Example:**
```python
account_id = config.get_account_id()
print(f"Account ID: {account_id}")
```

#### `get_region() -> str`

Get the configured AWS region.

**Returns:**
- Region string

**Example:**
```python
region = config.get_region()
print(f"Region: {region}")
```

#### `validate_credentials() -> bool`

Validate that AWS credentials are properly configured.

**Returns:**
- True if credentials are valid

**Raises:**
- ValueError: If credentials are invalid

**Example:**
```python
if config.validate_credentials():
    print("Credentials are valid")
```

---

## IAM Management

### Class: `IAMManager`

Manages IAM roles and policies for Bedrock Knowledge Base operations.

**Location:** `src/iam_manager.py`

### Methods

#### `create_knowledge_base_execution_role(role_name: str) -> Dict[str, Any]`

Create an IAM role for Knowledge Base execution.

**Parameters:**
- `role_name` (str): Name for the execution role

**Returns:**
- Dictionary with role information:
  - `role_name`: str - Role name
  - `role_arn`: str - Role ARN
  - `role_id`: str - Role ID

**Example:**
```python
from src.iam_manager import IAMManager

manager = IAMManager(config)
role = manager.create_knowledge_base_execution_role('bedrock-kb-role')
print(f"Role ARN: {role['role_arn']}")
```

#### `create_foundation_model_policy(policy_name: str, model_ids: List[str] = None) -> Dict[str, Any]`

Create a policy allowing access to foundation models.

**Parameters:**
- `policy_name` (str): Name for the policy
- `model_ids` (List[str], optional): Specific model IDs to allow (default: all)

**Returns:**
- Dictionary with policy information

**Example:**
```python
policy = manager.create_foundation_model_policy(
    policy_name='bedrock-models-policy',
    model_ids=['anthropic.claude-3-sonnet-20240229-v1:0']
)
```

#### `create_s3_bucket_policy(policy_name: str, bucket_names: List[str]) -> Dict[str, Any]`

Create a policy allowing S3 bucket access.

**Parameters:**
- `policy_name` (str): Name for the policy
- `bucket_names` (List[str]): List of S3 bucket names

**Returns:**
- Dictionary with policy information

**Example:**
```python
policy = manager.create_s3_bucket_policy(
    policy_name='bedrock-s3-policy',
    bucket_names=['my-documents-bucket']
)
```

#### `attach_policy_to_role(role_name: str, policy_arn: str) -> bool`

Attach a policy to a role.

**Parameters:**
- `role_name` (str): Name of the role
- `policy_arn` (str): ARN of the policy

**Returns:**
- True if successful

**Example:**
```python
manager.attach_policy_to_role('bedrock-kb-role', policy_arn)
```

---

## Secrets Management

### Class: `SecretsManager`

Manages credentials for data sources in AWS Secrets Manager.

**Location:** `src/secrets_manager.py`

### Methods

#### `store_credential(secret_name: str, credential_data: Dict[str, Any], tags: Dict[str, str] = None) -> Dict[str, Any]`

Store credentials in Secrets Manager.

**Parameters:**
- `secret_name` (str): Name for the secret
- `credential_data` (Dict): Credential data to store
- `tags` (Dict, optional): Tags for the secret

**Returns:**
- Dictionary with secret information

**Example:**
```python
from src.secrets_manager import SecretsManager

manager = SecretsManager(config)
secret = manager.store_credential(
    secret_name='confluence-credentials',
    credential_data={
        'username': 'user@example.com',
        'api_token': 'your-api-token'
    },
    tags={'source': 'confluence'}
)
```

#### `retrieve_credential(secret_name: str, version_id: str = None) -> Dict[str, Any]`

Retrieve credentials from Secrets Manager.

**Parameters:**
- `secret_name` (str): Name of the secret
- `version_id` (str, optional): Specific version ID

**Returns:**
- Dictionary with credential data

**Example:**
```python
credentials = manager.retrieve_credential('confluence-credentials')
username = credentials['username']
```

#### `validate_credential(secret_name: str) -> bool`

Validate that a credential exists and is accessible.

**Parameters:**
- `secret_name` (str): Name of the secret

**Returns:**
- True if credential is valid

**Example:**
```python
if manager.validate_credential('confluence-credentials'):
    print("Credential is valid")
```

---

## OpenSearch Serverless Security

### Class: `OSSSecurityManager`

Manages OpenSearch Serverless security policies.

**Location:** `src/oss_security.py`

### Methods

#### `create_encryption_policy(policy_name: str, description: str = None) -> Dict[str, Any]`

Create an encryption policy for OpenSearch Serverless.

**Parameters:**
- `policy_name` (str): Name for the encryption policy
- `description` (str, optional): Policy description

**Returns:**
- Dictionary with policy information:
  - `policy_name`: str
  - `policy_version`: str
  - `created_date`: int
  - `policy_type`: str

**Example:**
```python
from src.oss_security import OSSSecurityManager

manager = OSSSecurityManager(config)
policy = manager.create_encryption_policy('bedrock-encryption-policy')
```

#### `create_network_policy(policy_name: str, collection_names: List[str], allow_public_access: bool = False) -> Dict[str, Any]`

Create a network policy for OpenSearch Serverless.

**Parameters:**
- `policy_name` (str): Name for the network policy
- `collection_names` (List[str]): Collection names to apply policy to
- `allow_public_access` (bool): Allow public access (default: False)

**Returns:**
- Dictionary with policy information

**Example:**
```python
policy = manager.create_network_policy(
    policy_name='bedrock-network-policy',
    collection_names=['bedrock-collection'],
    allow_public_access=False
)
```

#### `create_data_access_policy(policy_name: str, collection_names: List[str], principal_arns: List[str]) -> Dict[str, Any]`

Create a data access policy for OpenSearch Serverless.

**Parameters:**
- `policy_name` (str): Name for the data access policy
- `collection_names` (List[str]): Collection names
- `principal_arns` (List[str]): Principal ARNs to grant access

**Returns:**
- Dictionary with policy information

**Example:**
```python
policy = manager.create_data_access_policy(
    policy_name='bedrock-data-access-policy',
    collection_names=['bedrock-collection'],
    principal_arns=['arn:aws:iam::123456789012:role/bedrock-kb-role']
)
```

---

## Vector Store Management

### Class: `VectorIndexManager`

Manages vector indices in OpenSearch Serverless.

**Location:** `src/vector_store.py`

### Methods

#### `create_vector_index(index_name: str, dimension: int = 1536, similarity_metric: str = 'cosine') -> Dict[str, Any]`

Create a vector index for semantic search.

**Parameters:**
- `index_name` (str): Name for the index
- `dimension` (int): Vector dimension (default: 1536 for Titan)
- `similarity_metric` (str): Similarity metric ('cosine', 'euclidean', 'dot_product')

**Returns:**
- Dictionary with index information

**Example:**
```python
from src.vector_store import VectorIndexManager

manager = VectorIndexManager(config)
index = manager.create_vector_index(
    index_name='bedrock-vectors',
    dimension=1536,
    similarity_metric='cosine'
)
```

#### `search_by_vector(index_name: str, query_vector: List[float], k: int = 5, metadata_filters: Dict = None) -> List[Dict[str, Any]]`

Search for similar vectors.

**Parameters:**
- `index_name` (str): Name of the index
- `query_vector` (List[float]): Query vector
- `k` (int): Number of results to return
- `metadata_filters` (Dict, optional): Metadata filters

**Returns:**
- List of search results with scores

**Example:**
```python
results = manager.search_by_vector(
    index_name='bedrock-vectors',
    query_vector=[0.1, 0.2, 0.3, ...],
    k=5
)
```

#### `search_by_text(index_name: str, query_text: str, k: int = 5) -> List[Dict[str, Any]]`

Search using text query.

**Parameters:**
- `index_name` (str): Name of the index
- `query_text` (str): Text query
- `k` (int): Number of results

**Returns:**
- List of search results

**Example:**
```python
results = manager.search_by_text(
    index_name='bedrock-vectors',
    query_text='machine learning',
    k=5
)
```

---

## S3 Management

### Class: `S3Manager`

Manages S3 bucket operations for document storage.

**Location:** `src/s3_manager.py`

### Methods

#### `create_bucket(bucket_name: str, region: str = None) -> Dict[str, Any]`

Create an S3 bucket.

**Parameters:**
- `bucket_name` (str): Name for the bucket
- `region` (str, optional): AWS region

**Returns:**
- Dictionary with bucket information

**Example:**
```python
from src.s3_manager import S3Manager

manager = S3Manager(config)
bucket = manager.create_bucket('my-documents-bucket')
```

#### `upload_document(bucket_name: str, file_path: str, key: str = None) -> Dict[str, Any]`

Upload a document to S3.

**Parameters:**
- `bucket_name` (str): Target bucket name
- `file_path` (str): Local file path
- `key` (str, optional): S3 object key (default: filename)

**Returns:**
- Dictionary with upload information

**Example:**
```python
result = manager.upload_document(
    bucket_name='my-documents-bucket',
    file_path='/path/to/document.pdf'
)
```

#### `list_objects(bucket_name: str, prefix: str = None) -> List[Dict[str, Any]]`

List objects in a bucket.

**Parameters:**
- `bucket_name` (str): Bucket name
- `prefix` (str, optional): Object key prefix

**Returns:**
- List of object information

**Example:**
```python
objects = manager.list_objects('my-documents-bucket', prefix='documents/')
```

---

## Data Source Connector

### Class: `S3DataSourceConnector`

Connects to S3 data sources for document retrieval.

**Location:** `src/data_source_connector.py`

### Methods

#### `connect(bucket_name: str) -> bool`

Connect to an S3 data source.

**Parameters:**
- `bucket_name` (str): S3 bucket name

**Returns:**
- True if connection successful

**Example:**
```python
from src.data_source_connector import S3DataSourceConnector

connector = S3DataSourceConnector(s3_manager)
connector.connect('my-documents-bucket')
```

#### `fetch_documents(limit: int = None) -> List[Document]`

Fetch documents from the data source.

**Parameters:**
- `limit` (int, optional): Maximum number of documents

**Returns:**
- List of Document objects

**Example:**
```python
documents = connector.fetch_documents(limit=100)
for doc in documents:
    print(f"Document: {doc.id}, Content: {doc.content[:100]}")
```

#### `fetch_document_by_id(document_id: str) -> Document`

Fetch a specific document.

**Parameters:**
- `document_id` (str): Document ID

**Returns:**
- Document object

**Example:**
```python
doc = connector.fetch_document_by_id('doc-123')
```

---

## Knowledge Base Management

### Class: `BedrockKnowledgeBase`

Manages Bedrock Knowledge Base creation and configuration.

**Location:** `src/knowledge_base_manager.py`

### Methods

#### `create_knowledge_base(kb_name: str, kb_description: str = None, embedding_model: str = None, generation_model: str = None) -> Dict[str, Any]`

Create a new Knowledge Base.

**Parameters:**
- `kb_name` (str): Name for the knowledge base
- `kb_description` (str, optional): Description
- `embedding_model` (str, optional): Embedding model ID
- `generation_model` (str, optional): Generation model ID

**Returns:**
- Dictionary with KB information:
  - `kb_id`: str - Knowledge base ID
  - `kb_name`: str
  - `status`: str
  - `created_at`: str

**Example:**
```python
from src.knowledge_base_manager import BedrockKnowledgeBase

manager = BedrockKnowledgeBase(config)
kb = manager.create_knowledge_base(
    kb_name='my-knowledge-base',
    kb_description='My RAG knowledge base'
)
print(f"KB ID: {kb['kb_id']}")
```

#### `create_data_source(kb_id: str, source_name: str, source_type: str, source_config: Dict) -> Dict[str, Any]`

Create a data source in the knowledge base.

**Parameters:**
- `kb_id` (str): Knowledge base ID
- `source_name` (str): Name for the data source
- `source_type` (str): Type ('S3', 'CONFLUENCE', 'SHAREPOINT', 'SALESFORCE', 'WEB')
- `source_config` (Dict): Source-specific configuration

**Returns:**
- Dictionary with data source information

**Example:**
```python
data_source = manager.create_data_source(
    kb_id='kb-123',
    source_name='my-s3-source',
    source_type='S3',
    source_config={'bucket_name': 'my-documents-bucket'}
)
```

#### `start_ingestion_job(kb_id: str, data_source_id: str) -> Dict[str, Any]`

Start document ingestion.

**Parameters:**
- `kb_id` (str): Knowledge base ID
- `data_source_id` (str): Data source ID

**Returns:**
- Dictionary with ingestion job information

**Example:**
```python
job = manager.start_ingestion_job(kb_id='kb-123', data_source_id='ds-456')
print(f"Ingestion job started: {job['ingestion_job_id']}")
```

---

## Document Chunking

### Class: `FixedSizeChunkingStrategy`

Chunks documents into fixed-size pieces.

**Location:** `src/chunking_strategy.py`

### Methods

#### `__init__(chunk_size: int = 1024, chunk_overlap: int = 20, chunk_size_unit: str = 'tokens')`

Initialize chunking strategy.

**Parameters:**
- `chunk_size` (int): Size of each chunk
- `chunk_overlap` (int): Overlap between chunks
- `chunk_size_unit` (str): 'tokens' or 'characters'

**Example:**
```python
from src.chunking_strategy import FixedSizeChunkingStrategy

strategy = FixedSizeChunkingStrategy(
    chunk_size=1024,
    chunk_overlap=20,
    chunk_size_unit='tokens'
)
```

#### `chunk(document_id: str, content: str, metadata: Dict = None) -> List[Chunk]`

Chunk a document.

**Parameters:**
- `document_id` (str): Document ID
- `content` (str): Document content
- `metadata` (Dict, optional): Document metadata

**Returns:**
- List of Chunk objects

**Example:**
```python
chunks = strategy.chunk(
    document_id='doc-123',
    content='Long document content...',
    metadata={'source': 'pdf', 'author': 'John Doe'}
)
```

---

## Ingestion Management

### Class: `IngestionJobManager`

Manages document ingestion jobs.

**Location:** `src/ingestion_manager.py`

### Methods

#### `start_ingestion_job(kb_id: str, data_source_id: str, description: str = None) -> Dict[str, Any]`

Start an ingestion job.

**Parameters:**
- `kb_id` (str): Knowledge base ID
- `data_source_id` (str): Data source ID
- `description` (str, optional): Job description

**Returns:**
- Dictionary with job information

**Example:**
```python
from src.ingestion_manager import IngestionJobManager

manager = IngestionJobManager(config)
job = manager.start_ingestion_job(
    kb_id='kb-123',
    data_source_id='ds-456'
)
```

#### `get_ingestion_job(kb_id: str, data_source_id: str, ingestion_job_id: str) -> Dict[str, Any]`

Get ingestion job details.

**Parameters:**
- `kb_id` (str): Knowledge base ID
- `data_source_id` (str): Data source ID
- `ingestion_job_id` (str): Job ID

**Returns:**
- Dictionary with job details including statistics

**Example:**
```python
job = manager.get_ingestion_job(
    kb_id='kb-123',
    data_source_id='ds-456',
    ingestion_job_id='job-789'
)
print(f"Status: {job['status']}")
print(f"Documents processed: {job['statistics']['numberOfDocumentsProcessed']}")
```

#### `wait_for_ingestion_job_complete(kb_id: str, data_source_id: str, ingestion_job_id: str, max_wait_seconds: int = 3600) -> bool`

Wait for ingestion to complete.

**Parameters:**
- `kb_id` (str): Knowledge base ID
- `data_source_id` (str): Data source ID
- `ingestion_job_id` (str): Job ID
- `max_wait_seconds` (int): Maximum wait time

**Returns:**
- True if job completed successfully

**Example:**
```python
if manager.wait_for_ingestion_job_complete(
    kb_id='kb-123',
    data_source_id='ds-456',
    ingestion_job_id='job-789'
):
    print("Ingestion completed successfully")
```

---

## Retrieval API

### Class: `RetrieveAPI`

Retrieves documents from the knowledge base.

**Location:** `src/retrieval_api.py`

### Methods

#### `retrieve(kb_id: str, query: str, retrieval_config: RetrievalConfiguration = None) -> RetrievalResponse`

Retrieve documents matching a query.

**Parameters:**
- `kb_id` (str): Knowledge base ID
- `query` (str): Search query
- `retrieval_config` (RetrievalConfiguration, optional): Retrieval configuration

**Returns:**
- RetrievalResponse object with results

**Example:**
```python
from src.retrieval_api import RetrieveAPI
from src.retrieval_config import RetrievalConfiguration, RetrievalType

api = RetrieveAPI(config)
config = RetrievalConfiguration(
    retrieval_type=RetrievalType.SEMANTIC,
    max_results=5
)
response = api.retrieve(
    kb_id='kb-123',
    query='machine learning algorithms',
    retrieval_config=config
)

for result in response.results:
    print(f"Score: {result.relevance_score}, Content: {result.content[:100]}")
```

---

## Retrieve and Generate API

### Class: `RetrieveAndGenerateAPI`

Retrieves documents and generates responses using foundation models.

**Location:** `src/retrieve_and_generate_api.py`

### Methods

#### `retrieve_and_generate(kb_id: str, query: str, generation_config: GenerationConfig = None) -> GenerationResponse`

Retrieve documents and generate a response.

**Parameters:**
- `kb_id` (str): Knowledge base ID
- `query` (str): User query
- `generation_config` (GenerationConfig, optional): Generation configuration

**Returns:**
- GenerationResponse with generated text and citations

**Example:**
```python
from src.retrieve_and_generate_api import RetrieveAndGenerateAPI
from src.retrieve_and_generate_api import GenerationConfig

api = RetrieveAndGenerateAPI(config)
config = GenerationConfig(
    max_tokens=512,
    temperature=0.7
)
response = api.retrieve_and_generate(
    kb_id='kb-123',
    query='What is machine learning?',
    generation_config=config
)

print(f"Generated response: {response.generated_text}")
for citation in response.citations:
    print(f"Citation: {citation.text} (Source: {citation.source_id})")
```

#### `retrieve_and_generate_stream(kb_id: str, query: str, generation_config: GenerationConfig = None) -> Iterator[str]`

Stream generated response tokens.

**Parameters:**
- `kb_id` (str): Knowledge base ID
- `query` (str): User query
- `generation_config` (GenerationConfig, optional): Generation configuration

**Returns:**
- Iterator yielding response tokens

**Example:**
```python
for token in api.retrieve_and_generate_stream(
    kb_id='kb-123',
    query='What is machine learning?'
):
    print(token, end='', flush=True)
```

---

## Error Handling

### Class: `ErrorHandler`

Manages error logging and reporting.

**Location:** `src/error_handler.py`

### Methods

#### `handle_malformed_document(document_id: str, error_message: str, severity: ErrorSeverity = ErrorSeverity.WARNING)`

Log a malformed document error.

**Parameters:**
- `document_id` (str): Document ID
- `error_message` (str): Error description
- `severity` (ErrorSeverity): Error severity level

**Example:**
```python
from src.error_handler import ErrorHandler, ErrorSeverity

handler = ErrorHandler()
handler.handle_malformed_document(
    document_id='doc-123',
    error_message='Invalid PDF format',
    severity=ErrorSeverity.WARNING
)
```

#### `handle_api_error(error: Exception, operation: str, retryable: bool = False)`

Log an API error.

**Parameters:**
- `error` (Exception): The exception
- `operation` (str): Operation that failed
- `retryable` (bool): Whether the error is retryable

**Example:**
```python
try:
    # API call
    pass
except Exception as e:
    handler.handle_api_error(e, 'retrieve_documents', retryable=True)
```

#### `get_error_logs() -> List[ErrorLog]`

Get all error logs.

**Returns:**
- List of ErrorLog objects

**Example:**
```python
logs = handler.get_error_logs()
for log in logs:
    print(f"{log.timestamp}: {log.error_type} - {log.message}")
```

---

## Retry Utilities

### Function: `retry_with_backoff`

Decorator for retrying functions with exponential backoff.

**Location:** `src/retry_utils.py`

**Parameters:**
- `max_attempts` (int): Maximum retry attempts
- `initial_delay` (float): Initial delay in seconds
- `max_delay` (float): Maximum delay in seconds
- `backoff_factor` (float): Backoff multiplier

**Example:**
```python
from src.retry_utils import retry_with_backoff

@retry_with_backoff(max_attempts=3, initial_delay=1, max_delay=10)
def call_bedrock_api():
    # API call that might fail
    pass

result = call_bedrock_api()
```

---

## Response Formatting

### Class: `ResponseFormatter`

Formats retrieval and generation responses.

**Location:** `src/response_formatter.py`

### Methods

#### `format_retrieval_response(response: RetrievalResponse, format_type: ResponseFormat = ResponseFormat.JSON) -> str`

Format retrieval response.

**Parameters:**
- `response` (RetrievalResponse): Retrieval response
- `format_type` (ResponseFormat): Output format (JSON, MARKDOWN, TEXT)

**Returns:**
- Formatted response string

**Example:**
```python
from src.response_formatter import ResponseFormatter, ResponseFormat

formatter = ResponseFormatter()
json_response = formatter.format_retrieval_response(
    response,
    format_type=ResponseFormat.JSON
)
```

#### `format_generation_response(response: GenerationResponse, format_type: ResponseFormat = ResponseFormat.MARKDOWN) -> str`

Format generation response.

**Parameters:**
- `response` (GenerationResponse): Generation response
- `format_type` (ResponseFormat): Output format

**Returns:**
- Formatted response string

**Example:**
```python
markdown_response = formatter.format_generation_response(
    response,
    format_type=ResponseFormat.MARKDOWN
)
```

---

## Configuration Options

### Embedding Models

- `amazon.titan-embed-text-v2:0` (default, 1536 dimensions)
- `cohere.embed-english-v3` (1024 dimensions)

### Generation Models

- `anthropic.claude-3-sonnet-20240229-v1:0` (default)
- `anthropic.claude-3-opus-20240229-v1:0`
- `anthropic.claude-3-haiku-20240307-v1:0`

### Retrieval Types

- `SEMANTIC`: Vector similarity search
- `KEYWORD`: Text-based search
- `HYBRID`: Combined semantic and keyword search

### Response Formats

- `JSON`: JSON format
- `MARKDOWN`: Markdown format
- `TEXT`: Plain text format
- `DICT`: Python dictionary

---

## Usage Examples

### Complete Workflow Example

```python
from config.aws_config import AWSConfig
from src.knowledge_base_manager import BedrockKnowledgeBase
from src.s3_manager import S3Manager
from src.iam_manager import IAMManager
from src.retrieve_and_generate_api import RetrieveAndGenerateAPI

# Initialize AWS configuration
config = AWSConfig(region='us-east-1')

# Create IAM role
iam_manager = IAMManager(config)
role = iam_manager.create_knowledge_base_execution_role('bedrock-kb-role')

# Create S3 bucket
s3_manager = S3Manager(config)
bucket = s3_manager.create_bucket('my-documents-bucket')

# Upload documents
s3_manager.upload_document('my-documents-bucket', '/path/to/document.pdf')

# Create Knowledge Base
kb_manager = BedrockKnowledgeBase(config)
kb = kb_manager.create_knowledge_base('my-kb', 'My knowledge base')

# Create data source
data_source = kb_manager.create_data_source(
    kb_id=kb['kb_id'],
    source_name='my-s3-source',
    source_type='S3',
    source_config={'bucket_name': 'my-documents-bucket'}
)

# Start ingestion
job = kb_manager.start_ingestion_job(kb['kb_id'], data_source['data_source_id'])

# Wait for ingestion to complete
from src.ingestion_manager import IngestionJobManager
ingestion_manager = IngestionJobManager(config)
ingestion_manager.wait_for_ingestion_job_complete(
    kb['kb_id'],
    data_source['data_source_id'],
    job['ingestion_job_id']
)

# Retrieve and generate
rag_api = RetrieveAndGenerateAPI(config)
response = rag_api.retrieve_and_generate(
    kb_id=kb['kb_id'],
    query='What is the main topic of the documents?'
)

print(f"Response: {response.generated_text}")
for citation in response.citations:
    print(f"Citation: {citation.text}")
```

---

## Error Handling Best Practices

1. Always validate inputs before API calls
2. Use retry logic for transient failures
3. Log errors with appropriate severity levels
4. Provide meaningful error messages to users
5. Handle rate limiting gracefully

---

## Performance Considerations

1. Batch document uploads when possible
2. Use appropriate chunk sizes (1024 tokens recommended)
3. Configure retrieval limits based on use case
4. Monitor ingestion job progress
5. Cache frequently accessed configurations

---

## Security Best Practices

1. Store credentials in AWS Secrets Manager
2. Use IAM roles with least privilege
3. Enable encryption for data at rest and in transit
4. Validate all user inputs
5. Monitor API access and errors

