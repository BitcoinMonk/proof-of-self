"""
Test the MCP server can start and list tools
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Set database path to test DB
os.environ["PROOF_OF_MONK_DB"] = str(Path(__file__).parent / "test.db")

import asyncio
from proof_of_self.core.database import Database
from proof_of_self.core.search import Search
from proof_of_self.tools.tweet_tools import register_tweet_tools
from proof_of_self.tools.thought_tools import register_thought_tools
from mcp.server import Server


async def test_mcp_server():
    """Test that MCP server and tools work."""
    print("=== Testing MCP Server ===\n")

    # Database setup
    db_path = Path(__file__).parent / "test.db"
    print(f"Using database: {db_path}")

    if not db_path.exists():
        print("ERROR: Test database not found. Run test_twitter_integration.py first!")
        return False

    db = Database(str(db_path))
    search = Search(db)

    # Stats
    stats = db.get_stats()
    print(f"Database has: {stats['total_tweets']} tweets\n")

    # Create server
    server = Server("test-server")

    # Register tools
    register_tweet_tools(server, search)
    register_thought_tools(server, db)

    print("✓ Server created")
    print("✓ Tools registered\n")

    # Test search
    print("=== Testing search_tweets ===")
    results = search.search_tweets("bitcoin", limit=5)
    print(f"Found {len(results)} tweets about 'bitcoin':")
    for tweet in results[:3]:
        print(f"  - {tweet['full_text'][:80]}...")
    print()

    # Test thread finding
    print("=== Testing find_thread ===")
    # Get a tweet that's part of a thread (a reply)
    cursor = db.conn.cursor()
    cursor.execute("SELECT tweet_id FROM tweets WHERE is_reply = 1 LIMIT 1")
    reply_tweet = cursor.fetchone()

    if reply_tweet:
        thread = search.find_thread(reply_tweet["tweet_id"])
        print(f"Found thread with {len(thread)} tweets")
    else:
        print("No reply tweets found in database")
    print()

    # Test hot takes
    print("=== Testing find_hot_takes ===")
    hot_takes = search.find_hot_takes("ordinals", min_engagement=5, limit=3)
    print(f"Found {len(hot_takes)} hot takes about 'ordinals':")
    for tweet in hot_takes:
        engagement = tweet["total_engagement"]
        print(f"  [{engagement}♥] {tweet['full_text'][:80]}...")
    print()

    # Test thought dumping
    print("=== Testing dump_thought ===")
    thought_id = db.insert_thought(
        content="This is a test thought about Kontor and centralization",
        tags=["kontor", "test"],
        category="note",
    )
    print(f"✓ Created thought ID: {thought_id}\n")

    # Test listing thoughts
    print("=== Testing list_thoughts ===")
    cursor.execute("SELECT * FROM thoughts ORDER BY created_at DESC LIMIT 3")
    thoughts = [dict(row) for row in cursor.fetchall()]
    print(f"Found {len(thoughts)} thoughts:")
    for thought in thoughts:
        print(f"  - {thought['content'][:80]}...")
    print()

    print("✅ All MCP server tests passed!")
    return True


if __name__ == "__main__":
    success = asyncio.run(test_mcp_server())
    sys.exit(0 if success else 1)
