"""Citation generation for Bedrock RAG Retrieval System"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class CitationMatch:
    """Citation match found in text"""
    text: str
    start_pos: int
    end_pos: int
    source_id: str
    source_location: str
    relevance_score: float


class CitationGenerator:
    """Generates citations linking generated text to source documents"""

    def __init__(self):
        """Initialize citation generator"""
        self.citation_patterns = [
            r'\[(\d+)\]',  # [1], [2], etc.
            r'\(Source:\s*(\d+)\)',  # (Source: 1)
            r'According to source (\d+)',  # According to source 1
            r'As mentioned in \[(\d+)\]',  # As mentioned in [1]
        ]

    def generate_citations(
        self,
        generated_text: str,
        source_documents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate citations from generated text and source documents.

        Args:
            generated_text: Generated response text
            source_documents: List of source document dictionaries

        Returns:
            List of citation dictionaries

        Raises:
            ValueError: If citation generation fails
        """
        citations = []

        # Extract explicit citations from text
        explicit_citations = self._extract_explicit_citations(
            generated_text,
            source_documents
        )
        citations.extend(explicit_citations)

        # Extract implicit citations based on content matching
        implicit_citations = self._extract_implicit_citations(
            generated_text,
            source_documents
        )
        citations.extend(implicit_citations)

        # Remove duplicates and sort by position
        unique_citations = self._deduplicate_citations(citations)
        unique_citations.sort(key=lambda c: c.get("position", 0))

        return unique_citations

    def _extract_explicit_citations(
        self,
        text: str,
        source_documents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extract explicit citations from text (e.g., [1], [2]).

        Args:
            text: Generated text
            source_documents: List of source documents

        Returns:
            List of explicit citations
        """
        citations = []

        # Look for numbered citations like [1], [2], etc.
        for match in re.finditer(r'\[(\d+)\]', text):
            citation_num = int(match.group(1))
            if 0 < citation_num <= len(source_documents):
                source_doc = source_documents[citation_num - 1]
                citations.append({
                    "text": f"[{citation_num}]",
                    "source_id": source_doc.get("chunk_id", ""),
                    "source_location": source_doc.get("location", ""),
                    "relevance_score": source_doc.get("relevance_score", 0.0),
                    "position": match.start(),
                    "type": "explicit"
                })

        return citations

    def _extract_implicit_citations(
        self,
        text: str,
        source_documents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extract implicit citations based on content matching.

        Args:
            text: Generated text
            source_documents: List of source documents

        Returns:
            List of implicit citations
        """
        citations = []

        # For each source document, check if its content appears in the generated text
        for source_doc in source_documents:
            content = source_doc.get("content", "")
            if not content:
                continue

            # Extract key phrases from source content (first 50 chars)
            key_phrase = content[:50].strip()

            # Look for the key phrase in the generated text
            for match in re.finditer(re.escape(key_phrase), text, re.IGNORECASE):
                citations.append({
                    "text": key_phrase,
                    "source_id": source_doc.get("chunk_id", ""),
                    "source_location": source_doc.get("location", ""),
                    "relevance_score": source_doc.get("relevance_score", 0.0),
                    "position": match.start(),
                    "type": "implicit"
                })

        return citations

    def _deduplicate_citations(
        self,
        citations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Remove duplicate citations.

        Args:
            citations: List of citations

        Returns:
            Deduplicated list of citations
        """
        seen = set()
        unique = []

        for citation in citations:
            key = (
                citation.get("source_id"),
                citation.get("source_location"),
                citation.get("position")
            )
            if key not in seen:
                seen.add(key)
                unique.append(citation)

        return unique

    def format_citations_as_footnotes(
        self,
        generated_text: str,
        citations: List[Dict[str, Any]]
    ) -> Tuple[str, str]:
        """
        Format citations as footnotes.

        Args:
            generated_text: Generated text
            citations: List of citations

        Returns:
            Tuple of (formatted_text, footnotes_section)
        """
        if not citations:
            return generated_text, ""

        # Add citation markers to text
        formatted_text = generated_text
        footnotes = []

        for i, citation in enumerate(citations, 1):
            footnotes.append(
                f"[{i}] {citation.get('text', '')} - "
                f"{citation.get('source_location', '')} "
                f"(Relevance: {citation.get('relevance_score', 0.0):.2%})"
            )

        footnotes_section = "\n\nFootnotes:\n" + "\n".join(footnotes)

        return formatted_text, footnotes_section

    def format_citations_as_links(
        self,
        generated_text: str,
        citations: List[Dict[str, Any]]
    ) -> str:
        """
        Format citations as markdown links.

        Args:
            generated_text: Generated text
            citations: List of citations

        Returns:
            Text with markdown links
        """
        formatted_text = generated_text

        for citation in citations:
            text = citation.get("text", "")
            location = citation.get("source_location", "")

            if text and location:
                # Replace text with markdown link
                markdown_link = f"[{text}]({location})"
                formatted_text = formatted_text.replace(text, markdown_link, 1)

        return formatted_text

    def format_citations_as_inline(
        self,
        generated_text: str,
        citations: List[Dict[str, Any]]
    ) -> str:
        """
        Format citations as inline references.

        Args:
            generated_text: Generated text
            citations: List of citations

        Returns:
            Text with inline citations
        """
        formatted_text = generated_text

        for i, citation in enumerate(citations, 1):
            text = citation.get("text", "")
            location = citation.get("source_location", "")

            if text and location:
                # Add inline citation
                inline_citation = f"{text}[{i}]"
                formatted_text = formatted_text.replace(text, inline_citation, 1)

        return formatted_text

    def extract_source_references(
        self,
        generated_text: str
    ) -> List[str]:
        """
        Extract source references from generated text.

        Args:
            generated_text: Generated text

        Returns:
            List of source references found
        """
        references = []

        # Look for common source reference patterns
        patterns = [
            r'According to (?:the )?(?:document|source|paper|article|study) (?:titled )?"([^"]+)"',
            r'In (?:the )?(?:document|source|paper|article|study) (?:titled )?"([^"]+)"',
            r'(?:The )?(?:document|source|paper|article|study) (?:titled )?"([^"]+)" (?:states|says|mentions)',
            r'\[([^\]]+)\]',  # [reference]
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, generated_text, re.IGNORECASE):
                reference = match.group(1)
                if reference not in references:
                    references.append(reference)

        return references

    def validate_citations(
        self,
        citations: List[Dict[str, Any]]
    ) -> bool:
        """
        Validate citations structure.

        Args:
            citations: List of citations to validate

        Returns:
            True if all citations are valid

        Raises:
            ValueError: If any citation is invalid
        """
        required_fields = ["text", "source_id", "source_location", "relevance_score"]

        for i, citation in enumerate(citations):
            for field in required_fields:
                if field not in citation:
                    raise ValueError(
                        f"Citation {i} missing required field: {field}"
                    )

            if not isinstance(citation["relevance_score"], (int, float)):
                raise ValueError(
                    f"Citation {i} has invalid relevance_score type"
                )

            if citation["relevance_score"] < 0.0 or citation["relevance_score"] > 1.0:
                raise ValueError(
                    f"Citation {i} has relevance_score outside valid range [0.0, 1.0]"
                )

        return True

    def merge_citations(
        self,
        citations_list: List[List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        Merge multiple citation lists.

        Args:
            citations_list: List of citation lists to merge

        Returns:
            Merged and deduplicated citations
        """
        merged = []
        for citations in citations_list:
            merged.extend(citations)

        return self._deduplicate_citations(merged)

    def filter_citations_by_score(
        self,
        citations: List[Dict[str, Any]],
        min_score: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Filter citations by minimum relevance score.

        Args:
            citations: List of citations
            min_score: Minimum relevance score threshold

        Returns:
            Filtered citations
        """
        return [
            c for c in citations
            if c.get("relevance_score", 0.0) >= min_score
        ]

    def get_citation_statistics(
        self,
        citations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get statistics about citations.

        Args:
            citations: List of citations

        Returns:
            Dictionary with citation statistics
        """
        if not citations:
            return {
                "total_citations": 0,
                "explicit_citations": 0,
                "implicit_citations": 0,
                "average_relevance_score": 0.0,
                "unique_sources": 0
            }

        explicit = [c for c in citations if c.get("type") == "explicit"]
        implicit = [c for c in citations if c.get("type") == "implicit"]
        unique_sources = len(set(c.get("source_id") for c in citations))

        avg_score = sum(c.get("relevance_score", 0.0) for c in citations) / len(citations)

        return {
            "total_citations": len(citations),
            "explicit_citations": len(explicit),
            "implicit_citations": len(implicit),
            "average_relevance_score": avg_score,
            "unique_sources": unique_sources
        }
