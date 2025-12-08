"""Tests for Retrieve and Generate API"""

import pytest
import json
from unittest.mock import MagicMock, patch
from src.retrieve_and_generate_api import RetrieveAndGenerateAPI, GenerationConfig
from src.response_formatter import GenerationResponse
from config.aws_config import AWSConfig
import os

# Disable hypothesis database to avoid Windows hanging issues
os.environ['HYPOTHESIS_DATABASE_DIRECTORY'] = 'none'


class TestGenerationConfig:
    """Tests for GenerationConfig"""

    def test_default_config(self):
        """Test default generation configuration"""
        config = GenerationConfig()
        assert config.model_id == "anthropic.claude-3-sonnet-20240229-v1:0"
        assert config.max_tokens == 1024
        assert config.temperature == 0.7

    def test_custom_config(self):
        """Test custom generation configuration"""
        config = GenerationConfig(
            model_id="anthropic.claude-3-haiku-20240307-v1:0",
            max_tokens=2048,
            temperature=0.5
        )
        assert config.model_id == "anthropic.claude-3-haiku-20240307-v1:0"
        assert config.max_tokens == 2048
        assert config.temperature == 0.5

    def test_validation_invalid_max_tokens(self):
        """Test validation with invalid max_tokens"""
        config = GenerationConfig(max_tokens=0)
        with pytest.raises(ValueError, match="max_tokens must be greater than 0"):
            config.validate()

    def test_validation_invalid_temperature(self):
        """Test validation with invalid temperature"""
        config = GenerationConfig(temperature=1.5)
        with pytest.raises(ValueError, match="temperature must be between"):
            config.validate()

    def test_validation_invalid_top_p(self):
        """Test validation with invalid top_p"""
        config = GenerationConfig(top_p=-0.1)
        with pytest.raises(ValueError, match="top_p must be between"):
            config.validate()

    def test_validation_success(self):
        """Test successful validation"""
        config = GenerationConfig()
        assert config.validate() is True


class TestRetrieveAndGenerateAPI:
    """Tests for Retrieve and Generate API"""

    def test_init(self, mock_bedrock_client):
        """Test API initialization"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    api = RetrieveAndGenerateAPI(config)

                    assert api.aws_config is config
                    assert api.retrieve_api is not None
                    assert api.bedrock_runtime is not None

    def test_retrieve_and_generate(self, mock_bedrock_client):
        """Test retrieve and generate operation"""
        from config.aws_config import AWSConfig

        # Mock retrieve response
        mock_bedrock_client.retrieve.return_value = {
            "retrievalResults": [
                {
                    "content": "Document content about AI",
                    "score": 0.95,
                    "retrievalResultMetadata": {
                        "location": {
                            "s3Location": {
                                "uri": "s3://bucket/doc.txt"
                            }
                        },
                        "document": {
                            "documentId": "doc-001"
                        }
                    }
                }
            ]
        }

        # Mock generation response
        mock_bedrock_client.invoke_model.return_value = {
            "body": MagicMock(read=lambda: json.dumps({
                "content": [{"text": "AI is a transformative technology..."}]
            }).encode())
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    api = RetrieveAndGenerateAPI(config)

                    response = api.retrieve_and_generate(
                        knowledge_base_id="kb-12345",
                        query="What is AI?"
                    )

                    assert isinstance(response, GenerationResponse)
                    assert response.generated_text
                    assert response.query == "What is AI?"

    def test_retrieve_and_generate_with_vector(self, mock_opensearch_client):
        """Test retrieve and generate with vector search"""
        from config.aws_config import AWSConfig

        # Mock vector search response
        mock_opensearch_client.search.return_value = {
            "hits": {
                "hits": [
                    {
                        "_id": "chunk-001",
                        "_score": 0.95,
                        "_source": {
                            "content": "Machine learning is a subset of AI",
                            "metadata": {"source": "s3://bucket/doc.txt"},
                            "document_id": "doc-001",
                            "chunk_index": 0
                        }
                    }
                ]
            }
        }

        # Mock generation response
        mock_opensearch_client.invoke_model.return_value = {
            "body": MagicMock(read=lambda: json.dumps({
                "content": [{"text": "Machine learning enables computers to learn..."}]
            }).encode())
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_opensearch_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    api = RetrieveAndGenerateAPI(config)

                    query_vector = [0.1] * 1536
                    response = api.retrieve_and_generate_with_vector(
                        collection_name="test-collection",
                        index_name="test-index",
                        query_vector=query_vector,
                        query_text="What is machine learning?"
                    )

                    assert isinstance(response, GenerationResponse)
                    assert response.query == "What is machine learning?"

    def test_build_context(self, mock_bedrock_client):
        """Test building context from documents"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    api = RetrieveAndGenerateAPI(config)

                    source_docs = [
                        {
                            "chunk_id": "chunk-001",
                            "content": "Document 1 content",
                            "relevance_score": 0.95,
                            "location": "s3://bucket/doc1.txt",
                            "metadata": {},
                            "source_document": "doc-001"
                        },
                        {
                            "chunk_id": "chunk-002",
                            "content": "Document 2 content",
                            "relevance_score": 0.85,
                            "location": "s3://bucket/doc2.txt",
                            "metadata": {},
                            "source_document": "doc-002"
                        }
                    ]

                    context = api._build_context(source_docs)
                    assert "Document 1 content" in context
                    assert "Document 2 content" in context
                    assert "95.00%" in context
                    assert "85.00%" in context

    def test_extract_citations(self, mock_bedrock_client):
        """Test extracting citations from generated text"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    api = RetrieveAndGenerateAPI(config)

                    generated_text = "According to the document, AI is transformative..."
                    source_docs = [
                        {
                            "chunk_id": "chunk-001",
                            "content": "AI is transformative technology",
                            "relevance_score": 0.95,
                            "location": "s3://bucket/doc.txt",
                            "metadata": {},
                            "source_document": "doc-001"
                        }
                    ]

                    citations = api._extract_citations(generated_text, source_docs)
                    assert isinstance(citations, list)

    def test_validate_generation_configuration(self, mock_bedrock_client):
        """Test validating generation configuration"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    api = RetrieveAndGenerateAPI(config)

                    gen_config = GenerationConfig()
                    assert api.validate_generation_configuration(gen_config) is True

    def test_get_supported_models(self, mock_bedrock_client):
        """Test getting supported models"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    api = RetrieveAndGenerateAPI(config)

                    models = api.get_supported_models()
                    assert isinstance(models, list)
                    assert len(models) > 0
                    assert "anthropic.claude-3-sonnet-20240229-v1:0" in models

    @pytest.mark.parametrize("max_tokens,temperature", [
        (512, 0.5),
        (1024, 0.7),
        (2048, 0.9),
        (4096, 0.3)
    ])
    def test_retrieve_and_generate_with_custom_config(
        self,
        max_tokens,
        temperature,
        mock_bedrock_client
    ):
        """Test retrieve and generate with custom configuration"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.retrieve.return_value = {
            "retrievalResults": [
                {
                    "content": "Test content",
                    "score": 0.95,
                    "retrievalResultMetadata": {
                        "location": {"s3Location": {"uri": "s3://bucket/doc.txt"}},
                        "document": {"documentId": "doc-001"}
                    }
                }
            ]
        }

        mock_bedrock_client.invoke_model.return_value = {
            "body": MagicMock(read=lambda: json.dumps({
                "content": [{"text": "Generated response"}]
            }).encode())
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    api = RetrieveAndGenerateAPI(config)

                    gen_config = GenerationConfig(
                        max_tokens=max_tokens,
                        temperature=temperature
                    )

                    response = api.retrieve_and_generate(
                        knowledge_base_id="kb-12345",
                        query="Test query",
                        generation_config=gen_config
                    )

                    assert isinstance(response, GenerationResponse)
                    assert response.generated_text

    def test_retrieve_and_generate_with_system_prompt(self, mock_bedrock_client):
        """Test retrieve and generate with custom system prompt"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.retrieve.return_value = {
            "retrievalResults": [
                {
                    "content": "Test content",
                    "score": 0.95,
                    "retrievalResultMetadata": {
                        "location": {"s3Location": {"uri": "s3://bucket/doc.txt"}},
                        "document": {"documentId": "doc-001"}
                    }
                }
            ]
        }

        mock_bedrock_client.invoke_model.return_value = {
            "body": MagicMock(read=lambda: json.dumps({
                "content": [{"text": "Generated response"}]
            }).encode())
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    api = RetrieveAndGenerateAPI(config)

                    custom_prompt = "You are an expert in technology. Answer questions concisely."
                    response = api.retrieve_and_generate(
                        knowledge_base_id="kb-12345",
                        query="What is AI?",
                        system_prompt=custom_prompt
                    )

                    assert isinstance(response, GenerationResponse)
                    assert response.generated_text


    def test_retrieve_and_generate_stream(self, mock_bedrock_client):
        """Test streaming retrieve and generate operation"""
        from config.aws_config import AWSConfig

        # Mock retrieve response
        mock_bedrock_client.retrieve.return_value = {
            "retrievalResults": [
                {
                    "content": "Document content about AI",
                    "score": 0.95,
                    "retrievalResultMetadata": {
                        "location": {
                            "s3Location": {
                                "uri": "s3://bucket/doc.txt"
                            }
                        },
                        "document": {
                            "documentId": "doc-001"
                        }
                    }
                }
            ]
        }

        # Mock streaming response
        mock_stream_event_1 = {
            "chunk": {
                "bytes": json.dumps({
                    "delta": {"text": "AI is "}
                }).encode()
            }
        }
        mock_stream_event_2 = {
            "chunk": {
                "bytes": json.dumps({
                    "delta": {"text": "transformative"}
                }).encode()
            }
        }

        mock_bedrock_client.invoke_model_with_response_stream.return_value = {
            "body": [mock_stream_event_1, mock_stream_event_2]
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    api = RetrieveAndGenerateAPI(config)

                    tokens = list(api.retrieve_and_generate_stream(
                        knowledge_base_id="kb-12345",
                        query="What is AI?"
                    ))

                    assert len(tokens) == 2
                    assert tokens[0] == "AI is "
                    assert tokens[1] == "transformative"

    def test_retrieve_and_generate_with_vector_stream(self, mock_opensearch_client):
        """Test streaming retrieve and generate with vector search"""
        from config.aws_config import AWSConfig

        # Mock vector search response
        mock_opensearch_client.search.return_value = {
            "hits": {
                "hits": [
                    {
                        "_id": "chunk-001",
                        "_score": 0.95,
                        "_source": {
                            "content": "Machine learning is a subset of AI",
                            "metadata": {"source": "s3://bucket/doc.txt"},
                            "document_id": "doc-001",
                            "chunk_index": 0
                        }
                    }
                ]
            }
        }

        # Mock streaming response
        mock_stream_event = {
            "chunk": {
                "bytes": json.dumps({
                    "delta": {"text": "Machine learning "}
                }).encode()
            }
        }

        mock_opensearch_client.invoke_model_with_response_stream.return_value = {
            "body": [mock_stream_event]
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_opensearch_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    api = RetrieveAndGenerateAPI(config)

                    query_vector = [0.1] * 1536
                    tokens = list(api.retrieve_and_generate_with_vector_stream(
                        collection_name="test-collection",
                        index_name="test-index",
                        query_vector=query_vector,
                        query_text="What is machine learning?"
                    ))

                    assert len(tokens) == 1
                    assert tokens[0] == "Machine learning "

    def test_generate_response_stream(self, mock_bedrock_client):
        """Test streaming response generation"""
        from config.aws_config import AWSConfig

        # Mock streaming response with multiple tokens
        mock_stream_events = [
            {
                "chunk": {
                    "bytes": json.dumps({
                        "delta": {"text": "Token1 "}
                    }).encode()
                }
            },
            {
                "chunk": {
                    "bytes": json.dumps({
                        "delta": {"text": "Token2 "}
                    }).encode()
                }
            },
            {
                "chunk": {
                    "bytes": json.dumps({
                        "delta": {"text": "Token3"}
                    }).encode()
                }
            }
        ]

        mock_bedrock_client.invoke_model_with_response_stream.return_value = {
            "body": mock_stream_events
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    api = RetrieveAndGenerateAPI(config)

                    gen_config = GenerationConfig()
                    tokens = list(api._generate_response_stream(
                        query="Test query",
                        context="Test context",
                        generation_config=gen_config
                    ))

                    assert len(tokens) == 3
                    assert tokens[0] == "Token1 "
                    assert tokens[1] == "Token2 "
                    assert tokens[2] == "Token3"

    def test_stream_with_empty_response(self, mock_bedrock_client):
        """Test streaming with empty response"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.invoke_model_with_response_stream.return_value = {
            "body": []
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            with patch.object(AWSConfig, 'get_account_id', return_value='123456789012'):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    api = RetrieveAndGenerateAPI(config)

                    gen_config = GenerationConfig()
                    tokens = list(api._generate_response_stream(
                        query="Test query",
                        context="Test context",
                        generation_config=gen_config
                    ))

                    assert len(tokens) == 0
