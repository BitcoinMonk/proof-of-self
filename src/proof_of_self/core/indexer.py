"""
Indexer module for Proof-of-Self

Coordinates data flow from adapters to database.
"""

from typing import Dict, Any
import logging

from proof_of_self.core.database import Database
from proof_of_self.adapters.base import BaseAdapter
from proof_of_self.core.chunker import generate_document_id

logger = logging.getLogger(__name__)


class Indexer:
    """Indexes data from adapters into the database."""

    def __init__(self, database: Database):
        """
        Initialize indexer.

        Args:
            database: Database instance to write to
        """
        self.db = database

    def index_from_adapter(self, adapter: BaseAdapter) -> Dict[str, int]:
        """
        Index all data from an adapter.

        Args:
            adapter: Data source adapter to read from

        Returns:
            Dictionary with counts of indexed items
        """
        logger.info(f"Starting indexing from {adapter.__class__.__name__}")

        # Validate source first
        if not adapter.validate_source():
            raise ValueError(f"Invalid data source for {adapter.__class__.__name__}")

        counts = {
            "documents": 0,
            "errors": 0,
        }

        # Process all records from adapter (all should be "document" type now)
        for record in adapter.parse():
            try:
                record_type = record.get("type")

                if record_type == "document":
                    self._index_document(record)
                    counts["documents"] += 1
                else:
                    logger.warning(f"Unknown record type: {record_type}")
                    counts["errors"] += 1

                # Log progress every 1000 items
                if counts["documents"] % 1000 == 0:
                    logger.info(f"Indexed {counts['documents']} documents so far...")

            except Exception as e:
                logger.error(f"Error indexing record: {e}")
                counts["errors"] += 1
                continue

        logger.info(f"Indexing complete: {counts}")
        return counts

    def _index_document(self, record: Dict[str, Any]) -> None:
        """
        Index a document record.

        Args:
            record: Document data dictionary
        """
        # Generate document ID using chunker's method
        content = record["content"]
        source_path = record.get("source_path", "")
        created_at = record.get("created_at")

        # Convert datetime to ISO string for ID generation
        created_at_str = created_at.isoformat() if created_at else ""

        doc_id = generate_document_id(
            content=content,
            source_path=source_path,
            created_at=created_at_str,
        )

        self.db.insert_document(
            doc_id=doc_id,
            source_type=record.get("source_type", "unknown"),
            content_type=record.get("content_type"),
            title=record.get("title"),
            author=record.get("author"),
            content=content,
            source_path=source_path,
            is_chunked=False,  # TODO: Handle chunking in Phase 1 Week 2
            metadata=record.get("metadata"),
            tags=record.get("tags"),
            created_at=created_at,
        )
