"""
Indexer module for Proof-of-Monk

Coordinates data flow from adapters to database.
"""

from typing import Dict, Any
import logging
import hashlib

from proof_of_monk.core.database import Database
from proof_of_monk.adapters.base import BaseAdapter

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
            "tweets": 0,
            "bookmarks": 0,
            "likes": 0,
            "documents": 0,
            "errors": 0,
        }

        # Process all records from adapter
        for record in adapter.parse():
            try:
                record_type = record.get("type")

                if record_type == "tweet":
                    self._index_tweet(record)
                    counts["tweets"] += 1

                elif record_type == "bookmark":
                    self._index_bookmark(record)
                    counts["bookmarks"] += 1

                elif record_type == "like":
                    self._index_like(record)
                    counts["likes"] += 1

                elif record_type == "document":
                    self._index_document(record)
                    counts["documents"] += 1

                else:
                    logger.warning(f"Unknown record type: {record_type}")
                    counts["errors"] += 1

                # Log progress every 1000 items
                total = sum(v for k, v in counts.items() if k != "errors")
                if total % 1000 == 0:
                    logger.info(f"Indexed {total} items so far...")

            except Exception as e:
                logger.error(f"Error indexing record: {e}")
                counts["errors"] += 1
                continue

        logger.info(f"Indexing complete: {counts}")
        return counts

    def _index_tweet(self, record: Dict[str, Any]) -> None:
        """
        Index a tweet record.

        Args:
            record: Tweet data dictionary
        """
        self.db.insert_tweet(
            tweet_id=record["tweet_id"],
            user_id=record.get("user_id", "unknown"),
            created_at=record["created_at"],
            full_text=record["full_text"],
            reply_to_tweet_id=record.get("reply_to_tweet_id"),
            reply_to_user=record.get("reply_to_user"),
            retweet_count=record.get("retweet_count", 0),
            favorite_count=record.get("favorite_count", 0),
            is_retweet=record.get("is_retweet", False),
            is_reply=record.get("is_reply", False),
            entities=record.get("entities"),
        )

    def _index_bookmark(self, record: Dict[str, Any]) -> None:
        """
        Index a bookmark record.

        Args:
            record: Bookmark data dictionary
        """
        self.db.insert_bookmark(
            tweet_id=record["tweet_id"],
            expanded_url=record.get("expanded_url"),
            full_text=record.get("full_text"),
            bookmarked_at=record.get("bookmarked_at"),
        )

    def _index_like(self, record: Dict[str, Any]) -> None:
        """
        Index a like record.

        Args:
            record: Like data dictionary
        """
        self.db.insert_like(
            tweet_id=record["tweet_id"],
            expanded_url=record.get("expanded_url"),
            full_text=record.get("full_text"),
            liked_at=record.get("liked_at"),
        )

    def _index_document(self, record: Dict[str, Any]) -> None:
        """
        Index a document record.

        Args:
            record: Document data dictionary
        """
        # Generate document ID from content hash
        content = record["content"]
        source_path = record.get("source_path", "")
        doc_id = hashlib.sha256(f"{source_path}::{content}".encode("utf-8")).hexdigest()[:16]

        self.db.insert_document(
            doc_id=doc_id,
            source_type=record.get("source_type", "unknown"),
            content_type=record.get("content_type"),
            title=record.get("title"),
            content=content,
            metadata=record.get("metadata"),
            tags=record.get("tags"),
            source_path=source_path,
            created_at=record.get("created_at"),
        )
