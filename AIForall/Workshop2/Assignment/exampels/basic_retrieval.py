"""
Example: Basic Retrieval API Usage

This example demonstrates how to use the Retrieve API to search for relevant
documents in a Bedrock Knowledge Base using semantic search.

The example shows:
1. Initializing AWS configuration
2. Creating a Retrieve API instance
3. Performing semantic search queries
4. Processing and displaying results
"""

import os
import sys
from typing import List

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config.aws_config import AWSConfig
from src.retrieval_api import RetrieveAPI, RetrievalConfig, RetrievalType, RetrievalResult
from src.response_formatter import ResponseFormatter, ResponseFormat


def initialize_aws_config() -> AWSConfig:
    """
    Initialize AWS configuration.
    
    Returns:
        AWSConfig instance configured for the current AWS environment
    """
    # Get AWS configuration from environment or use defaults
    region = os.getenv("AWS_REGION", "us-east-1")
    
    # Create AWS config instance
    aws_config = AWSConfig(region=region)
    
    print(f"✓ AWS Configuration initialized")
    print(f"  Region: {aws_config.get_region()}")
    print(f"  Account ID: {aws_config.get_account_id()}")
    
    return aws_config


def perform_semantic_search(
    retrieve_api: RetrieveAPI,
    knowledge_base_id: str,
    query: str,
    max_results: int = 5
) -> List[RetrievalResult]:
    """
    Perform a semantic search query.
    
    Args:
        retrieve_api: RetrieveAPI instance
        knowledge_base_id: ID of the knowledge base to search
        query: Search query string
        max_results: Maximum number of results to return
        
    Returns:
        List of RetrievalResult objects
    """
    print(f"\n📚 Performing semantic search...")
    print(f"   Query: '{query}'")
    print(f"   Max Results: {max_results}")
    
    # Create retrieval configuration
    config = RetrievalConfig(
        max_results=max_results,
        retrieval_type=RetrievalType.SEMANTIC,
        min_relevance_score=0.0
    )
    
    # Perform retrieval
    results = retrieve_api.retrieve(
        knowledge_base_id=knowledge_base_id,
        query=query,
        config=config
    )
    
    print(f"✓ Retrieved {len(results)} results")
    
    return results


def display_results(results: List[RetrievalResult]) -> None:
    """
    Display retrieval results in a formatted way.
    
    Args:
        results: List of RetrievalResult objects to display
    """
    if not results:
        print("\n⚠️  No results found")
        return
    
    print("\n" + "=" * 80)
    print("RETRIEVAL RESULTS")
    print("=" * 80)
    
    for i, result in enumerate(results, 1):
        print(f"\n[Result {i}]")
        print(f"  Relevance Score: {result.relevance_score:.2%}")
        print(f"  Source Document: {result.source_document}")
        print(f"  Location: {result.location}")
        print(f"  Content Preview: {result.content[:200]}...")
        
        if result.metadata:
            print(f"  Metadata:")
            for key, value in result.metadata.items():
                print(f"    - {key}: {value}")
    
    print("\n" + "=" * 80)


def perform_filtered_search(
    retrieve_api: RetrieveAPI,
    knowledge_base_id: str,
    query: str,
    metadata_filters: dict,
    max_results: int = 5
) -> List[RetrievalResult]:
    """
    Perform a semantic search with metadata filtering.
    
    Args:
        retrieve_api: RetrieveAPI instance
        knowledge_base_id: ID of the knowledge base to search
        query: Search query string
        metadata_filters: Dictionary of metadata filters to apply
        max_results: Maximum number of results to return
        
    Returns:
        List of RetrievalResult objects
    """
    print(f"\n🔍 Performing filtered semantic search...")
    print(f"   Query: '{query}'")
    print(f"   Filters: {metadata_filters}")
    print(f"   Max Results: {max_results}")
    
    # Create retrieval configuration with filters
    config = RetrievalConfig(
        max_results=max_results,
        retrieval_type=RetrievalType.SEMANTIC,
        metadata_filters=metadata_filters,
        min_relevance_score=0.0
    )
    
    # Perform retrieval
    results = retrieve_api.retrieve(
        knowledge_base_id=knowledge_base_id,
        query=query,
        config=config
    )
    
    print(f"✓ Retrieved {len(results)} filtered results")
    
    return results


def main():
    """
    Main function demonstrating basic retrieval API usage.
    """
    print("\n" + "=" * 80)
    print("BEDROCK RAG RETRIEVAL - BASIC RETRIEVAL EXAMPLE")
    print("=" * 80)
    
    # Step 1: Initialize AWS configuration
    print("\n[Step 1] Initializing AWS Configuration")
    aws_config = initialize_aws_config()
    
    # Step 2: Create Retrieve API instance
    print("\n[Step 2] Creating Retrieve API Instance")
    retrieve_api = RetrieveAPI(aws_config)
    print("✓ Retrieve API instance created")
    
    # Step 3: Define knowledge base ID
    # In a real scenario, this would be obtained from your knowledge base setup
    knowledge_base_id = os.getenv("KNOWLEDGE_BASE_ID", "your-kb-id-here")
    
    if knowledge_base_id == "your-kb-id-here":
        print("\n⚠️  WARNING: KNOWLEDGE_BASE_ID environment variable not set")
        print("   Please set KNOWLEDGE_BASE_ID to your actual knowledge base ID")
        print("   Example: export KNOWLEDGE_BASE_ID='kb-12345abcde'")
        return
    
    print(f"\n[Step 3] Using Knowledge Base: {knowledge_base_id}")
    
    # Step 4: Perform basic semantic search
    print("\n[Step 4] Performing Basic Semantic Search")
    query1 = "What are the key features of the product?"
    results1 = perform_semantic_search(
        retrieve_api=retrieve_api,
        knowledge_base_id=knowledge_base_id,
        query=query1,
        max_results=5
    )
    display_results(results1)
    
    # Step 5: Perform another search with different query
    print("\n[Step 5] Performing Another Search")
    query2 = "How do I get started with the system?"
    results2 = perform_semantic_search(
        retrieve_api=retrieve_api,
        knowledge_base_id=knowledge_base_id,
        query=query2,
        max_results=3
    )
    display_results(results2)
    
    # Step 6: Perform filtered search (if metadata is available)
    print("\n[Step 6] Performing Filtered Search")
    metadata_filters = {
        "source_type": "documentation"
    }
    results3 = perform_filtered_search(
        retrieve_api=retrieve_api,
        knowledge_base_id=knowledge_base_id,
        query="Getting started guide",
        metadata_filters=metadata_filters,
        max_results=3
    )
    display_results(results3)
    
    # Step 7: Demonstrate result analysis
    print("\n[Step 7] Result Analysis")
    if results1:
        top_result = results1[0]
        print(f"✓ Top result relevance score: {top_result.relevance_score:.2%}")
        print(f"✓ Top result source: {top_result.source_document}")
        
        # Filter results by relevance threshold
        high_relevance = [r for r in results1 if r.relevance_score > 0.7]
        print(f"✓ Results with >70% relevance: {len(high_relevance)}")
    
    print("\n" + "=" * 80)
    print("✓ Basic Retrieval Example Completed Successfully")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
