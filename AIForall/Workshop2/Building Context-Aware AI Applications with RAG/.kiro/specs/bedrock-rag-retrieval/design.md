# Design Document: Bedrock RAG Retrieval System

## Overview

This design describes a comprehensive system for retrieving data from documents using AWS Bedrock and Knowledge Bases. The system enables organizations to ingest documents from multiple data sources (S3, Confluence, Sharepoint, Salesforce, Web), process them through a semantic search pipeline, and retrieve relevant information using foundation models.

The architecture follows the Retrieval-Augmented Generation (RAG) pattern, combining document retrieval with LLM-based response generation to provide accurate, source-grounded answers.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Data Sources Layer                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐│
│  │    S3    │ │Confluence│ │SharePoint│ │Salesforce│ │  Web   ││
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └────────┘│
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│              AWS Bedrock Knowledge Base                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Document Ingestion & Processing                        │  │
│  │  - Document chunking (FIXED_SIZE, CUSTOM)              │  │
│  │  - Text extraction and preprocessing                    │  │
│  │  - Embedding generation (Titan, Cohere)                │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│           Vector Store (OpenSearch Serverless)                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  - Vector embeddings storage                            │  │
│  │  - Semantic search index                                │  │
│  │  - Document metadata and references                     │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
┌───────▼──────────┐          ┌──────────▼────────┐
│  Retrieve API    │          │ Retrieve & Gen API│
│  - Vector search │          │ - Retrieval       │
│  - Metadata      │          │ - Generation      │
│  - Ranking       │          │ - Citations       │
└───────┬──────────┘          └──────────┬────────┘
        │                                 │
        └────────────────┬────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│         Foundation Models (Claude, Nova, Titan)                 │
│  - Response generation                                          │
│  - Embedding creation                                           │
│  - Reranking (Cohere)                                           │
└────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. Knowledge Base Manager
Responsible for creating, configuring, and managing the Bedrock Knowledge Base.

**Interface:**
```python
class BedrockKnowledgeBase:
    def __init__(kb_name, kb_description, data_sources, embedding_model, generation_model)
    def create_knowledge_base() -> KnowledgeBase
    def create_data_source(source_config) -> DataSource
    def start_ingestion_job() -> IngestionJob
    def get_knowledge_base_id() -> str
    def delete_kb(delete_s3_bucket, delete_iam_roles_and_policies)
```

### 2. Data Source Connector
Handles connections to various data sources and document retrieval.

**Supported Sources:**
- S3 buckets
- Confluence pages
- Sharepoint sites
- Salesforce instances
- Web crawlers

**Interface:**
```python
class DataSourceConnector:
    def connect(credentials) -> Connection
    def fetch_documents() -> List[Document]
    def validate_connection() -> bool
```

### 3. Document Ingestion Pipeline
Processes documents through chunking, embedding, and storage.

**Pipeline Steps:**
1. Document extraction (text, metadata)
2. Chunking (FIXED_SIZE or CUSTOM strategy)
3. Embedding generation
4. Vector storage in OpenSearch Serverless
5. Metadata indexing

### 4. Retrieval Engine
Provides two retrieval modes for different use cases.

**Retrieve API:**
- Vector similarity search
- Metadata filtering
- Result ranking by relevance score
- Configurable result limits

**Retrieve and Generate API:**
- Automatic document retrieval
- Foundation model response generation
- Source citation linking
- Streaming support

### 5. Vector Store (OpenSearch Serverless)
Manages vector embeddings and semantic search.

**Capabilities:**
- Vector similarity search
- Metadata filtering
- Scalable indexing
- Security policies (encryption, network, access)

### 6. IAM and Security Layer
Manages authentication, authorization, and resource access.

**Components:**
- Knowledge Base Execution Role
- S3 bucket policies
- Secrets Manager access
- CloudWatch logging
- OpenSearch Serverless policies

## Data Models

### Document
```python
{
    "id": str,
    "content": str,
    "metadata": {
        "source": str,
        "source_type": str,  # S3, CONFLUENCE, SHAREPOINT, etc.
        "created_date": datetime,
        "modified_date": datetime,
        "author": str,
        "tags": List[str]
    },
    "chunks": List[Chunk]
}
```

### Chunk
```python
{
    "id": str,
    "document_id": str,
    "content": str,
    "embedding": List[float],
    "metadata": {
        "chunk_index": int,
        "chunk_size": int,
        "overlap": int
    }
}
```

### RetrievalResult
```python
{
    "chunk_id": str,
    "content": str,
    "relevance_score": float,
    "location": str,
    "metadata": dict,
    "source_document": str
}
```

### GenerationResponse
```python
{
    "generated_text": str,
    "source_documents": List[RetrievalResult],
    "citations": List[Citation],
    "model_used": str,
    "generation_time_ms": int
}
```

### Citation
```python
{
    "text": str,
    "source_id": str,
    "source_location": str,
    "relevance_score": float
}
```

## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property 1: Knowledge Base Creation Idempotence
*For any* knowledge base configuration, creating the knowledge base multiple times with the same parameters should result in the same knowledge base being retrieved rather than creating duplicates.
**Validates: Requirements 1.1, 1.2, 1.3**

### Property 2: Document Ingestion Completeness
*For any* set of documents uploaded to a data source, after ingestion completes, all documents should be retrievable through the knowledge base search.
**Validates: Requirements 2.1, 2.2**

### Property 3: Retrieval Result Relevance
*For any* query submitted to the knowledge base, all returned documents should have a relevance score greater than zero and should be ranked in descending order by relevance score.
**Validates: Requirements 3.2, 3.3**

### Property 4: Retrieve and Generate Round Trip
*For any* query submitted to the Retrieve and Generate API, the generated response should include citations that reference documents actually retrieved from the knowledge base.
**Validates: Requirements 4.1, 4.2, 4.3, 4.4**

### Property 5: Metadata Filtering Consistency
*For any* retrieval operation with metadata filters applied, all returned results should satisfy the specified filter conditions.
**Validates: Requirements 5.2, 5.3**

### Property 6: Error Handling Stability
*For any* failed API call or malformed document, the system should catch the exception, log it appropriately, and continue processing without crashing.
**Validates: Requirements 6.1, 6.2, 6.3, 6.4**

## Error Handling

### API Error Handling
- Catch `ClientError` exceptions from boto3 calls
- Log error details with context (operation, parameters, timestamp)
- Implement retry logic with exponential backoff for transient failures
- Return meaningful error messages to callers

### Document Processing Errors
- Skip malformed documents and log the error
- Continue processing remaining documents
- Track failed documents for later review
- Provide summary of ingestion results

### Knowledge Base Unavailability
- Check knowledge base status before operations
- Implement health checks with configurable timeouts
- Return appropriate error messages when KB is unavailable
- Suggest retry strategies to callers

### Rate Limiting
- Implement exponential backoff for rate limit errors
- Track rate limit headers from API responses
- Queue requests when rate limits are approached
- Log rate limiting events for monitoring

## Testing Strategy

### Unit Testing
- Test individual components in isolation
- Verify correct behavior with valid inputs
- Test error handling with invalid inputs
- Mock AWS service calls where appropriate
- Focus on business logic and data transformations

### Property-Based Testing
The system will use **Hypothesis** (Python) for property-based testing with a minimum of 100 iterations per property.

Each property-based test will be tagged with:
```
**Feature: bedrock-rag-retrieval, Property {number}: {property_text}**
```

**Property-Based Test Coverage:**
- Property 1: Knowledge Base Creation Idempotence
  - Generate random KB configurations
  - Verify duplicate creation returns same KB
  
- Property 2: Document Ingestion Completeness
  - Generate random document sets
  - Verify all documents are retrievable after ingestion
  
- Property 3: Retrieval Result Relevance
  - Generate random queries and documents
  - Verify results are ranked by relevance score
  
- Property 4: Retrieve and Generate Round Trip
  - Generate random queries
  - Verify citations reference retrieved documents
  
- Property 5: Metadata Filtering Consistency
  - Generate random metadata filters
  - Verify all results satisfy filter conditions
  
- Property 6: Error Handling Stability
  - Generate random error conditions
  - Verify system handles errors gracefully

### Integration Testing
- Test end-to-end workflows (ingest → retrieve → generate)
- Verify data flows correctly through all components
- Test with real AWS services in test environment
- Validate multi-data source scenarios

### Performance Testing
- Measure ingestion throughput (documents/second)
- Measure retrieval latency (query → results)
- Measure generation latency (retrieval → response)
- Monitor memory usage during large ingestions
- Test with various document sizes and quantities

## Implementation Notes

### AWS Service Dependencies
- AWS Bedrock (foundation models, knowledge bases)
- AWS Bedrock Agent Runtime (retrieve and generate APIs)
- Amazon OpenSearch Serverless (vector storage)
- Amazon Neptune Analytics (optional, for graph-based RAG)
- Amazon S3 (document storage)
- AWS IAM (authentication and authorization)
- AWS Secrets Manager (credential storage for data sources)
- AWS CloudWatch (logging and monitoring)
- AWS Bedrock Data Automation (optional, for multi-modal document processing)

### Configuration Parameters
- Embedding model: `amazon.titan-embed-text-v2:0` (default)
- Generation model: `anthropic.claude-3-sonnet-20240229-v1:0` (default)
- Reranking model: `cohere.rerank-v3-5:0` (default)
- Chunking strategy: `FIXED_SIZE` (default) or `CUSTOM`
- Chunk size: 1024 tokens (default)
- Chunk overlap: 20% (default)
- Max retrieval results: 5 (default)

### Deployment Considerations
- All resources should be created in the same AWS region
- IAM roles and policies must be created before knowledge base
- OpenSearch Serverless collection creation takes 2-3 minutes
- Document ingestion is asynchronous and can take time based on document volume
- Implement monitoring and alerting for ingestion job status
