"""
Proof-of-Self: Your personal AI knowledge base that respects your privacy.

A self-hosted MCP server for indexing and querying personal data.
"""

__version__ = "0.1.0"
__author__ = "BitcoinMonk"
__license__ = "MIT"

from proof_of_self.core.database import Database
from proof_of_self.core.indexer import Indexer
from proof_of_self.core.search import Search

__all__ = ["Database", "Indexer", "Search"]
