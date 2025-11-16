# Deprecated Features and Documentation

**Date**: November 16, 2025
**Reason**: Architecture refocus and project rebrand to "Proof-of-Self"

This document explains what was deprecated during the project's pivot from a Twitter-focused tool to a universal knowledge base.

---

## Deprecated Documentation (Archived)

### Planning Documents
- **`AUDIT_REPORT.md`** - Comprehensive code audit from Nov 16, 2025
  - Status: Archived for historical reference
  - Reason: Identified Twitter-centricity problem; specific refactoring plan superseded
  - Value: Good analysis of technical debt, worth reading for context

- **`REFACTORING_PLAN.md`** - 4-week refactoring plan
  - Status: Archived
  - Reason: Phase numbering conflicted with earlier roadmap; plan superseded by unified approach
  - Value: Contains good technical ideas about database schema and MCP tool unification

- **`AUDIT_COMPLETE.md`** - Summary of audit findings
  - Status: Archived
  - Reason: Temporary summary document, content integrated into new docs

- **`roadmap.md`** - Earlier iteration roadmap
  - Status: Archived
  - Reason: Had "Phase 1.5" concepts that conflicted with refactoring plan
  - Value: Contains valid ideas about consciousness streams and semantic search (deferred)

- **`status.md`** - Project status snapshot
  - Status: Archived
  - Reason: Described old architecture and Twitter-focused implementation

- **`quickstart.md`** - Quick setup guide
  - Status: Archived
  - Reason: Entirely Twitter-focused; will be rewritten for universal approach

- **`setup.md`** - Detailed setup instructions
  - Status: Archived
  - Reason: Twitter-centric setup process; will be rewritten

- **`architecture.md`** (formerly PROJECT_STRUCTURE.md)
  - Status: Archived
  - Reason: Described Twitter-first architecture; will be replaced with new ARCHITECTURE.md

---

## Deprecated Features

### 1. Inbox Scanner (`src/proof_of_monk/core/inbox_scanner.py`)

**Status**: Feature exists but deprecated

**Original Purpose**: Drop files in `data/inbox/`, run `proof-of-monk index-inbox`, files move to `processed/`

**Why Deprecated**:
- User wants MCP-first interaction (AI finds files, not CLI)
- Adds complexity for a feature that should be an MCP tool
- Better approach: `add_to_knowledge_base(path)` MCP tool where AI locates and adds files

**Migration Path**:
- Refactor into `add_to_knowledge_base()` MCP tool
- AI can find files user mentions and add them
- Remove CLI `index-inbox` command
- Keep file adapter logic, just change how it's invoked

**Timeline**: Refactor in Phase 1

---

### 2. Twitter-Specific MCP Tools

**Status**: Currently implemented, will be deprecated

**Current Tools**:
- `search_tweets()`
- `find_thread()`
- `find_hot_takes()`
- `get_recent_tweets()`
- `get_tweet_stats()`

**Why Deprecated**:
- Project is now universal, not Twitter-focused
- Need generic equivalents that work across all content types

**Migration Path**:
- Create universal tools:
  - `search_knowledge_base()` (replaces `search_tweets`)
  - `find_conversation()` (replaces `find_thread`, works for any threaded content)
  - `find_popular_content()` (replaces `find_hot_takes`)
  - `get_recent_content()` (replaces `get_recent_tweets`)
  - `get_stats()` (replaces `get_tweet_stats`)
- Keep Twitter-specific tools as thin wrappers temporarily
- Add deprecation warnings
- Remove in Phase 2 after migration

**Timeline**: Phase 1 (create universal tools), Phase 2 (remove Twitter-specific)

---

### 3. CLI Index Commands

**Status**: Currently implemented, will be deprecated

**Current Commands**:
- `proof-of-monk index --twitter-archive <path>`
- `proof-of-monk index-inbox`

**Why Deprecated**:
- User wants MCP-first interaction (talk to AI, not run CLI)
- Better UX: "Claude, add my Twitter archive" vs running command
- Aligns with vision: "You never interact with Proof-of-Self directly"

**Keeping**:
- `proof-of-self init` - Initialize database (setup)
- `proof-of-self stats` - View what's indexed (debugging)
- `proof-of-self serve` - Start MCP server if needed (setup)

**Migration Path**:
- Implement `add_to_knowledge_base()` MCP tool
- Remove CLI index commands
- Update documentation to show MCP-only usage

**Timeline**: Phase 1

---

### 4. "Consciousness Streams" Concept

**Status**: Partially designed, not implemented, **deferred**

**Original Idea**:
- Daily markdown files for thought streams
- Directory structure: `streams/`, `memory/`, `knowledge/`, `artifacts/`
- Hybrid database + file storage

**Why Deferred**:
- Need to validate core architecture first (SQL + chunking)
- Unclear if consciousness directory adds value vs complexity
- Should test with real usage before committing to this structure
- Research needed on best file organization patterns

**Future Consideration**:
- May implement in Phase 2 or 3 if needed
- Good idea, but premature for Phase 1
- Focus first on universal content ingestion and search

**Timeline**: Deferred to Phase 2+ (pending research and real-world testing)

---

### 5. Twitter-First Database Schema

**Status**: Currently implemented, **will be refactored**

**Current Issue**:
- `tweets`, `bookmarks`, `likes` tables are primary
- `documents` table is secondary/afterthought
- Search methods are Twitter-specific

**Refactoring To**:
- `documents` table as PRIMARY universal store
- Twitter content just another `source_type`
- Universal search across all content types
- Optional: Keep old tables as views for backward compatibility

**Timeline**: Phase 1 (critical refactoring)

---

## What This Means for Users

### If You Were Using Phase 1 (Twitter-focused version)

**Your data is safe**:
- Database schema will migrate automatically
- Original Twitter archive files unchanged
- Indexed tweets will remain accessible

**What will change**:
- CLI commands replaced with MCP tools
- Twitter-specific tools replaced with universal tools
- Better: Search across ALL your content, not just tweets

**Migration**:
- Re-index with new universal approach
- Use MCP tools instead of CLI
- Benefit from generic architecture

### If You're New

**Start fresh**:
- Universal architecture from day 1
- MCP-first interaction
- Add any content type (Twitter, books, notes, PDFs)
- Clean, consistent interface

---

## Lessons Learned

### What Went Wrong
1. **Started too specific**: Building for Twitter first created architecture that's hard to generalize
2. **Conflicting plans**: Had two different roadmaps (progressive vs refactoring) causing confusion
3. **Feature creep**: Inbox scanner and consciousness streams added before core was solid
4. **Documentation sprawl**: Too many planning docs without clear hierarchy

### What Went Right
1. **Good adapter pattern**: Pluggable adapters work well, just need generic interface
2. **SQLite + FTS5 choice**: Proven correct by research, keep this
3. **MCP integration**: Works well, just need to make tools universal
4. **Privacy-first principle**: Never compromised on this, maintain it

### Going Forward
1. **Refactor first, then add features**: Fix foundation before building
2. **Universal from start**: No more Twitter-specific anything
3. **MCP-first**: AI is the interface, CLI minimal
4. **One clear roadmap**: Single source of truth, no conflicting plans
5. **Test at scale**: Index diverse content, see what breaks

---

## Reference

**For historical context**, archived documents are available in `docs/archive/`:
- Architecture decisions: See archived `AUDIT_REPORT.md`
- Technical debt analysis: See archived `REFACTORING_PLAN.md`
- Earlier vision: See archived `roadmap.md`

**For current direction**, see:
- `ARCHITECTURE.md` - Current architecture and decisions
- `ROADMAP.md` - Unified development plan
- `PROJECT_VISION.md` - Overall vision and philosophy

---

**Status**: Documentation cleanup complete. Ready for Phase 1 implementation.
