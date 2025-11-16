"""
Search module for Proof-of-Monk

Provides search functionality over indexed data.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Search:
    """Search engine for querying indexed data."""

    def __init__(self, database):
        """
        Initialize search engine.

        Args:
            database: Database instance
        """
        self.db = database

    def search_tweets(
        self,
        query: str,
        limit: int = 50,
        offset: int = 0,
        min_date: Optional[str] = None,
        max_date: Optional[str] = None,
        include_replies: bool = True,
        include_retweets: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Search tweets using full-text search.

        Args:
            query: Search query (full-text search syntax)
            limit: Maximum results to return
            offset: Number of results to skip
            min_date: Minimum date (YYYY-MM-DD)
            max_date: Maximum date (YYYY-MM-DD)
            include_replies: Include replies in results
            include_retweets: Include retweets in results

        Returns:
            List of tweet dictionaries
        """
        cursor = self.db.conn.cursor()

        # Build WHERE clause
        where_clauses = []
        params = [query]

        if not include_replies:
            where_clauses.append("t.is_reply = 0")

        if not include_retweets:
            where_clauses.append("t.is_retweet = 0")

        if min_date:
            where_clauses.append("t.created_at >= ?")
            params.append(min_date)

        if max_date:
            where_clauses.append("t.created_at <= ?")
            params.append(max_date)

        where_sql = " AND " + " AND ".join(where_clauses) if where_clauses else ""

        # Query using FTS5
        sql = f"""
            SELECT
                t.tweet_id,
                t.user_id,
                t.created_at,
                t.full_text,
                t.is_reply,
                t.is_retweet,
                t.reply_to_tweet_id,
                t.reply_to_user,
                t.retweet_count,
                t.favorite_count,
                t.entities
            FROM tweets_fts fts
            JOIN tweets t ON t.rowid = fts.rowid
            WHERE fts.full_text MATCH ?
            {where_sql}
            ORDER BY t.created_at DESC
            LIMIT ? OFFSET ?
        """

        params.extend([limit, offset])

        cursor.execute(sql, params)
        results = [dict(row) for row in cursor.fetchall()]

        logger.info(f"Search for '{query}' returned {len(results)} results")
        return results

    def find_thread(self, tweet_id: str) -> List[Dict[str, Any]]:
        """
        Find a complete thread starting from a tweet.

        Args:
            tweet_id: Starting tweet ID

        Returns:
            List of tweets in the thread, ordered chronologically
        """
        cursor = self.db.conn.cursor()

        # Get the root tweet (walk up reply chain)
        root_id = self._find_thread_root(tweet_id)

        # Get all tweets in thread
        cursor.execute(
            """
            WITH RECURSIVE thread AS (
                -- Start with root tweet
                SELECT * FROM tweets WHERE tweet_id = ?

                UNION ALL

                -- Get all replies recursively
                SELECT t.*
                FROM tweets t
                JOIN thread th ON t.reply_to_tweet_id = th.tweet_id
            )
            SELECT * FROM thread
            ORDER BY created_at ASC
            """,
            (root_id,),
        )

        results = [dict(row) for row in cursor.fetchall()]
        logger.info(f"Found thread with {len(results)} tweets")
        return results

    def _find_thread_root(self, tweet_id: str) -> str:
        """
        Walk up the reply chain to find the root tweet.

        Args:
            tweet_id: Starting tweet ID

        Returns:
            Root tweet ID
        """
        cursor = self.db.conn.cursor()
        current_id = tweet_id
        visited = set()

        while current_id and current_id not in visited:
            visited.add(current_id)

            cursor.execute(
                "SELECT reply_to_tweet_id FROM tweets WHERE tweet_id = ?",
                (current_id,),
            )

            row = cursor.fetchone()
            if not row or not row["reply_to_tweet_id"]:
                return current_id

            current_id = row["reply_to_tweet_id"]

        return current_id

    def get_tweet_context(self, tweet_id: str, context_size: int = 3) -> Dict[str, Any]:
        """
        Get a tweet with surrounding context.

        Args:
            tweet_id: Tweet ID
            context_size: Number of tweets before/after to include

        Returns:
            Dictionary with tweet, before_tweets, after_tweets
        """
        cursor = self.db.conn.cursor()

        # Get the tweet
        cursor.execute("SELECT * FROM tweets WHERE tweet_id = ?", (tweet_id,))
        tweet = cursor.fetchone()

        if not tweet:
            return {"tweet": None, "before": [], "after": []}

        tweet = dict(tweet)
        created_at = tweet["created_at"]

        # Get tweets before
        cursor.execute(
            """
            SELECT * FROM tweets
            WHERE created_at < ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (created_at, context_size),
        )
        before_tweets = [dict(row) for row in cursor.fetchall()]
        before_tweets.reverse()  # Chronological order

        # Get tweets after
        cursor.execute(
            """
            SELECT * FROM tweets
            WHERE created_at > ?
            ORDER BY created_at ASC
            LIMIT ?
            """,
            (created_at, context_size),
        )
        after_tweets = [dict(row) for row in cursor.fetchall()]

        return {
            "tweet": tweet,
            "before": before_tweets,
            "after": after_tweets,
        }

    def search_bookmarks(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search bookmarked tweets.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of bookmark dictionaries
        """
        cursor = self.db.conn.cursor()

        cursor.execute(
            """
            SELECT
                b.tweet_id,
                b.expanded_url,
                b.full_text,
                b.bookmarked_at
            FROM bookmarks_fts fts
            JOIN bookmarks b ON b.rowid = fts.rowid
            WHERE fts.full_text MATCH ?
            LIMIT ?
            """,
            (query, limit),
        )

        results = [dict(row) for row in cursor.fetchall()]
        logger.info(f"Bookmark search for '{query}' returned {len(results)} results")
        return results

    def find_hot_takes(
        self, topic: str, min_engagement: int = 10, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Find your strongest opinions (high engagement tweets) about a topic.

        Args:
            topic: Topic to search for
            min_engagement: Minimum combined likes + retweets
            limit: Maximum results

        Returns:
            List of high-engagement tweets about the topic
        """
        cursor = self.db.conn.cursor()

        cursor.execute(
            """
            SELECT
                t.tweet_id,
                t.user_id,
                t.created_at,
                t.full_text,
                t.retweet_count,
                t.favorite_count,
                (t.retweet_count + t.favorite_count) as total_engagement
            FROM tweets_fts fts
            JOIN tweets t ON t.rowid = fts.rowid
            WHERE fts.full_text MATCH ?
                AND (t.retweet_count + t.favorite_count) >= ?
                AND t.is_retweet = 0
            ORDER BY total_engagement DESC
            LIMIT ?
            """,
            (topic, min_engagement, limit),
        )

        results = [dict(row) for row in cursor.fetchall()]
        logger.info(f"Found {len(results)} hot takes about '{topic}'")
        return results

    def get_recent_tweets(self, limit: int = 20, include_replies: bool = True) -> List[Dict[str, Any]]:
        """
        Get most recent tweets.

        Args:
            limit: Number of tweets to return
            include_replies: Include replies

        Returns:
            List of recent tweets
        """
        cursor = self.db.conn.cursor()

        where = "" if include_replies else "WHERE is_reply = 0"

        cursor.execute(
            f"""
            SELECT * FROM tweets
            {where}
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        )

        return [dict(row) for row in cursor.fetchall()]
