"""
Proof-of-Self MCP Server

This is the main entry point for the MCP server that exposes your personal data
as tools for AI assistants like Claude.
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server

from proof_of_self.core.database import Database
from proof_of_self.core.search import Search
from proof_of_self.tools.tweet_tools import register_tweet_tools
from proof_of_self.tools.thought_tools import register_thought_tools
from proof_of_self.tools.document_tools import register_document_tools

logging.basicConfig(level=logging.CRITICAL)  # Disable logging for MCP stdio
logger = logging.getLogger("proof-of-self")


async def main() -> None:
    """Main entry point for the Proof-of-Self MCP server."""

    logger.info("Starting Proof-of-Self MCP server...")

    # Get database path from environment or use default
    db_path = os.getenv("PROOF_OF_SELF_DB", "./data/proof-of-self.db")
    db_path = Path(db_path).expanduser()

    if not db_path.exists():
        logger.error(f"Database not found at {db_path}")
        logger.error("Please run 'proof-of-self index' first to index your data")
        return

    logger.info(f"Using database: {db_path}")

    # Initialize database and search
    db = Database(str(db_path))
    search = Search(db)

    # Get stats
    stats = db.get_stats()
    logger.info(
        f"Loaded: {stats.get('total_documents', 0)} documents"
    )

    # Create MCP server instance
    server = Server("proof-of-self")

    # Register tools
    register_tweet_tools(server, search)
    register_thought_tools(server, db)
    register_document_tools(server, db)

    logger.info("Proof-of-Self is ready!")
    logger.info("Available tools: search_documents, list_recent_documents, dump_thought, list_thoughts")

    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
