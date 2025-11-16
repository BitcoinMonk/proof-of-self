"""
MCP tools for searching documents in the knowledge base.
"""

import json
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent

from proof_of_self.core.database import Database


def register_document_tools(server: Server, db: Database) -> None:
    """
    Register document search MCP tools.

    Args:
        server: MCP server instance
        db: Database instance
    """

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available document tools."""
        return [
            Tool(
                name="search_documents",
                description="Search all documents in your knowledge base (markdown files, notes, PDFs, etc.). Returns matching documents with relevant snippets.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (full-text search)",
                        },
                        "content_type": {
                            "type": "string",
                            "description": "Filter by content type (e.g., 'markdown', 'text', 'pdf')",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results (default: 10)",
                            "default": 10,
                        },
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="list_recent_documents",
                description="List recently added documents in the knowledge base.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results (default: 10)",
                            "default": 10,
                        },
                        "content_type": {
                            "type": "string",
                            "description": "Filter by content type (e.g., 'markdown', 'text', 'pdf')",
                        },
                    },
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Any) -> list[TextContent]:
        """Handle tool calls."""

        if name == "search_documents":
            query = arguments["query"]
            content_type = arguments.get("content_type")
            limit = arguments.get("limit", 10)

            cursor = db.conn.cursor()

            # Build search query
            where_clauses = ["documents_fts MATCH ?"]
            params = [query]

            if content_type:
                where_clauses.append("content_type = ?")
                params.append(content_type)

            where_sql = " AND ".join(where_clauses)
            params.append(limit)

            cursor.execute(
                f"""
                SELECT
                    d.id, d.title, d.content, d.content_type,
                    d.tags, d.source_path, d.created_at,
                    snippet(documents_fts, 1, '<mark>', '</mark>', '...', 40) as snippet
                FROM documents_fts
                JOIN documents d ON documents_fts.rowid = d.rowid
                WHERE {where_sql}
                ORDER BY rank
                LIMIT ?
                """,
                params,
            )

            results = [dict(row) for row in cursor.fetchall()]

            if not results:
                return [TextContent(type="text", text=f"No documents found matching '{query}'")]

            output = f"Found {len(results)} documents matching '{query}':\n\n"

            for doc in results:
                title = doc["title"] or doc["source_path"] or "Untitled"
                content_type = doc["content_type"] or "unknown"
                date = doc["created_at"][:10] if doc["created_at"] else "unknown"
                snippet = doc["snippet"] or doc["content"][:200]

                output += f"📄 {title}\n"
                output += f"   Type: {content_type} | Date: {date}\n"

                # Show tags if available
                if doc["tags"]:
                    tags = json.loads(doc["tags"])
                    if tags:
                        output += f"   Tags: {', '.join(tags)}\n"

                output += f"   {snippet}\n"
                output += f"   ID: {doc['id']}\n\n"

            return [TextContent(type="text", text=output)]

        elif name == "list_recent_documents":
            limit = arguments.get("limit", 10)
            content_type = arguments.get("content_type")

            cursor = db.conn.cursor()

            where_clause = ""
            params = []

            if content_type:
                where_clause = "WHERE content_type = ?"
                params.append(content_type)

            params.append(limit)

            cursor.execute(
                f"""
                SELECT id, title, content, content_type, tags, source_path, created_at, indexed_at
                FROM documents
                {where_clause}
                ORDER BY indexed_at DESC
                LIMIT ?
                """,
                params,
            )

            results = [dict(row) for row in cursor.fetchall()]

            if not results:
                filter_str = f" of type '{content_type}'" if content_type else ""
                return [TextContent(type="text", text=f"No documents found{filter_str}")]

            output = f"Recent documents ({len(results)}):\n\n"

            for doc in results:
                title = doc["title"] or doc["source_path"] or "Untitled"
                content_type = doc["content_type"] or "unknown"
                date = doc["indexed_at"][:10] if doc["indexed_at"] else "unknown"
                content_preview = doc["content"][:150].replace("\n", " ")

                output += f"📄 {title}\n"
                output += f"   Type: {content_type} | Added: {date}\n"

                # Show tags if available
                if doc["tags"]:
                    tags = json.loads(doc["tags"])
                    if tags:
                        output += f"   Tags: {', '.join(tags)}\n"

                output += f"   {content_preview}...\n"
                output += f"   ID: {doc['id']}\n\n"

            return [TextContent(type="text", text=output)]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
