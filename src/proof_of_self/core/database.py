"""
Database module for Proof-of-Self

Handles SQLite database operations, schema management, and full-text search indexing.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import json
import logging

logger = logging.getLogger(__name__)


class Database:
    """SQLite database manager for Proof-of-Self."""

    def __init__(self, db_path: str):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn: Optional[sqlite3.Connection] = None
        self._connect()
        self._initialize_schema()

    def _connect(self) -> None:
        """Establish database connection."""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row  # Return rows as dicts
        # Enable foreign keys
        self.conn.execute("PRAGMA foreign_keys = ON")
        logger.info(f"Connected to database: {self.db_path}")

    def _initialize_schema(self) -> None:
        """Create database schema if it doesn't exist."""
        cursor = self.conn.cursor()

        # UNIVERSAL TABLES ONLY - No Twitter-specific tables!

        # Documents table (universal storage for all content)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                source_type TEXT NOT NULL,
                content_type TEXT,
                title TEXT,
                author TEXT,
                content TEXT,
                source_path TEXT,
                is_chunked BOOLEAN DEFAULT 0,
                metadata TEXT,
                tags TEXT,
                created_at TIMESTAMP,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Chunks table (for large documents like books, long PDFs)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
                UNIQUE(document_id, chunk_index)
            )
        """)

        # FTS for documents
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
                id UNINDEXED,
                title,
                author,
                content,
                tags,
                content=documents,
                content_rowid=rowid,
                tokenize='porter unicode61'
            )
        """)

        # FTS for chunks
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
                id UNINDEXED,
                content,
                content=chunks,
                content_rowid=rowid,
                tokenize='porter unicode61'
            )
        """)

        # Triggers for documents FTS
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS documents_ai AFTER INSERT ON documents BEGIN
                INSERT INTO documents_fts(rowid, id, title, author, content, tags)
                VALUES (new.rowid, new.id, new.title, new.author, new.content, new.tags);
            END
        """)

        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS documents_ad AFTER DELETE ON documents BEGIN
                DELETE FROM documents_fts WHERE rowid = old.rowid;
            END
        """)

        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS documents_au AFTER UPDATE ON documents BEGIN
                UPDATE documents_fts
                SET title = new.title, author = new.author, content = new.content, tags = new.tags
                WHERE rowid = old.rowid;
            END
        """)

        # Triggers for chunks FTS
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS chunks_ai AFTER INSERT ON chunks BEGIN
                INSERT INTO chunks_fts(rowid, id, content)
                VALUES (new.rowid, new.id, new.content);
            END
        """)

        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS chunks_ad AFTER DELETE ON chunks BEGIN
                DELETE FROM chunks_fts WHERE rowid = old.rowid;
            END
        """)

        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS chunks_au AFTER UPDATE ON chunks BEGIN
                UPDATE chunks_fts SET content = new.content WHERE rowid = old.rowid;
            END
        """)

        # Indexes for common queries (documents and chunks only)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_created ON documents(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_source_type ON documents(source_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_content_type ON documents(content_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_is_chunked ON documents(is_chunked)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_chunk_index ON chunks(document_id, chunk_index)")

        self.conn.commit()
        logger.info("Database schema initialized")

    def insert_document(
        self,
        doc_id: str,
        source_type: str,
        content: Optional[str],
        content_type: Optional[str] = None,
        title: Optional[str] = None,
        author: Optional[str] = None,
        is_chunked: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        source_path: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ) -> None:
        """Insert a document into the database."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO documents (
                id, source_type, content_type, title, author, content,
                source_path, is_chunked, metadata, tags, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                doc_id,
                source_type,
                content_type,
                title,
                author,
                content,
                source_path,
                is_chunked,
                json.dumps(metadata) if metadata else None,
                json.dumps(tags) if tags else None,
                created_at or datetime.now(),
            ),
        )
        self.conn.commit()

    def insert_chunk(
        self,
        chunk_id: str,
        document_id: str,
        chunk_index: int,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Insert a chunk for a large document."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO chunks (
                id, document_id, chunk_index, content, metadata
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                chunk_id,
                document_id,
                chunk_index,
                content,
                json.dumps(metadata) if metadata else None,
            ),
        )
        self.conn.commit()

    def get_chunks(self, document_id: str) -> List[Dict[str, Any]]:
        """Get all chunks for a document in order."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, document_id, chunk_index, content, metadata
            FROM chunks
            WHERE document_id = ?
            ORDER BY chunk_index
            """,
            (document_id,),
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_stats(self) -> Dict[str, int]:
        """Get statistics about indexed data."""
        cursor = self.conn.cursor()

        stats = {}

        # Universal tables
        cursor.execute("SELECT COUNT(*) FROM documents")
        stats["total_documents"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM documents WHERE is_chunked = 0")
        stats["complete_documents"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM documents WHERE is_chunked = 1")
        stats["chunked_documents"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM chunks")
        stats["total_chunks"] = cursor.fetchone()[0]

        # Breakdown by source type
        cursor.execute("""
            SELECT source_type, COUNT(*) as count
            FROM documents
            GROUP BY source_type
        """)
        for row in cursor.fetchall():
            stats[f"source_{row['source_type']}"] = row['count']

        # Breakdown by content type
        cursor.execute("""
            SELECT content_type, COUNT(*) as count
            FROM documents
            GROUP BY content_type
        """)
        for row in cursor.fetchall():
            stats[f"type_{row['content_type']}"] = row['count']

        return stats

    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
