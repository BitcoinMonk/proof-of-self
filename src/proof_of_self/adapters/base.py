"""
Base adapter class for Proof-of-Self data sources.

All data source adapters should inherit from BaseAdapter.
"""

from abc import ABC, abstractmethod
from typing import Iterator, Dict, Any


class BaseAdapter(ABC):
    """Abstract base class for data source adapters."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize adapter with configuration.

        Args:
            config: Configuration dictionary for this data source
        """
        self.config = config

    @abstractmethod
    def parse(self) -> Iterator[Dict[str, Any]]:
        """
        Parse the data source and yield structured records.

        Yields:
            Dictionary containing structured data ready for indexing
        """
        pass

    @abstractmethod
    def validate_source(self) -> bool:
        """
        Validate that the data source is accessible and in the correct format.

        Returns:
            True if source is valid, False otherwise
        """
        pass

    @abstractmethod
    def get_source_info(self) -> Dict[str, Any]:
        """
        Get metadata about the data source.

        Returns:
            Dictionary with source metadata (size, date range, etc.)
        """
        pass
