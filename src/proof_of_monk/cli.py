"""
Command-line interface for Proof-of-Monk
"""

import os
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from proof_of_monk.core.database import Database
from proof_of_monk.core.indexer import Indexer
from proof_of_monk.adapters.twitter import TwitterAdapter
from proof_of_monk.adapters.file import FileAdapter
from proof_of_monk.core.inbox_scanner import InboxScanner

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main() -> None:
    """Proof-of-Monk: Your personal AI knowledge base."""
    pass


@main.command()
@click.option(
    "--db-path",
    default="./data/proof-of-monk.db",
    help="Path to database file",
    type=click.Path(),
)
def init(db_path: str) -> None:
    """Initialize Proof-of-Monk database."""
    db_path = Path(db_path).expanduser()

    if db_path.exists():
        console.print(f"[yellow]Database already exists at {db_path}[/yellow]")
        if not click.confirm("Do you want to recreate it?"):
            return
        db_path.unlink()

    console.print(f"[green]Initializing database at {db_path}...[/green]")
    db = Database(str(db_path))
    db.close()
    console.print("[green]Database initialized successfully![/green]")


@main.command()
@click.option(
    "--twitter-archive",
    required=True,
    help="Path to Twitter archive folder (containing tweets.js)",
    type=click.Path(exists=True),
)
@click.option(
    "--db-path",
    default="./data/proof-of-monk.db",
    help="Path to database file",
    type=click.Path(),
)
@click.option(
    "--exclude-retweets",
    is_flag=True,
    help="Exclude retweets from indexing",
)
@click.option(
    "--exclude-replies",
    is_flag=True,
    help="Exclude replies from indexing",
)
def index(twitter_archive: str, db_path: str, exclude_retweets: bool, exclude_replies: bool) -> None:
    """Index your Twitter archive."""
    twitter_path = Path(twitter_archive).expanduser()
    db_path = Path(db_path).expanduser()

    console.print(f"[yellow]Indexing Twitter archive from {twitter_path}...[/yellow]")

    # Initialize database
    db = Database(str(db_path))

    # Create Twitter adapter
    config = {
        "archive_path": str(twitter_path),
        "exclude_retweets": exclude_retweets,
        "index_bookmarks": True,
        "index_likes": True,
    }

    adapter = TwitterAdapter(config)

    # Index the data
    indexer = Indexer(db)

    try:
        counts = indexer.index_from_adapter(adapter)

        # Display results
        table = Table(title="Indexing Complete")
        table.add_column("Data Type", style="cyan")
        table.add_column("Count", style="green", justify="right")

        table.add_row("Tweets", str(counts["tweets"]))
        table.add_row("Bookmarks", str(counts["bookmarks"]))
        table.add_row("Likes", str(counts["likes"]))
        if counts["errors"] > 0:
            table.add_row("Errors", str(counts["errors"]), style="red")

        console.print(table)
        console.print(f"\n[green]Successfully indexed to {db_path}[/green]")
        console.print("\nYou can now:")
        console.print("  1. Run [cyan]proof-of-monk stats[/cyan] to see statistics")
        console.print("  2. Use the MCP server with Claude Code or Claude Desktop")

    except Exception as e:
        console.print(f"[red]Error during indexing: {e}[/red]")
        sys.exit(1)
    finally:
        db.close()


@main.command()
@click.option(
    "--inbox-path",
    default="./data/inbox",
    help="Path to inbox directory",
    type=click.Path(),
)
@click.option(
    "--db-path",
    default="./data/proof-of-monk.db",
    help="Path to database file",
    type=click.Path(),
)
@click.option(
    "--processed-path",
    default="./data/processed",
    help="Path to move processed files",
    type=click.Path(),
)
@click.option(
    "--keep-files",
    is_flag=True,
    help="Keep files in inbox after indexing (don't move to processed)",
)
def index_inbox(inbox_path: str, db_path: str, processed_path: str, keep_files: bool) -> None:
    """Index files from the inbox directory."""
    inbox_path = Path(inbox_path).expanduser()
    db_path = Path(db_path).expanduser()
    processed_path = Path(processed_path).expanduser()

    if not inbox_path.exists():
        console.print(f"[yellow]Inbox directory not found, creating: {inbox_path}[/yellow]")
        inbox_path.mkdir(parents=True, exist_ok=True)
        console.print("[yellow]Inbox is empty. Drop files there and run this command again.[/yellow]")
        return

    console.print(f"[yellow]Scanning inbox: {inbox_path}...[/yellow]")

    # Initialize database
    db = Database(str(db_path))
    indexer = Indexer(db)

    # Scan inbox
    scanner = InboxScanner(str(inbox_path), str(processed_path))
    files = scanner.scan()

    if not files:
        console.print("[yellow]No files found in inbox.[/yellow]")
        db.close()
        return

    console.print(f"[green]Found {len(files)} items to process[/green]\n")

    total_counts = {
        "tweets": 0,
        "bookmarks": 0,
        "likes": 0,
        "documents": 0,
        "errors": 0,
    }

    # Process each file
    for file_path, file_type in files:
        console.print(f"[cyan]Processing:[/cyan] {file_path.name} ({file_type})")

        try:
            if file_type == "twitter_archive":
                # Twitter archive
                config = {
                    "archive_path": str(file_path / "data"),
                    "exclude_retweets": False,
                    "index_bookmarks": True,
                    "index_likes": True,
                }
                adapter = TwitterAdapter(config)

            elif file_type in ["markdown", "text", "org"]:
                # Text-based files
                config = {
                    "file_path": str(file_path),
                    "content_type": file_type,
                }
                adapter = FileAdapter(config)

            else:
                console.print(f"  [yellow]Skipping unsupported file type: {file_type}[/yellow]")
                continue

            # Index the file
            counts = indexer.index_from_adapter(adapter)

            # Update totals
            for key in total_counts:
                if key in counts:
                    total_counts[key] += counts[key]

            # Show what was indexed
            indexed_items = [f"{v} {k}" for k, v in counts.items() if k != "errors" and v > 0]
            if indexed_items:
                console.print(f"  [green]✓ Indexed: {', '.join(indexed_items)}[/green]")

            # Move to processed unless keep_files is set
            if not keep_files:
                scanner.move_to_processed(file_path)

        except Exception as e:
            console.print(f"  [red]✗ Error: {e}[/red]")
            total_counts["errors"] += 1

    # Display final results
    console.print()
    table = Table(title="Inbox Processing Complete")
    table.add_column("Data Type", style="cyan")
    table.add_column("Count", style="green", justify="right")

    if total_counts["tweets"] > 0:
        table.add_row("Tweets", str(total_counts["tweets"]))
    if total_counts["bookmarks"] > 0:
        table.add_row("Bookmarks", str(total_counts["bookmarks"]))
    if total_counts["likes"] > 0:
        table.add_row("Likes", str(total_counts["likes"]))
    if total_counts["documents"] > 0:
        table.add_row("Documents", str(total_counts["documents"]))
    if total_counts["errors"] > 0:
        table.add_row("Errors", str(total_counts["errors"]), style="red")

    console.print(table)
    console.print(f"\n[green]Successfully indexed to {db_path}[/green]")

    if not keep_files:
        console.print(f"[green]Processed files moved to {processed_path}[/green]")

    db.close()


@main.command()
@click.option(
    "--db-path",
    default="./data/proof-of-monk.db",
    help="Path to database file",
    type=click.Path(),
)
def stats(db_path: str) -> None:
    """Show statistics about your indexed data."""
    db_path = Path(db_path).expanduser()

    if not db_path.exists():
        console.print(f"[red]Database not found at {db_path}[/red]")
        console.print("Run [cyan]proof-of-monk index --twitter-archive <path>[/cyan] first")
        return

    db = Database(str(db_path))

    try:
        stats = db.get_stats()

        table = Table(title="Proof-of-Monk Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Count", style="green", justify="right")

        table.add_row("Total Tweets", str(stats["total_tweets"]))
        table.add_row("  - Original Tweets", str(stats["original_tweets"]))
        table.add_row("  - Replies", str(stats["replies"]))
        table.add_row("  - Retweets", str(stats["retweets"]))
        table.add_row("", "")
        table.add_row("Bookmarks", str(stats["bookmarks"]))
        table.add_row("Likes", str(stats["likes"]))
        table.add_row("", "")
        table.add_row("Documents", str(stats["documents"]))
        table.add_row("Thoughts/Notes", str(stats["thoughts"]))
        table.add_row("Articles", str(stats["articles"]))

        console.print(table)

    finally:
        db.close()


@main.command()
@click.option(
    "--db-path",
    default="./data/proof-of-monk.db",
    help="Path to database file",
    type=click.Path(),
)
def serve(db_path: str) -> None:
    """Start the MCP server."""
    db_path = Path(db_path).expanduser()

    if not db_path.exists():
        console.print(f"[red]Database not found at {db_path}[/red]")
        console.print("Run [cyan]proof-of-monk index --twitter-archive <path>[/cyan] first")
        return

    console.print("[green]Starting Proof-of-Monk MCP server...[/green]")
    console.print(f"Using database: {db_path}")

    # Set environment variable and run server
    os.environ["PROOF_OF_MONK_DB"] = str(db_path)

    from proof_of_monk.server import main as server_main
    import asyncio

    asyncio.run(server_main())


if __name__ == "__main__":
    main()
