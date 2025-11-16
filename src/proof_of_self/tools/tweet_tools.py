"""
MCP tools for querying tweets.
"""

import json
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent

from proof_of_self.core.search import Search


def register_tweet_tools(server: Server, search: Search) -> None:
    """
    Register tweet-related MCP tools.

    Args:
        server: MCP server instance
        search: Search engine instance
    """

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available tweet tools."""
        return [
            Tool(
                name="search_tweets",
                description="Search your tweets using full-text search. Returns matching tweets with metadata.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (e.g., 'bitcoin' or 'ordinals AND inscriptions')",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results (default: 20)",
                            "default": 20,
                        },
                        "include_replies": {
                            "type": "boolean",
                            "description": "Include reply tweets (default: true)",
                            "default": True,
                        },
                        "include_retweets": {
                            "type": "boolean",
                            "description": "Include retweets (default: false)",
                            "default": False,
                        },
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="find_thread",
                description="Find a complete Twitter thread given any tweet ID in the thread. Returns all tweets in chronological order.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "tweet_id": {
                            "type": "string",
                            "description": "Any tweet ID from the thread",
                        },
                    },
                    "required": ["tweet_id"],
                },
            ),
            Tool(
                name="find_hot_takes",
                description="Find your most engaging tweets (high likes/retweets) about a topic. Great for finding your strongest opinions.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "Topic to search for (e.g., 'ordinals', 'core', 'layer2')",
                        },
                        "min_engagement": {
                            "type": "integer",
                            "description": "Minimum combined likes + retweets (default: 10)",
                            "default": 10,
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results (default: 10)",
                            "default": 10,
                        },
                    },
                    "required": ["topic"],
                },
            ),
            Tool(
                name="get_recent_tweets",
                description="Get your most recent tweets, optionally excluding replies.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Number of tweets to return (default: 20)",
                            "default": 20,
                        },
                        "include_replies": {
                            "type": "boolean",
                            "description": "Include reply tweets (default: true)",
                            "default": True,
                        },
                    },
                },
            ),
            Tool(
                name="get_tweet_stats",
                description="Get statistics about your Twitter archive (total tweets, replies, retweets, etc.)",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Any) -> list[TextContent]:
        """Handle tool calls."""

        if name == "search_tweets":
            query = arguments["query"]
            limit = arguments.get("limit", 20)
            include_replies = arguments.get("include_replies", True)
            include_retweets = arguments.get("include_retweets", False)

            results = search.search_tweets(
                query=query,
                limit=limit,
                include_replies=include_replies,
                include_retweets=include_retweets,
            )

            # Format results
            output = f"Found {len(results)} tweets matching '{query}':\n\n"
            for tweet in results:
                date = tweet["created_at"][:10]  # Just the date
                text = tweet["full_text"][:200]  # First 200 chars
                engagement = tweet["favorite_count"] + tweet["retweet_count"]
                tweet_id = tweet["tweet_id"]
                user_id = tweet.get("user_id", "unknown")
                output += f"[{date}] {engagement}♥ {text}\n"
                output += f"  Tweet: https://twitter.com/{user_id}/status/{tweet_id}\n\n"

            return [TextContent(type="text", text=output)]

        elif name == "find_thread":
            tweet_id = arguments["tweet_id"]

            results = search.find_thread(tweet_id)

            if not results:
                return [TextContent(type="text", text=f"No thread found for tweet {tweet_id}")]

            output = f"Thread with {len(results)} tweets:\n\n"
            for i, tweet in enumerate(results, 1):
                date = tweet["created_at"][:16]  # Date + time
                text = tweet["full_text"]
                tweet_id = tweet["tweet_id"]
                user_id = tweet.get("user_id", "unknown")
                output += f"{i}. [{date}] {text}\n"
                output += f"   Tweet: https://twitter.com/{user_id}/status/{tweet_id}\n\n"

            return [TextContent(type="text", text=output)]

        elif name == "find_hot_takes":
            topic = arguments["topic"]
            min_engagement = arguments.get("min_engagement", 10)
            limit = arguments.get("limit", 10)

            results = search.find_hot_takes(
                topic=topic, min_engagement=min_engagement, limit=limit
            )

            if not results:
                return [
                    TextContent(
                        type="text",
                        text=f"No high-engagement tweets found about '{topic}' (min {min_engagement} engagement)",
                    )
                ]

            output = f"Your hottest takes about '{topic}':\n\n"
            for tweet in results:
                date = tweet["created_at"][:10]
                text = tweet["full_text"]
                engagement = tweet["total_engagement"]
                tweet_id = tweet["tweet_id"]
                user_id = tweet.get("user_id", "unknown")
                output += f"[{date}] {engagement}♥ {text}\n"
                output += f"  Tweet: https://twitter.com/{user_id}/status/{tweet_id}\n\n"

            return [TextContent(type="text", text=output)]

        elif name == "get_recent_tweets":
            limit = arguments.get("limit", 20)
            include_replies = arguments.get("include_replies", True)

            results = search.get_recent_tweets(limit=limit, include_replies=include_replies)

            output = f"Your {len(results)} most recent tweets:\n\n"
            for tweet in results:
                date = tweet["created_at"][:16]
                text = tweet["full_text"][:200]
                is_reply = " (reply)" if tweet["is_reply"] else ""
                tweet_id = tweet["tweet_id"]
                user_id = tweet.get("user_id", "unknown")
                output += f"[{date}]{is_reply} {text}\n"
                output += f"  Tweet: https://twitter.com/{user_id}/status/{tweet_id}\n\n"

            return [TextContent(type="text", text=output)]

        elif name == "get_tweet_stats":
            stats = search.db.get_stats()

            output = "Your Twitter Archive Statistics:\n\n"
            output += f"Total Tweets: {stats['total_tweets']}\n"
            output += f"  - Original Tweets: {stats['original_tweets']}\n"
            output += f"  - Replies: {stats['replies']}\n"
            output += f"  - Retweets: {stats['retweets']}\n"
            output += f"\nBookmarks: {stats['bookmarks']}\n"
            output += f"Likes: {stats['likes']}\n"
            output += f"\nNotes/Thoughts: {stats['thoughts']}\n"
            output += f"Articles: {stats['articles']}\n"

            return [TextContent(type="text", text=output)]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
