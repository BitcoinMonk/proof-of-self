#!/usr/bin/env python3
"""Test script for indexing Twitter data with new schema"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from proof_of_monk.core.database import Database
from proof_of_monk.core.indexer import Indexer
from proof_of_monk.adapters.twitter import TwitterAdapter

def main():
    # Path to Twitter archive
    twitter_path = "/home/monk/Downloads/twitter-2025-11-07-12cfd06263c8ce354d9a83fa16a00f8fc0fef695e6bd9706166661cadebb73b6 (3)/data"
    
    # Create new database
    db_path = "./data/proof-of-self.db"
    print(f"Creating database: {db_path}")
    db = Database(db_path)
    
    # Show initial stats
    print("\nInitial stats:")
    stats = db.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Create adapter
    print(f"\nIndexing Twitter archive from: {twitter_path}")
    adapter = TwitterAdapter({
        "archive_path": twitter_path,
        "exclude_retweets": False,
        "index_bookmarks": False,
        "index_likes": False,
    })
    
    # Index
    indexer = Indexer(db)
    counts = indexer.index_from_adapter(adapter)
    
    print("\nIndexing complete!")
    print(f"Counts: {counts}")
    
    # Show final stats
    print("\nFinal database stats:")
    stats = db.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Test search
    print("\n" + "="*60)
    print("Testing search...")
    cursor = db.conn.cursor()
    
    # Search for "bitcoin"
    cursor.execute("""
        SELECT d.id, d.title, d.author, d.content_type,
               substr(d.content, 1, 100) as preview
        FROM documents_fts fts
        JOIN documents d ON fts.rowid = d.rowid
        WHERE documents_fts MATCH 'bitcoin'
        LIMIT 5
    """)
    
    results = cursor.fetchall()
    print(f"\nFound {len(results)} tweets about 'bitcoin' (showing first 5):")
    for i, row in enumerate(results, 1):
        print(f"\n{i}. [{row['content_type']}] by @{row['author']}")
        print(f"   {row['preview']}...")
    
    db.close()
    print("\nTest complete!")

if __name__ == "__main__":
    main()
