"""Tests for Response Formatting and Result Objects"""

import pytest
import json
from src.response_formatter import (
    ResponseFormat,
    Citation,
    RetrievalResultItem,
    RetrievalResponse,
    GenerationResponse,
    ResponseFormatter
)
import os

# Disable hypothesis database to avoid Windows hanging issues
os.environ['HYPOTHESIS_DATABASE_DIRECTORY'] = 'none'


class TestCitation:
    """Tests for Citation"""

    def test_citation_creation(self):
        """Test creating a citation"""
        citation = Citation(
            text="sample text",
            source_id="source-001",
            source_location="s3://bucket/doc.txt",
            relevance_score=0.95
        )
        assert citation.text == "sample text"
        assert citation.relevance_score == 0.95

    def test_citation_to_dict(self):
        """Test converting citation to dictionary"""
        citation = Citation(
            text="sample text",
            source_id="source-001",
            source_location="s3://bucket/doc.txt",
            relevance_score=0.95
        )
        citation_dict = citation.to_dict()
        assert isinstance(citation_dict, dict)
        assert citation_dict["text"] == "sample text"

    def test_citation_to_markdown(self):
        """Test converting citation to markdown"""
        citation = Citation(
            text="sample text",
            source_id="source-001",
            source_location="s3://bucket/doc.txt",
            relevance_score=0.95
        )
        markdown = citation.to_markdown()
        assert isinstance(markdown, str)
        assert "sample text" in markdown


class TestRetrievalResultItem:
    """Tests for RetrievalResultItem"""

    def test_result_item_creation(self):
        """Test creating a retrieval result item"""
        item = RetrievalResultItem(
            chunk_id="chunk-001",
            content="Sample content",
            relevance_score=0.95,
            location="s3://bucket/doc.txt"
        )
        assert item.chunk_id == "chunk-001"
        assert item.relevance_score == 0.95

    def test_result_item_to_dict(self):
        """Test converting result item to dictionary"""
        item = RetrievalResultItem(
            chunk_id="chunk-001",
            content="Sample content",
            relevance_score=0.95,
            location="s3://bucket/doc.txt"
        )
        item_dict = item.to_dict()
        assert isinstance(item_dict, dict)
        assert item_dict["chunk_id"] == "chunk-001"

    def test_result_item_to_markdown(self):
        """Test converting result item to markdown"""
        item = RetrievalResultItem(
            chunk_id="chunk-001",
            content="Sample content",
            relevance_score=0.95,
            location="s3://bucket/doc.txt",
            source_document="doc-001"
        )
        markdown = item.to_markdown()
        assert isinstance(markdown, str)
        assert "Sample content" in markdown
        assert "95.00%" in markdown

    def test_result_item_to_text(self):
        """Test converting result item to text"""
        item = RetrievalResultItem(
            chunk_id="chunk-001",
            content="Sample content",
            relevance_score=0.95,
            location="s3://bucket/doc.txt"
        )
        text = item.to_text()
        assert isinstance(text, str)
        assert "Sample content" in text


class TestRetrievalResponse:
    """Tests for RetrievalResponse"""

    def test_retrieval_response_creation(self):
        """Test creating a retrieval response"""
        response = RetrievalResponse(
            query="test query",
            retrieval_type="semantic"
        )
        assert response.query == "test query"
        assert response.retrieval_type == "semantic"

    def test_add_result(self):
        """Test adding results to response"""
        response = RetrievalResponse()
        item = RetrievalResultItem(
            chunk_id="chunk-001",
            content="Content",
            relevance_score=0.95,
            location="s3://bucket/doc.txt"
        )
        response.add_result(item)
        assert len(response.results) == 1
        assert response.total_results == 1

    def test_get_top_result(self):
        """Test getting top result"""
        response = RetrievalResponse()
        item1 = RetrievalResultItem(
            chunk_id="chunk-001",
            content="Content 1",
            relevance_score=0.85,
            location="s3://bucket/doc1.txt"
        )
        item2 = RetrievalResultItem(
            chunk_id="chunk-002",
            content="Content 2",
            relevance_score=0.95,
            location="s3://bucket/doc2.txt"
        )
        response.add_result(item1)
        response.add_result(item2)
        top = response.get_top_result()
        assert top.relevance_score == 0.95

    def test_get_results_above_threshold(self):
        """Test getting results above threshold"""
        response = RetrievalResponse()
        item1 = RetrievalResultItem(
            chunk_id="chunk-001",
            content="Content 1",
            relevance_score=0.85,
            location="s3://bucket/doc1.txt"
        )
        item2 = RetrievalResultItem(
            chunk_id="chunk-002",
            content="Content 2",
            relevance_score=0.95,
            location="s3://bucket/doc2.txt"
        )
        response.add_result(item1)
        response.add_result(item2)
        above_threshold = response.get_results_above_threshold(0.9)
        assert len(above_threshold) == 1
        assert above_threshold[0].relevance_score == 0.95

    def test_retrieval_response_to_dict(self):
        """Test converting response to dictionary"""
        response = RetrievalResponse(query="test")
        response_dict = response.to_dict()
        assert isinstance(response_dict, dict)
        assert response_dict["query"] == "test"

    def test_retrieval_response_to_json(self):
        """Test converting response to JSON"""
        response = RetrievalResponse(query="test")
        json_str = response.to_json()
        assert isinstance(json_str, str)
        data = json.loads(json_str)
        assert data["query"] == "test"

    def test_retrieval_response_to_markdown(self):
        """Test converting response to markdown"""
        response = RetrievalResponse(query="test query")
        markdown = response.to_markdown()
        assert isinstance(markdown, str)
        assert "test query" in markdown

    def test_retrieval_response_to_text(self):
        """Test converting response to text"""
        response = RetrievalResponse(query="test query")
        text = response.to_text()
        assert isinstance(text, str)
        assert "test query" in text

    @pytest.mark.parametrize("format_type", [
        ResponseFormat.JSON,
        ResponseFormat.MARKDOWN,
        ResponseFormat.TEXT,
        ResponseFormat.DICT
    ])
    def test_retrieval_response_format(self, format_type):
        """Test formatting response in different formats"""
        response = RetrievalResponse(query="test")
        formatted = response.format(format_type)
        assert isinstance(formatted, str)
        assert len(formatted) > 0


class TestGenerationResponse:
    """Tests for GenerationResponse"""

    def test_generation_response_creation(self):
        """Test creating a generation response"""
        response = GenerationResponse(
            generated_text="Generated answer",
            model_used="claude-3",
            query="test query"
        )
        assert response.generated_text == "Generated answer"
        assert response.model_used == "claude-3"

    def test_add_source_document(self):
        """Test adding source document"""
        response = GenerationResponse(generated_text="Answer")
        doc = RetrievalResultItem(
            chunk_id="chunk-001",
            content="Source content",
            relevance_score=0.95,
            location="s3://bucket/doc.txt"
        )
        response.add_source_document(doc)
        assert len(response.source_documents) == 1

    def test_add_citation(self):
        """Test adding citation"""
        response = GenerationResponse(generated_text="Answer")
        citation = Citation(
            text="cited text",
            source_id="source-001",
            source_location="s3://bucket/doc.txt",
            relevance_score=0.95
        )
        response.add_citation(citation)
        assert len(response.citations) == 1

    def test_generation_response_to_dict(self):
        """Test converting response to dictionary"""
        response = GenerationResponse(
            generated_text="Answer",
            query="test"
        )
        response_dict = response.to_dict()
        assert isinstance(response_dict, dict)
        assert response_dict["generated_text"] == "Answer"

    def test_generation_response_to_json(self):
        """Test converting response to JSON"""
        response = GenerationResponse(generated_text="Answer")
        json_str = response.to_json()
        assert isinstance(json_str, str)
        data = json.loads(json_str)
        assert data["generated_text"] == "Answer"

    def test_generation_response_to_markdown(self):
        """Test converting response to markdown"""
        response = GenerationResponse(
            generated_text="Generated answer",
            query="test query"
        )
        markdown = response.to_markdown()
        assert isinstance(markdown, str)
        assert "Generated answer" in markdown

    def test_generation_response_to_text(self):
        """Test converting response to text"""
        response = GenerationResponse(
            generated_text="Generated answer",
            query="test query"
        )
        text = response.to_text()
        assert isinstance(text, str)
        assert "Generated answer" in text

    @pytest.mark.parametrize("format_type", [
        ResponseFormat.JSON,
        ResponseFormat.MARKDOWN,
        ResponseFormat.TEXT,
        ResponseFormat.DICT
    ])
    def test_generation_response_format(self, format_type):
        """Test formatting response in different formats"""
        response = GenerationResponse(generated_text="Answer")
        formatted = response.format(format_type)
        assert isinstance(formatted, str)
        assert len(formatted) > 0


class TestResponseFormatter:
    """Tests for ResponseFormatter utility"""

    def test_format_retrieval_response(self):
        """Test formatting retrieval response"""
        results = [
            {
                "chunk_id": "chunk-001",
                "content": "Content 1",
                "relevance_score": 0.95,
                "location": "s3://bucket/doc1.txt",
                "source_document": "doc-001"
            },
            {
                "chunk_id": "chunk-002",
                "content": "Content 2",
                "relevance_score": 0.85,
                "location": "s3://bucket/doc2.txt",
                "source_document": "doc-002"
            }
        ]
        response = ResponseFormatter.format_retrieval_response(
            results=results,
            query="test query",
            retrieval_type="semantic"
        )
        assert isinstance(response, RetrievalResponse)
        assert len(response.results) == 2
        assert response.query == "test query"

    def test_format_generation_response(self):
        """Test formatting generation response"""
        source_docs = [
            {
                "chunk_id": "chunk-001",
                "content": "Source content",
                "relevance_score": 0.95,
                "location": "s3://bucket/doc.txt",
                "source_document": "doc-001"
            }
        ]
        citations = [
            {
                "text": "cited text",
                "source_id": "source-001",
                "source_location": "s3://bucket/doc.txt",
                "relevance_score": 0.95
            }
        ]
        response = ResponseFormatter.format_generation_response(
            generated_text="Generated answer",
            source_documents=source_docs,
            citations=citations,
            model_used="claude-3",
            query="test query"
        )
        assert isinstance(response, GenerationResponse)
        assert response.generated_text == "Generated answer"
        assert len(response.source_documents) == 1
        assert len(response.citations) == 1
