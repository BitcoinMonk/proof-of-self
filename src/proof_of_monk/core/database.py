"""
Database module for Proof-of-Monk

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
    """SQLite database manager for Proof-of-Monk."""

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

        # Tweets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tweets (
                tweet_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                full_text TEXT NOT NULL,
                reply_to_tweet_id TEXT,
                reply_to_user TEXT,
                retweet_count INTEGER DEFAULT 0,
                favorite_count INTEGER DEFAULT 0,
                is_retweet BOOLEAN DEFAULT 0,
                is_reply BOOLEAN DEFAULT 0,
                entities TEXT,  -- JSON blob with hashtags, mentions, urls
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Full-text search index for tweets
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS tweets_fts USING fts5(
                tweet_id UNINDEXED,
                full_text,
                content=tweets,
                content_rowid=rowid
            )
        """)

        # Triggers to keep FTS in sync
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS tweets_ai AFTER INSERT ON tweets BEGIN
                INSERT INTO tweets_fts(rowid, tweet_id, full_text)
                VALUES (new.rowid, new.tweet_id, new.full_text);
            END
        """)

        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS tweets_ad AFTER DELETE ON tweets BEGIN
                DELETE FROM tweets_fts WHERE rowid = old.rowid;
            END
        """)

        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS tweets_au AFTER UPDATE ON tweets BEGIN
                UPDATE tweets_fts SET full_text = new.full_text WHERE rowid = old.rowid;
            END
        """)

        # Bookmarks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookmarks (
                tweet_id TEXT PRIMARY KEY,
                expanded_url TEXT,
                full_text TEXT,
                bookmarked_at TIMESTAMP,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # FTS for bookmarks
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS bookmarks_fts USING fts5(
                tweet_id UNINDEXED,
                full_text,
                content=bookmarks,
                content_rowid=rowid
            )
        """)

        # Likes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS likes (
                tweet_id TEXT PRIMARY KEY,
                expanded_url TEXT,
                full_text TEXT,
                liked_at TIMESTAMP,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Thoughts/notes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS thoughts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                tags TEXT,  -- JSON array
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # FTS for thoughts
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS thoughts_fts USING fts5(
                id UNINDEXED,
                content,
                content=thoughts,
                content_rowid=id
            )
        """)

        # Articles table (for tracking published work)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                status TEXT DEFAULT 'draft',  -- draft, published
                published_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                published_at TIMESTAMP
            )
        """)

        # Link tweets to articles
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tweet_to_article (
                tweet_id TEXT NOT NULL,
                article_id INTEGER NOT NULL,
                relationship TEXT DEFAULT 'inspired_by',  -- inspired_by, quoted_in, etc.
                FOREIGN KEY (article_id) REFERENCES articles(id),
                PRIMARY KEY (tweet_id, article_id)
            )
        """)

        # Documents table (universal storage for all content)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                source_type TEXT NOT NULL,
                content_type TEXT,
                title TEXT,
                content TEXT NOT NULL,
                metadata TEXT,
                tags TEXT,
                source_path TEXT,
                created_at TIMESTAMP,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # FTS for documents
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
                id UNINDEXED,
                title,
                content,
                content=documents,
                content_rowid=rowid
            )
        """)

        # Triggers for documents FTS
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS documents_ai AFTER INSERT ON documents BEGIN
                INSERT INTO documents_fts(rowid, id, title, content)
                VALUES (new.rowid, new.id, new.title, new.content);
            END
        """)

        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS documents_ad AFTER DELETE ON documents BEGIN
                DELETE FROM documents_fts WHERE rowid = old.rowid;
            END
        """)

        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS documents_au AFTER UPDATE ON documents BEGIN
                UPDATE documents_fts SET title = new.title, content = new.content
                WHERE rowid = old.rowid;
            END
        """)

        # Indexes for common queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tweets_created ON tweets(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tweets_user ON tweets(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tweets_reply ON tweets(reply_to_tweet_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_thoughts_created ON thoughts(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_thoughts_category ON thoughts(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_created ON documents(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_source_type ON documents(source_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_content_type ON documents(content_type)")

        self.conn.commit()
        logger.info("Database schema initialized")

    def insert_tweet(
        self,
        tweet_id: str,
        user_id: str,
        created_at: datetime,
        full_text: str,
        reply_to_tweet_id: Optional[str] = None,
        reply_to_user: Optional[str] = None,
        retweet_count: int = 0,
        favorite_count: int = 0,
        is_retweet: bool = False,
        is_reply: bool = False,
        entities: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Insert a tweet into the database."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO tweets (
                tweet_id, user_id, created_at, full_text,
                reply_to_tweet_id, reply_to_user,
                retweet_count, favorite_count,
                is_retweet, is_reply, entities
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                tweet_id,
                user_id,
                created_at,
                full_text,
                reply_to_tweet_id,
                reply_to_user,
                retweet_count,
                favorite_count,
                is_retweet,
                is_reply,
                json.dumps(entities) if entities else None,
            ),
        )
        self.conn.commit()

    def insert_bookmark(
        self,
        tweet_id: str,
        expanded_url: Optional[str] = None,
        full_text: Optional[str] = None,
        bookmarked_at: Optional[datetime] = None,
    ) -> None:
        """Insert a bookmarked tweet."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO bookmarks (tweet_id, expanded_url, full_text, bookmarked_at)
            VALUES (?, ?, ?, ?)
            """,
            (tweet_id, expanded_url, full_text, bookmarked_at),
        )
        self.conn.commit()

    def insert_like(
        self,
        tweet_id: str,
        expanded_url: Optional[str] = None,
        full_text: Optional[str] = None,
        liked_at: Optional[datetime] = None,
    ) -> None:
        """Insert a liked tweet."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO likes (tweet_id, expanded_url, full_text, liked_at)
            VALUES (?, ?, ?, ?)
            """,
            (tweet_id, expanded_url, full_text, liked_at),
        )
        self.conn.commit()

    def insert_thought(
        self, content: str, tags: Optional[List[str]] = None, category: Optional[str] = None
    ) -> int:
        """Insert a new thought/note."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO thoughts (content, tags, category)
            VALUES (?, ?, ?)
            """,
            (content, json.dumps(tags) if tags else None, category),
        )
        self.conn.commit()
        return cursor.lastrowid

    def insert_document(
        self,
        doc_id: str,
        source_type: str,
        content: str,
        content_type: Optional[str] = None,
        title: Optional[str] = None,
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
                id, source_type, content_type, title, content,
                metadata, tags, source_path, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                doc_id,
                source_type,
                content_type,
                title,
                content,
                json.dumps(metadata) if metadata else None,
                json.dumps(tags) if tags else None,
                source_path,
                created_at or datetime.now(),
            ),
        )
        self.conn.commit()

    def get_stats(self) -> Dict[str, int]:
        """Get statistics about indexed data."""
        cursor = self.conn.cursor()

        stats = {}
        cursor.execute("SELECT COUNT(*) FROM tweets")
        stats["total_tweets"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM tweets WHERE is_reply = 0 AND is_retweet = 0")
        stats["original_tweets"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM tweets WHERE is_reply = 1")
        stats["replies"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM tweets WHERE is_retweet = 1")
        stats["retweets"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM bookmarks")
        stats["bookmarks"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM likes")
        stats["likes"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM thoughts")
        stats["thoughts"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM articles")
        stats["articles"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM documents")
        stats["documents"] = cursor.fetchone()[0]

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
