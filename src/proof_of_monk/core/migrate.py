"""
Migration scripts for Proof-of-Self

Migrates data from legacy Twitter-specific tables to universal documents table.
"""

import json
import logging
from typing import Dict, Any
from datetime import datetime

from proof_of_monk.core.database import Database
from proof_of_monk.core.chunker import generate_document_id

logger = logging.getLogger(__name__)


class DataMigration:
    """Handles migration from legacy schema to universal schema."""

    def __init__(self, db: Database):
        """
        Initialize migration.

        Args:
            db: Database instance
        """
        self.db = db

    def migrate_tweets_to_documents(self, dry_run: bool = False) -> Dict[str, int]:
        """
        Migrate tweets from tweets table to documents table.

        Args:
            dry_run: If True, don't actually insert, just count

        Returns:
            Dictionary with migration stats
        """
        cursor = self.db.conn.cursor()

        # Get all tweets
        cursor.execute("""
            SELECT
                tweet_id, user_id, created_at, full_text,
                reply_to_tweet_id, reply_to_user,
                retweet_count, favorite_count,
                is_retweet, is_reply, entities
            FROM tweets
        """)

        tweets = cursor.fetchall()
        total = len(tweets)
        migrated = 0
        skipped = 0
        errors = 0

        logger.info(f"Found {total} tweets to migrate")

        for row in tweets:
            try:
                tweet_id = row["tweet_id"]
                user_id = row["user_id"]
                created_at = row["created_at"]
                full_text = row["full_text"]
                reply_to_tweet_id = row["reply_to_tweet_id"]
                reply_to_user = row["reply_to_user"]
                retweet_count = row["retweet_count"]
                favorite_count = row["favorite_count"]
                is_retweet = row["is_retweet"]
                is_reply = row["is_reply"]
                entities_json = row["entities"]

                # Parse entities if present
                entities = json.loads(entities_json) if entities_json else None

                # Generate document ID
                doc_id = generate_document_id(
                    content=full_text,
                    source_path=f"twitter://{user_id}/{tweet_id}",
                    created_at=created_at,
                )

                # Check if already migrated
                cursor.execute(
                    "SELECT id FROM documents WHERE id = ?",
                    (doc_id,),
                )
                if cursor.fetchone():
                    skipped += 1
                    continue

                # Extract hashtags for tags
                tags = []
                if entities and "hashtags" in entities:
                    tags = entities["hashtags"]

                # Build metadata
                metadata = {
                    "tweet_id": tweet_id,
                    "username": user_id,
                    "retweet_count": retweet_count,
                    "favorite_count": favorite_count,
                    "is_retweet": bool(is_retweet),
                    "is_reply": bool(is_reply),
                }

                if reply_to_tweet_id:
                    metadata["reply_to_tweet_id"] = reply_to_tweet_id
                if reply_to_user:
                    metadata["reply_to_user"] = reply_to_user
                if entities:
                    metadata["entities"] = entities

                # Determine content type
                if is_retweet:
                    content_type = "retweet"
                elif is_reply:
                    content_type = "reply"
                else:
                    content_type = "tweet"

                # Convert created_at to datetime if string
                if isinstance(created_at, str):
                    created_at_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                else:
                    created_at_dt = created_at

                # Insert into documents table
                if not dry_run:
                    self.db.insert_document(
                        doc_id=doc_id,
                        source_type="twitter",
                        content_type=content_type,
                        title=None,  # Tweets don't have titles
                        author=user_id,
                        content=full_text,
                        source_path=f"twitter://{user_id}/{tweet_id}",
                        is_chunked=False,
                        metadata=metadata,
                        tags=tags,
                        created_at=created_at_dt,
                    )

                migrated += 1

                if migrated % 1000 == 0:
                    logger.info(f"Migrated {migrated}/{total} tweets")

            except Exception as e:
                logger.error(f"Error migrating tweet {tweet_id}: {e}")
                errors += 1

        stats = {
            "total": total,
            "migrated": migrated,
            "skipped": skipped,
            "errors": errors,
        }

        logger.info(f"Migration complete: {stats}")
        return stats

    def migrate_thoughts_to_documents(self, dry_run: bool = False) -> Dict[str, int]:
        """
        Migrate thoughts from thoughts table to documents table.

        Args:
            dry_run: If True, don't actually insert, just count

        Returns:
            Dictionary with migration stats
        """
        cursor = self.db.conn.cursor()

        # Get all thoughts
        cursor.execute("""
            SELECT id, content, tags, category, created_at, updated_at
            FROM thoughts
        """)

        thoughts = cursor.fetchall()
        total = len(thoughts)
        migrated = 0
        skipped = 0
        errors = 0

        logger.info(f"Found {total} thoughts to migrate")

        for row in thoughts:
            try:
                thought_id = row["id"]
                content = row["content"]
                tags_json = row["tags"]
                category = row["category"]
                created_at = row["created_at"]
                updated_at = row["updated_at"]

                # Parse tags if present
                tags = json.loads(tags_json) if tags_json else []

                # Generate document ID
                doc_id = generate_document_id(
                    content=content,
                    source_path=f"thought://{thought_id}",
                    created_at=created_at,
                )

                # Check if already migrated
                cursor.execute(
                    "SELECT id FROM documents WHERE id = ?",
                    (doc_id,),
                )
                if cursor.fetchone():
                    skipped += 1
                    continue

                # Build metadata
                metadata = {
                    "thought_id": thought_id,
                    "category": category,
                    "updated_at": updated_at,
                }

                # Convert created_at to datetime if string
                if isinstance(created_at, str):
                    created_at_dt = datetime.fromisoformat(created_at)
                else:
                    created_at_dt = created_at

                # Insert into documents table
                if not dry_run:
                    self.db.insert_document(
                        doc_id=doc_id,
                        source_type="user",
                        content_type="note",
                        title=None,
                        author=None,
                        content=content,
                        source_path=f"thought://{thought_id}",
                        is_chunked=False,
                        metadata=metadata,
                        tags=tags,
                        created_at=created_at_dt,
                    )

                migrated += 1

            except Exception as e:
                logger.error(f"Error migrating thought {thought_id}: {e}")
                errors += 1

        stats = {
            "total": total,
            "migrated": migrated,
            "skipped": skipped,
            "errors": errors,
        }

        logger.info(f"Thought migration complete: {stats}")
        return stats

    def run_full_migration(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Run full migration of all legacy data.

        Args:
            dry_run: If True, don't actually insert, just count

        Returns:
            Dictionary with all migration stats
        """
        logger.info("Starting full migration")
        logger.info(f"Dry run: {dry_run}")

        results = {}

        # Migrate tweets
        logger.info("Migrating tweets...")
        results["tweets"] = self.migrate_tweets_to_documents(dry_run=dry_run)

        # Migrate thoughts
        logger.info("Migrating thoughts...")
        results["thoughts"] = self.migrate_thoughts_to_documents(dry_run=dry_run)

        # Summary
        total_migrated = results["tweets"]["migrated"] + results["thoughts"]["migrated"]
        total_errors = results["tweets"]["errors"] + results["thoughts"]["errors"]

        results["summary"] = {
            "total_migrated": total_migrated,
            "total_errors": total_errors,
            "dry_run": dry_run,
        }

        logger.info(f"Full migration complete: {results['summary']}")

        return results


def run_migration(db_path: str, dry_run: bool = False) -> Dict[str, Any]:
    """
    Convenience function to run migration.

    Args:
        db_path: Path to database
        dry_run: If True, don't actually migrate

    Returns:
        Migration results
    """
    db = Database(db_path)
    migration = DataMigration(db)
    results = migration.run_full_migration(dry_run=dry_run)
    db.close()
    return results
