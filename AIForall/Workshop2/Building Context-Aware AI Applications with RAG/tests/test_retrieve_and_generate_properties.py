"""Property-based tests for Retrieve and Generate API

**Feature: bedrock-rag-retrieval, Property 4: Retrieve and Generate Round Trip**
**Validates: Requirements 4.1, 4.2, 4.3, 4.4**
"""

import pytest
import json
import os
from unittest.mock import MagicMock, patch
from src.retrieve_and_generate_api import RetrieveAndGenerateAPI, GenerationConfig
from src.retrieval_api import RetrievalResult, RetrievalConfig
from src.response_formatter import GenerationResponse, RetrievalResultItem, Citation
from config.aws_config import AWSConfig

# Disable hypothesis database to avoid Windows hanging issues
os.environ['HYPOTHESIS_DATABASE_DIRECTORY'] = 'none'


class TestRetrieveAndGenerateRoundTrip:
    """
    Property 4: Retrieve and Generate Round Trip
    
    *For any* query submitted to the Retrieve and Generate API, the generated 
    response should include citations that reference documents actually retrieved 
    from the knowledge base.
    
    **Validates: Requirements 4.1, 4.2, 4.3, 4.4**
    """

    def test_citations_reference_retrieved_documents(self):
        """
        Property: All citations in the generated response should reference 
        documents that were actually retrieved from the knowledge base.
        
        For any query and set of retrieved documents, when the Retrieve and 
        Generate API generates a response, every citation in that response 
        should have a source_id that matches a chunk_id from the retrieved 
        documents.
        """
        # Test data
        query = "What is machine learning?"
        retrieval_results = [
            {
                "chunk_id": "chunk-001",
                "content": "Machine learning is a subset of artificial intelligence",
                "relevance_score": 0.95,
                "location": "s3://test-bucket/document.txt",
                "metadata": {"source": "s3://test-bucket/document.txt"},
                "source_document": "doc-001"
            },
            {
                "chunk_id": "chunk-002",
                "content": "Deep learning uses neural networks for pattern recognition",
                "relevance_score": 0.87,
                "location": "s3://test-bucket/document.txt",
                "metadata": {"source": "s3://test-bucket/document.txt"},
                "source_document": "doc-001"
            }
        ]

        # Create mock RetrievalResult objects
        mock_retrieval_results = [
            RetrievalResult(
                chunk_id=r["chunk_id"],
                content=r["content"],
                relevance_score=r["relevance_score"],
                location=r["location"],
                metadata=r["metadata"],
                source_document=r["source_document"]
            )
            for r in retrieval_results
        ]

        # Mock the API components
        with patch('src.retrieve_and_generate_api.RetrieveAPI') as mock_retrieve_api_class:
            with patch('src.retrieve_and_generate_api.AWSConfig') as mock_aws_config_class:
                mock_retrieve_api = MagicMock()
                mock_retrieve_api_class.return_value = mock_retrieve_api
                mock_retrieve_api.retrieve.return_value = mock_retrieval_results

                mock_aws_config = MagicMock()
                mock_aws_config_class.return_value = mock_aws_config
                
                # Mock bedrock runtime
                mock_bedrock_runtime = MagicMock()
                mock_aws_config.get_client.return_value = mock_bedrock_runtime
                mock_bedrock_runtime.invoke_model.return_value = {
                    "body": MagicMock(read=lambda: json.dumps({
                        "content": [{"text": "Machine learning is a subset of AI that enables systems to learn from data."}]
                    }).encode())
                }

                # Create API and execute
                api = RetrieveAndGenerateAPI(mock_aws_config)
                response = api.retrieve_and_generate(
                    knowledge_base_id="kb-12345",
                    query=query
                )

                # Property assertion: All citations must reference retrieved documents
                retrieved_chunk_ids = {r.chunk_id for r in mock_retrieval_results}
                
                for citation in response.citations:
                    # Each citation's source_id must be in the retrieved documents
                    assert citation.source_id in retrieved_chunk_ids, (
                        f"Citation source_id '{citation.source_id}' not found in "
                        f"retrieved documents: {retrieved_chunk_ids}"
                    )

    def test_response_includes_source_documents(self):
        """
        Property: The generated response should include all source documents 
        that were retrieved from the knowledge base.
        
        For any query and set of retrieved documents, the response should 
        contain all retrieved documents in its source_documents list.
        """
        # Test data
        query = "What is AI?"
        retrieval_results = [
            {
                "chunk_id": "chunk-001",
                "content": "Artificial intelligence is the simulation of human intelligence",
                "relevance_score": 0.92,
                "location": "s3://test-bucket/ai.txt",
                "metadata": {"source": "s3://test-bucket/ai.txt"},
                "source_document": "doc-001"
            }
        ]

        # Create mock RetrievalResult objects
        mock_retrieval_results = [
            RetrievalResult(
                chunk_id=r["chunk_id"],
                content=r["content"],
                relevance_score=r["relevance_score"],
                location=r["location"],
                metadata=r["metadata"],
                source_document=r["source_document"]
            )
            for r in retrieval_results
        ]

        # Mock the API components
        with patch('src.retrieve_and_generate_api.RetrieveAPI') as mock_retrieve_api_class:
            with patch('src.retrieve_and_generate_api.AWSConfig') as mock_aws_config_class:
                mock_retrieve_api = MagicMock()
                mock_retrieve_api_class.return_value = mock_retrieve_api
                mock_retrieve_api.retrieve.return_value = mock_retrieval_results

                mock_aws_config = MagicMock()
                mock_aws_config_class.return_value = mock_aws_config
                
                # Mock bedrock runtime
                mock_bedrock_runtime = MagicMock()
                mock_aws_config.get_client.return_value = mock_bedrock_runtime
                mock_bedrock_runtime.invoke_model.return_value = {
                    "body": MagicMock(read=lambda: json.dumps({
                        "content": [{"text": "AI is transformative technology"}]
                    }).encode())
                }

                # Create API and execute
                api = RetrieveAndGenerateAPI(mock_aws_config)
                response = api.retrieve_and_generate(
                    knowledge_base_id="kb-12345",
                    query=query
                )

                # Property assertion: Response must include all retrieved documents
                assert len(response.source_documents) == len(retrieval_results), (
                    f"Expected {len(retrieval_results)} source documents, "
                    f"got {len(response.source_documents)}"
                )

                # All retrieved chunk IDs should be in source documents
                response_chunk_ids = {d.chunk_id for d in response.source_documents}
                retrieved_chunk_ids = {r["chunk_id"] for r in retrieval_results}
                
                assert response_chunk_ids == retrieved_chunk_ids, (
                    f"Source document chunk IDs {response_chunk_ids} do not match "
                    f"retrieved chunk IDs {retrieved_chunk_ids}"
                )

    def test_response_preserves_relevance_scores(self):
        """
        Property: The generated response should preserve the relevance scores 
        from the retrieved documents.
        
        For any query and set of retrieved documents, the relevance scores 
        in the response should match the scores from the retrieval operation.
        """
        # Test data
        query = "What is deep learning?"
        retrieval_results = [
            {
                "chunk_id": "chunk-001",
                "content": "Deep learning uses neural networks with multiple layers",
                "relevance_score": 0.98,
                "location": "s3://test-bucket/dl.txt",
                "metadata": {"source": "s3://test-bucket/dl.txt"},
                "source_document": "doc-001"
            },
            {
                "chunk_id": "chunk-002",
                "content": "Neural networks are inspired by biological neurons",
                "relevance_score": 0.75,
                "location": "s3://test-bucket/nn.txt",
                "metadata": {"source": "s3://test-bucket/nn.txt"},
                "source_document": "doc-002"
            }
        ]

        # Create mock RetrievalResult objects
        mock_retrieval_results = [
            RetrievalResult(
                chunk_id=r["chunk_id"],
                content=r["content"],
                relevance_score=r["relevance_score"],
                location=r["location"],
                metadata=r["metadata"],
                source_document=r["source_document"]
            )
            for r in retrieval_results
        ]

        # Mock the API components
        with patch('src.retrieve_and_generate_api.RetrieveAPI') as mock_retrieve_api_class:
            with patch('src.retrieve_and_generate_api.AWSConfig') as mock_aws_config_class:
                mock_retrieve_api = MagicMock()
                mock_retrieve_api_class.return_value = mock_retrieve_api
                mock_retrieve_api.retrieve.return_value = mock_retrieval_results

                mock_aws_config = MagicMock()
                mock_aws_config_class.return_value = mock_aws_config
                
                # Mock bedrock runtime
                mock_bedrock_runtime = MagicMock()
                mock_aws_config.get_client.return_value = mock_bedrock_runtime
                mock_bedrock_runtime.invoke_model.return_value = {
                    "body": MagicMock(read=lambda: json.dumps({
                        "content": [{"text": "Deep learning is powerful for complex tasks"}]
                    }).encode())
                }

                # Create API and execute
                api = RetrieveAndGenerateAPI(mock_aws_config)
                response = api.retrieve_and_generate(
                    knowledge_base_id="kb-12345",
                    query=query
                )

                # Property assertion: Relevance scores must be preserved
                retrieved_scores = {r.chunk_id: r.relevance_score for r in mock_retrieval_results}
                
                for doc in response.source_documents:
                    expected_score = retrieved_scores[doc.chunk_id]
                    assert abs(doc.relevance_score - expected_score) < 0.001, (
                        f"Relevance score mismatch for chunk {doc.chunk_id}: "
                        f"expected {expected_score}, got {doc.relevance_score}"
                    )

    def test_response_is_generation_response_type(self):
        """
        Property: The retrieve and generate API should always return a 
        GenerationResponse object.
        
        For any valid query and retrieval results, the response should be 
        an instance of GenerationResponse with all required fields populated.
        """
        # Test data
        query = "What is NLP?"
        retrieval_results = [
            {
                "chunk_id": "chunk-001",
                "content": "Natural Language Processing enables computers to understand text",
                "relevance_score": 0.89,
                "location": "s3://test-bucket/nlp.txt",
                "metadata": {"source": "s3://test-bucket/nlp.txt"},
                "source_document": "doc-001"
            }
        ]

        # Create mock RetrievalResult objects
        mock_retrieval_results = [
            RetrievalResult(
                chunk_id=r["chunk_id"],
                content=r["content"],
                relevance_score=r["relevance_score"],
                location=r["location"],
                metadata=r["metadata"],
                source_document=r["source_document"]
            )
            for r in retrieval_results
        ]

        # Mock the API components
        with patch('src.retrieve_and_generate_api.RetrieveAPI') as mock_retrieve_api_class:
            with patch('src.retrieve_and_generate_api.AWSConfig') as mock_aws_config_class:
                mock_retrieve_api = MagicMock()
                mock_retrieve_api_class.return_value = mock_retrieve_api
                mock_retrieve_api.retrieve.return_value = mock_retrieval_results

                mock_aws_config = MagicMock()
                mock_aws_config_class.return_value = mock_aws_config
                
                # Mock bedrock runtime
                mock_bedrock_runtime = MagicMock()
                mock_aws_config.get_client.return_value = mock_bedrock_runtime
                mock_bedrock_runtime.invoke_model.return_value = {
                    "body": MagicMock(read=lambda: json.dumps({
                        "content": [{"text": "NLP is a key AI technology"}]
                    }).encode())
                }

                # Create API and execute
                api = RetrieveAndGenerateAPI(mock_aws_config)
                response = api.retrieve_and_generate(
                    knowledge_base_id="kb-12345",
                    query=query
                )

                # Property assertion: Response must be GenerationResponse type
                assert isinstance(response, GenerationResponse), (
                    f"Expected GenerationResponse, got {type(response)}"
                )
                
                # All required fields must be populated
                assert response.generated_text is not None, "generated_text is None"
                assert isinstance(response.source_documents, list), "source_documents is not a list"
                assert isinstance(response.citations, list), "citations is not a list"
                assert response.model_used, "model_used is empty"
                assert response.query == query, f"query mismatch: expected {query}, got {response.query}"

    def test_citations_have_valid_structure(self):
        """
        Property: All citations in the response should have valid structure 
        with required fields.
        
        For any generated response, each citation should have text, source_id, 
        source_location, and relevance_score fields.
        """
        # Test data
        query = "What is computer vision?"
        retrieval_results = [
            {
                "chunk_id": "chunk-001",
                "content": "Computer vision enables machines to interpret visual information",
                "relevance_score": 0.91,
                "location": "s3://test-bucket/cv.txt",
                "metadata": {"source": "s3://test-bucket/cv.txt"},
                "source_document": "doc-001"
            }
        ]

        # Create mock RetrievalResult objects
        mock_retrieval_results = [
            RetrievalResult(
                chunk_id=r["chunk_id"],
                content=r["content"],
                relevance_score=r["relevance_score"],
                location=r["location"],
                metadata=r["metadata"],
                source_document=r["source_document"]
            )
            for r in retrieval_results
        ]

        # Mock the API components
        with patch('src.retrieve_and_generate_api.RetrieveAPI') as mock_retrieve_api_class:
            with patch('src.retrieve_and_generate_api.AWSConfig') as mock_aws_config_class:
                mock_retrieve_api = MagicMock()
                mock_retrieve_api_class.return_value = mock_retrieve_api
                mock_retrieve_api.retrieve.return_value = mock_retrieval_results

                mock_aws_config = MagicMock()
                mock_aws_config_class.return_value = mock_aws_config
                
                # Mock bedrock runtime
                mock_bedrock_runtime = MagicMock()
                mock_aws_config.get_client.return_value = mock_bedrock_runtime
                mock_bedrock_runtime.invoke_model.return_value = {
                    "body": MagicMock(read=lambda: json.dumps({
                        "content": [{"text": "Computer vision is used in many applications"}]
                    }).encode())
                }

                # Create API and execute
                api = RetrieveAndGenerateAPI(mock_aws_config)
                response = api.retrieve_and_generate(
                    knowledge_base_id="kb-12345",
                    query=query
                )

                # Property assertion: All citations must have valid structure
                for citation in response.citations:
                    assert isinstance(citation, Citation), (
                        f"Citation is not a Citation object: {type(citation)}"
                    )
                    assert citation.text, "Citation text is empty"
                    assert citation.source_id, "Citation source_id is empty"
                    assert citation.source_location, "Citation source_location is empty"
                    assert isinstance(citation.relevance_score, (int, float)), (
                        f"Citation relevance_score is not numeric: {type(citation.relevance_score)}"
                    )
                    assert 0.0 <= citation.relevance_score <= 1.0, (
                        f"Citation relevance_score out of range: {citation.relevance_score}"
                    )

    def test_source_documents_have_valid_structure(self):
        """
        Property: All source documents in the response should have valid 
        structure with required fields.
        
        For any generated response, each source document should have chunk_id, 
        content, relevance_score, and location fields.
        """
        # Test data
        query = "What is reinforcement learning?"
        retrieval_results = [
            {
                "chunk_id": "chunk-001",
                "content": "Reinforcement learning trains agents through rewards and penalties",
                "relevance_score": 0.88,
                "location": "s3://test-bucket/rl.txt",
                "metadata": {"source": "s3://test-bucket/rl.txt"},
                "source_document": "doc-001"
            }
        ]

        # Create mock RetrievalResult objects
        mock_retrieval_results = [
            RetrievalResult(
                chunk_id=r["chunk_id"],
                content=r["content"],
                relevance_score=r["relevance_score"],
                location=r["location"],
                metadata=r["metadata"],
                source_document=r["source_document"]
            )
            for r in retrieval_results
        ]

        # Mock the API components
        with patch('src.retrieve_and_generate_api.RetrieveAPI') as mock_retrieve_api_class:
            with patch('src.retrieve_and_generate_api.AWSConfig') as mock_aws_config_class:
                mock_retrieve_api = MagicMock()
                mock_retrieve_api_class.return_value = mock_retrieve_api
                mock_retrieve_api.retrieve.return_value = mock_retrieval_results

                mock_aws_config = MagicMock()
                mock_aws_config_class.return_value = mock_aws_config
                
                # Mock bedrock runtime
                mock_bedrock_runtime = MagicMock()
                mock_aws_config.get_client.return_value = mock_bedrock_runtime
                mock_bedrock_runtime.invoke_model.return_value = {
                    "body": MagicMock(read=lambda: json.dumps({
                        "content": [{"text": "RL is used in game playing and robotics"}]
                    }).encode())
                }

                # Create API and execute
                api = RetrieveAndGenerateAPI(mock_aws_config)
                response = api.retrieve_and_generate(
                    knowledge_base_id="kb-12345",
                    query=query
                )

                # Property assertion: All source documents must have valid structure
                for doc in response.source_documents:
                    assert isinstance(doc, RetrievalResultItem), (
                        f"Source document is not a RetrievalResultItem: {type(doc)}"
                    )
                    assert doc.chunk_id, "Source document chunk_id is empty"
                    assert doc.content, "Source document content is empty"
                    assert isinstance(doc.relevance_score, (int, float)), (
                        f"Source document relevance_score is not numeric: {type(doc.relevance_score)}"
                    )
                    assert 0.0 <= doc.relevance_score <= 1.0, (
                        f"Source document relevance_score out of range: {doc.relevance_score}"
                    )
                    assert doc.location, "Source document location is empty"
