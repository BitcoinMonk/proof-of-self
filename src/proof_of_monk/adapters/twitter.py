"""
Twitter Archive adapter for Proof-of-Monk

Parses Twitter data export files and extracts tweets, bookmarks, and likes.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Iterator, Dict, Any, Optional, List
import logging

from proof_of_monk.adapters.base import BaseAdapter

logger = logging.getLogger(__name__)


class TwitterAdapter(BaseAdapter):
    """Adapter for parsing Twitter archive exports."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Twitter adapter.

        Args:
            config: Configuration with 'archive_path' pointing to Twitter data folder
        """
        super().__init__(config)
        self.archive_path = Path(config["archive_path"]).expanduser()
        self.username = self._extract_username()

    def validate_source(self) -> bool:
        """
        Validate that the Twitter archive exists and has expected files.

        Returns:
            True if valid Twitter archive, False otherwise
        """
        if not self.archive_path.exists():
            logger.error(f"Archive path does not exist: {self.archive_path}")
            return False

        # Check for essential files
        tweets_file = self.archive_path / "tweets.js"
        if not tweets_file.exists():
            logger.error(f"tweets.js not found in {self.archive_path}")
            return False

        logger.info(f"Valid Twitter archive found at {self.archive_path}")
        return True

    def get_source_info(self) -> Dict[str, Any]:
        """
        Get metadata about the Twitter archive.

        Returns:
            Dictionary with archive metadata
        """
        info = {
            "type": "twitter_archive",
            "path": str(self.archive_path),
            "files": {},
        }

        # Check which files exist
        for filename in ["tweets.js", "like.js", "bookmark.js"]:
            filepath = self.archive_path / filename
            if filepath.exists():
                info["files"][filename] = {
                    "exists": True,
                    "size_bytes": filepath.stat().st_size,
                }
            else:
                info["files"][filename] = {"exists": False}

        return info

    def parse(self) -> Iterator[Dict[str, Any]]:
        """
        Parse the entire Twitter archive.

        Yields:
            Dictionaries with type='tweet', 'bookmark', or 'like'
        """
        # Parse tweets
        yield from self.parse_tweets()

        # Parse bookmarks if enabled
        if self.config.get("index_bookmarks", True):
            yield from self.parse_bookmarks()

        # Parse likes if enabled
        if self.config.get("index_likes", True):
            yield from self.parse_likes()

    def parse_tweets(self) -> Iterator[Dict[str, Any]]:
        """
        Parse tweets.js file.

        Yields:
            Tweet dictionaries
        """
        tweets_file = self.archive_path / "tweets.js"
        if not tweets_file.exists():
            logger.warning(f"tweets.js not found at {tweets_file}")
            return

        logger.info(f"Parsing tweets from {tweets_file}")

        # Read and parse the JavaScript file
        tweets_data = self._load_js_file(tweets_file)
        if not tweets_data:
            return

        exclude_retweets = self.config.get("exclude_retweets", False)
        min_date = self._parse_date_filter(self.config.get("min_date"))
        max_date = self._parse_date_filter(self.config.get("max_date"))

        tweet_count = 0
        for item in tweets_data:
            if "tweet" not in item:
                continue

            tweet = item["tweet"]

            # Parse created_at
            created_at = self._parse_twitter_date(tweet.get("created_at"))
            if not created_at:
                continue

            # Apply date filters
            if min_date and created_at < min_date:
                continue
            if max_date and created_at > max_date:
                continue

            # Check if retweet
            is_retweet = tweet.get("full_text", "").startswith("RT @")
            if exclude_retweets and is_retweet:
                continue

            # Extract data
            tweet_data = {
                "type": "tweet",
                "tweet_id": tweet.get("id_str"),
                "user_id": self.username,
                "created_at": created_at,
                "full_text": tweet.get("full_text", ""),
                "is_retweet": is_retweet,
                "is_reply": bool(tweet.get("in_reply_to_status_id_str")),
                "reply_to_tweet_id": tweet.get("in_reply_to_status_id_str"),
                "reply_to_user": tweet.get("in_reply_to_screen_name"),
                "retweet_count": int(tweet.get("retweet_count", 0)),
                "favorite_count": int(tweet.get("favorite_count", 0)),
                "entities": self._extract_entities(tweet.get("entities", {})),
            }

            tweet_count += 1
            yield tweet_data

        logger.info(f"Parsed {tweet_count} tweets")

    def parse_bookmarks(self) -> Iterator[Dict[str, Any]]:
        """
        Parse like.js file (bookmarks).

        Yields:
            Bookmark dictionaries
        """
        # Twitter changed naming - could be bookmark.js or like.js for bookmarks
        bookmarks_file = self.archive_path / "bookmark.js"
        if not bookmarks_file.exists():
            bookmarks_file = self.archive_path / "bookmarks.js"

        if not bookmarks_file.exists():
            logger.info("No bookmarks file found")
            return

        logger.info(f"Parsing bookmarks from {bookmarks_file}")

        bookmarks_data = self._load_js_file(bookmarks_file)
        if not bookmarks_data:
            return

        bookmark_count = 0
        for item in bookmarks_data:
            if "like" in item:
                # Old format
                data = item["like"]
            elif "bookmark" in item:
                # New format
                data = item["bookmark"]
            else:
                continue

            bookmark_data = {
                "type": "bookmark",
                "tweet_id": data.get("tweetId"),
                "expanded_url": data.get("expandedUrl"),
                "full_text": data.get("fullText"),
            }

            bookmark_count += 1
            yield bookmark_data

        logger.info(f"Parsed {bookmark_count} bookmarks")

    def parse_likes(self) -> Iterator[Dict[str, Any]]:
        """
        Parse like.js file.

        Yields:
            Like dictionaries
        """
        likes_file = self.archive_path / "like.js"
        if not likes_file.exists():
            logger.info("No likes file found")
            return

        logger.info(f"Parsing likes from {likes_file}")

        likes_data = self._load_js_file(likes_file)
        if not likes_data:
            return

        like_count = 0
        for item in likes_data:
            if "like" not in item:
                continue

            like = item["like"]

            like_data = {
                "type": "like",
                "tweet_id": like.get("tweetId"),
                "expanded_url": like.get("expandedUrl"),
                "full_text": like.get("fullText"),
            }

            like_count += 1
            yield like_data

        logger.info(f"Parsed {like_count} likes")

    def _load_js_file(self, filepath: Path) -> Optional[List[Dict[str, Any]]]:
        """
        Load a Twitter .js file and parse it as JSON.

        Twitter exports are JavaScript files like:
        window.YTD.tweets.part0 = [{...}]

        Args:
            filepath: Path to .js file

        Returns:
            Parsed data array or None if parsing fails
        """
        try:
            content = filepath.read_text(encoding="utf-8")

            # Remove the JavaScript wrapper to get just the JSON
            # Pattern: window.YTD.something.partN = [...]
            match = re.search(r"window\.YTD\.\w+\.\w+\s*=\s*(\[.+\])", content, re.DOTALL)
            if match:
                json_str = match.group(1)
                return json.loads(json_str)
            else:
                # Try parsing as plain JSON
                return json.loads(content)

        except Exception as e:
            logger.error(f"Failed to parse {filepath}: {e}")
            return None

    def _parse_twitter_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """
        Parse Twitter's date format: "Thu Nov 06 04:18:45 +0000 2025"

        Args:
            date_str: Twitter date string

        Returns:
            datetime object or None
        """
        if not date_str:
            return None

        try:
            # Twitter format: "Day Mon DD HH:MM:SS +0000 YYYY"
            return datetime.strptime(date_str, "%a %b %d %H:%M:%S %z %Y")
        except Exception as e:
            logger.warning(f"Failed to parse date '{date_str}': {e}")
            return None

    def _parse_date_filter(self, date_str: Optional[str]) -> Optional[datetime]:
        """
        Parse date filter from config (format: "YYYY-MM-DD").

        Args:
            date_str: Date string or None

        Returns:
            datetime object or None
        """
        if not date_str:
            return None

        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except Exception as e:
            logger.warning(f"Invalid date filter '{date_str}': {e}")
            return None

    def _extract_username(self) -> str:
        """
        Extract username from account.js file.

        Returns:
            Username/screen_name or "unknown"
        """
        account_file = self.archive_path / "account.js"
        if not account_file.exists():
            logger.warning("account.js not found, username will be 'unknown'")
            return "unknown"

        try:
            account_data = self._load_js_file(account_file)
            if account_data and len(account_data) > 0:
                account = account_data[0].get("account", {})
                username = account.get("username") or account.get("accountDisplayName")
                if username:
                    logger.info(f"Extracted username: {username}")
                    return username
        except Exception as e:
            logger.warning(f"Failed to extract username from account.js: {e}")

        return "unknown"

    def _extract_entities(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and simplify entities (hashtags, mentions, URLs).

        Args:
            entities: Raw entities dict from Twitter

        Returns:
            Simplified entities dict
        """
        simplified = {
            "hashtags": [tag.get("text") for tag in entities.get("hashtags", [])],
            "mentions": [
                {
                    "screen_name": m.get("screen_name"),
                    "name": m.get("name"),
                }
                for m in entities.get("user_mentions", [])
            ],
            "urls": [
                {
                    "url": url.get("url"),
                    "expanded_url": url.get("expanded_url"),
                    "display_url": url.get("display_url"),
                }
                for url in entities.get("urls", [])
            ],
        }

        return simplified
