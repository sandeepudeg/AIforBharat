"""Retrieve and Generate API for Bedrock RAG Retrieval System"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from botocore.exceptions import ClientError
from config.aws_config import AWSConfig
from src.retrieval_api import RetrieveAPI, RetrievalConfig
from src.response_formatter import GenerationResponse, RetrievalResultItem, Citation, ResponseFormatter


@dataclass
class GenerationConfig:
    """Configuration for generation operations"""
    model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    max_tokens: int = 1024
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 50
    stop_sequences: List[str] = None

    def validate(self) -> bool:
        """
        Validate generation configuration.

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        if not self.model_id:
            raise ValueError("model_id cannot be empty")

        if self.max_tokens <= 0:
            raise ValueError("max_tokens must be greater than 0")

        if self.temperature < 0.0 or self.temperature > 1.0:
            raise ValueError("temperature must be between 0.0 and 1.0")

        if self.top_p < 0.0 or self.top_p > 1.0:
            raise ValueError("top_p must be between 0.0 and 1.0")

        if self.top_k <= 0:
            raise ValueError("top_k must be greater than 0")

        return True


class RetrieveAndGenerateAPI:
    """
    Retrieve and Generate API for RAG operations.

    Combines document retrieval with foundation model response generation
    to provide accurate, source-grounded answers.
    """

    def __init__(self, aws_config: AWSConfig):
        """
        Initialize Retrieve and Generate API.

        Args:
            aws_config: AWSConfig instance for AWS client management
        """
        self.aws_config = aws_config
        self.retrieve_api = RetrieveAPI(aws_config)
        self.bedrock_runtime = aws_config.get_client("bedrock-runtime")

    def retrieve_and_generate(
        self,
        knowledge_base_id: str,
        query: str,
        retrieval_config: Optional[RetrievalConfig] = None,
        generation_config: Optional[GenerationConfig] = None,
        system_prompt: Optional[str] = None
    ) -> GenerationResponse:
        """
        Retrieve documents and generate a response using a foundation model.

        Args:
            knowledge_base_id: ID of the knowledge base
            query: Query string for retrieval and generation
            retrieval_config: RetrievalConfig for document retrieval
            generation_config: GenerationConfig for response generation
            system_prompt: Optional system prompt for the model

        Returns:
            GenerationResponse with generated text and source documents

        Raises:
            ValueError: If retrieval or generation fails
        """
        if not retrieval_config:
            retrieval_config = RetrievalConfig()

        if not generation_config:
            generation_config = GenerationConfig()

        retrieval_config.validate()
        generation_config.validate()

        try:
            # Step 1: Retrieve relevant documents
            retrieved_results = self.retrieve_api.retrieve(
                knowledge_base_id=knowledge_base_id,
                query=query,
                config=retrieval_config
            )

            # Convert retrieval results to source documents
            source_documents = [
                {
                    "chunk_id": r.chunk_id,
                    "content": r.content,
                    "relevance_score": r.relevance_score,
                    "location": r.location,
                    "metadata": r.metadata,
                    "source_document": r.source_document
                }
                for r in retrieved_results
            ]

            # Step 2: Build context from retrieved documents
            context = self._build_context(source_documents)

            # Step 3: Generate response using foundation model
            generated_text = self._generate_response(
                query=query,
                context=context,
                generation_config=generation_config,
                system_prompt=system_prompt
            )

            # Step 4: Extract citations from generated text
            citations = self._extract_citations(
                generated_text=generated_text,
                source_documents=source_documents
            )

            # Step 5: Format response
            response = GenerationResponse(
                generated_text=generated_text,
                source_documents=[
                    RetrievalResultItem(
                        chunk_id=doc["chunk_id"],
                        content=doc["content"],
                        relevance_score=doc["relevance_score"],
                        location=doc["location"],
                        metadata=doc["metadata"],
                        source_document=doc["source_document"]
                    )
                    for doc in source_documents
                ],
                citations=[
                    Citation(
                        text=c["text"],
                        source_id=c["source_id"],
                        source_location=c["source_location"],
                        relevance_score=c["relevance_score"]
                    )
                    for c in citations
                ],
                model_used=generation_config.model_id,
                query=query
            )

            return response

        except Exception as e:
            raise ValueError(f"Retrieve and generate failed: {str(e)}")

    def retrieve_and_generate_with_vector(
        self,
        collection_name: str,
        index_name: str,
        query_vector: List[float],
        query_text: str,
        retrieval_config: Optional[RetrievalConfig] = None,
        generation_config: Optional[GenerationConfig] = None,
        system_prompt: Optional[str] = None
    ) -> GenerationResponse:
        """
        Retrieve documents using vector search and generate a response.

        Args:
            collection_name: Name of the OpenSearch Serverless collection
            index_name: Name of the vector index
            query_vector: Query vector for similarity search
            query_text: Query text for display and context
            retrieval_config: RetrievalConfig for document retrieval
            generation_config: GenerationConfig for response generation
            system_prompt: Optional system prompt for the model

        Returns:
            GenerationResponse with generated text and source documents

        Raises:
            ValueError: If retrieval or generation fails
        """
        if not retrieval_config:
            retrieval_config = RetrievalConfig()

        if not generation_config:
            generation_config = GenerationConfig()

        retrieval_config.validate()
        generation_config.validate()

        try:
            # Step 1: Retrieve relevant documents using vector search
            retrieved_results = self.retrieve_api.retrieve_with_vector(
                collection_name=collection_name,
                index_name=index_name,
                query_vector=query_vector,
                config=retrieval_config
            )

            # Convert retrieval results to source documents
            source_documents = [
                {
                    "chunk_id": r.chunk_id,
                    "content": r.content,
                    "relevance_score": r.relevance_score,
                    "location": r.location,
                    "metadata": r.metadata,
                    "source_document": r.source_document
                }
                for r in retrieved_results
            ]

            # Step 2: Build context from retrieved documents
            context = self._build_context(source_documents)

            # Step 3: Generate response using foundation model
            generated_text = self._generate_response(
                query=query_text,
                context=context,
                generation_config=generation_config,
                system_prompt=system_prompt
            )

            # Step 4: Extract citations from generated text
            citations = self._extract_citations(
                generated_text=generated_text,
                source_documents=source_documents
            )

            # Step 5: Format response
            response = GenerationResponse(
                generated_text=generated_text,
                source_documents=[
                    RetrievalResultItem(
                        chunk_id=doc["chunk_id"],
                        content=doc["content"],
                        relevance_score=doc["relevance_score"],
                        location=doc["location"],
                        metadata=doc["metadata"],
                        source_document=doc["source_document"]
                    )
                    for doc in source_documents
                ],
                citations=[
                    Citation(
                        text=c["text"],
                        source_id=c["source_id"],
                        source_location=c["source_location"],
                        relevance_score=c["relevance_score"]
                    )
                    for c in citations
                ],
                model_used=generation_config.model_id,
                query=query_text
            )

            return response

        except Exception as e:
            raise ValueError(f"Vector retrieve and generate failed: {str(e)}")

    def _build_context(self, source_documents: List[Dict[str, Any]]) -> str:
        """
        Build context string from source documents.

        Args:
            source_documents: List of source document dictionaries

        Returns:
            Formatted context string

        Raises:
            ValueError: If context building fails
        """
        if not source_documents:
            return ""

        context_parts = []
        for i, doc in enumerate(source_documents, 1):
            context_parts.append(
                f"Source {i} (Relevance: {doc['relevance_score']:.2%}):\n"
                f"{doc['content']}\n"
                f"Location: {doc['location']}\n"
            )

        return "\n".join(context_parts)

    def _generate_response(
    self,
    query: str,
    context: str,
    generation_config: GenerationConfig,
    system_prompt: Optional[str] = None
) -> str:
        """
        Generate response using foundation model.
        """
    
        if not system_prompt:
            system_prompt = (
                "You are a helpful assistant that answers questions based on provided context. "
                "Always cite your sources when referencing information from the context. "
                "If the context doesn't contain relevant information, say so."
            )
    
        prompt = f"""System: {system_prompt}
    
    Context:
    {context}
    
    Question: {query}
    
    Answer:"""
    
        try:
            import json
    
            # Call Bedrock API
            response = self.bedrock_runtime.invoke_model(
                modelId=generation_config.model_id,
                body=self._build_request_body(
                    prompt=prompt,
                    config=generation_config,
                ),  # 👈 already json.dumps-ed in _build_request_body
                contentType="application/json",
                accept="application/json",
            )
    
            # Parse response
            response_body = json.loads(response["body"].read())
            generated_text = response_body.get("content", [{}])[0].get("text", "")
    
            return generated_text
    
        except ClientError as e:
            raise ValueError(f"Model invocation failed: {str(e)}")


    def _build_request_body(
        self,
        prompt: str,
        config: GenerationConfig
    ) -> str:
        """
        Build request body for Bedrock API.

        Args:
            prompt: Prompt for the model
            config: Generation configuration

        Returns:
            JSON request body

        Raises:
            ValueError: If request body building fails
        """
        import json

        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            # "temperature": config.temperature,
            "top_p": config.top_p,
            "top_k": config.top_k
        }

        if config.stop_sequences:
            request_body["stop_sequences"] = config.stop_sequences

        return json.dumps(request_body)

    def _extract_citations(
        self,
        generated_text: str,
        source_documents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extract citations from generated text.

        Args:
            generated_text: Generated response text
            source_documents: List of source documents

        Returns:
            List of citation dictionaries

        Raises:
            ValueError: If citation extraction fails
        """
        citations = []

        # Simple citation extraction: look for source references in the text
        for i, doc in enumerate(source_documents, 1):
            # Check if document content is referenced in generated text
            if doc["content"][:50] in generated_text or doc["source_document"] in generated_text:
                citations.append({
                    "text": doc["content"][:100],
                    "source_id": doc["chunk_id"],
                    "source_location": doc["location"],
                    "relevance_score": doc["relevance_score"]
                })

        return citations

    def validate_generation_configuration(
        self,
        generation_config: GenerationConfig
    ) -> bool:
        """
        Validate generation configuration.

        Args:
            generation_config: Generation configuration to validate

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        return generation_config.validate()

    def get_supported_models(self) -> List[str]:
        """
        Get list of supported foundation models.

        Returns:
            List of supported model IDs
        """
        return [
            "anthropic.claude-3-sonnet-20240229-v1:0",
            "anthropic.claude-3-haiku-20240307-v1:0",
            "anthropic.claude-3-opus-20240229-v1:0",
            "meta.llama2-13b-chat-v1",
            "meta.llama2-70b-chat-v1",
            "mistral.mistral-7b-instruct-v0:2",
            "mistral.mistral-large-2402-v1:0"
        ]

    def retrieve_and_generate_stream(
        self,
        knowledge_base_id: str,
        query: str,
        retrieval_config: Optional[RetrievalConfig] = None,
        generation_config: Optional[GenerationConfig] = None,
        system_prompt: Optional[str] = None
    ):
        """
        Retrieve documents and generate a streaming response.

        Yields tokens from the foundation model as they are generated,
        allowing for real-time response streaming.

        Args:
            knowledge_base_id: ID of the knowledge base
            query: Query string for retrieval and generation
            retrieval_config: RetrievalConfig for document retrieval
            generation_config: GenerationConfig for response generation
            system_prompt: Optional system prompt for the model

        Yields:
            Token strings as they are generated

        Raises:
            ValueError: If retrieval or generation fails
        """
        if not retrieval_config:
            retrieval_config = RetrievalConfig()

        if not generation_config:
            generation_config = GenerationConfig()

        retrieval_config.validate()
        generation_config.validate()

        try:
            # Step 1: Retrieve relevant documents
            retrieved_results = self.retrieve_api.retrieve(
                knowledge_base_id=knowledge_base_id,
                query=query,
                config=retrieval_config
            )

            # Convert retrieval results to source documents
            source_documents = [
                {
                    "chunk_id": r.chunk_id,
                    "content": r.content,
                    "relevance_score": r.relevance_score,
                    "location": r.location,
                    "metadata": r.metadata,
                    "source_document": r.source_document
                }
                for r in retrieved_results
            ]

            # Step 2: Build context from retrieved documents
            context = self._build_context(source_documents)

            # Step 3: Generate streaming response
            yield from self._generate_response_stream(
                query=query,
                context=context,
                generation_config=generation_config,
                system_prompt=system_prompt
            )

        except Exception as e:
            raise ValueError(f"Streaming retrieve and generate failed: {str(e)}")

    def retrieve_and_generate_with_vector_stream(
        self,
        collection_name: str,
        index_name: str,
        query_vector: List[float],
        query_text: str,
        retrieval_config: Optional[RetrievalConfig] = None,
        generation_config: Optional[GenerationConfig] = None,
        system_prompt: Optional[str] = None
    ):
        """
        Retrieve documents using vector search and generate a streaming response.

        Yields tokens from the foundation model as they are generated.

        Args:
            collection_name: Name of the OpenSearch Serverless collection
            index_name: Name of the vector index
            query_vector: Query vector for similarity search
            query_text: Query text for display and context
            retrieval_config: RetrievalConfig for document retrieval
            generation_config: GenerationConfig for response generation
            system_prompt: Optional system prompt for the model

        Yields:
            Token strings as they are generated

        Raises:
            ValueError: If retrieval or generation fails
        """
        if not retrieval_config:
            retrieval_config = RetrievalConfig()

        if not generation_config:
            generation_config = GenerationConfig()

        retrieval_config.validate()
        generation_config.validate()

        try:
            # Step 1: Retrieve relevant documents using vector search
            retrieved_results = self.retrieve_api.retrieve_with_vector(
                collection_name=collection_name,
                index_name=index_name,
                query_vector=query_vector,
                config=retrieval_config
            )

            # Convert retrieval results to source documents
            source_documents = [
                {
                    "chunk_id": r.chunk_id,
                    "content": r.content,
                    "relevance_score": r.relevance_score,
                    "location": r.location,
                    "metadata": r.metadata,
                    "source_document": r.source_document
                }
                for r in retrieved_results
            ]

            # Step 2: Build context from retrieved documents
            context = self._build_context(source_documents)

            # Step 3: Generate streaming response
            yield from self._generate_response_stream(
                query=query_text,
                context=context,
                generation_config=generation_config,
                system_prompt=system_prompt
            )

        except Exception as e:
            raise ValueError(f"Vector streaming retrieve and generate failed: {str(e)}")

    def _generate_response_stream(
        self,
        query: str,
        context: str,
        generation_config: GenerationConfig,
        system_prompt: Optional[str] = None
    ):
        """
        Generate streaming response using foundation model.

        Yields tokens as they are generated by the model.

        Args:
            query: User query
            context: Context from retrieved documents
            generation_config: Generation configuration
            system_prompt: Optional system prompt

        Yields:
            Token strings as they are generated

        Raises:
            ValueError: If generation fails
        """
        # Build the prompt
        if not system_prompt:
            system_prompt = (
                "You are a helpful assistant that answers questions based on provided context. "
                "Always cite your sources when referencing information from the context. "
                "If the context doesn't contain relevant information, say so."
            )

        prompt = f"""System: {system_prompt}

Context:
{context}

Question: {query}

Answer:"""

        try:
            # Call Bedrock API with streaming
            response = self.bedrock_runtime.invoke_model_with_response_stream(
                modelId=generation_config.model_id,
                body=self._build_request_body(
                    prompt=prompt,
                    config=generation_config
                )
            )

            # Process streaming response
            import json
            for event in response.get("body", []):
                if "chunk" in event:
                    chunk = event["chunk"]
                    if "bytes" in chunk:
                        # Decode the chunk
                        chunk_data = json.loads(chunk["bytes"].decode("utf-8"))
                        
                        # Extract token from different response formats
                        if "delta" in chunk_data:
                            delta = chunk_data["delta"]
                            if "text" in delta:
                                yield delta["text"]
                        elif "content" in chunk_data:
                            content = chunk_data["content"]
                            if isinstance(content, list) and len(content) > 0:
                                if "text" in content[0]:
                                    yield content[0]["text"]

        except ClientError as e:
            raise ValueError(f"Streaming model invocation failed: {str(e)}")
        except Exception as e:
            raise ValueError(f"Stream processing failed: {str(e)}")
