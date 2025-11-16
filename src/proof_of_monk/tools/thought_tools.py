"""
MCP tools for managing thoughts and notes.
"""

import json
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent

from proof_of_monk.core.database import Database


def register_thought_tools(server: Server, db: Database) -> None:
    """
    Register thought/note-taking MCP tools.

    Args:
        server: MCP server instance
        db: Database instance
    """

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available thought tools."""
        return [
            Tool(
                name="dump_thought",
                description="Save a thought, note, or idea to your personal knowledge base. Use this to capture insights, article ideas, or anything you want to remember.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "The thought/note content",
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional tags for categorization (e.g., ['bitcoin', 'article-idea'])",
                        },
                        "category": {
                            "type": "string",
                            "description": "Optional category (e.g., 'draft', 'idea', 'quote')",
                        },
                    },
                    "required": ["content"],
                },
            ),
            Tool(
                name="list_thoughts",
                description="List your saved thoughts/notes, optionally filtered by tag or category.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "tag": {
                            "type": "string",
                            "description": "Filter by tag",
                        },
                        "category": {
                            "type": "string",
                            "description": "Filter by category",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results (default: 20)",
                            "default": 20,
                        },
                    },
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Any) -> list[TextContent]:
        """Handle tool calls."""

        if name == "dump_thought":
            content = arguments["content"]
            tags = arguments.get("tags", [])
            category = arguments.get("category")

            thought_id = db.insert_thought(content=content, tags=tags, category=category)

            output = f"✓ Thought saved (ID: {thought_id})\n\n"
            output += f"Content: {content}\n"
            if tags:
                output += f"Tags: {', '.join(tags)}\n"
            if category:
                output += f"Category: {category}\n"

            return [TextContent(type="text", text=output)]

        elif name == "list_thoughts":
            tag = arguments.get("tag")
            category = arguments.get("category")
            limit = arguments.get("limit", 20)

            cursor = db.conn.cursor()

            # Build query
            where_clauses = []
            params = []

            if tag:
                where_clauses.append("tags LIKE ?")
                params.append(f'%"{tag}"%')

            if category:
                where_clauses.append("category = ?")
                params.append(category)

            where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
            params.append(limit)

            cursor.execute(
                f"""
                SELECT id, content, tags, category, created_at
                FROM thoughts
                WHERE {where_sql}
                ORDER BY created_at DESC
                LIMIT ?
                """,
                params,
            )

            results = [dict(row) for row in cursor.fetchall()]

            if not results:
                filters = []
                if tag:
                    filters.append(f"tag={tag}")
                if category:
                    filters.append(f"category={category}")
                filter_str = f" ({', '.join(filters)})" if filters else ""
                return [TextContent(type="text", text=f"No thoughts found{filter_str}")]

            output = f"Found {len(results)} thoughts:\n\n"
            for thought in results:
                date = thought["created_at"][:10]
                content = thought["content"][:200]
                tags_str = json.loads(thought["tags"]) if thought["tags"] else []
                cat = thought["category"] or "uncategorized"

                output += f"[{date}] {cat}\n"
                output += f"{content}\n"
                if tags_str:
                    output += f"Tags: {', '.join(tags_str)}\n"
                output += f"ID: {thought['id']}\n\n"

            return [TextContent(type="text", text=output)]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
