# Ingestion Data Guide - Bedrock RAG Retrieval System

## Overview

For ingestion in the Bedrock RAG Retrieval System, the workshop provides **synthetic sample data** that you can use for testing and demonstration purposes.

---

## Available Sample Data

The workshop includes the following sample datasets in:
`rag-workshop-amazon-bedrock-knowledge-bases/synthetic_dataset/`

### 1. **octank_financial_10K.pdf** (Primary Document)
- **Type**: PDF Document
- **Content**: Synthetic financial 10-K report
- **Size**: ~2-3 MB
- **Use Case**: Financial document analysis, Q&A about company financials
- **Format**: Structured financial document with sections, tables, and metrics

### 2. **podcastdemo.mp3** (Audio File)
- **Type**: Audio/Podcast
- **Content**: Synthetic podcast content
- **Use Case**: Multi-modal RAG (audio transcription and analysis)
- **Note**: Requires Bedrock Data Automation for processing

### 3. **bda.m4v** (Video File)
- **Type**: Video
- **Content**: Synthetic video content
- **Use Case**: Multi-modal RAG (video transcription and analysis)
- **Note**: Requires Bedrock Data Automation for processing

---

## How to Use Sample Data for Ingestion

### Step 1: Copy Sample Data to S3

```python
import shutil
from src.s3_manager import S3Manager
from config.aws_config import AWSConfig

# Initialize managers
config = AWSConfig(region='us-east-1')
s3_manager = S3Manager(config)

# Copy sample PDF to S3
sample_pdf = 'rag-workshop-amazon-bedrock-knowledge-bases/synthetic_dataset/octank_financial_10K.pdf'
s3_manager.upload_document('my-bedrock-documents', sample_pdf)
print("✓ Sample PDF uploaded to S3")
```

### Step 2: Start Ingestion with Sample Data

```python
from src.ingestion_manager import IngestionJobManager

ingestion_manager = IngestionJobManager(config)

# Start ingestion job
job = ingestion_manager.start_ingestion_job(
    kb_id=kb_id,
    data_source_id=data_source_id
)

# Wait for completion
ingestion_manager.wait_for_ingestion_job_complete(
    kb_id=kb_id,
    data_source_id=data_source_id,
    ingestion_job_id=job['ingestion_job_id'],
    max_wait_seconds=3600
)
print("✓ Ingestion completed with sample data")
```

### Step 3: Query the Ingested Data

```python
from src.retrieval_api import RetrieveAPI
from src.retrieval_config import RetrievalConfiguration, RetrievalType

retrieval_api = RetrieveAPI(config)
retrieval_config = RetrievalConfiguration(
    retrieval_type=RetrievalType.SEMANTIC,
    max_results=5
)

# Query about financial information
response = retrieval_api.retrieve(
    kb_id=kb_id,
    query='What are the company revenues?',
    retrieval_config=retrieval_config
)

print(f"Retrieved {len(response.results)} documents")
for result in response.results:
    print(f"Score: {result.relevance_score:.2f}")
    print(f"Content: {result.content[:200]}...")
```

---

## Sample Queries for Testing

### Financial Document Queries (octank_financial_10K.pdf)

```python
queries = [
    "What are the total revenues?",
    "What is the net income?",
    "What are the main business segments?",
    "What are the risk factors?",
    "What is the company's strategy?",
    "What are the operating expenses?",
    "What is the gross profit margin?",
    "What are the key financial metrics?"
]

for query in queries:
    response = retrieval_api.retrieve(
        kb_id=kb_id,
        query=query,
        retrieval_config=retrieval_config
    )
    print(f"\nQuery: {query}")
    print(f"Results: {len(response.results)}")
```

---

## Data Ingestion Process

### What Happens During Ingestion

1. **Document Retrieval**: Bedrock retrieves documents from the data source (S3 bucket)
2. **Chunking**: Documents are split into smaller chunks (default: 1024 tokens)
3. **Embedding Generation**: Each chunk is converted to embeddings using Titan Embeddings
4. **Vector Storage**: Embeddings are stored in OpenSearch Serverless
5. **Metadata Indexing**: Document metadata is indexed for filtering

### Ingestion Timeline

- **Small documents (< 1 MB)**: 2-5 minutes
- **Medium documents (1-10 MB)**: 5-15 minutes
- **Large documents (> 10 MB)**: 15-60 minutes

---

## Using Your Own Data

### Supported File Formats

```
Text Documents:
- .pdf (PDF files)
- .txt (Plain text)
- .docx (Microsoft Word)
- .doc (Microsoft Word 97-2003)
- .html (HTML files)
- .md (Markdown)

Structured Data:
- .csv (Comma-separated values)
- .json (JSON files)
- .xml (XML files)

Presentations:
- .pptx (PowerPoint)
- .ppt (PowerPoint 97-2003)

Spreadsheets:
- .xlsx (Excel)
- .xls (Excel 97-2003)

Multi-modal (with BDA):
- .mp3, .wav (Audio)
- .mp4, .m4v (Video)
- .jpg, .png (Images)
```

### Upload Your Own Documents

```python
# Upload a single document
s3_manager.upload_document(
    bucket_name='my-bedrock-documents',
    file_path='/path/to/your/document.pdf'
)

# Upload multiple documents
documents = [
    '/path/to/document1.pdf',
    '/path/to/document2.docx',
    '/path/to/document3.txt'
]

for doc in documents:
    s3_manager.upload_document('my-bedrock-documents', doc)
    print(f"✓ Uploaded {doc}")
```

---

## Data Ingestion Configuration

### Chunking Strategy

```python
# FIXED_SIZE chunking (default)
kb = kb_manager.create_knowledge_base(
    kb_name='my-kb',
    chunking_strategy='FIXED_SIZE',
    chunk_size=1024,  # tokens
    chunk_overlap=20  # percentage
)

# CUSTOM chunking (requires Lambda)
kb = kb_manager.create_knowledge_base(
    kb_name='my-kb',
    chunking_strategy='CUSTOM',
    lambda_function_name='my-chunking-function'
)
```

### Embedding Models

```python
# Available embedding models
embedding_models = [
    'amazon.titan-embed-text-v2:0',      # Recommended
    'amazon.titan-embed-text-v1',
    'cohere.embed-english-v3',
    'cohere.embed-multilingual-v3'
]

kb = kb_manager.create_knowledge_base(
    kb_name='my-kb',
    embedding_model='amazon.titan-embed-text-v2:0'
)
```

---

## Monitoring Ingestion

### Check Ingestion Status

```python
# Get ingestion job status
job_status = ingestion_manager.get_ingestion_job_status(
    kb_id=kb_id,
    data_source_id=data_source_id,
    ingestion_job_id=ingestion_job_id
)

print(f"Status: {job_status['status']}")
print(f"Documents processed: {job_status['documents_processed']}")
print(f"Documents failed: {job_status['documents_failed']}")
```

### Get Ingestion Results

```python
# Get detailed ingestion results
results = ingestion_manager.get_ingestion_job_results(
    kb_id=kb_id,
    data_source_id=data_source_id,
    ingestion_job_id=ingestion_job_id
)

print(f"Total documents: {results['total_documents']}")
print(f"Successfully ingested: {results['successful_documents']}")
print(f"Failed documents: {results['failed_documents']}")
```

---

## Best Practices for Data Ingestion

### 1. Document Preparation
- Ensure documents are in supported formats
- Remove sensitive information before ingestion
- Validate document integrity
- Organize documents logically

### 2. Batch Ingestion
```python
# Ingest documents in batches
batch_size = 10
documents = get_all_documents()

for i in range(0, len(documents), batch_size):
    batch = documents[i:i+batch_size]
    for doc in batch:
        s3_manager.upload_document('my-bedrock-documents', doc)
    
    # Start ingestion for batch
    job = ingestion_manager.start_ingestion_job(kb_id, data_source_id)
    ingestion_manager.wait_for_ingestion_job_complete(...)
```

### 3. Error Handling
```python
from src.error_handler import ErrorHandler

error_handler = ErrorHandler()

try:
    job = ingestion_manager.start_ingestion_job(kb_id, data_source_id)
    ingestion_manager.wait_for_ingestion_job_complete(...)
except Exception as e:
    error_handler.handle_ingestion_error(str(e))
    logs = error_handler.get_error_logs()
    for log in logs:
        print(f"{log.timestamp}: {log.message}")
```

### 4. Metadata Management
```python
# Add metadata to documents
metadata = {
    'source': 'financial_reports',
    'year': 2024,
    'department': 'finance',
    'confidential': False
}

# Use metadata for filtering during retrieval
retrieval_config = RetrievalConfiguration(
    retrieval_type=RetrievalType.SEMANTIC,
    max_results=5,
    metadata_filters={
        'year': 2024,
        'department': 'finance'
    }
)
```

---

## Troubleshooting Ingestion Issues

### Issue: Ingestion Job Fails

**Cause**: Document format not supported or corrupted

**Solution**:
```python
# Validate document before upload
import os

def validate_document(file_path):
    supported_formats = ['.pdf', '.txt', '.docx', '.html', '.md']
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext not in supported_formats:
        raise ValueError(f"Unsupported format: {ext}")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if os.path.getsize(file_path) == 0:
        raise ValueError("File is empty")
    
    return True

# Use validation
validate_document('/path/to/document.pdf')
s3_manager.upload_document('my-bedrock-documents', '/path/to/document.pdf')
```

### Issue: Ingestion Takes Too Long

**Cause**: Large documents or network issues

**Solution**:
- Split large documents into smaller files
- Increase timeout value
- Check network connectivity
- Reduce chunk size

```python
# Increase timeout
ingestion_manager.wait_for_ingestion_job_complete(
    kb_id=kb_id,
    data_source_id=data_source_id,
    ingestion_job_id=ingestion_job_id,
    max_wait_seconds=7200  # 2 hours
)
```

### Issue: No Results After Ingestion

**Cause**: Documents not properly indexed or query doesn't match content

**Solution**:
```python
# Verify ingestion completed
job_status = ingestion_manager.get_ingestion_job_status(...)
if job_status['status'] != 'COMPLETE':
    print("Ingestion not complete")
    return

# Try different query
queries = [
    'financial information',
    'revenue',
    'company',
    'report'
]

for query in queries:
    response = retrieval_api.retrieve(kb_id, query, retrieval_config)
    if response.results:
        print(f"Found results for: {query}")
        break
```

---

## Summary

**For your AWS workshop:**

1. **Use the provided sample data**: `octank_financial_10K.pdf`
2. **Upload to S3**: Use `s3_manager.upload_document()`
3. **Start ingestion**: Use `ingestion_manager.start_ingestion_job()`
4. **Wait for completion**: Use `wait_for_ingestion_job_complete()`
5. **Query results**: Use `retrieval_api.retrieve()`

All sample data is located in:
```
rag-workshop-amazon-bedrock-knowledge-bases/synthetic_dataset/
```

Ready to ingest! 🚀
