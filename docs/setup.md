# Proof-of-Monk Setup Guide

**Status**: ✅ Complete and tested (v0.1.0)

## Prerequisites

- Python 3.10 or higher
- Claude Desktop or Claude Code (for MCP support)
- Your Twitter archive (download from Twitter settings)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/proof-of-monk
cd proof-of-monk
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -e .
```

### 4. Download Your Twitter Archive

1. Go to https://twitter.com/settings/download_your_data
2. Request your archive
3. Wait for email (can take 24 hours)
4. Download and extract the ZIP file

### 5. Index Your Twitter Archive

```bash
# Index your Twitter archive (will create database automatically)
proof-of-monk index --twitter-archive /path/to/twitter-archive/data

# The data folder should contain tweets.js, account.js, etc.
# For example:
proof-of-monk index --twitter-archive ~/Downloads/twitter-YYYY-MM-DD-xxxxx/data

# By default, data is stored in ~/.local/share/proof-of-monk/
```

**Optional flags:**
```bash
# Use custom database location
proof-of-monk index --twitter-archive ~/archive/twitter --db-path ~/my-db.db

# Exclude retweets from indexing
proof-of-monk index --twitter-archive ~/archive/twitter --exclude-retweets
```

This will:
- Parse your Twitter archive
- Create the SQLite database in `~/.local/share/proof-of-monk/proof-of-monk.db`
- Index all tweets with full-text search
- Index bookmarks and likes
- Extract your username automatically

### 6. Verify the Index

```bash
proof-of-monk stats
```

You should see output like:
```
   Proof-of-Monk Statistics
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Metric              ┃ Count ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ Total Tweets        │  8349 │
│   - Original Tweets │  1071 │
│   - Replies         │  6075 │
│   - Retweets        │  1203 │
│ ...                 │   ... │
└─────────────────────┴───────┘
```

### 7. Configure Claude Code/Desktop

**For Claude Code:** Edit `~/.config/claude/mcp_settings.json`

**For Claude Desktop (Mac):** Edit `~/Library/Application Support/Claude/claude_desktop_config.json`

**For Claude Desktop (Windows):** Edit `%APPDATA%\Claude\claude_desktop_config.json`

**For Claude Desktop (Linux):** Edit `~/.config/Claude/claude_desktop_config.json`

Add this configuration:

```json
{
  "mcpServers": {
    "proof-of-monk": {
      "command": "venv/bin/python3",
      "args": ["src/proof_of_monk/server.py"],
      "cwd": "/absolute/path/to/proof-of-monk",
      "env": {
        "PROOF_OF_MONK_DB": "/home/yourusername/.local/share/proof-of-monk/proof-of-monk.db"
      }
    }
  }
}
```

**Replace:**
- `/absolute/path/to/proof-of-monk` with where you cloned the repo
- `/home/yourusername/.local/share/proof-of-monk/proof-of-monk.db` with your actual database path

**Example (Linux/Mac):**
```json
{
  "mcpServers": {
    "proof-of-monk": {
      "command": "venv/bin/python3",
      "args": ["src/proof_of_monk/server.py"],
      "cwd": "/home/monk/repos/proof-of-monk",
      "env": {
        "PROOF_OF_MONK_DB": "/home/monk/.local/share/proof-of-monk/proof-of-monk.db"
      }
    }
  }
}
```

### 8. Restart MCP Server

**In Claude Code:**
1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type "MCP" and select "MCP: Restart Server"
3. Choose "proof-of-monk"

**In Claude Desktop:**
- Restart the Claude Desktop app

You should see "Connected to proof-of-monk" or similar confirmation.

### 9. Test It Out

Open Claude and try asking:

**Search examples:**
- "Search my tweets about datum"
- "Find my hot takes about ordinals with at least 50 likes"
- "What are my most recent tweets?"
- "Show me stats on my Twitter archive"

**Thread reconstruction:**
- "Find the thread starting from tweet ID 1234567890"
- "Show me the complete thread for this tweet about mining"

**Knowledge base:**
- "Save this idea: DATUM solves mining centralization"
- "List all my saved thoughts about bitcoin"

The AI will use the MCP tools to search your local database and return results with direct tweet URLs.

## Troubleshooting

### Can't find Twitter archive

**Problem:** `tweets.js not found` error

**Solution:** Make sure you're pointing to the **data** folder inside the extracted archive, not the root folder or ZIP file.

```bash
# Wrong:
proof-of-monk index --twitter-archive ~/Downloads/twitter-archive.zip

# Wrong:
proof-of-monk index --twitter-archive ~/Downloads/twitter-YYYY-MM-DD-xxxxx

# Correct:
proof-of-monk index --twitter-archive ~/Downloads/twitter-YYYY-MM-DD-xxxxx/data
```

### Database errors

**Problem:** `database is locked` or corruption errors

**Solution:** Close any running MCP servers and delete the database:
```bash
rm ~/.local/share/proof-of-monk/proof-of-monk.db
proof-of-monk index --twitter-archive /path/to/archive/data
```

### MCP server not connecting

**Problem:** "proof-of-monk not found" or connection errors

**Solution checklist:**
1. Verify paths in MCP config are absolute, not relative
2. Check that `venv/bin/python3` exists in the repo directory
3. Verify database path exists: `ls ~/.local/share/proof-of-monk/proof-of-monk.db`
4. Restart Claude Code/Desktop after config changes
5. Check MCP logs for errors

**Debug commands:**
```bash
# Test database directly
proof-of-monk stats --db-path ~/.local/share/proof-of-monk/proof-of-monk.db

# Test Python import
cd /path/to/proof-of-monk
source venv/bin/activate
python -c "from proof_of_monk.server import main; print('OK')"
```

### No search results

**Problem:** Search returns 0 results for terms you know exist

**Solution:** FTS5 uses exact word matching by default. Try:
- Single keywords: `datum` instead of `datum mining`
- OR queries: `datum OR mining`
- Prefix matching: `datums*` for datum/datums
- Check your filters (include_replies, include_retweets)

### Permission denied errors

**Problem:** Can't write to database location

**Solution:** Make sure the directory exists and is writable:
```bash
mkdir -p ~/.local/share/proof-of-monk
chmod 755 ~/.local/share/proof-of-monk
```

## Advanced Configuration

### Multiple Twitter Archives

You can index multiple archives into the same database:

```bash
proof-of-monk index --twitter-archive ~/archive1/data
proof-of-monk index --twitter-archive ~/archive2/data
```

### Custom Database Location

Set a different database path:

```bash
# Index with custom location
proof-of-monk index --twitter-archive ~/archive/data --db-path ~/my-tweets.db

# Update MCP config to match
# Edit: ~/.config/claude/mcp_settings.json
# Set: "PROOF_OF_MONK_DB": "/home/you/my-tweets.db"
```

### Exclude Content

```bash
# Exclude retweets
proof-of-monk index --twitter-archive ~/archive/data --exclude-retweets

# Re-index with different settings
rm ~/.local/share/proof-of-monk/proof-of-monk.db
proof-of-monk index --twitter-archive ~/archive/data --exclude-retweets
```

## Next Steps

- **Organize your archive:** Move Twitter archives to `~/.local/share/proof-of-monk/twitter-archive/`
- **Regular updates:** Download new Twitter archives monthly and re-index
- **Explore tools:** Try all 7 MCP tools (see README for full list)
- **Contribute:** Add new data source adapters or search features
- **Give feedback:** Open issues on GitHub with feature requests

## Data Privacy Note

All your data stays on your machine:
- Database: `~/.local/share/proof-of-monk/proof-of-monk.db`
- Archives: wherever you store them
- No cloud uploads
- No external API calls
- SQLite = local files only

Your data never leaves your computer unless you explicitly share it.

---

**Need help?** Open an issue on [GitHub](https://github.com/bitcoinmonk21/proof-of-monk/issues)
