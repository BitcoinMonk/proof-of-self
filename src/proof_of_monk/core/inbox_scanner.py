"""
Inbox scanner for Proof-of-Monk

Scans the inbox directory for files to index and routes them to appropriate adapters.
"""

import hashlib
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class InboxScanner:
    """Scans inbox directory and identifies files for indexing."""

    def __init__(self, inbox_path: str, processed_path: str):
        """
        Initialize inbox scanner.

        Args:
            inbox_path: Path to inbox directory
            processed_path: Path to move processed files
        """
        self.inbox_path = Path(inbox_path)
        self.processed_path = Path(processed_path)

        # Create directories if they don't exist
        self.inbox_path.mkdir(parents=True, exist_ok=True)
        self.processed_path.mkdir(parents=True, exist_ok=True)

    def scan(self) -> List[Tuple[Path, str]]:
        """
        Scan inbox and identify files by type.

        Returns:
            List of (file_path, file_type) tuples
        """
        files = []

        for item in self.inbox_path.rglob("*"):
            if not item.is_file():
                # Check if it's a Twitter archive directory
                if item.is_dir() and self._is_twitter_archive(item):
                    files.append((item, "twitter_archive"))
                continue

            # Determine file type by extension
            file_type = self._detect_file_type(item)
            if file_type:
                files.append((item, file_type))

        logger.info(f"Found {len(files)} files/archives in inbox")
        return files

    def _is_twitter_archive(self, path: Path) -> bool:
        """Check if directory is a Twitter archive."""
        # Twitter archives have specific structure
        data_dir = path / "data"
        if not data_dir.exists():
            return False

        # Look for tweets.js or tweet.js
        tweets_file = data_dir / "tweets.js"
        tweet_file = data_dir / "tweet.js"

        return tweets_file.exists() or tweet_file.exists()

    def _detect_file_type(self, path: Path) -> Optional[str]:
        """Detect file type from extension."""
        ext = path.suffix.lower()

        type_mapping = {
            ".md": "markdown",
            ".markdown": "markdown",
            ".txt": "text",
            ".text": "text",
            ".pdf": "pdf",
            ".html": "html",
            ".htm": "html",
            ".json": "json",
            ".org": "org",
        }

        return type_mapping.get(ext)

    def move_to_processed(self, source_path: Path, preserve_structure: bool = True) -> Path:
        """
        Move a file/directory to processed folder.

        Args:
            source_path: Source file or directory
            preserve_structure: Keep relative path structure

        Returns:
            New path in processed directory
        """
        if preserve_structure:
            # Preserve relative path from inbox
            try:
                relative_path = source_path.relative_to(self.inbox_path)
            except ValueError:
                # Not relative to inbox, just use name
                relative_path = source_path.name
        else:
            relative_path = source_path.name

        dest_path = self.processed_path / relative_path

        # Create parent directories
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        # Move file or directory
        shutil.move(str(source_path), str(dest_path))
        logger.info(f"Moved {source_path.name} to processed/")

        return dest_path

    @staticmethod
    def generate_doc_id(content: str, source_path: Optional[str] = None) -> str:
        """
        Generate unique document ID from content hash.

        Args:
            content: Document content
            source_path: Optional source path for additional uniqueness

        Returns:
            Unique document ID (hash)
        """
        # Use content + path for hash to handle duplicates
        hash_input = content
        if source_path:
            hash_input = f"{source_path}::{content}"

        return hashlib.sha256(hash_input.encode("utf-8")).hexdigest()[:16]

    @staticmethod
    def extract_file_metadata(file_path: Path) -> Dict[str, any]:
        """Extract metadata from a file."""
        stat = file_path.stat()

        return {
            "file_name": file_path.name,
            "file_size": stat.st_size,
            "file_extension": file_path.suffix,
            "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        }
