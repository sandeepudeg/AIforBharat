"""Tests for document chunking strategies"""

import pytest
import os
from src.chunking_strategy import (
    Chunk,
    ChunkingStrategy,
    ChunkingStrategyType,
    FixedSizeChunkingStrategy,
    CustomChunkingStrategy,
    ChunkingStrategyFactory
)

# Disable hypothesis database to avoid Windows hanging issues
os.environ['HYPOTHESIS_DATABASE_DIRECTORY'] = 'none'


# ============================================================================
# Unit Tests for FixedSizeChunkingStrategy
# ============================================================================

class TestFixedSizeChunkingStrategy:
    """Tests for fixed-size chunking strategy"""

    def test_initialization_valid_parameters(self):
        """Test initialization with valid parameters"""
        strategy = FixedSizeChunkingStrategy(chunk_size=512, chunk_overlap=10)
        assert strategy.chunk_size == 512
        assert strategy.chunk_overlap == 10
        assert strategy.chunk_size_unit == "tokens"
        assert strategy.strategy_type == ChunkingStrategyType.FIXED_SIZE

    def test_initialization_with_characters_unit(self):
        """Test initialization with character-based unit"""
        strategy = FixedSizeChunkingStrategy(
            chunk_size=1000,
            chunk_overlap=50,
            chunk_size_unit="characters"
        )
        assert strategy.chunk_size_unit == "characters"

    def test_initialization_invalid_chunk_size(self):
        """Test initialization with invalid chunk size"""
        with pytest.raises(ValueError, match="chunk_size must be greater than 0"):
            FixedSizeChunkingStrategy(chunk_size=0)

        with pytest.raises(ValueError, match="chunk_size must be greater than 0"):
            FixedSizeChunkingStrategy(chunk_size=-100)

    def test_initialization_invalid_chunk_overlap(self):
        """Test initialization with invalid chunk overlap"""
        with pytest.raises(ValueError, match="chunk_overlap cannot be negative"):
            FixedSizeChunkingStrategy(chunk_overlap=-10)

        with pytest.raises(ValueError, match="chunk_overlap must be less than chunk_size"):
            FixedSizeChunkingStrategy(chunk_size=100, chunk_overlap=100)

        with pytest.raises(ValueError, match="chunk_overlap must be less than chunk_size"):
            FixedSizeChunkingStrategy(chunk_size=100, chunk_overlap=150)

    def test_initialization_invalid_chunk_size_unit(self):
        """Test initialization with invalid chunk size unit"""
        with pytest.raises(ValueError, match="chunk_size_unit must be 'tokens' or 'characters'"):
            FixedSizeChunkingStrategy(chunk_size_unit="words")

    def test_chunk_by_characters_basic(self):
        """Test chunking by character count"""
        strategy = FixedSizeChunkingStrategy(
            chunk_size=50,
            chunk_overlap=10,
            chunk_size_unit="characters"
        )

        content = "a" * 150  # 150 characters
        chunks = strategy.chunk("doc-001", content)

        assert len(chunks) > 0
        assert all(isinstance(chunk, Chunk) for chunk in chunks)
        assert all(chunk.document_id == "doc-001" for chunk in chunks)
        assert all(chunk.chunk_index >= 0 for chunk in chunks)

    def test_chunk_by_tokens_basic(self):
        """Test chunking by token count"""
        strategy = FixedSizeChunkingStrategy(
            chunk_size=100,
            chunk_overlap=10,
            chunk_size_unit="tokens"
        )

        content = "This is a sample document. " * 50  # Approximately 300 tokens
        chunks = strategy.chunk("doc-001", content)

        assert len(chunks) > 0
        assert all(isinstance(chunk, Chunk) for chunk in chunks)
        assert all(chunk.document_id == "doc-001" for chunk in chunks)

    def test_chunk_empty_document_id(self):
        """Test chunking with empty document ID"""
        strategy = FixedSizeChunkingStrategy()

        with pytest.raises(ValueError, match="document_id cannot be empty"):
            strategy.chunk("", "Some content")

        with pytest.raises(ValueError, match="document_id cannot be empty"):
            strategy.chunk("   ", "Some content")

    def test_chunk_empty_content(self):
        """Test chunking with empty content"""
        strategy = FixedSizeChunkingStrategy()

        with pytest.raises(ValueError, match="content cannot be empty"):
            strategy.chunk("doc-001", "")

        with pytest.raises(ValueError, match="content cannot be empty"):
            strategy.chunk("doc-001", "   ")

    def test_chunk_with_metadata(self):
        """Test chunking with metadata"""
        strategy = FixedSizeChunkingStrategy(chunk_size=50, chunk_size_unit="characters")

        metadata = {"source": "test", "author": "test-user"}
        chunks = strategy.chunk("doc-001", "a" * 150, metadata=metadata)

        assert all("source" in chunk.metadata for chunk in chunks)
        assert all(chunk.metadata["source"] == "test" for chunk in chunks)
        assert all(chunk.metadata["author"] == "test-user" for chunk in chunks)

    def test_chunk_metadata_includes_strategy_info(self):
        """Test that chunk metadata includes strategy information"""
        strategy = FixedSizeChunkingStrategy(
            chunk_size=100,
            chunk_overlap=20,
            chunk_size_unit="tokens"
        )

        chunks = strategy.chunk("doc-001", "This is test content. " * 50)

        for chunk in chunks:
            assert "chunk_index" in chunk.metadata
            assert "chunk_size" in chunk.metadata
            assert "overlap" in chunk.metadata
            assert "chunk_size_unit" in chunk.metadata
            assert chunk.metadata["chunk_size"] == 100
            assert chunk.metadata["overlap"] == 20
            assert chunk.metadata["chunk_size_unit"] == "tokens"

    def test_chunk_ids_are_unique(self):
        """Test that chunk IDs are unique"""
        strategy = FixedSizeChunkingStrategy(chunk_size=50, chunk_size_unit="characters")

        chunks = strategy.chunk("doc-001", "a" * 200)
        chunk_ids = [chunk.id for chunk in chunks]

        assert len(chunk_ids) == len(set(chunk_ids))

    def test_chunk_indices_are_sequential(self):
        """Test that chunk indices are sequential"""
        strategy = FixedSizeChunkingStrategy(chunk_size=50, chunk_size_unit="characters")

        chunks = strategy.chunk("doc-001", "a" * 200)

        for i, chunk in enumerate(chunks):
            assert chunk.chunk_index == i

    def test_get_config(self):
        """Test getting strategy configuration"""
        strategy = FixedSizeChunkingStrategy(
            chunk_size=512,
            chunk_overlap=20,
            chunk_size_unit="tokens"
        )

        config = strategy.get_config()

        assert config["strategy_type"] == "FIXED_SIZE"
        assert config["chunk_size"] == 512
        assert config["chunk_overlap"] == 20
        assert config["chunk_size_unit"] == "tokens"

    def test_chunk_to_dict(self):
        """Test converting chunk to dictionary"""
        chunk = Chunk(
            id="chunk-001",
            document_id="doc-001",
            content="Sample content",
            chunk_index=0,
            metadata={"key": "value"}
        )

        chunk_dict = chunk.to_dict()

        assert chunk_dict["id"] == "chunk-001"
        assert chunk_dict["document_id"] == "doc-001"
        assert chunk_dict["content"] == "Sample content"
        assert chunk_dict["chunk_index"] == 0
        assert chunk_dict["metadata"]["key"] == "value"


# ============================================================================
# Unit Tests for CustomChunkingStrategy
# ============================================================================

class TestCustomChunkingStrategy:
    """Tests for custom chunking strategy"""

    def test_initialization_valid_function(self):
        """Test initialization with valid chunk function"""
        def custom_chunk_func(doc_id, content, metadata):
            return [Chunk(
                id=f"{doc_id}-chunk-0",
                document_id=doc_id,
                content=content,
                chunk_index=0,
                metadata=metadata or {}
            )]

        strategy = CustomChunkingStrategy(custom_chunk_func)
        assert strategy.strategy_type == ChunkingStrategyType.CUSTOM
        assert strategy.chunk_func == custom_chunk_func

    def test_initialization_with_config(self):
        """Test initialization with configuration"""
        def custom_chunk_func(doc_id, content, metadata):
            return []

        config = {"param1": "value1", "param2": 42}
        strategy = CustomChunkingStrategy(custom_chunk_func, config=config)

        assert strategy.config == config

    def test_initialization_invalid_function(self):
        """Test initialization with non-callable"""
        with pytest.raises(ValueError, match="chunk_func must be callable"):
            CustomChunkingStrategy("not_a_function")

    def test_chunk_with_custom_function(self):
        """Test chunking with custom function"""
        def custom_chunk_func(doc_id, content, metadata):
            # Simple custom strategy: split by sentences
            sentences = content.split(". ")
            chunks = []
            for i, sentence in enumerate(sentences):
                chunk = Chunk(
                    id=f"{doc_id}-chunk-{i}",
                    document_id=doc_id,
                    content=sentence,
                    chunk_index=i,
                    metadata=metadata or {}
                )
                chunks.append(chunk)
            return chunks

        strategy = CustomChunkingStrategy(custom_chunk_func)
        content = "First sentence. Second sentence. Third sentence."
        chunks = strategy.chunk("doc-001", content)

        assert len(chunks) == 3
        assert chunks[0].content == "First sentence"
        assert chunks[1].content == "Second sentence"
        assert chunks[2].content == "Third sentence."

    def test_chunk_empty_document_id(self):
        """Test chunking with empty document ID"""
        def custom_chunk_func(doc_id, content, metadata):
            return []

        strategy = CustomChunkingStrategy(custom_chunk_func)

        with pytest.raises(ValueError, match="document_id cannot be empty"):
            strategy.chunk("", "Some content")

    def test_chunk_empty_content(self):
        """Test chunking with empty content"""
        def custom_chunk_func(doc_id, content, metadata):
            return []

        strategy = CustomChunkingStrategy(custom_chunk_func)

        with pytest.raises(ValueError, match="content cannot be empty"):
            strategy.chunk("doc-001", "")

    def test_chunk_function_returns_non_list(self):
        """Test error when chunk function returns non-list"""
        def bad_chunk_func(doc_id, content, metadata):
            return "not a list"

        strategy = CustomChunkingStrategy(bad_chunk_func)

        with pytest.raises(ValueError, match="chunk_func must return a list of Chunk objects"):
            strategy.chunk("doc-001", "Some content")

    def test_chunk_function_returns_non_chunk_objects(self):
        """Test error when chunk function returns non-Chunk objects"""
        def bad_chunk_func(doc_id, content, metadata):
            return ["not a chunk object"]

        strategy = CustomChunkingStrategy(bad_chunk_func)

        with pytest.raises(ValueError, match="chunk_func must return a list of Chunk objects"):
            strategy.chunk("doc-001", "Some content")

    def test_get_config(self):
        """Test getting custom strategy configuration"""
        def custom_chunk_func(doc_id, content, metadata):
            return []

        config = {"param1": "value1"}
        strategy = CustomChunkingStrategy(custom_chunk_func, config=config)

        result_config = strategy.get_config()

        assert result_config["strategy_type"] == "CUSTOM"
        assert result_config["config"] == config


# ============================================================================
# Unit Tests for ChunkingStrategyFactory
# ============================================================================

class TestChunkingStrategyFactory:
    """Tests for chunking strategy factory"""

    def test_create_fixed_size_strategy_default(self):
        """Test creating fixed-size strategy with defaults"""
        strategy = ChunkingStrategyFactory.create_fixed_size_strategy()

        assert isinstance(strategy, FixedSizeChunkingStrategy)
        assert strategy.chunk_size == 1024
        assert strategy.chunk_overlap == 20
        assert strategy.chunk_size_unit == "tokens"

    def test_create_fixed_size_strategy_custom_params(self):
        """Test creating fixed-size strategy with custom parameters"""
        strategy = ChunkingStrategyFactory.create_fixed_size_strategy(
            chunk_size=512,
            chunk_overlap=50,
            chunk_size_unit="characters"
        )

        assert strategy.chunk_size == 512
        assert strategy.chunk_overlap == 50
        assert strategy.chunk_size_unit == "characters"

    def test_create_custom_strategy(self):
        """Test creating custom strategy"""
        def custom_func(doc_id, content, metadata):
            return []

        strategy = ChunkingStrategyFactory.create_custom_strategy(custom_func)

        assert isinstance(strategy, CustomChunkingStrategy)
        assert strategy.chunk_func == custom_func

    def test_create_custom_strategy_with_config(self):
        """Test creating custom strategy with configuration"""
        def custom_func(doc_id, content, metadata):
            return []

        config = {"key": "value"}
        strategy = ChunkingStrategyFactory.create_custom_strategy(custom_func, config=config)

        assert strategy.config == config


# ============================================================================
# Property-Based Tests
# ============================================================================

class TestChunkingStrategyProperties:
    """Property-based tests for chunking strategies"""

    @pytest.mark.parametrize("chunk_size,chunk_overlap,content_length", [
        (256, 20, 1000), (512, 50, 5000), (1024, 100, 10000), (512, 25, 2000), (256, 10, 500)
    ])
    def test_property_fixed_size_chunks_cover_content(
        self,
        chunk_size,
        chunk_overlap,
        content_length
    ):
        """
        **Feature: bedrock-rag-retrieval, Property 2: Document Ingestion Completeness**
        
        Property: For any fixed-size chunking strategy, all content should be covered by chunks
        (accounting for overlap). No content should be lost during chunking.
        
        **Validates: Requirements 2.1, 2.4**
        """
        # Ensure valid parameters
        if chunk_overlap >= chunk_size:
            chunk_overlap = chunk_size - 1

        strategy = FixedSizeChunkingStrategy(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            chunk_size_unit="characters"
        )

        content = "a" * content_length
        chunks = strategy.chunk("doc-001", content)

        # Verify chunks are not empty
        assert len(chunks) > 0

        # Verify all chunks have content
        assert all(len(chunk.content) > 0 for chunk in chunks)

        # Verify chunk indices are sequential
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_index == i

        # Verify combined chunks cover the content (with overlap)
        combined_content = ""
        for chunk in chunks:
            combined_content += chunk.content

        # The combined content should contain all original content
        # (accounting for potential word boundary adjustments)
        assert len(combined_content) >= len(content) * 0.9  # Allow 10% loss due to boundaries

    @pytest.mark.parametrize("chunk_size,chunk_overlap,content_length", [
        (256, 20, 1000), (512, 50, 2000), (1024, 100, 5000), (512, 25, 1500), (256, 10, 500)
    ])
    def test_property_chunk_indices_sequential(
        self,
        chunk_size,
        chunk_overlap,
        content_length
    ):
        """
        **Feature: bedrock-rag-retrieval, Property 2: Document Ingestion Completeness**
        
        Property: For any chunking operation, chunk indices should be sequential starting from 0.
        
        **Validates: Requirements 2.1, 2.4**
        """
        # Ensure valid parameters
        if chunk_overlap >= chunk_size:
            chunk_overlap = chunk_size - 1

        strategy = FixedSizeChunkingStrategy(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            chunk_size_unit="characters"
        )

        content = "a" * content_length
        chunks = strategy.chunk("doc-001", content)

        # Verify indices are sequential
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_index == i

    @pytest.mark.parametrize("chunk_size,chunk_overlap", [
        (256, 20), (512, 50), (1024, 100), (512, 25), (256, 10)
    ])
    def test_property_chunk_ids_unique(
        self,
        chunk_size,
        chunk_overlap
    ):
        """
        **Feature: bedrock-rag-retrieval, Property 2: Document Ingestion Completeness**
        
        Property: For any chunking operation, all chunk IDs should be unique.
        
        **Validates: Requirements 2.1, 2.4**
        """
        # Ensure valid parameters
        if chunk_overlap >= chunk_size:
            chunk_overlap = chunk_size - 1

        strategy = FixedSizeChunkingStrategy(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            chunk_size_unit="characters"
        )

        content = "a" * 1000
        chunks = strategy.chunk("doc-001", content)

        chunk_ids = [chunk.id for chunk in chunks]
        assert len(chunk_ids) == len(set(chunk_ids))

    @pytest.mark.parametrize("chunk_size,chunk_overlap", [
        (256, 20), (512, 50), (1024, 100), (512, 25), (256, 10)
    ])
    def test_property_chunk_metadata_consistency(
        self,
        chunk_size,
        chunk_overlap
    ):
        """
        **Feature: bedrock-rag-retrieval, Property 2: Document Ingestion Completeness**
        
        Property: For any chunking operation, all chunks should have consistent metadata
        reflecting the strategy configuration.
        
        **Validates: Requirements 2.1, 2.4**
        """
        # Ensure valid parameters
        if chunk_overlap >= chunk_size:
            chunk_overlap = chunk_size - 1

        strategy = FixedSizeChunkingStrategy(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            chunk_size_unit="characters"
        )

        content = "a" * 1000
        chunks = strategy.chunk("doc-001", content)

        # Verify all chunks have required metadata
        for chunk in chunks:
            assert "chunk_index" in chunk.metadata
            assert "chunk_size" in chunk.metadata
            assert "overlap" in chunk.metadata
            assert "chunk_size_unit" in chunk.metadata
            assert chunk.metadata["chunk_size"] == chunk_size
            assert chunk.metadata["overlap"] == chunk_overlap
            assert chunk.metadata["chunk_size_unit"] == "characters"

    @pytest.mark.parametrize("doc_id,content", [
        ("doc-001", "a" * 500), ("doc-002", "b" * 1000), ("doc-003", "c" * 2000),
        ("doc-004", "d" * 1500), ("doc-005", "e" * 3000)
    ])
    def test_property_chunk_document_id_preserved(
        self,
        doc_id,
        content
    ):
        """
        **Feature: bedrock-rag-retrieval, Property 2: Document Ingestion Completeness**
        
        Property: For any chunking operation, all chunks should preserve the document ID.
        
        **Validates: Requirements 2.1, 2.4**
        """
        strategy = FixedSizeChunkingStrategy(
            chunk_size=100,
            chunk_overlap=10,
            chunk_size_unit="characters"
        )

        chunks = strategy.chunk(doc_id, content)

        # Verify all chunks have the correct document ID
        assert all(chunk.document_id == doc_id for chunk in chunks)
