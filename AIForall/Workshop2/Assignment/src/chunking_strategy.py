"""Document chunking strategies for Bedrock RAG Retrieval System"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class ChunkingStrategyType(Enum):
    """Supported chunking strategy types"""
    FIXED_SIZE = "FIXED_SIZE"
    CUSTOM = "CUSTOM"


@dataclass
class Chunk:
    """Represents a chunk of text from a document"""
    id: str
    document_id: str
    content: str
    chunk_index: int
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk to dictionary"""
        return {
            "id": self.id,
            "document_id": self.document_id,
            "content": self.content,
            "chunk_index": self.chunk_index,
            "metadata": self.metadata
        }


class ChunkingStrategy(ABC):
    """Abstract base class for document chunking strategies"""

    def __init__(self, strategy_type: ChunkingStrategyType):
        """
        Initialize the chunking strategy.

        Args:
            strategy_type: Type of chunking strategy
        """
        self.strategy_type = strategy_type

    @abstractmethod
    def chunk(
        self,
        document_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Chunk]:
        """
        Chunk a document into smaller pieces.

        Args:
            document_id: ID of the document being chunked
            content: Full text content of the document
            metadata: Optional metadata to include in chunks

        Returns:
            List of Chunk objects

        Raises:
            ValueError: If chunking operation fails
        """
        pass

    @abstractmethod
    def get_config(self) -> Dict[str, Any]:
        """
        Get the configuration of the chunking strategy.

        Returns:
            Dictionary containing strategy configuration
        """
        pass


class FixedSizeChunkingStrategy(ChunkingStrategy):
    """Fixed-size chunking strategy with configurable overlap"""

    def __init__(
        self,
        chunk_size: int = 1024,
        chunk_overlap: int = 20,
        chunk_size_unit: str = "tokens"
    ):
        """
        Initialize fixed-size chunking strategy.

        Args:
            chunk_size: Size of each chunk (default: 1024 tokens)
            chunk_overlap: Number of overlapping tokens between chunks (default: 20)
            chunk_size_unit: Unit of chunk size - "tokens" or "characters" (default: "tokens")

        Raises:
            ValueError: If chunk_size or chunk_overlap are invalid
        """
        super().__init__(ChunkingStrategyType.FIXED_SIZE)

        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")

        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")

        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")

        if chunk_size_unit not in ["tokens", "characters"]:
            raise ValueError("chunk_size_unit must be 'tokens' or 'characters'")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.chunk_size_unit = chunk_size_unit

    def chunk(
        self,
        document_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Chunk]:
        """
        Chunk a document using fixed-size strategy.

        Args:
            document_id: ID of the document being chunked
            content: Full text content of the document
            metadata: Optional metadata to include in chunks

        Returns:
            List of Chunk objects

        Raises:
            ValueError: If chunking operation fails
        """
        if not document_id or len(document_id.strip()) == 0:
            raise ValueError("document_id cannot be empty")

        if not content or len(content.strip()) == 0:
            raise ValueError("content cannot be empty")

        if metadata is None:
            metadata = {}

        chunks = []

        try:
            if self.chunk_size_unit == "characters":
                chunks = self._chunk_by_characters(document_id, content, metadata)
            else:  # tokens
                chunks = self._chunk_by_tokens(document_id, content, metadata)

            return chunks
        except Exception as e:
            raise ValueError(f"Failed to chunk document: {str(e)}")

    def _chunk_by_characters(
        self,
        document_id: str,
        content: str,
        metadata: Dict[str, Any]
    ) -> List[Chunk]:
        """
        Chunk document by character count.

        Args:
            document_id: ID of the document
            content: Full text content
            metadata: Metadata to include in chunks

        Returns:
            List of Chunk objects
        """
        chunks = []
        chunk_index = 0
        start_pos = 0

        while start_pos < len(content):
            # Calculate end position
            end_pos = min(start_pos + self.chunk_size, len(content))

            # Extract chunk content
            chunk_content = content[start_pos:end_pos]

            # Create chunk
            chunk_id = f"{document_id}-chunk-{chunk_index}"
            chunk_metadata = {
                **metadata,
                "chunk_index": chunk_index,
                "chunk_size": self.chunk_size,
                "overlap": self.chunk_overlap,
                "chunk_size_unit": self.chunk_size_unit,
                "start_position": start_pos,
                "end_position": end_pos
            }

            chunk = Chunk(
                id=chunk_id,
                document_id=document_id,
                content=chunk_content,
                chunk_index=chunk_index,
                metadata=chunk_metadata
            )
            chunks.append(chunk)

            # Move to next chunk position (accounting for overlap)
            # Ensure we always make progress to avoid infinite loops
            next_start = end_pos - self.chunk_overlap
            if next_start <= start_pos:
                next_start = start_pos + 1
            start_pos = next_start
            chunk_index += 1

        return chunks

    def _chunk_by_tokens(
        self,
        document_id: str,
        content: str,
        metadata: Dict[str, Any]
    ) -> List[Chunk]:
        """
        Chunk document by approximate token count.

        Uses a simple heuristic: average of 4 characters per token.
        This is an approximation and may vary based on actual tokenization.

        Args:
            document_id: ID of the document
            content: Full text content
            metadata: Metadata to include in chunks

        Returns:
            List of Chunk objects
        """
        # Approximate token count: 1 token ≈ 4 characters
        # This is a rough heuristic; actual tokenization may vary
        chars_per_token = 4
        chunk_size_chars = self.chunk_size * chars_per_token
        overlap_chars = self.chunk_overlap * chars_per_token

        chunks = []
        chunk_index = 0
        start_pos = 0

        while start_pos < len(content):
            # Calculate end position
            end_pos = min(start_pos + chunk_size_chars, len(content))

            # Try to break at word boundary if not at end
            if end_pos < len(content):
                # Find last space before end_pos
                last_space = content.rfind(" ", start_pos, end_pos)
                if last_space > start_pos:
                    end_pos = last_space

            # Extract chunk content
            chunk_content = content[start_pos:end_pos].strip()

            if not chunk_content:
                # Skip empty chunks
                start_pos = end_pos
                continue

            # Create chunk
            chunk_id = f"{document_id}-chunk-{chunk_index}"
            chunk_metadata = {
                **metadata,
                "chunk_index": chunk_index,
                "chunk_size": self.chunk_size,
                "overlap": self.chunk_overlap,
                "chunk_size_unit": self.chunk_size_unit,
                "start_position": start_pos,
                "end_position": end_pos,
                "approximate_tokens": len(chunk_content) // chars_per_token
            }

            chunk = Chunk(
                id=chunk_id,
                document_id=document_id,
                content=chunk_content,
                chunk_index=chunk_index,
                metadata=chunk_metadata
            )
            chunks.append(chunk)

            # Move to next chunk position (accounting for overlap)
            # Ensure we always make progress to avoid infinite loops
            next_start = end_pos - overlap_chars
            if next_start <= start_pos:
                next_start = start_pos + 1
            start_pos = next_start
            chunk_index += 1

        return chunks

    def get_config(self) -> Dict[str, Any]:
        """
        Get the configuration of the fixed-size chunking strategy.

        Returns:
            Dictionary containing strategy configuration
        """
        return {
            "strategy_type": self.strategy_type.value,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "chunk_size_unit": self.chunk_size_unit
        }


class CustomChunkingStrategy(ChunkingStrategy):
    """Custom chunking strategy with user-defined logic"""

    def __init__(self, chunk_func, config: Optional[Dict[str, Any]] = None):
        """
        Initialize custom chunking strategy.

        Args:
            chunk_func: Callable that takes (document_id, content, metadata) and returns List[Chunk]
            config: Optional configuration dictionary for the custom strategy

        Raises:
            ValueError: If chunk_func is not callable
        """
        super().__init__(ChunkingStrategyType.CUSTOM)

        if not callable(chunk_func):
            raise ValueError("chunk_func must be callable")

        self.chunk_func = chunk_func
        self.config = config or {}

    def chunk(
        self,
        document_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Chunk]:
        """
        Chunk a document using custom strategy.

        Args:
            document_id: ID of the document being chunked
            content: Full text content of the document
            metadata: Optional metadata to include in chunks

        Returns:
            List of Chunk objects

        Raises:
            ValueError: If chunking operation fails
        """
        if not document_id or len(document_id.strip()) == 0:
            raise ValueError("document_id cannot be empty")

        if not content or len(content.strip()) == 0:
            raise ValueError("content cannot be empty")

        if metadata is None:
            metadata = {}

        try:
            chunks = self.chunk_func(document_id, content, metadata)

            # Validate that chunks are Chunk objects
            if not isinstance(chunks, list):
                raise ValueError("chunk_func must return a list of Chunk objects")

            for chunk in chunks:
                if not isinstance(chunk, Chunk):
                    raise ValueError("chunk_func must return a list of Chunk objects")

            return chunks
        except Exception as e:
            raise ValueError(f"Failed to chunk document with custom strategy: {str(e)}")

    def get_config(self) -> Dict[str, Any]:
        """
        Get the configuration of the custom chunking strategy.

        Returns:
            Dictionary containing strategy configuration
        """
        return {
            "strategy_type": self.strategy_type.value,
            "config": self.config
        }


class ChunkingStrategyFactory:
    """Factory for creating chunking strategy instances"""

    @staticmethod
    def create_fixed_size_strategy(
        chunk_size: int = 1024,
        chunk_overlap: int = 20,
        chunk_size_unit: str = "tokens"
    ) -> FixedSizeChunkingStrategy:
        """
        Create a fixed-size chunking strategy.

        Args:
            chunk_size: Size of each chunk (default: 1024 tokens)
            chunk_overlap: Number of overlapping tokens between chunks (default: 20)
            chunk_size_unit: Unit of chunk size - "tokens" or "characters" (default: "tokens")

        Returns:
            FixedSizeChunkingStrategy instance

        Raises:
            ValueError: If parameters are invalid
        """
        return FixedSizeChunkingStrategy(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            chunk_size_unit=chunk_size_unit
        )

    @staticmethod
    def create_custom_strategy(
        chunk_func,
        config: Optional[Dict[str, Any]] = None
    ) -> CustomChunkingStrategy:
        """
        Create a custom chunking strategy.

        Args:
            chunk_func: Callable that implements chunking logic
            config: Optional configuration dictionary

        Returns:
            CustomChunkingStrategy instance

        Raises:
            ValueError: If chunk_func is not callable
        """
        return CustomChunkingStrategy(chunk_func, config)
