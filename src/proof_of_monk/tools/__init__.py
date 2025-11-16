"""MCP tools for Proof-of-Monk."""

from proof_of_monk.tools.tweet_tools import register_tweet_tools
from proof_of_monk.tools.thought_tools import register_thought_tools

__all__ = ["register_tweet_tools", "register_thought_tools"]
