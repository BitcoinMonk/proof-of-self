"""
Integration test for Twitter archive parsing

Run this to test the full pipeline: Twitter Archive → Parser → Database
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from proof_of_self.core.database import Database
from proof_of_self.core.indexer import Indexer
from proof_of_self.adapters.twitter import TwitterAdapter


def test_twitter_integration():
    """Test parsing BitcoinMonk's Twitter archive."""

    # Path to your Twitter archive
    archive_path = Path.home() / "Downloads" / "twitter-2025-11-07-12cfd06263c8ce354d9a83fa16a00f8fc0fef695e6bd9706166661cadebb73b6 (3)" / "data"

    print(f"Testing with archive at: {archive_path}")

    # Create test database
    test_db_path = Path(__file__).parent / "test.db"
    if test_db_path.exists():
        test_db_path.unlink()  # Delete old test DB

    print(f"Creating database at: {test_db_path}")

    # Initialize database
    db = Database(str(test_db_path))

    # Create Twitter adapter
    config = {
        "archive_path": str(archive_path),
        "index_tweets": True,
        "index_bookmarks": True,
        "index_likes": True,
        "exclude_retweets": False,
    }

    adapter = TwitterAdapter(config)

    # Validate source
    print("\n=== Validating Twitter Archive ===")
    if not adapter.validate_source():
        print("ERROR: Invalid Twitter archive!")
        return False

    source_info = adapter.get_source_info()
    print(f"Source info: {source_info}")

    # Index data
    print("\n=== Indexing Data ===")
    indexer = Indexer(db)

    try:
        counts = indexer.index_from_adapter(adapter)
        print(f"\nIndexing complete!")
        print(f"  Tweets: {counts['tweets']}")
        print(f"  Bookmarks: {counts['bookmarks']}")
        print(f"  Likes: {counts['likes']}")
        print(f"  Errors: {counts['errors']}")

        # Get stats from database
        print("\n=== Database Stats ===")
        stats = db.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")

        # Test a simple query
        print("\n=== Sample Queries ===")
        cursor = db.conn.cursor()

        # Get most recent tweets
        cursor.execute("""
            SELECT tweet_id, created_at, full_text
            FROM tweets
            ORDER BY created_at DESC
            LIMIT 5
        """)

        print("\nMost recent 5 tweets:")
        for row in cursor.fetchall():
            print(f"  [{row['created_at']}] {row['full_text'][:80]}...")

        # Search for "bitcoin"
        cursor.execute("""
            SELECT tweet_id, full_text
            FROM tweets_fts
            WHERE full_text MATCH 'bitcoin'
            LIMIT 5
        """)

        print("\nTweets mentioning 'bitcoin' (first 5):")
        for row in cursor.fetchall():
            print(f"  {row['full_text'][:80]}...")

        print("\n✅ All tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        db.close()


if __name__ == "__main__":
    success = test_twitter_integration()
    sys.exit(0 if success else 1)
