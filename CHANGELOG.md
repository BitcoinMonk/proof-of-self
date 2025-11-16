# Changelog

All notable changes to Proof-of-Self will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.0] - 2025-11-16 - ARCHITECTURE RESET

### Major Changes - Rebrand & Refocus

**Project Rebrand**: "Proof-of-Monk" → "Proof-of-Self"
- Emphasizes universal personal knowledge base (not Twitter-specific)
- Aligns with vision: privacy-first AI memory system
- Package will be renamed in Phase 1 implementation

**Architecture Decisions**:
- Adopted documents-first schema (Twitter as one source among many)
- Chose SQLite + FTS5 for storage (proven, local, scales to 100k+ docs)
- Implemented chunking strategy: 500-1000 tokens, 10-20% overlap
- Deferred semantic search to Phase 3 (evaluate after keyword search proves itself)
- MCP-first interaction model (AI is the interface, minimal CLI)

**Documentation Overhaul**:
- Created **ARCHITECTURE.md** - Technical architecture with research findings
- Created **ROADMAP.md** - Unified 3-phase development plan
- Updated **README.md** - Universal focus, clear current status
- Updated **PROJECT_VISION.md** - Aligned with decisions
- Archived deprecated docs to `docs/archive/`:
  - Previous roadmap.md (phase numbering conflicts)
  - AUDIT_REPORT.md (superseded by new plan)
  - REFACTORING_PLAN.md (specific plan superseded)
  - AUDIT_COMPLETE.md (temporary document)
  - Old status.md, quickstart.md, setup.md (Twitter-focused)
  - Old architecture.md (PROJECT_STRUCTURE.md)
- Created **docs/archive/DEPRECATED.md** - Documents what was deprecated and why

### Deprecated Features

- **Inbox scanner** - Will be refactored into `add_to_knowledge_base()` MCP tool
- **Twitter-specific MCP tools** - Will be replaced with universal equivalents
- **CLI index commands** - MCP-first approach, AI does the indexing
- **"Consciousness streams" concept** - Deferred pending Phase 2 research

### Current Status

**Phase 1 Goals (2-3 weeks)**:
- Complete rebrand throughout codebase
- Refactor database to documents-first schema
- Implement universal MCP tools
- Add PDF support with chunking
- Remove Twitter-specific CLI commands

See **ROADMAP.md** for detailed development plan.

---

## [0.1.0] - 2025-11-15

### Added - Initial MVP (Twitter-Focused)

#### Core Infrastructure
- SQLite database with FTS5 full-text search indexing
- Database schema for tweets, bookmarks, likes, thoughts, and articles
- Automatic schema initialization and migration
- Support for `~/.local/share/proof-of-monk/` data directory (XDG standard)

#### Twitter Archive Adapter
- Parse Twitter archive exports (tweets.js, bookmarks.js, likes.js)
- Automatic username extraction from account.js
- Date filtering and retweet exclusion options
- Entity extraction (hashtags, mentions, URLs)
- Support for replies, retweets, and thread reconstruction
- Indexed 8,349+ tweets successfully in testing

#### Search Functionality
- Full-text search across all tweets
- Thread reconstruction (find complete threads from any tweet)
- "Hot takes" finder (high-engagement tweets on topics)
- Recent tweets query
- Context-aware search with date and engagement filters
- Search results include direct Twitter URLs for verification

#### MCP Server
- Complete MCP (Model Context Protocol) integration
- Works with Claude Code and Claude Desktop
- 7 MCP tools exposed:
  - `search_tweets` - Full-text search with filters
  - `find_thread` - Reconstruct complete threads
  - `find_hot_takes` - Find high-engagement tweets
  - `get_recent_tweets` - Get latest tweets
  - `get_tweet_stats` - Archive statistics
  - `dump_thought` - Save notes to knowledge base
  - `list_thoughts` - Retrieve saved thoughts

#### Command-Line Interface
- `proof-of-monk init` - Initialize database
- `proof-of-monk index` - Index Twitter archive
- `proof-of-monk stats` - View database statistics
- `proof-of-monk serve` - Start MCP server (standalone mode)
- Rich terminal output with tables and colors
- Custom database path support
- Progress logging during indexing

#### Developer Experience
- Project structure with adapters, core, and tools modules
- Base adapter interface for future data sources
- Comprehensive logging
- Error handling and validation
- Type hints throughout codebase

### Technical Details

**Dependencies:**
- Python 3.10+
- mcp >= 0.9.0
- click >= 8.1.0
- rich >= 13.0.0
- pyyaml >= 6.0
- pydantic >= 2.0.0

**Database:**
- SQLite with FTS5 virtual tables
- Indexed fields: tweet text, dates, engagement metrics
- Foreign key constraints enabled
- Automatic trigger-based FTS sync

**Testing:**
- Successfully indexed and searched 8,349 tweets
- Verified thread reconstruction
- Confirmed high-engagement tweet discovery
- Validated tweet URL generation

### Documentation
- Comprehensive README with installation instructions
- MCP server configuration examples
- Usage examples for CLI and AI integration
- Architecture overview
- Data storage location standards

## [Unreleased]

### In Progress - Phase 1.5: Consciousness Streams

**Consciousness Directory Structure:**
- Daily thought streams (date-based markdown files)
- Organized hierarchy: streams/ memory/ knowledge/ artifacts/
- Hybrid storage: database + files working together
- File-based research and long-form content capture

**Database Extensions:**
- `file_path` column in thoughts table (link to markdown files)
- `content_type` column ('short'|'long'|'stream')
- `source_type` column ('thought'|'tweet'|'article'|'research')
- Smart routing based on content length

**New MCP Tools:**
- `stream_thought` - Dump thoughts to daily stream files
- `save_research` - Save articles/papers to knowledge folder
- `search_consciousness` - Search across database AND files
- `list_streams` - Browse daily thought streams

**New Core Module:**
- `src/proof_of_monk/core/consciousness.py` - File-based knowledge management
- ConsciousnessStream class for managing daily streams
- Automatic indexing of file-based content
- Hash-based change detection for incremental updates

### Planned Features - Phase 2+

**Phase 2: Semantic Search (January 2026)**
- SQLite-Vec integration for vector embeddings
- Local embeddings with sentence-transformers (all-MiniLM-L6-v2)
- Hybrid search combining FTS5 + vector similarity
- RAG-style discovery tools (find_connections, explore_topic)
- "I know I thought about this somewhere" queries

**Phase 3: Knowledge Graph (Q1 2026)**
- Entity extraction from all content types
- Lightweight knowledge graph (NetworkX + SQLite)
- Graph navigation and relationship discovery
- Automated consolidation suggestions
- Timeline view of idea evolution

**Additional Data Source Adapters:**
- Markdown files / Obsidian vaults
- PDF document indexing
- Web bookmarks (HTML, Pocket exports)
- Email archives (mbox, maildir)
- Chat log adapters (Signal, Telegram)
- Voice notes with transcription

**Feature Enhancements:**
- Bookmark and like search tools
- Article tracking and source linking
- Export functionality (Obsidian, Roam formats)
- Automated Twitter archive updates
- Web dashboard (optional)

---

**Legend:**
- Added: New features
- Changed: Changes in existing functionality
- Deprecated: Soon-to-be removed features
- Removed: Removed features
- Fixed: Bug fixes
- Security: Security fixes
