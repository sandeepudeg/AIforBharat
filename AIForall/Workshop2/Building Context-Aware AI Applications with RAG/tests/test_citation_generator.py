"""Tests for Citation Generation"""

import pytest
from src.citation_generator import CitationGenerator, CitationMatch
import os

# Disable hypothesis database to avoid Windows hanging issues
os.environ['HYPOTHESIS_DATABASE_DIRECTORY'] = 'none'


class TestCitationGenerator:
    """Tests for CitationGenerator"""

    def test_init(self):
        """Test citation generator initialization"""
        generator = CitationGenerator()
        assert generator is not None
        assert len(generator.citation_patterns) > 0

    def test_generate_citations_explicit(self):
        """Test generating explicit citations"""
        generator = CitationGenerator()
        
        text = "According to [1], AI is transformative. [2] mentions machine learning."
        sources = [
            {
                "chunk_id": "chunk-001",
                "content": "AI is transformative",
                "relevance_score": 0.95,
                "location": "s3://bucket/doc1.txt"
            },
            {
                "chunk_id": "chunk-002",
                "content": "Machine learning is important",
                "relevance_score": 0.85,
                "location": "s3://bucket/doc2.txt"
            }
        ]
        
        citations = generator.generate_citations(text, sources)
        assert len(citations) > 0
        assert any(c.get("type") == "explicit" for c in citations)

    def test_generate_citations_implicit(self):
        """Test generating implicit citations"""
        generator = CitationGenerator()
        
        text = "AI is transformative technology that changes everything."
        sources = [
            {
                "chunk_id": "chunk-001",
                "content": "AI is transformative technology",
                "relevance_score": 0.95,
                "location": "s3://bucket/doc1.txt"
            }
        ]
        
        citations = generator.generate_citations(text, sources)
        assert len(citations) > 0

    def test_extract_explicit_citations(self):
        """Test extracting explicit citations"""
        generator = CitationGenerator()
        
        text = "First point [1]. Second point [2]. Third point [3]."
        sources = [
            {"chunk_id": f"chunk-{i:03d}", "content": f"Content {i}", 
             "relevance_score": 0.9, "location": f"s3://bucket/doc{i}.txt"}
            for i in range(1, 4)
        ]
        
        citations = generator._extract_explicit_citations(text, sources)
        assert len(citations) == 3

    def test_extract_implicit_citations(self):
        """Test extracting implicit citations"""
        generator = CitationGenerator()
        
        text = "The document mentions that AI is transformative."
        sources = [
            {
                "chunk_id": "chunk-001",
                "content": "AI is transformative",
                "relevance_score": 0.95,
                "location": "s3://bucket/doc1.txt"
            }
        ]
        
        citations = generator._extract_implicit_citations(text, sources)
        assert isinstance(citations, list)

    def test_deduplicate_citations(self):
        """Test deduplicating citations"""
        generator = CitationGenerator()
        
        citations = [
            {"source_id": "1", "source_location": "loc1", "position": 0, "text": "text1"},
            {"source_id": "1", "source_location": "loc1", "position": 0, "text": "text1"},
            {"source_id": "2", "source_location": "loc2", "position": 10, "text": "text2"}
        ]
        
        unique = generator._deduplicate_citations(citations)
        assert len(unique) == 2

    def test_format_citations_as_footnotes(self):
        """Test formatting citations as footnotes"""
        generator = CitationGenerator()
        
        text = "This is generated text with citations."
        citations = [
            {
                "text": "Citation 1",
                "source_location": "s3://bucket/doc1.txt",
                "relevance_score": 0.95
            },
            {
                "text": "Citation 2",
                "source_location": "s3://bucket/doc2.txt",
                "relevance_score": 0.85
            }
        ]
        
        formatted_text, footnotes = generator.format_citations_as_footnotes(text, citations)
        assert "Footnotes:" in footnotes
        assert "Citation 1" in footnotes
        assert "95.00%" in footnotes

    def test_format_citations_as_links(self):
        """Test formatting citations as markdown links"""
        generator = CitationGenerator()
        
        text = "This mentions Citation 1 and Citation 2."
        citations = [
            {
                "text": "Citation 1",
                "source_location": "s3://bucket/doc1.txt"
            },
            {
                "text": "Citation 2",
                "source_location": "s3://bucket/doc2.txt"
            }
        ]
        
        formatted = generator.format_citations_as_links(text, citations)
        assert "[Citation 1]" in formatted
        assert "s3://bucket/doc1.txt" in formatted

    def test_format_citations_as_inline(self):
        """Test formatting citations as inline references"""
        generator = CitationGenerator()
        
        text = "This mentions Citation 1 and Citation 2."
        citations = [
            {"text": "Citation 1", "source_location": "s3://bucket/doc1.txt"},
            {"text": "Citation 2", "source_location": "s3://bucket/doc2.txt"}
        ]
        
        formatted = generator.format_citations_as_inline(text, citations)
        assert "[1]" in formatted or "[2]" in formatted

    def test_extract_source_references(self):
        """Test extracting source references"""
        generator = CitationGenerator()
        
        text = 'According to the document "AI Overview", AI is transformative.'
        references = generator.extract_source_references(text)
        assert len(references) > 0

    def test_validate_citations_valid(self):
        """Test validating valid citations"""
        generator = CitationGenerator()
        
        citations = [
            {
                "text": "Citation 1",
                "source_id": "chunk-001",
                "source_location": "s3://bucket/doc1.txt",
                "relevance_score": 0.95
            }
        ]
        
        assert generator.validate_citations(citations) is True

    def test_validate_citations_missing_field(self):
        """Test validating citations with missing field"""
        generator = CitationGenerator()
        
        citations = [
            {
                "text": "Citation 1",
                "source_id": "chunk-001",
                # Missing source_location
                "relevance_score": 0.95
            }
        ]
        
        with pytest.raises(ValueError, match="missing required field"):
            generator.validate_citations(citations)

    def test_validate_citations_invalid_score(self):
        """Test validating citations with invalid score"""
        generator = CitationGenerator()
        
        citations = [
            {
                "text": "Citation 1",
                "source_id": "chunk-001",
                "source_location": "s3://bucket/doc1.txt",
                "relevance_score": 1.5  # Invalid: > 1.0
            }
        ]
        
        with pytest.raises(ValueError, match="outside valid range"):
            generator.validate_citations(citations)

    def test_merge_citations(self):
        """Test merging citation lists"""
        generator = CitationGenerator()
        
        citations_list = [
            [
                {"source_id": "1", "source_location": "loc1", "position": 0, "text": "text1"},
                {"source_id": "2", "source_location": "loc2", "position": 10, "text": "text2"}
            ],
            [
                {"source_id": "3", "source_location": "loc3", "position": 20, "text": "text3"}
            ]
        ]
        
        merged = generator.merge_citations(citations_list)
        assert len(merged) >= 3

    def test_filter_citations_by_score(self):
        """Test filtering citations by score"""
        generator = CitationGenerator()
        
        citations = [
            {"text": "High score", "source_id": "1", "source_location": "loc1", "relevance_score": 0.95},
            {"text": "Low score", "source_id": "2", "source_location": "loc2", "relevance_score": 0.3},
            {"text": "Medium score", "source_id": "3", "source_location": "loc3", "relevance_score": 0.7}
        ]
        
        filtered = generator.filter_citations_by_score(citations, min_score=0.5)
        assert len(filtered) == 2
        assert all(c["relevance_score"] >= 0.5 for c in filtered)

    def test_get_citation_statistics(self):
        """Test getting citation statistics"""
        generator = CitationGenerator()
        
        citations = [
            {"text": "Citation 1", "source_id": "1", "source_location": "loc1", 
             "relevance_score": 0.95, "type": "explicit"},
            {"text": "Citation 2", "source_id": "2", "source_location": "loc2", 
             "relevance_score": 0.85, "type": "implicit"},
            {"text": "Citation 3", "source_id": "1", "source_location": "loc1", 
             "relevance_score": 0.75, "type": "explicit"}
        ]
        
        stats = generator.get_citation_statistics(citations)
        assert stats["total_citations"] == 3
        assert stats["explicit_citations"] == 2
        assert stats["implicit_citations"] == 1
        assert stats["unique_sources"] == 2
        assert 0.8 < stats["average_relevance_score"] < 0.9

    def test_get_citation_statistics_empty(self):
        """Test getting statistics for empty citations"""
        generator = CitationGenerator()
        
        stats = generator.get_citation_statistics([])
        assert stats["total_citations"] == 0
        assert stats["average_relevance_score"] == 0.0

    @pytest.mark.parametrize("min_score", [0.5, 0.7, 0.9])
    def test_filter_citations_various_thresholds(self, min_score):
        """Test filtering citations with various thresholds"""
        generator = CitationGenerator()
        
        citations = [
            {"text": f"Citation {i}", "source_id": str(i), "source_location": f"loc{i}",
             "relevance_score": 0.5 + (i * 0.1)}
            for i in range(1, 6)
        ]
        
        filtered = generator.filter_citations_by_score(citations, min_score=min_score)
        assert all(c["relevance_score"] >= min_score for c in filtered)
