"""Response formatting and result objects for Bedrock RAG Retrieval System"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
import json


class ResponseFormat(Enum):
    """Enumeration of response formats"""
    JSON = "json"
    DICT = "dict"
    TEXT = "text"
    MARKDOWN = "markdown"


@dataclass
class Citation:
    """Citation linking to source document"""
    text: str
    source_id: str
    source_location: str
    relevance_score: float
    page_number: Optional[int] = None
    section: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    def to_markdown(self) -> str:
        """Convert to markdown format"""
        citation_text = f"[{self.text}]({self.source_location})"
        if self.page_number:
            citation_text += f" (p. {self.page_number})"
        return citation_text


@dataclass
class RetrievalResultItem:
    """Single retrieval result item"""
    chunk_id: str
    content: str
    relevance_score: float
    location: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    source_document: str = ""
    chunk_index: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    def to_markdown(self) -> str:
        """Convert to markdown format"""
        md = f"### Result: {self.source_document}\n\n"
        md += f"**Relevance Score:** {self.relevance_score:.2%}\n\n"
        md += f"**Location:** {self.location}\n\n"
        md += f"**Content:**\n\n{self.content}\n\n"
        if self.metadata:
            md += "**Metadata:**\n\n"
            for key, value in self.metadata.items():
                md += f"- {key}: {value}\n"
        return md

    def to_text(self) -> str:
        """Convert to plain text format"""
        text = f"Result: {self.source_document}\n"
        text += f"Relevance Score: {self.relevance_score:.2%}\n"
        text += f"Location: {self.location}\n"
        text += f"Content: {self.content}\n"
        return text


@dataclass
class RetrievalResponse:
    """Response from retrieval operation"""
    results: List[RetrievalResultItem] = field(default_factory=list)
    total_results: int = 0
    query: str = ""
    retrieval_type: str = "semantic"
    execution_time_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "results": [r.to_dict() for r in self.results],
            "total_results": self.total_results,
            "query": self.query,
            "retrieval_type": self.retrieval_type,
            "execution_time_ms": self.execution_time_ms,
            "timestamp": self.timestamp
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent)

    def to_markdown(self) -> str:
        """Convert to markdown format"""
        md = f"# Retrieval Results\n\n"
        md += f"**Query:** {self.query}\n\n"
        md += f"**Retrieval Type:** {self.retrieval_type}\n\n"
        md += f"**Total Results:** {self.total_results}\n\n"
        md += f"**Execution Time:** {self.execution_time_ms:.2f}ms\n\n"
        md += f"**Timestamp:** {self.timestamp}\n\n"
        md += "---\n\n"

        for i, result in enumerate(self.results, 1):
            md += f"## Result {i}\n\n"
            md += result.to_markdown()
            md += "\n---\n\n"

        return md

    def to_text(self) -> str:
        """Convert to plain text format"""
        text = "RETRIEVAL RESULTS\n"
        text += "=" * 50 + "\n\n"
        text += f"Query: {self.query}\n"
        text += f"Retrieval Type: {self.retrieval_type}\n"
        text += f"Total Results: {self.total_results}\n"
        text += f"Execution Time: {self.execution_time_ms:.2f}ms\n"
        text += f"Timestamp: {self.timestamp}\n"
        text += "=" * 50 + "\n\n"

        for i, result in enumerate(self.results, 1):
            text += f"Result {i}:\n"
            text += result.to_text()
            text += "\n" + "-" * 50 + "\n\n"

        return text

    def add_result(self, result: RetrievalResultItem) -> None:
        """Add a result to the response"""
        self.results.append(result)
        self.total_results = len(self.results)

    def get_top_result(self) -> Optional[RetrievalResultItem]:
        """Get the top result by relevance score"""
        if not self.results:
            return None
        return max(self.results, key=lambda r: r.relevance_score)

    def get_results_above_threshold(self, threshold: float) -> List[RetrievalResultItem]:
        """Get results above a relevance score threshold"""
        return [r for r in self.results if r.relevance_score >= threshold]

    def format(self, format_type: ResponseFormat = ResponseFormat.JSON) -> str:
        """Format response in specified format"""
        if format_type == ResponseFormat.JSON:
            return self.to_json()
        elif format_type == ResponseFormat.MARKDOWN:
            return self.to_markdown()
        elif format_type == ResponseFormat.TEXT:
            return self.to_text()
        elif format_type == ResponseFormat.DICT:
            return str(self.to_dict())
        else:
            return self.to_json()


@dataclass
class GenerationResponse:
    """Response from retrieve and generate operation"""
    generated_text: str
    source_documents: List[RetrievalResultItem] = field(default_factory=list)
    citations: List[Citation] = field(default_factory=list)
    model_used: str = ""
    generation_time_ms: float = 0.0
    retrieval_time_ms: float = 0.0
    total_time_ms: float = 0.0
    query: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "generated_text": self.generated_text,
            "source_documents": [d.to_dict() for d in self.source_documents],
            "citations": [c.to_dict() for c in self.citations],
            "model_used": self.model_used,
            "generation_time_ms": self.generation_time_ms,
            "retrieval_time_ms": self.retrieval_time_ms,
            "total_time_ms": self.total_time_ms,
            "query": self.query,
            "timestamp": self.timestamp
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent)

    def to_markdown(self) -> str:
        """Convert to markdown format"""
        md = f"# Generated Response\n\n"
        md += f"**Query:** {self.query}\n\n"
        md += f"**Model:** {self.model_used}\n\n"
        md += "---\n\n"
        md += f"## Response\n\n{self.generated_text}\n\n"
        md += "---\n\n"

        if self.citations:
            md += "## Citations\n\n"
            for i, citation in enumerate(self.citations, 1):
                md += f"{i}. {citation.to_markdown()}\n"
            md += "\n"

        if self.source_documents:
            md += "## Source Documents\n\n"
            for i, doc in enumerate(self.source_documents, 1):
                md += f"### Source {i}\n\n"
                md += f"**Location:** {doc.location}\n\n"
                md += f"**Relevance:** {doc.relevance_score:.2%}\n\n"
                md += f"**Content:** {doc.content}\n\n"

        md += "---\n\n"
        md += f"**Retrieval Time:** {self.retrieval_time_ms:.2f}ms\n"
        md += f"**Generation Time:** {self.generation_time_ms:.2f}ms\n"
        md += f"**Total Time:** {self.total_time_ms:.2f}ms\n"
        md += f"**Timestamp:** {self.timestamp}\n"

        return md

    def to_text(self) -> str:
        """Convert to plain text format"""
        text = "GENERATED RESPONSE\n"
        text += "=" * 50 + "\n\n"
        text += f"Query: {self.query}\n"
        text += f"Model: {self.model_used}\n"
        text += "=" * 50 + "\n\n"
        text += f"Response:\n{self.generated_text}\n\n"

        if self.citations:
            text += "Citations:\n"
            for i, citation in enumerate(self.citations, 1):
                text += f"{i}. {citation.text} ({citation.source_location})\n"
            text += "\n"

        if self.source_documents:
            text += "Source Documents:\n"
            for i, doc in enumerate(self.source_documents, 1):
                text += f"Source {i}: {doc.location}\n"
                text += f"Relevance: {doc.relevance_score:.2%}\n"
                text += f"Content: {doc.content}\n\n"

        text += "=" * 50 + "\n"
        text += f"Retrieval Time: {self.retrieval_time_ms:.2f}ms\n"
        text += f"Generation Time: {self.generation_time_ms:.2f}ms\n"
        text += f"Total Time: {self.total_time_ms:.2f}ms\n"
        text += f"Timestamp: {self.timestamp}\n"

        return text

    def add_source_document(self, document: RetrievalResultItem) -> None:
        """Add a source document"""
        self.source_documents.append(document)

    def add_citation(self, citation: Citation) -> None:
        """Add a citation"""
        self.citations.append(citation)

    def format(self, format_type: ResponseFormat = ResponseFormat.JSON) -> str:
        """Format response in specified format"""
        if format_type == ResponseFormat.JSON:
            return self.to_json()
        elif format_type == ResponseFormat.MARKDOWN:
            return self.to_markdown()
        elif format_type == ResponseFormat.TEXT:
            return self.to_text()
        elif format_type == ResponseFormat.DICT:
            return str(self.to_dict())
        else:
            return self.to_json()


class ResponseFormatter:
    """Utility class for formatting responses"""

    @staticmethod
    def format_retrieval_response(
        results: List[Dict[str, Any]],
        query: str,
        retrieval_type: str = "semantic",
        execution_time_ms: float = 0.0
    ) -> RetrievalResponse:
        """
        Format retrieval results into a RetrievalResponse.

        Args:
            results: List of retrieval result dictionaries
            query: Original query string
            retrieval_type: Type of retrieval performed
            execution_time_ms: Time taken for retrieval

        Returns:
            Formatted RetrievalResponse
        """
        response = RetrievalResponse(
            query=query,
            retrieval_type=retrieval_type,
            execution_time_ms=execution_time_ms
        )

        for result in results:
            item = RetrievalResultItem(
                chunk_id=result.get("chunk_id", ""),
                content=result.get("content", ""),
                relevance_score=result.get("relevance_score", 0.0),
                location=result.get("location", ""),
                metadata=result.get("metadata", {}),
                source_document=result.get("source_document", ""),
                chunk_index=result.get("chunk_index")
            )
            response.add_result(item)

        return response

    @staticmethod
    def format_generation_response(
        generated_text: str,
        source_documents: List[Dict[str, Any]],
        citations: List[Dict[str, Any]],
        model_used: str = "",
        generation_time_ms: float = 0.0,
        retrieval_time_ms: float = 0.0,
        query: str = ""
    ) -> GenerationResponse:
        """
        Format generation results into a GenerationResponse.

        Args:
            generated_text: Generated response text
            source_documents: List of source document dictionaries
            citations: List of citation dictionaries
            model_used: Name of the model used
            generation_time_ms: Time taken for generation
            retrieval_time_ms: Time taken for retrieval
            query: Original query string

        Returns:
            Formatted GenerationResponse
        """
        response = GenerationResponse(
            generated_text=generated_text,
            model_used=model_used,
            generation_time_ms=generation_time_ms,
            retrieval_time_ms=retrieval_time_ms,
            total_time_ms=generation_time_ms + retrieval_time_ms,
            query=query
        )

        for doc in source_documents:
            item = RetrievalResultItem(
                chunk_id=doc.get("chunk_id", ""),
                content=doc.get("content", ""),
                relevance_score=doc.get("relevance_score", 0.0),
                location=doc.get("location", ""),
                metadata=doc.get("metadata", {}),
                source_document=doc.get("source_document", ""),
                chunk_index=doc.get("chunk_index")
            )
            response.add_source_document(item)

        for citation in citations:
            cite = Citation(
                text=citation.get("text", ""),
                source_id=citation.get("source_id", ""),
                source_location=citation.get("source_location", ""),
                relevance_score=citation.get("relevance_score", 0.0),
                page_number=citation.get("page_number"),
                section=citation.get("section")
            )
            response.add_citation(cite)

        return response
