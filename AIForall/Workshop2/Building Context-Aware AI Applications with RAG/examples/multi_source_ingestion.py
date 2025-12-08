"""
Example: Multi-Source Document Ingestion

This example demonstrates how to ingest documents from multiple data sources
(S3, Confluence, Sharepoint, Salesforce, Web) into a Bedrock Knowledge Base.

The example shows:
1. Initializing AWS configuration and managers
2. Creating a knowledge base with multiple data sources
3. Configuring different data source types
4. Starting ingestion jobs for each source
5. Monitoring ingestion progress
6. Handling errors and retries
"""

import os
import sys
import time
from typing import Dict, List, Optional

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config.aws_config import AWSConfig
from src.knowledge_base_manager import BedrockKnowledgeBase
from src.s3_manager import S3Manager
from src.iam_manager import IAMManager
from src.vector_store import VectorIndexManager
from src.data_source_connector import DataSourceType


def initialize_aws_config() -> AWSConfig:
    """
    Initialize AWS configuration.
    
    Returns:
        AWSConfig instance configured for the current AWS environment
    """
    region = os.getenv("AWS_REGION", "us-east-1")
    aws_config = AWSConfig(region=region)
    
    print(f"✓ AWS Configuration initialized")
    print(f"  Region: {aws_config.get_region()}")
    print(f"  Account ID: {aws_config.get_account_id()}")
    
    return aws_config


def create_knowledge_base(
    kb_manager: BedrockKnowledgeBase,
    kb_name: str,
    kb_description: str,
    role_arn: str,
    vector_store_config: Dict
) -> Dict:
    """
    Create a new knowledge base.
    
    Args:
        kb_manager: BedrockKnowledgeBase instance
        kb_name: Name for the knowledge base
        kb_description: Description of the knowledge base
        role_arn: ARN of the IAM role for KB execution
        vector_store_config: Configuration for the vector store
        
    Returns:
        Dictionary containing knowledge base information
    """
    print(f"\n📚 Creating Knowledge Base: {kb_name}")
    
    kb_info = kb_manager.create_knowledge_base(
        kb_name=kb_name,
        kb_description=kb_description,
        role_arn=role_arn,
        vector_store_config=vector_store_config,
        embedding_model="amazon.titan-embed-text-v2:0",
        generation_model="anthropic.claude-3-sonnet-20240229-v1:0",
        chunk_size=1024,
        chunk_overlap=20
    )
    
    print(f"✓ Knowledge Base created")
    print(f"  KB ID: {kb_info['kb_id']}")
    print(f"  Status: {kb_info['status']}")
    
    return kb_info


def create_s3_data_source(
    kb_manager: BedrockKnowledgeBase,
    kb_id: str,
    source_name: str,
    bucket_name: str,
    prefix: str = ""
) -> Dict:
    """
    Create an S3 data source within a knowledge base.
    
    Args:
        kb_manager: BedrockKnowledgeBase instance
        kb_id: ID of the knowledge base
        source_name: Name for the data source
        bucket_name: S3 bucket name
        prefix: Optional prefix for objects in the bucket
        
    Returns:
        Dictionary containing data source information
    """
    print(f"\n📦 Creating S3 Data Source: {source_name}")
    print(f"   Bucket: {bucket_name}")
    if prefix:
        print(f"   Prefix: {prefix}")
    
    s3_config = {
        "bucketArn": f"arn:aws:s3:::{bucket_name}",
        "inclusionPrefixes": [prefix] if prefix else []
    }
    
    ds_info = kb_manager.create_data_source(
        kb_id=kb_id,
        data_source_name=source_name,
        data_source_config=s3_config,
        data_source_type="S3"
    )
    
    print(f"✓ S3 Data Source created")
    print(f"  Data Source ID: {ds_info['data_source_id']}")
    print(f"  Status: {ds_info['status']}")
    
    return ds_info


def create_confluence_data_source(
    kb_manager: BedrockKnowledgeBase,
    kb_id: str,
    source_name: str,
    confluence_url: str,
    space_key: str,
    credentials_secret_arn: str
) -> Dict:
    """
    Create a Confluence data source within a knowledge base.
    
    Args:
        kb_manager: BedrockKnowledgeBase instance
        kb_id: ID of the knowledge base
        source_name: Name for the data source
        confluence_url: URL of the Confluence instance
        space_key: Confluence space key to ingest
        credentials_secret_arn: ARN of the secret containing Confluence credentials
        
    Returns:
        Dictionary containing data source information
    """
    print(f"\n📖 Creating Confluence Data Source: {source_name}")
    print(f"   URL: {confluence_url}")
    print(f"   Space Key: {space_key}")
    
    confluence_config = {
        "sourceConfiguration": {
            "hostUrl": confluence_url,
            "spaceConfiguration": {
                "spaceNames": [space_key]
            },
            "authConfiguration": {
                "basicAuthConfiguration": {
                    "secretArn": credentials_secret_arn
                }
            }
        }
    }
    
    ds_info = kb_manager.create_data_source(
        kb_id=kb_id,
        data_source_name=source_name,
        data_source_config=confluence_config,
        data_source_type="CONFLUENCE"
    )
    
    print(f"✓ Confluence Data Source created")
    print(f"  Data Source ID: {ds_info['data_source_id']}")
    print(f"  Status: {ds_info['status']}")
    
    return ds_info


def create_sharepoint_data_source(
    kb_manager: BedrockKnowledgeBase,
    kb_id: str,
    source_name: str,
    sharepoint_url: str,
    site_name: str,
    credentials_secret_arn: str
) -> Dict:
    """
    Create a Sharepoint data source within a knowledge base.
    
    Args:
        kb_manager: BedrockKnowledgeBase instance
        kb_id: ID of the knowledge base
        source_name: Name for the data source
        sharepoint_url: URL of the Sharepoint instance
        site_name: Sharepoint site name
        credentials_secret_arn: ARN of the secret containing Sharepoint credentials
        
    Returns:
        Dictionary containing data source information
    """
    print(f"\n📄 Creating Sharepoint Data Source: {source_name}")
    print(f"   URL: {sharepoint_url}")
    print(f"   Site: {site_name}")
    
    sharepoint_config = {
        "sourceConfiguration": {
            "hostUrl": sharepoint_url,
            "siteNames": [site_name],
            "authConfiguration": {
                "basicAuthConfiguration": {
                    "secretArn": credentials_secret_arn
                }
            }
        }
    }
    
    ds_info = kb_manager.create_data_source(
        kb_id=kb_id,
        data_source_name=source_name,
        data_source_config=sharepoint_config,
        data_source_type="SHAREPOINT"
    )
    
    print(f"✓ Sharepoint Data Source created")
    print(f"  Data Source ID: {ds_info['data_source_id']}")
    print(f"  Status: {ds_info['status']}")
    
    return ds_info


def start_ingestion_job(
    kb_manager: BedrockKnowledgeBase,
    kb_id: str,
    data_source_id: str,
    source_name: str
) -> Dict:
    """
    Start an ingestion job for a data source.
    
    Args:
        kb_manager: BedrockKnowledgeBase instance
        kb_id: ID of the knowledge base
        data_source_id: ID of the data source
        source_name: Name of the data source (for logging)
        
    Returns:
        Dictionary containing ingestion job information
    """
    print(f"\n⚙️  Starting ingestion job for: {source_name}")
    
    job_info = kb_manager.start_ingestion_job(
        kb_id=kb_id,
        data_source_id=data_source_id,
        description=f"Ingestion job for {source_name}"
    )
    
    print(f"✓ Ingestion job started")
    print(f"  Job ID: {job_info['ingestion_job_id']}")
    print(f"  Status: {job_info['status']}")
    
    return job_info


def monitor_ingestion_job(
    kb_manager: BedrockKnowledgeBase,
    kb_id: str,
    data_source_id: str,
    ingestion_job_id: str,
    source_name: str,
    max_wait_seconds: int = 300,
    check_interval_seconds: int = 10
) -> bool:
    """
    Monitor an ingestion job until completion.
    
    Args:
        kb_manager: BedrockKnowledgeBase instance
        kb_id: ID of the knowledge base
        data_source_id: ID of the data source
        ingestion_job_id: ID of the ingestion job
        source_name: Name of the data source (for logging)
        max_wait_seconds: Maximum time to wait for completion
        check_interval_seconds: Interval between status checks
        
    Returns:
        True if job completed successfully, False if timeout
    """
    print(f"\n⏳ Monitoring ingestion job for: {source_name}")
    
    elapsed = 0
    while elapsed < max_wait_seconds:
        job_info = kb_manager.get_ingestion_job(
            kb_id=kb_id,
            data_source_id=data_source_id,
            ingestion_job_id=ingestion_job_id
        )
        
        status = job_info.get("status")
        stats = job_info.get("statistics", {})
        
        print(f"  Status: {status}")
        if stats:
            print(f"  Documents processed: {stats.get('documentsProcessed', 0)}")
            print(f"  Documents failed: {stats.get('documentsFailed', 0)}")
        
        if status == "COMPLETED":
            print(f"✓ Ingestion job completed successfully")
            return True
        elif status == "FAILED":
            failure_reasons = job_info.get("failure_reasons", [])
            print(f"❌ Ingestion job failed: {failure_reasons}")
            return False
        
        time.sleep(check_interval_seconds)
        elapsed += check_interval_seconds
    
    print(f"⚠️  Ingestion job timeout after {max_wait_seconds} seconds")
    return False


def ingest_from_multiple_sources(
    kb_manager: BedrockKnowledgeBase,
    kb_id: str,
    data_sources: List[Dict]
) -> Dict:
    """
    Ingest documents from multiple data sources.
    
    Args:
        kb_manager: BedrockKnowledgeBase instance
        kb_id: ID of the knowledge base
        data_sources: List of data source configurations
        
    Returns:
        Dictionary with ingestion results for each source
    """
    print(f"\n[Multi-Source Ingestion]")
    print("=" * 80)
    
    ingestion_results = {}
    
    for source_config in data_sources:
        source_name = source_config.get("name")
        source_type = source_config.get("type")
        
        try:
            print(f"\n[{source_type}] Processing: {source_name}")
            
            # Create data source
            if source_type == "S3":
                ds_info = create_s3_data_source(
                    kb_manager=kb_manager,
                    kb_id=kb_id,
                    source_name=source_name,
                    bucket_name=source_config.get("bucket_name"),
                    prefix=source_config.get("prefix", "")
                )
            elif source_type == "CONFLUENCE":
                ds_info = create_confluence_data_source(
                    kb_manager=kb_manager,
                    kb_id=kb_id,
                    source_name=source_name,
                    confluence_url=source_config.get("url"),
                    space_key=source_config.get("space_key"),
                    credentials_secret_arn=source_config.get("credentials_secret_arn")
                )
            elif source_type == "SHAREPOINT":
                ds_info = create_sharepoint_data_source(
                    kb_manager=kb_manager,
                    kb_id=kb_id,
                    source_name=source_name,
                    sharepoint_url=source_config.get("url"),
                    site_name=source_config.get("site_name"),
                    credentials_secret_arn=source_config.get("credentials_secret_arn")
                )
            else:
                print(f"⚠️  Unsupported source type: {source_type}")
                continue
            
            # Start ingestion job
            job_info = start_ingestion_job(
                kb_manager=kb_manager,
                kb_id=kb_id,
                data_source_id=ds_info["data_source_id"],
                source_name=source_name
            )
            
            # Monitor ingestion job
            success = monitor_ingestion_job(
                kb_manager=kb_manager,
                kb_id=kb_id,
                data_source_id=ds_info["data_source_id"],
                ingestion_job_id=job_info["ingestion_job_id"],
                source_name=source_name,
                max_wait_seconds=300
            )
            
            ingestion_results[source_name] = {
                "type": source_type,
                "data_source_id": ds_info["data_source_id"],
                "job_id": job_info["ingestion_job_id"],
                "success": success
            }
        
        except Exception as e:
            print(f"❌ Error processing {source_name}: {str(e)}")
            ingestion_results[source_name] = {
                "type": source_type,
                "success": False,
                "error": str(e)
            }
    
    return ingestion_results


def display_ingestion_summary(results: Dict) -> None:
    """
    Display a summary of ingestion results.
    
    Args:
        results: Dictionary of ingestion results
    """
    print("\n" + "=" * 80)
    print("INGESTION SUMMARY")
    print("=" * 80)
    
    successful = sum(1 for r in results.values() if r.get("success"))
    failed = len(results) - successful
    
    print(f"\n✓ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {len(results)}")
    
    print(f"\nDetails:")
    for source_name, result in results.items():
        status = "✓" if result.get("success") else "❌"
        print(f"  {status} {source_name} ({result.get('type')})")
        if not result.get("success") and result.get("error"):
            print(f"     Error: {result.get('error')}")
    
    print("\n" + "=" * 80)


def main():
    """
    Main function demonstrating multi-source ingestion.
    """
    print("\n" + "=" * 80)
    print("BEDROCK RAG RETRIEVAL - MULTI-SOURCE INGESTION EXAMPLE")
    print("=" * 80)
    
    # Step 1: Initialize AWS configuration
    print("\n[Step 1] Initializing AWS Configuration")
    aws_config = initialize_aws_config()
    
    # Step 2: Create manager instances
    print("\n[Step 2] Creating Manager Instances")
    kb_manager = BedrockKnowledgeBase(aws_config)
    print("✓ Knowledge Base Manager created")
    
    # Step 3: Define knowledge base configuration
    print("\n[Step 3] Defining Knowledge Base Configuration")
    kb_name = os.getenv("KB_NAME", "multi-source-kb")
    kb_description = "Knowledge base with documents from multiple sources"
    
    # Get or create IAM role (simplified for example)
    role_arn = os.getenv("KB_ROLE_ARN", "arn:aws:iam::ACCOUNT_ID:role/BedrockKBRole")
    
    # Vector store configuration (OpenSearch Serverless)
    vector_store_config = {
        "collectionArn": os.getenv(
            "OSS_COLLECTION_ARN",
            "arn:aws:aoss:us-east-1:ACCOUNT_ID:collection/COLLECTION_ID"
        ),
        "fieldMapping": {
            "vectorField": "embedding",
            "textField": "content",
            "metadataField": "metadata"
        }
    }
    
    # Step 4: Create knowledge base
    print("\n[Step 4] Creating Knowledge Base")
    kb_info = create_knowledge_base(
        kb_manager=kb_manager,
        kb_name=kb_name,
        kb_description=kb_description,
        role_arn=role_arn,
        vector_store_config=vector_store_config
    )
    kb_id = kb_info["kb_id"]
    
    # Step 5: Define data sources
    print("\n[Step 5] Defining Data Sources")
    data_sources = [
        {
            "name": "Product Documentation",
            "type": "S3",
            "bucket_name": os.getenv("DOC_BUCKET", "my-docs-bucket"),
            "prefix": "documentation/"
        },
        {
            "name": "Internal Wiki",
            "type": "CONFLUENCE",
            "url": os.getenv("CONFLUENCE_URL", "https://confluence.example.com"),
            "space_key": "DOCS",
            "credentials_secret_arn": os.getenv(
                "CONFLUENCE_CREDS_ARN",
                "arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:confluence-creds"
            )
        },
        {
            "name": "Company Policies",
            "type": "SHAREPOINT",
            "url": os.getenv("SHAREPOINT_URL", "https://company.sharepoint.com"),
            "site_name": "Policies",
            "credentials_secret_arn": os.getenv(
                "SHAREPOINT_CREDS_ARN",
                "arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:sharepoint-creds"
            )
        }
    ]
    
    print(f"✓ Configured {len(data_sources)} data sources")
    for source in data_sources:
        print(f"  - {source['name']} ({source['type']})")
    
    # Step 6: Perform multi-source ingestion
    print("\n[Step 6] Performing Multi-Source Ingestion")
    ingestion_results = ingest_from_multiple_sources(
        kb_manager=kb_manager,
        kb_id=kb_id,
        data_sources=data_sources
    )
    
    # Step 7: Display summary
    print("\n[Step 7] Displaying Ingestion Summary")
    display_ingestion_summary(ingestion_results)
    
    # Step 8: List all data sources in the knowledge base
    print("\n[Step 8] Listing All Data Sources in Knowledge Base")
    all_data_sources = kb_manager.list_data_sources(kb_id)
    print(f"✓ Total data sources in KB: {len(all_data_sources)}")
    for ds in all_data_sources:
        print(f"  - {ds['data_source_name']} (Status: {ds['status']})")
    
    print("\n" + "=" * 80)
    print("✓ Multi-Source Ingestion Example Completed")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
