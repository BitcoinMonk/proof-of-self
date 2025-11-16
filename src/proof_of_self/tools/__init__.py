"""MCP tools for Proof-of-Self."""

from proof_of_self.tools.tweet_tools import register_tweet_tools
from proof_of_self.tools.thought_tools import register_thought_tools

__all__ = ["register_tweet_tools", "register_thought_tools"]
