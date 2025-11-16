"""Data source adapters for Proof-of-Monk."""

from proof_of_monk.adapters.base import BaseAdapter
from proof_of_monk.adapters.twitter import TwitterAdapter

__all__ = ["BaseAdapter", "TwitterAdapter"]
