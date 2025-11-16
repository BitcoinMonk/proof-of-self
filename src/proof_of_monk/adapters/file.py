"""
File adapter for Proof-of-Monk

Handles various file formats: markdown, text, PDF, etc.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Iterator, Dict, Any, Optional
import logging

from proof_of_monk.adapters.base import BaseAdapter

logger = logging.getLogger(__name__)


class FileAdapter(BaseAdapter):
    """Adapter for processing various file formats."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize file adapter.

        Config keys:
            - file_path: Path to file to process
            - content_type: Type of content (markdown, text, pdf, etc.)
        """
        super().__init__(config)
        self.file_path = Path(config["file_path"])
        self.content_type = config.get("content_type", "text")

    def validate_source(self) -> bool:
        """Validate that the file exists and is readable."""
        return self.file_path.exists() and self.file_path.is_file()

    def get_source_info(self) -> Dict[str, Any]:
        """Get metadata about the file."""
        stat = self.file_path.stat()

        return {
            "file_name": self.file_path.name,
            "file_size": stat.st_size,
            "content_type": self.content_type,
            "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        }

    def parse(self) -> Iterator[Dict[str, Any]]:
        """
        Parse the file and yield document record.

        Yields:
            Document record dictionary
        """
        if not self.validate_source():
            logger.error(f"Invalid file source: {self.file_path}")
            return

        # Read file content
        try:
            content = self.file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            logger.error(f"Could not decode file as UTF-8: {self.file_path}")
            return
        except Exception as e:
            logger.error(f"Error reading file {self.file_path}: {e}")
            return

        # Extract title and metadata based on content type
        if self.content_type == "markdown":
            title, metadata, tags = self._parse_markdown(content)
        else:
            title = self.file_path.stem
            metadata = {}
            tags = []

        # Get file metadata
        file_metadata = {
            "file_name": self.file_path.name,
            "file_size": self.file_path.stat().st_size,
            "file_path": str(self.file_path),
        }
        file_metadata.update(metadata)

        yield {
            "type": "document",
            "source_type": "file",
            "content_type": self.content_type,
            "title": title,
            "content": content,
            "metadata": file_metadata,
            "tags": tags,
            "source_path": str(self.file_path),
            "created_at": datetime.fromtimestamp(self.file_path.stat().st_mtime),
        }

    def _parse_markdown(self, content: str) -> tuple[Optional[str], Dict[str, Any], list[str]]:
        """
        Parse markdown content to extract title, frontmatter, and tags.

        Args:
            content: Markdown file content

        Returns:
            Tuple of (title, metadata, tags)
        """
        title = None
        metadata = {}
        tags = []

        # Try to parse YAML frontmatter
        frontmatter_match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
        if frontmatter_match:
            frontmatter = frontmatter_match.group(1)

            # Simple parsing (not full YAML, but good enough for common cases)
            for line in frontmatter.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()

                    if key == "title":
                        title = value.strip('"\'')
                    elif key == "tags":
                        # Parse tags (handle both list and comma-separated)
                        if value.startswith("["):
                            # List format: [tag1, tag2]
                            tags_str = value.strip("[]")
                            tags = [t.strip().strip('"\'') for t in tags_str.split(",")]
                        else:
                            # Comma-separated: tag1, tag2
                            tags = [t.strip() for t in value.split(",")]
                    else:
                        metadata[key] = value

        # If no title from frontmatter, try to get first heading
        if not title:
            heading_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            if heading_match:
                title = heading_match.group(1).strip()

        return title, metadata, tags
