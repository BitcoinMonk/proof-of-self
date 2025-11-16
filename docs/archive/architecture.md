# Proof-of-Monk Project Structure

This document explains the organization of the Proof-of-Monk codebase.

## Directory Layout

```
proof-of-monk/
├── README.md                   # Project overview and vision
├── ROADMAP.md                  # Detailed technical plan and phases
├── PROJECT_STRUCTURE.md        # This file
├── LICENSE                     # MIT License
├── pyproject.toml             # Python project configuration
├── .gitignore                 # Git ignore rules (IMPORTANT: protects your data)
│
├── config/
│   └── config.example.yaml    # Example configuration (copy to config.yaml)
│
├── data/                      # Your personal data (gitignored!)
│   ├── proof-of-monk.db      # SQLite database (structured data)
│   │
│   ├── consciousness/        # Consciousness directory (Phase 1.5+)
│   │   ├── streams/         # Daily thought streams (markdown)
│   │   ├── memory/          # Consolidated topic files
│   │   ├── knowledge/       # Research, articles, external data
│   │   └── artifacts/       # Published work
│   │
│   ├── backups/              # Database backups
│   └── sources/              # Original data files (Twitter archives, etc.)
│
├── docs/                      # Documentation
│   ├── setup.md              # Setup and installation guide
│   ├── twitter-setup.md      # Twitter archive specific guide
│   └── api-reference.md      # MCP tools API documentation
│
├── src/
│   └── proof_of_monk/        # Main Python package
│       ├── __init__.py       # Package initialization
│       ├── server.py         # MCP server entry point
│       ├── cli.py            # Command-line interface
│       │
│       ├── core/             # Core functionality
│       │   ├── __init__.py
│       │   ├── database.py   # SQLite database operations
│       │   ├── indexer.py    # Index data into database
│       │   └── search.py     # Search implementations
│       │
│       ├── adapters/         # Data source adapters (pluggable)
│       │   ├── __init__.py
│       │   ├── base.py       # Base adapter class
│       │   ├── twitter.py    # Twitter archive parser
│       │   └── [future].py   # More adapters in Phase 2
│       │
│       └── tools/            # MCP tool implementations
│           ├── __init__.py
│           ├── tweet_tools.py    # Tools for querying tweets
│           └── thought_tools.py  # Tools for notes/thoughts
│
└── tests/                    # Test suite
    ├── __init__.py
    ├── test_database.py
    ├── test_twitter_adapter.py
    └── test_search.py
```

## Key Files Explained

### Configuration

- **`config/config.example.yaml`**: Template configuration file. Copy this to `config/config.yaml` and customize it with your settings.
- **`.gitignore`**: Ensures your personal data never gets committed to Git. Very important!

### Source Code

- **`src/proof_of_monk/server.py`**: The MCP server that exposes your data as tools for AI assistants.
- **`src/proof_of_monk/cli.py`**: Command-line interface for managing Proof-of-Monk (index, serve, stats, etc.)
- **`src/proof_of_monk/core/`**: Core functionality shared across all data sources
  - `database.py`: SQLite operations, schema management
  - `indexer.py`: Indexing pipeline (parse → transform → store)
  - `search.py`: Full-text search, filtering, ranking
  - `consciousness.py`: File-based knowledge management (Phase 1.5+)
- **`src/proof_of_monk/adapters/`**: Pluggable data source adapters
  - `base.py`: Abstract base class for adapters
  - `twitter.py`: Parse Twitter archive format
  - Future: `markdown.py`, `json.py`, `email.py`, etc.
- **`src/proof_of_monk/tools/`**: MCP tool implementations
  - `tweet_tools.py`: search_tweets, find_thread, etc.
  - `thought_tools.py`: dump_thought, list_thoughts, etc.

### Documentation

- **`README.md`**: High-level vision and philosophy
- **`ROADMAP.md`**: Detailed technical plan (architecture, phases, timeline)
- **`PROJECT_STRUCTURE.md`**: This file - explains code organization
- **`docs/setup.md`**: Step-by-step installation and configuration guide

### Data Directory

The `data/` directory is where all your personal information lives:

- **`proof-of-monk.db`**: SQLite database with indexed content
- **`consciousness/`**: Your consciousness directory (Phase 1.5+)
  - `streams/`: Daily thought streams (markdown files)
  - `memory/`: Consolidated topic files
  - `knowledge/`: Research articles, PDFs, bookmarks
  - `artifacts/`: Published work (articles, threads)
- **`sources/`**: Original data files (Twitter archive, notes, etc.)
- **`backups/`**: Automatic database backups

**Hybrid Architecture**: Database for structured data and fast queries, files for long-form human-readable content. Database indexes files via `file_path` references.

**IMPORTANT**: The entire `data/` directory is gitignored. Your personal data never leaves your machine unless you explicitly choose to.

## Data Flow

```
1. Raw Data (tweets, thoughts, research, articles)
           ↓
2. Adapter (pluggable parsers)
           ↓
3. Consciousness Directory (organized files)
           ├─ streams/ (daily markdown)
           ├─ memory/ (topics)
           ├─ knowledge/ (research)
           └─ artifacts/ (published)
           ↓
4. Hybrid Storage
           ├─ Database (SQLite + FTS5, structured data)
           └─ Files (long-form, human-readable)
           ↓
5. Search Layer (query both DB + files)
           ↓
6. MCP Tools (expose to AI)
           ↓
7. AI Assistant (Claude, etc.)
           ↓
8. You (discover connections in YOUR intellectual work)
```

## Phase 1 Implementation Order

1. **Database Schema** (`core/database.py`)
   - Create tables for tweets, bookmarks, thoughts
   - Set up FTS5 indexes
   - Migration system

2. **Twitter Adapter** (`adapters/twitter.py`)
   - Parse tweets.js, bookmarks.js, likes.js
   - Extract metadata (hashtags, mentions, URLs)
   - Handle threads and replies

3. **Indexer** (`core/indexer.py`)
   - Take parsed data and insert into database
   - Build full-text search indexes
   - Handle incremental updates

4. **Search** (`core/search.py`)
   - Full-text search with FTS5
   - Filtering (date range, has media, etc.)
   - Ranking and relevance

5. **MCP Tools** (`tools/tweet_tools.py`)
   - Implement search_tweets()
   - Implement find_thread()
   - Implement search_bookmarks()
   - etc.

6. **MCP Server** (`server.py`)
   - Register all tools
   - Handle requests from AI assistants
   - Error handling and logging

7. **CLI** (`cli.py`)
   - `proof-of-monk init`
   - `proof-of-monk index`
   - `proof-of-monk serve`
   - `proof-of-monk stats`

## Development Workflow

```bash
# 1. Set up development environment
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# 2. Make changes to code

# 3. Run tests
pytest

# 4. Format code
black src/
ruff check src/

# 5. Test with real data
proof-of-monk index
proof-of-monk serve

# 6. Test with Claude
# (Open Claude Desktop/Code and try queries)
```

## Extending Proof-of-Monk

### Adding a New Data Source Adapter

1. Create `src/proof_of_monk/adapters/your_source.py`
2. Extend `BaseAdapter` class
3. Implement `parse()` method
4. Register in `adapters/__init__.py`
5. Add config options in `config.example.yaml`

### Adding a New MCP Tool

1. Create function in appropriate tools file
2. Use `@server.tool()` decorator
3. Define input schema with Pydantic
4. Return structured results
5. Add tests

### Adding New Database Tables

1. Update schema in `core/database.py`
2. Create migration function
3. Update indexer to populate new table
4. Add search methods if needed

## Security Considerations

- **Never commit `config/config.yaml`** - Contains personal paths
- **Never commit `data/` directory** - Contains all your personal data
- **Be careful with logs** - May contain sensitive query content
- **Review privacy settings** - Enable redaction for phone/email/IP if needed

## Questions?

- Check the [ROADMAP.md](ROADMAP.md) for technical details
- Read [docs/setup.md](docs/setup.md) for installation help
- Open an issue on GitHub for bugs or features
- Join discussions for questions and ideas

---

Last updated: 2025-11-15
