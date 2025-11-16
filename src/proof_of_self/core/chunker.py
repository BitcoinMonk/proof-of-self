"""
Document chunking for Proof-of-Self

Handles semantic chunking of large documents (books, PDFs, long articles)
with configurable chunk size and overlap.
"""

import hashlib
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Chunk:
    """Represents a chunk of a larger document."""
    chunk_id: str
    document_id: str
    chunk_index: int
    content: str
    metadata: Dict[str, Any]


class DocumentChunker:
    """Semantic document chunker with configurable size and overlap."""

    def __init__(
        self,
        chunk_size: int = 800,  # Target tokens (roughly 3200 characters)
        overlap_percent: float = 0.15,  # 15% overlap
        min_chunk_size: int = 500,  # Minimum tokens
    ):
        """
        Initialize chunker.

        Args:
            chunk_size: Target size in tokens (default: 800)
            overlap_percent: Overlap as fraction (default: 0.15 = 15%)
            min_chunk_size: Minimum chunk size in tokens
        """
        self.chunk_size = chunk_size
        self.overlap_percent = overlap_percent
        self.min_chunk_size = min_chunk_size
        self.overlap_size = int(chunk_size * overlap_percent)

    def should_chunk(self, content: str) -> bool:
        """
        Determine if content should be chunked.

        Args:
            content: Document content

        Returns:
            True if content exceeds threshold for chunking
        """
        token_count = self._estimate_tokens(content)
        return token_count > self.chunk_size

    def chunk_document(
        self,
        document_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Chunk]:
        """
        Chunk a document into overlapping pieces.

        Args:
            document_id: Unique document ID
            content: Full document content
            metadata: Optional metadata to attach to chunks

        Returns:
            List of Chunk objects
        """
        if not self.should_chunk(content):
            # Don't chunk if content is small enough
            return []

        # Split into semantic boundaries (paragraphs, then sentences)
        segments = self._split_into_segments(content)

        # Group segments into chunks
        chunks = []
        current_chunk_content = []
        current_token_count = 0
        chunk_index = 0

        for segment in segments:
            segment_tokens = self._estimate_tokens(segment)

            # If this segment alone exceeds chunk size, split it further
            if segment_tokens > self.chunk_size * 1.5:
                # Force split long segment at sentence boundaries
                sentences = self._split_into_sentences(segment)
                for sentence in sentences:
                    sentence_tokens = self._estimate_tokens(sentence)

                    if current_token_count + sentence_tokens > self.chunk_size:
                        # Save current chunk
                        if current_chunk_content:
                            chunk = self._create_chunk(
                                document_id,
                                chunk_index,
                                " ".join(current_chunk_content),
                                metadata,
                            )
                            chunks.append(chunk)
                            chunk_index += 1

                        # Start new chunk with overlap from previous
                        overlap_content = self._get_overlap_content(current_chunk_content)
                        current_chunk_content = [overlap_content, sentence] if overlap_content else [sentence]
                        current_token_count = self._estimate_tokens(" ".join(current_chunk_content))
                    else:
                        current_chunk_content.append(sentence)
                        current_token_count += sentence_tokens

            elif current_token_count + segment_tokens > self.chunk_size:
                # Save current chunk
                if current_chunk_content:
                    chunk = self._create_chunk(
                        document_id,
                        chunk_index,
                        "\n\n".join(current_chunk_content),
                        metadata,
                    )
                    chunks.append(chunk)
                    chunk_index += 1

                # Start new chunk with overlap
                overlap_content = self._get_overlap_content(current_chunk_content)
                current_chunk_content = [overlap_content, segment] if overlap_content else [segment]
                current_token_count = self._estimate_tokens("\n\n".join(current_chunk_content))
            else:
                # Add to current chunk
                current_chunk_content.append(segment)
                current_token_count += segment_tokens

        # Save final chunk
        if current_chunk_content:
            chunk = self._create_chunk(
                document_id,
                chunk_index,
                "\n\n".join(current_chunk_content),
                metadata,
            )
            chunks.append(chunk)

        return chunks

    def _split_into_segments(self, content: str) -> List[str]:
        """
        Split content into semantic segments (paragraphs).

        Args:
            content: Document content

        Returns:
            List of paragraph segments
        """
        # Split on multiple newlines (paragraph boundaries)
        segments = re.split(r'\n\s*\n', content)

        # Filter out empty segments
        segments = [s.strip() for s in segments if s.strip()]

        return segments

    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.

        Args:
            text: Text to split

        Returns:
            List of sentences
        """
        # Simple sentence splitting (could be improved with nltk if needed)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _get_overlap_content(self, chunks: List[str]) -> str:
        """
        Get overlap content from previous chunks.

        Args:
            chunks: List of content chunks

        Returns:
            Overlap content string
        """
        if not chunks:
            return ""

        # Get last chunk(s) for overlap
        full_content = " ".join(chunks)
        tokens = self._estimate_tokens(full_content)

        if tokens <= self.overlap_size:
            return full_content

        # Take approximately overlap_size worth of content from the end
        words = full_content.split()
        overlap_words = int(len(words) * (self.overlap_size / tokens))
        return " ".join(words[-overlap_words:]) if overlap_words > 0 else ""

    def _create_chunk(
        self,
        document_id: str,
        chunk_index: int,
        content: str,
        metadata: Optional[Dict[str, Any]],
    ) -> Chunk:
        """
        Create a Chunk object.

        Args:
            document_id: Parent document ID
            chunk_index: Position in document
            content: Chunk content
            metadata: Additional metadata

        Returns:
            Chunk object
        """
        # Generate unique chunk ID
        chunk_id = f"{document_id}_chunk_{chunk_index}"

        # Build chunk metadata
        chunk_metadata = {
            "chunk_index": chunk_index,
            "token_count": self._estimate_tokens(content),
            "char_count": len(content),
        }
        if metadata:
            chunk_metadata.update(metadata)

        return Chunk(
            chunk_id=chunk_id,
            document_id=document_id,
            chunk_index=chunk_index,
            content=content,
            metadata=chunk_metadata,
        )

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Uses simple heuristic: 1 token ≈ 4 characters for English text.
        This is approximate but works well for chunking purposes.

        Args:
            text: Text to estimate

        Returns:
            Estimated token count
        """
        return len(text) // 4


def generate_document_id(
    content: str,
    source_path: str,
    created_at: str,
) -> str:
    """
    Generate deterministic document ID.

    Args:
        content: Document content (or first 1000 chars for large docs)
        source_path: Source file path or identifier
        created_at: Creation timestamp (ISO format)

    Returns:
        SHA256 hash as document ID
    """
    # For large content, only use first 1000 chars for hashing
    content_sample = content[:1000] if len(content) > 1000 else content

    unique_str = f"{content_sample}{source_path}{created_at}"
    return hashlib.sha256(unique_str.encode()).hexdigest()
