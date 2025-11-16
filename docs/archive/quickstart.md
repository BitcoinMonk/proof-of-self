# Proof-of-Monk Quickstart Guide

## What We've Built (Phase 1 MVP - 80% Complete!)

✅ **Working:**
- SQLite database with full-text search
- Twitter archive parser (tweets, bookmarks, likes)
- Search engine with 7 different search methods
- MCP tools ready to use with Claude
- Successfully indexed 8,349 tweets + 4,640 likes

⏳ **Needs Setup:**
- Virtual environment + dependencies
- Claude Code configuration
- Optional: CLI commands

---

## Quick Setup (5 minutes)

### 1. Install Python Virtual Environment Support

```bash
sudo apt install python3.13-venv
```

### 2. Create Virtual Environment

```bash
cd ~/repos/proof-of-monk
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install mcp pyyaml click rich
```

### 4. Index Your Twitter Archive

First time setup - this creates the database:

```bash
cd ~/repos/proof-of-monk
export PROOF_OF_MONK_DB="$HOME/repos/proof-of-monk/data/proof-of-monk.db"

# Run the indexer (we already have a test version, but let's make it official)
python3 -c "
import sys
sys.path.insert(0, 'src')
from pathlib import Path
from proof_of_monk.core.database import Database
from proof_of_monk.core.indexer import Indexer
from proof_of_monk.adapters.twitter import TwitterAdapter

# Create database
db = Database('data/proof-of-monk.db')

# Configure Twitter adapter
config = {
    'archive_path': str(Path.home() / 'Downloads' / 'twitter-2025-11-07-12cfd06263c8ce354d9a83fa16a00f8fc0fef695e6bd9706166661cadebb73b6 (3)' / 'data'),
    'index_tweets': True,
    'index_bookmarks': True,
    'index_likes': True,
}

# Index data
adapter = TwitterAdapter(config)
indexer = Indexer(db)
counts = indexer.index_from_adapter(adapter)

print(f'Indexed {counts[\"tweets\"]} tweets, {counts[\"bookmarks\"]} bookmarks, {counts[\"likes\"]} likes')
"
```

### 5. Test the MCP Server

```bash
cd ~/repos/proof-of-monk
source venv/bin/activate
export PROOF_OF_MONK_DB="$HOME/repos/proof-of-monk/data/proof-of-monk.db"

python3 src/proof_of_monk/server.py
```

You should see:
```
INFO:proof-of-monk:Starting Proof-of-Monk MCP server...
INFO:proof-of-monk:Using database: /home/monk/repos/proof-of-monk/data/proof-of-monk.db
INFO:proof-of-monk:Loaded: 8349 tweets, 0 bookmarks, 4640 likes
INFO:proof-of-monk:Proof-of-Monk is ready!
```

Press Ctrl+C to stop.

### 6. Configure Claude Code

Add this to your Claude Code config (`~/.config/Claude/claude_desktop_config.json` or similar):

```json
{
  "mcpServers": {
    "proof-of-monk": {
      "command": "/home/monk/repos/proof-of-monk/venv/bin/python3",
      "args": [
        "/home/monk/repos/proof-of-monk/src/proof_of_monk/server.py"
      ],
      "env": {
        "PROOF_OF_MONK_DB": "/home/monk/repos/proof-of-monk/data/proof-of-monk.db"
      }
    }
  }
}
```

### 7. Test in Claude!

Restart Claude Code, then try:

```
"Search my tweets about ordinals"
"Find my hot takes about Bitcoin Core"
"What did I tweet about Kontor?"
"Show me my most recent tweets"
"Get my Twitter stats"
```

---

## Available Tools

Once connected to Claude, you can:

### Tweet Tools
- **`search_tweets`** - Full-text search your tweets
  - Example: "search my tweets about inscriptions"
- **`find_thread`** - Get complete thread from any tweet ID
  - Example: "find the thread for tweet 1234567890"
- **`find_hot_takes`** - Find high-engagement tweets on a topic
  - Example: "what are my hot takes about layer 2"
- **`get_recent_tweets`** - Get your latest tweets
  - Example: "show me my 10 most recent original tweets"
- **`get_tweet_stats`** - Get archive statistics
  - Example: "how many tweets do I have"

### Thought Tools
- **`dump_thought`** - Save a note/idea
  - Example: "save this thought: Kontor's centralization problem is similar to Ordinals"
- **`list_thoughts`** - Browse your saved thoughts
  - Example: "show me my recent notes"

---

## What's Next (Phase 2)

Once this is working:
- Build the CLI (`proof-of-monk index`, `proof-of-monk serve`)
- Add bookmark search (if your archive has bookmarks)
- Add semantic search with embeddings
- Generalize to other data sources (markdown files, etc.)
- Build optional web UI
- Publish on GitHub

---

## Troubleshooting

**"ModuleNotFoundError: No module named 'mcp'"**
- Activate venv: `source venv/bin/activate`
- Install deps: `pip install mcp pyyaml click rich`

**"Database not found"**
- Set env var: `export PROOF_OF_MONK_DB="/path/to/your/db"`
- Or run the indexer script in step 4

**"Twitter archive not found"**
- Update the path in the indexing script (step 4)
- Make sure it points to the `data` folder inside your extracted archive

**Claude Code not seeing the server**
- Check config path (varies by platform)
- Restart Claude Code after config changes
- Check logs in Claude Code's developer console

---

## Current Database

You already have a working test database at:
`~/repos/proof-of-monk/tests/test.db`

With:
- 8,349 tweets
- 4,640 likes
- Full-text search indexes
- 6.9 MB size

You can use this for testing! Just set:
```bash
export PROOF_OF_MONK_DB="$HOME/repos/proof-of-monk/tests/test.db"
```

---

**Ready to query your tweets with AI!** 🚀
