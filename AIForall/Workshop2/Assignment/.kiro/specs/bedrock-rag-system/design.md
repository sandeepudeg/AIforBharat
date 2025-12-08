# Design Document: AWS Bedrock RAG System

## Overview

The AWS Bedrock RAG System is a comprehensive solution for building Retrieval-Augmented Generation applications. It integrates AWS Bedrock (for LLMs and embeddings), OpenSearch Serverless (for vector storage), S3 (for document storage), and IAM (for security). The system provides a modular architecture with clear separation of concerns, enabling organizations to ingest documents, create searchable knowledge bases, and generate contextually accurate responses augmented with retrieved information.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Application Layer                            │
│  (Retrieval API, Generation API, Response Formatter)            │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                   Core Services Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Knowledge    │  │ Ingestion    │  │ Retrieval    │          │
│  │ Base Manager │  │ Manager      │  │ Manager      │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                  Infrastructure Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ AWS Config   │  │ IAM Manager  │  │ S3 Manager   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Vector Store │  │ Secrets Mgr  │  │ Health Check │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                    AWS Services                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Bedrock      │  │ OpenSearch   │  │ S3           │          │
│  │ (LLM, Embed) │  │ Serverless   │  │ (Documents)  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │ IAM          │  │ Secrets Mgr  │                            │
│  └──────────────┘  └──────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Ingestion Flow**: Documents → S3 → Bedrock KB → OpenSearch Serverless (embeddings)
2. **Retrieval Flow**: Query → Embedding → Vector Search → Ranked Results
3. **Generation Flow**: Query + Retrieved Docs → LLM → Response with Citations

## Components and Interfaces

### 1. AWS Configuration Manager (`aws_config.py`)

**Purpose**: Centralized AWS service initialization and credential management

**Key Methods**:
- `__init__(region: str)`: Initialize with AWS region
- `validate_credentials()`: Verify AWS credentials are valid
- `get_client(service_name: str)`: Get boto3 client for specified service
- `get_resource(resource_name: str)`: Get boto3 resource for specified service

**Responsibilities**:
- Manage AWS credentials from environment or Secrets Manager
- Initialize boto3 clients for all required services
- Handle region-specific configuration
- Validate connectivity to AWS services

### 2. IAM Manager (`iam_manager.py`)

**Purpose**: Create and manage IAM roles and policies for Bedrock operations

**Key Methods**:
- `create_knowledge_base_execution_role(role_name: str)`: Create KB execution role
- `create_foundation_model_policy(policy_name: str)`: Create policy for model access
- `create_s3_bucket_policy(policy_name: str, bucket_names: List[str])`: Create S3 access policy
- `attach_policy_to_role(role_name: str, policy_arn: str)`: Attach policy to role

**Responsibilities**:
- Create IAM roles with appropriate trust relationships
- Define and attach policies for least-privilege access
- Manage policy versions and updates
- Validate role configurations

### 3. OpenSearch Serverless Security Manager (`oss_security.py`)

**Purpose**: Configure security policies for OpenSearch Serverless vector store

**Key Methods**:
- `create_encryption_policy(policy_name: str)`: Create encryption policy
- `create_network_policy(policy_name: str, collection_names: List[str])`: Create network policy
- `create_data_access_policy(policy_name: str, collection_names: List[str], principal_arns: List[str])`: Create data access policy

**Responsibilities**:
- Define encryption policies for data at rest
- Configure network access policies
- Manage data access policies for principals
- Validate policy configurations

### 4. Vector Store Manager (`vector_store.py`)

**Purpose**: Manage OpenSearch Serverless collections and vector indices

**Key Methods**:
- `create_vector_index(collection_name: str, index_name: str, vector_dimension: int, similarity_metric: str)`: Create vector index
- `list_collections()`: List all OSS collections
- `get_collection_details(collection_name: str)`: Get collection configuration
- `delete_vector_index(collection_name: str, index_name: str)`: Delete vector index

**Responsibilities**:
- Create and manage vector indices
- Configure field mappings (vectorField, textField, metadataField)
- Handle collection lifecycle
- Manage index settings and similarity metrics

### 5. Knowledge Base Manager (`knowledge_base_manager.py`)

**Purpose**: Create and manage Bedrock Knowledge Bases

**Key Methods**:
- `create_knowledge_base(kb_name: str, kb_description: str, role_arn: str, vector_store_config: Dict, embedding_model: str, generation_model: str)`: Create KB
- `create_data_source(kb_id: str, data_source_name: str, data_source_config: Dict, data_source_type: str)`: Create data source
- `get_knowledge_base(kb_id: str)`: Get KB details
- `list_knowledge_bases()`: List all KBs
- `delete_knowledge_base(kb_id: str)`: Delete KB

**Responsibilities**:
- Create and configure knowledge bases
- Manage data sources (S3, web, etc.)
- Configure embedding and generation models
- Handle KB lifecycle and status tracking

### 6. Ingestion Manager (`ingestion_manager.py`)

**Purpose**: Manage document ingestion and processing

**Key Methods**:
- `ingest_documents(kb_id: str, data_source_id: str)`: Trigger document ingestion
- `get_ingestion_status(kb_id: str, data_source_id: str)`: Get ingestion status
- `list_ingestion_jobs(kb_id: str)`: List ingestion jobs

**Responsibilities**:
- Trigger document processing and embedding generation
- Monitor ingestion progress
- Handle ingestion errors and retries
- Track ingestion job status

### 7. Chunking Strategy (`chunking_strategy.py`)

**Purpose**: Implement configurable document chunking strategies

**Key Methods**:
- `chunk_document(document: str, chunk_size: int, overlap: int)`: Split document into chunks
- `chunk_with_metadata(document: str, metadata: Dict, strategy: str)`: Chunk with metadata preservation
- `get_chunk_references(chunks: List[str])`: Get source references for chunks

**Responsibilities**:
- Split documents into appropriately sized chunks
- Preserve document structure and metadata
- Support multiple chunking strategies (fixed-size, semantic, hierarchical)
- Maintain chunk-to-source mappings

### 8. Retrieval API (`retrieval_api.py`)

**Purpose**: Query knowledge base and retrieve relevant documents

**Key Methods**:
- `retrieve_documents(kb_id: str, query: str, max_results: int, filters: Dict)`: Retrieve relevant documents
- `search_with_metadata_filter(kb_id: str, query: str, filters: Dict)`: Search with metadata filtering
- `get_document_details(kb_id: str, document_id: str)`: Get document details

**Responsibilities**:
- Execute semantic search queries
- Return ranked results with relevance scores
- Support metadata-based filtering
- Handle query preprocessing and embedding

### 9. Response Formatter (`response_formatter.py`)

**Purpose**: Format retrieval results and generate responses with citations

**Key Methods**:
- `format_response(query: str, retrieved_docs: List[Dict], generated_text: str)`: Format response with citations
- `generate_citations(documents: List[Dict])`: Generate citation references
- `format_with_metadata(response: str, metadata: List[Dict])`: Format with metadata

**Responsibilities**:
- Combine retrieved documents with generated text
- Generate proper citations for sources
- Format responses for end-user consumption
- Track document references and chunk positions

### 10. Citation Generator (`citation_generator.py`)

**Purpose**: Create and manage citations for retrieved documents

**Key Methods**:
- `create_citation(document_id: str, chunk_position: int, source_url: str)`: Create citation
- `format_citation(citation: Dict)`: Format citation for display
- `validate_citation(citation: Dict)`: Validate citation integrity

**Responsibilities**:
- Generate citations from document references
- Track source documents and positions
- Format citations for various output formats
- Validate citation accuracy

### 11. Error Handler (`error_handler.py`)

**Purpose**: Centralized error handling and logging

**Key Methods**:
- `handle_api_error(error: Exception, context: str)`: Handle API errors
- `log_error(error: Exception, level: str, context: str)`: Log errors with context
- `get_error_message(error_code: str)`: Get user-friendly error message

**Responsibilities**:
- Catch and handle exceptions
- Log errors with sufficient detail
- Provide meaningful error messages
- Support error recovery strategies

### 12. Retry Utilities (`retry_utils.py`)

**Purpose**: Implement retry logic with exponential backoff

**Key Methods**:
- `retry_with_backoff(func: Callable, max_retries: int, base_delay: float)`: Execute function with retries
- `exponential_backoff(attempt: int, base_delay: float)`: Calculate backoff delay
- `is_retryable_error(error: Exception)`: Determine if error is retryable

**Responsibilities**:
- Implement exponential backoff retry logic
- Handle transient failures gracefully
- Support configurable retry parameters
- Track retry attempts and failures

### 13. Secrets Manager (`secrets_manager.py`)

**Purpose**: Manage sensitive configuration and credentials

**Key Methods**:
- `get_secret(secret_name: str)`: Retrieve secret from Secrets Manager
- `store_secret(secret_name: str, secret_value: str)`: Store secret
- `update_secret(secret_name: str, secret_value: str)`: Update secret

**Responsibilities**:
- Retrieve credentials from AWS Secrets Manager
- Prevent credential exposure in logs
- Support secret rotation
- Audit credential access

### 14. S3 Manager (`s3_manager.py`)

**Purpose**: Manage S3 bucket operations and document uploads

**Key Methods**:
- `create_bucket(bucket_name: str, region: str)`: Create S3 bucket
- `upload_file(bucket_name: str, file_path: str, s3_key: str)`: Upload single file
- `upload_directory(bucket_name: str, directory_path: str, prefix: str)`: Upload directory
- `list_objects(bucket_name: str, prefix: str)`: List bucket objects

**Responsibilities**:
- Create and configure S3 buckets
- Handle file uploads (single and batch)
- Manage bucket location constraints
- Verify bucket accessibility

### 15. Health Check Manager (`health_check_manager.py`)

**Purpose**: Monitor system health and component availability

**Key Methods**:
- `check_system_health()`: Check overall system health
- `check_service_connectivity(service_name: str)`: Check individual service connectivity
- `get_component_status()`: Get status of all components
- `generate_health_report()`: Generate comprehensive health report

**Responsibilities**:
- Verify connectivity to all AWS services
- Report component status (KB, vector store, data sources)
- Identify unavailable services
- Provide diagnostic information

### 16. Cleanup Manager (`cleanup_manager.py`)

**Purpose**: Manage resource cleanup and lifecycle

**Key Methods**:
- `cleanup_knowledge_base(kb_id: str)`: Clean up KB resources
- `cleanup_data_source(kb_id: str, data_source_id: str)`: Clean up data source
- `cleanup_all_resources()`: Clean up all resources

**Responsibilities**:
- Delete knowledge bases and data sources
- Clean up temporary resources
- Handle resource dependencies
- Validate cleanup completion

### 17. Data Source Connector (`data_source_connector.py`)

**Purpose**: Connect to various data sources (S3, web, etc.)

**Key Methods**:
- `connect_s3_source(bucket_name: str)`: Connect to S3 bucket
- `connect_web_source(url: str)`: Connect to web source
- `validate_connection()`: Validate data source connection

**Responsibilities**:
- Establish connections to data sources
- Validate data source accessibility
- Support multiple data source types
- Handle connection errors

### 18. Retrieval Configuration (`retrieval_config.py`)

**Purpose**: Manage retrieval parameters and settings

**Key Methods**:
- `get_retrieval_config()`: Get current retrieval configuration
- `set_retrieval_config(config: Dict)`: Set retrieval configuration
- `validate_config()`: Validate configuration parameters

**Responsibilities**:
- Store retrieval parameters (max results, filters, etc.)
- Manage similarity thresholds
- Configure ranking parameters
- Validate configuration values

## Data Models

### Knowledge Base Model
```python
{
    "kb_id": str,
    "kb_name": str,
    "kb_description": str,
    "status": str,  # ACTIVE, CREATING, DELETING, FAILED
    "role_arn": str,
    "created_at": datetime,
    "updated_at": datetime,
    "failure_reasons": List[str]
}
```

### Data Source Model
```python
{
    "data_source_id": str,
    "data_source_name": str,
    "kb_id": str,
    "status": str,  # AVAILABLE, DELETING, FAILED
    "data_source_type": str,  # S3, WEB, etc.
    "data_source_config": Dict,
    "created_at": datetime,
    "updated_at": datetime
}
```

### Document Chunk Model
```python
{
    "chunk_id": str,
    "document_id": str,
    "content": str,
    "embedding": List[float],
    "metadata": Dict,
    "source_reference": str,
    "chunk_position": int,
    "created_at": datetime
}
```

### Retrieval Result Model
```python
{
    "document_id": str,
    "chunk_id": str,
    "content": str,
    "relevance_score": float,
    "metadata": Dict,
    "source_reference": str
}
```

### Response Model
```python
{
    "query": str,
    "generated_text": str,
    "retrieved_documents": List[Dict],
    "citations": List[Dict],
    "confidence_score": float,
    "generated_at": datetime
}
```

## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property 1: AWS Credential Validation
*For any* AWS configuration with valid credentials, the system SHALL successfully establish connections to all required AWS services (IAM, S3, Bedrock, OpenSearch Serverless).
**Validates: Requirements 1.1**

### Property 2: IAM Role Creation with Permissions
*For any* IAM role creation request, the system SHALL create a role with all required permissions for Bedrock Knowledge Base operations attached.
**Validates: Requirements 1.2**

### Property 3: OpenSearch Security Policies
*For any* OpenSearch Serverless configuration, the system SHALL create all three required security policies (encryption, network, data access).
**Validates: Requirements 1.3**

### Property 4: S3 Bucket Configuration
*For any* S3 bucket creation request, the system SHALL configure the bucket with correct location constraints and verify accessibility.
**Validates: Requirements 1.4**

### Property 5: Knowledge Base Creation with Models
*For any* knowledge base creation request with specified embedding and generation models, the system SHALL create a KB with those models configured.
**Validates: Requirements 2.1**

### Property 6: Vector Store Field Mappings
*For any* vector store configuration, the system SHALL create collections with all required field mappings (vectorField, textField, metadataField).
**Validates: Requirements 2.2**

### Property 7: Vector Index Specifications
*For any* vector index creation request with specified dimensions and similarity metrics, the system SHALL create an index with those exact specifications.
**Validates: Requirements 2.3**

### Property 8: Knowledge Base Status Retrieval
*For any* knowledge base status retrieval request, the system SHALL return complete status information including all required fields.
**Validates: Requirements 2.4**

### Property 9: Data Source Registration
*For any* data source creation request, the system SHALL register the S3 bucket as a data source and make it appear in the knowledge base's data source list.
**Validates: Requirements 3.1**

### Property 10: Batch Document Upload
*For any* batch upload of multiple files to S3, the system SHALL upload all files with correct paths and make them accessible.
**Validates: Requirements 3.2**

### Property 11: Document Ingestion Triggering
*For any* document ingestion request, the system SHALL trigger document processing and embedding generation.
**Validates: Requirements 3.3**

### Property 12: Data Source Listing
*For any* data source listing request, the system SHALL return all registered data sources for a knowledge base with their current status.
**Validates: Requirements 3.4**

### Property 13: Document Chunking with Parameters
*For any* document and specified chunk size and overlap parameters, the system SHALL split the document into chunks respecting those parameters.
**Validates: Requirements 4.1**

### Property 14: Metadata Preservation in Chunks
*For any* document with metadata, the system SHALL preserve metadata associations during chunking.
**Validates: Requirements 4.2**

### Property 15: Document Type Chunking Strategies
*For any* document of a specific type, the system SHALL apply the appropriate chunking strategy for that type.
**Validates: Requirements 4.3**

### Property 16: Chunk Reference Integrity
*For any* retrieved chunk, the system SHALL maintain correct references to source documents and chunk positions.
**Validates: Requirements 4.4**

### Property 17: Semantic Search Retrieval
*For any* query and knowledge base, the system SHALL retrieve documents that are semantically similar to the query.
**Validates: Requirements 5.1**

### Property 18: Result Ranking by Relevance
*For any* retrieval result set, the system SHALL rank results by relevance score in descending order.
**Validates: Requirements 5.2**

### Property 19: Metadata-Based Filtering
*For any* metadata filter criteria, the system SHALL return only results matching those criteria.
**Validates: Requirements 5.3**

### Property 20: Query Processing and Embedding
*For any* query, the system SHALL preprocess the query and generate embeddings for semantic search.
**Validates: Requirements 5.4**

### Property 21: Response Generation with Retrieved Content
*For any* query with retrieved documents, the system SHALL generate a response combining both retrieved content and generated text.
**Validates: Requirements 6.1**

### Property 22: Citation Inclusion in Responses
*For any* response generated from retrieved documents, the system SHALL include citations linking to source documents.
**Validates: Requirements 6.2**

### Property 23: Citation Reference Tracking
*For any* citation, the system SHALL maintain correct document references and chunk positions.
**Validates: Requirements 6.3**

### Property 24: Response Source Attribution
*For any* response, the system SHALL format it with clear source attribution for all retrieved content.
**Validates: Requirements 6.4**

### Property 25: Exponential Backoff Retry Logic
*For any* failed API call, the system SHALL implement exponential backoff retry logic with configurable parameters.
**Validates: Requirements 7.1**

### Property 26: Error Logging with Detail
*For any* error occurrence, the system SHALL log detailed error information including context for debugging.
**Validates: Requirements 7.2**

### Property 27: Graceful Degradation on Service Unavailability
*For any* service unavailability, the system SHALL provide meaningful error messages and gracefully degrade.
**Validates: Requirements 7.3**

### Property 28: Input Validation and Error Messages
*For any* invalid input, the system SHALL reject it and provide clear validation error messages.
**Validates: Requirements 7.4**

### Property 29: Credential Storage in Secrets Manager
*For any* credential storage operation, the system SHALL store credentials in AWS Secrets Manager.
**Validates: Requirements 8.1**

### Property 30: Secure Credential Retrieval
*For any* credential access operation, the system SHALL retrieve credentials securely without exposing them in logs.
**Validates: Requirements 8.2**

### Property 31: Least-Privilege Access Enforcement
*For any* service configuration, the system SHALL enforce least-privilege access principles in IAM policies.
**Validates: Requirements 8.3**

### Property 32: Credential Usage Audit Trail
*For any* credential access, the system SHALL maintain audit trails of credential usage.
**Validates: Requirements 8.4**

### Property 33: System Health Verification
*For any* health check operation, the system SHALL verify connectivity to all required AWS services.
**Validates: Requirements 9.1**

### Property 34: Component Status Reporting
*For any* monitoring operation, the system SHALL report status of Knowledge Base, vector store, and data sources.
**Validates: Requirements 9.2**

### Property 35: Service Failure Detection
*For any* service failure, the system SHALL identify unavailable services and provide diagnostic information.
**Validates: Requirements 9.3**

### Property 36: Performance Metrics Logging
*For any* operation, the system SHALL record performance and operational metrics for analysis.
**Validates: Requirements 9.4**

### Property 37: Configuration Loading from Sources
*For any* system initialization, the system SHALL load configuration from environment variables and configuration files.
**Validates: Requirements 10.1**

### Property 38: Multi-Region Deployment Support
*For any* region configuration, the system SHALL support multi-region deployment with region-specific settings.
**Validates: Requirements 10.2**

### Property 39: Centralized Configuration Management
*For any* configuration management operation, the system SHALL provide centralized configuration for models, endpoints, and resource names.
**Validates: Requirements 10.3**

### Property 40: Configuration Validation Before Operation
*For any* system initialization, the system SHALL verify all required settings are present and valid before operation.
**Validates: Requirements 10.4**

## Error Handling

### Error Categories

1. **AWS Service Errors**: Handle API errors from Bedrock, S3, IAM, OpenSearch
2. **Authentication Errors**: Handle credential validation failures
3. **Configuration Errors**: Handle invalid or missing configuration
4. **Data Validation Errors**: Handle invalid input data
5. **Network Errors**: Handle transient network failures
6. **Resource Errors**: Handle resource not found or already exists errors

### Error Recovery Strategies

1. **Retry with Exponential Backoff**: For transient errors (network timeouts, rate limits)
2. **Graceful Degradation**: Provide partial functionality when services are unavailable
3. **Clear Error Messages**: Provide actionable error messages to users
4. **Logging and Monitoring**: Log all errors with context for debugging
5. **Circuit Breaker**: Stop retrying after threshold to prevent cascading failures

## Testing Strategy

### Unit Testing Approach

Unit tests verify specific examples and edge cases:
- Test individual component methods with known inputs and expected outputs
- Test error handling for invalid inputs
- Test boundary conditions (empty lists, null values, etc.)
- Test component interactions through mocked dependencies
- Focus on core logic and business rules

### Property-Based Testing Approach

Property-based tests verify universal properties that should hold across all inputs:
- Use Hypothesis (Python) for property-based testing
- Configure each property test to run minimum 100 iterations
- Generate random valid inputs within the problem domain
- Verify properties hold for all generated inputs
- Tag each test with the property number and requirements reference

### Testing Framework

- **Unit Testing**: pytest with fixtures for setup/teardown
- **Property-Based Testing**: Hypothesis library
- **Mocking**: unittest.mock for AWS service mocking
- **Test Organization**: Co-locate tests with source files using `.test.py` suffix

### Test Coverage Requirements

- All public methods must have corresponding tests
- All error paths must be tested
- All properties must have property-based tests
- Integration tests for component interactions
- End-to-end tests for complete workflows

### Property Test Annotation Format

Each property-based test MUST include:
```python
# **Feature: bedrock-rag-system, Property {number}: {property_text}**
# **Validates: Requirements {requirement_number}**
```

Example:
```python
# **Feature: bedrock-rag-system, Property 1: AWS Credential Validation**
# **Validates: Requirements 1.1**
def test_property_aws_credential_validation():
    # Test implementation
    pass
```

## Deployment Considerations

### Prerequisites
- AWS Account with appropriate permissions
- Python 3.8+
- boto3 library
- AWS CLI configured with credentials

### Configuration
- Set AWS_REGION environment variable
- Configure AWS credentials (IAM user or role)
- Set up Secrets Manager for sensitive configuration
- Create S3 bucket for documents

### Scaling Considerations
- OpenSearch Serverless auto-scales based on demand
- Bedrock Knowledge Base handles large document collections
- S3 supports unlimited document storage
- Consider chunking strategy for large documents

### Monitoring and Logging
- Enable CloudWatch logging for all AWS services
- Monitor Knowledge Base ingestion jobs
- Track vector search performance
- Monitor API call latencies and error rates
