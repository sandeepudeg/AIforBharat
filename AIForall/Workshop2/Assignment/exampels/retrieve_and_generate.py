"""
Example: Retrieve and Generate API Usage

This example demonstrates how to use the Retrieve and Generate API to combine
document retrieval with foundation model response generation for a complete
Retrieval-Augmented Generation (RAG) workflow.

The example shows:
1. Initializing AWS configuration
2. Creating a Retrieve and Generate API instance
3. Performing RAG queries with automatic retrieval and generation
4. Processing citations and source documents
5. Formatting and displaying generated responses
"""

import os
import sys
import time
from typing import Optional

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config.aws_config import AWSConfig
from src.retrieve_and_generate_api import RetrieveAndGenerateAPI, GenerationConfig
from src.retrieval_api import RetrievalConfig, RetrievalType
from src.response_formatter import ResponseFormat


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


def perform_rag_query(
    rag_api: RetrieveAndGenerateAPI,
    knowledge_base_id: str,
    query: str,
    max_retrieval_results: int = 5,
    model_id: Optional[str] = None,
    system_prompt: Optional[str] = None
):
    """
    Perform a complete RAG query with retrieval and generation.
    
    Args:
        rag_api: RetrieveAndGenerateAPI instance
        knowledge_base_id: ID of the knowledge base
        query: User query string
        max_retrieval_results: Maximum number of documents to retrieve
        model_id: Optional foundation model ID to use
        system_prompt: Optional custom system prompt
        
    Returns:
        GenerationResponse object
    """
    print(f"\n🔄 Performing RAG Query...")
    print(f"   Query: '{query}'")
    print(f"   Max Retrieval Results: {max_retrieval_results}")
    
    # Create retrieval configuration
    retrieval_config = RetrievalConfig(
        max_results=max_retrieval_results,
        retrieval_type=RetrievalType.SEMANTIC,
        min_relevance_score=0.0
    )
    
    # Create generation configuration
    generation_config = GenerationConfig(
        model_id=model_id or "anthropic.claude-3-sonnet-20240229-v1:0",
        max_tokens=1024,
        temperature=0.7,
        top_p=0.9
    )
    
    print(f"   Model: {generation_config.model_id}")
    
    # Perform RAG query
    start_time = time.time()
    response = rag_api.retrieve_and_generate(
        knowledge_base_id=knowledge_base_id,
        query=query,
        retrieval_config=retrieval_config,
        generation_config=generation_config,
        system_prompt=system_prompt
    )
    elapsed_time = time.time() - start_time
    
    print(f"✓ RAG Query completed in {elapsed_time:.2f}s")
    print(f"  Retrieved {len(response.source_documents)} documents")
    print(f"  Generated {len(response.generated_text)} characters of response")
    
    return response


def display_generation_response(response) -> None:
    """
    Display a generation response with all components.
    
    Args:
        response: GenerationResponse object to display
    """
    print("\n" + "=" * 80)
    print("GENERATED RESPONSE")
    print("=" * 80)
    
    # Display the generated text
    print(f"\n📝 Generated Answer:\n")
    print(response.generated_text)
    
    # Display source documents
    if response.source_documents:
        print(f"\n📚 Source Documents ({len(response.source_documents)}):\n")
        for i, doc in enumerate(response.source_documents, 1):
            print(f"[Source {i}]")
            print(f"  Relevance: {doc.relevance_score:.2%}")
            print(f"  Location: {doc.location}")
            print(f"  Content Preview: {doc.content[:150]}...")
            print()
    
    # Display citations
    if response.citations:
        print(f"\n🔗 Citations ({len(response.citations)}):\n")
        for i, citation in enumerate(response.citations, 1):
            print(f"[Citation {i}]")
            print(f"  Text: {citation.text}")
            print(f"  Source: {citation.source_location}")
            print(f"  Relevance: {citation.relevance_score:.2%}")
            print()
    
    # Display metadata
    print(f"\n⏱️  Performance Metrics:")
    print(f"  Model: {response.model_used}")
    print(f"  Retrieval Time: {response.retrieval_time_ms:.2f}ms")
    print(f"  Generation Time: {response.generation_time_ms:.2f}ms")
    print(f"  Total Time: {response.total_time_ms:.2f}ms")
    print(f"  Timestamp: {response.timestamp}")
    
    print("\n" + "=" * 80)


def demonstrate_response_formatting(response) -> None:
    """
    Demonstrate different response formatting options.
    
    Args:
        response: GenerationResponse object to format
    """
    print("\n[Response Formatting Examples]")
    
    # JSON format
    print("\n1️⃣  JSON Format (first 200 chars):")
    json_output = response.format(ResponseFormat.JSON)
    print(json_output[:200] + "...")
    
    # Markdown format
    print("\n2️⃣  Markdown Format (first 300 chars):")
    markdown_output = response.format(ResponseFormat.MARKDOWN)
    print(markdown_output[:300] + "...")
    
    # Text format
    print("\n3️⃣  Text Format (first 300 chars):")
    text_output = response.format(ResponseFormat.TEXT)
    print(text_output[:300] + "...")


def perform_multi_turn_conversation(
    rag_api: RetrieveAndGenerateAPI,
    knowledge_base_id: str,
    queries: list
) -> None:
    """
    Perform multiple RAG queries in sequence to simulate a conversation.
    
    Args:
        rag_api: RetrieveAndGenerateAPI instance
        knowledge_base_id: ID of the knowledge base
        queries: List of query strings
    """
    print("\n[Multi-Turn Conversation Example]")
    print("=" * 80)
    
    for i, query in enumerate(queries, 1):
        print(f"\n[Turn {i}] User Query: {query}")
        
        try:
            response = perform_rag_query(
                rag_api=rag_api,
                knowledge_base_id=knowledge_base_id,
                query=query,
                max_retrieval_results=3
            )
            
            print(f"\n[Turn {i}] Assistant Response:")
            print(response.generated_text[:300] + "...")
            
            if response.citations:
                print(f"\nCitations: {len(response.citations)} source(s) cited")
        
        except Exception as e:
            print(f"❌ Error in turn {i}: {str(e)}")


def main():
    """
    Main function demonstrating Retrieve and Generate API usage.
    """
    print("\n" + "=" * 80)
    print("BEDROCK RAG RETRIEVAL - RETRIEVE AND GENERATE EXAMPLE")
    print("=" * 80)
    
    # Step 1: Initialize AWS configuration
    print("\n[Step 1] Initializing AWS Configuration")
    aws_config = initialize_aws_config()
    
    # Step 2: Create Retrieve and Generate API instance
    print("\n[Step 2] Creating Retrieve and Generate API Instance")
    rag_api = RetrieveAndGenerateAPI(aws_config)
    print("✓ Retrieve and Generate API instance created")
    
    # Step 3: Define knowledge base ID
    knowledge_base_id = os.getenv("KNOWLEDGE_BASE_ID", "your-kb-id-here")
    
    if knowledge_base_id == "your-kb-id-here":
        print("\n⚠️  WARNING: KNOWLEDGE_BASE_ID environment variable not set")
        print("   Please set KNOWLEDGE_BASE_ID to your actual knowledge base ID")
        print("   Example: export KNOWLEDGE_BASE_ID='kb-12345abcde'")
        return
    
    print(f"\n[Step 3] Using Knowledge Base: {knowledge_base_id}")
    
    # Step 4: Perform a basic RAG query
    print("\n[Step 4] Performing Basic RAG Query")
    query1 = "What are the main benefits of using this system?"
    response1 = perform_rag_query(
        rag_api=rag_api,
        knowledge_base_id=knowledge_base_id,
        query=query1,
        max_retrieval_results=5
    )
    display_generation_response(response1)
    
    # Step 5: Demonstrate response formatting
    print("\n[Step 5] Demonstrating Response Formatting")
    demonstrate_response_formatting(response1)
    
    # Step 6: Perform another RAG query with custom system prompt
    print("\n[Step 6] Performing RAG Query with Custom System Prompt")
    custom_prompt = (
        "You are a technical expert. Provide detailed, technical answers "
        "based on the provided context. Always cite your sources."
    )
    query2 = "How does the system architecture work?"
    response2 = perform_rag_query(
        rag_api=rag_api,
        knowledge_base_id=knowledge_base_id,
        query=query2,
        max_retrieval_results=5,
        system_prompt=custom_prompt
    )
    display_generation_response(response2)
    
    # Step 7: Demonstrate multi-turn conversation
    print("\n[Step 7] Demonstrating Multi-Turn Conversation")
    conversation_queries = [
        "What is the primary use case?",
        "How do I get started?",
        "What are the system requirements?"
    ]
    perform_multi_turn_conversation(
        rag_api=rag_api,
        knowledge_base_id=knowledge_base_id,
        queries=conversation_queries
    )
    
    # Step 8: Demonstrate supported models
    print("\n[Step 8] Supported Foundation Models")
    supported_models = rag_api.get_supported_models()
    print(f"✓ {len(supported_models)} supported models:")
    for model in supported_models[:5]:
        print(f"  - {model}")
    if len(supported_models) > 5:
        print(f"  ... and {len(supported_models) - 5} more")
    
    print("\n" + "=" * 80)
    print("✓ Retrieve and Generate Example Completed Successfully")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
