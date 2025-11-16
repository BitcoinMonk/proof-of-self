# Refactoring Plan: From Twitter-Centric to Universal

**Date**: November 16, 2025
**Goal**: Transform Proof-of-Monk into a truly universal knowledge base (Proof-of-Self)
**Status**: Planning Phase

---

## Current State

The codebase is functional but Twitter-focused:
- ✅ MCP server works
- ✅ Twitter adapter works well
- ✅ Basic file adapter exists
- ❌ Architecture is Twitter-first
- ❌ Search is Twitter-only
- ❌ Documentation emphasizes Twitter

## Target State

A universal personal knowledge base where:
- ✅ Documents table is primary
- ✅ Search works across all content types
- ✅ Twitter is just another adapter
- ✅ Users interact via AI (MCP only)
- ✅ Clean, well-tested codebase

---

## Phase 1: Foundation Refactor (Week 1-2)

### 1.1 Database Schema Refactoring

**Current Problem**: Twitter tables (tweets, bookmarks, likes) are first-class, documents are afterthought.

**Solution**: Make `documents` the primary table, create views for backward compatibility.

**Tasks**:
- [ ] Add migration system (alembic or custom)
- [ ] Keep existing tables for now (backward compatibility)
- [ ] Ensure documents table has all needed fields
- [ ] Create database views:
  ```sql
  CREATE VIEW tweets_unified AS
  SELECT * FROM documents WHERE source_type = 'twitter' AND content_type = 'tweet';
  ```
- [ ] Update Database class methods to use documents table
- [ ] Add proper transaction management (context managers)

**Files to modify**:
- `src/proof_of_monk/core/database.py`

**Estimated time**: 2-3 days

### 1.2 Search Class Generalization

**Current Problem**: Search class (search.py) has only Twitter-specific methods.

**Solution**: Create universal search methods, keep Twitter-specific as wrappers.

**Tasks**:
- [ ] Rename `Search` → `ContentSearch` (or keep Search but generalize)
- [ ] Add `search_content(query, filters)` - universal search
- [ ] Add `search_by_source(query, source_type, filters)`
- [ ] Keep Twitter methods as convenience wrappers:
  ```python
  def search_tweets(self, query, ...):
      return self.search_content(query, source_type="twitter", ...)
  ```
- [ ] Add `find_conversation(root_id)` - generalized from `find_thread`
- [ ] Add `find_related(content_id, limit)` - similarity search

**Files to modify**:
- `src/proof_of_monk/core/search.py`

**Estimated time**: 2-3 days

### 1.3 MCP Tools Refactoring

**Current Problem**: Tools are fragmented (tweet_tools, thought_tools, document_tools) with duplicate code.

**Solution**: Create unified MCP tools that work across all content.

**New MCP Tools**:
```python
# Core tools (user-facing via AI)
add_to_knowledge_base(path: str, source_type: Optional[str]) → status
search_knowledge_base(query: str, filters: dict) → results
save_to_knowledge_base(content: str, metadata: dict) → id
list_knowledge_base(filters: dict) → list
remove_from_knowledge_base(id: str) → status

# Legacy tools (keep for backward compat, mark deprecated)
search_tweets(query, ...) → results  # Wrapper around search_knowledge_base
find_thread(tweet_id) → thread  # Wrapper around find_conversation
dump_thought(...) → id  # Wrapper around save_to_knowledge_base
```

**Tasks**:
- [ ] Create `src/proof_of_monk/tools/knowledge_base_tools.py`
- [ ] Implement unified tools
- [ ] Refactor existing tools to use unified base
- [ ] Add deprecation warnings to Twitter-specific tools
- [ ] Update server.py to register new tools

**Files to create/modify**:
- `src/proof_of_monk/tools/knowledge_base_tools.py` (NEW)
- `src/proof_of_monk/tools/` (refactor existing)
- `src/proof_of_monk/server.py`

**Estimated time**: 3-4 days

### 1.4 Indexer Improvements

**Current Problem**: Indexer treats documents as "another type" instead of primary.

**Solution**: Refactor indexer to be document-centric.

**Tasks**:
- [ ] All adapters should yield document records
- [ ] Twitter adapter wraps tweets in document structure
- [ ] Remove type-specific index methods, use single `_index_document`
- [ ] Add deduplication logic (check hash before insert)
- [ ] Add update logic (update metadata if content exists)

**Files to modify**:
- `src/proof_of_monk/core/indexer.py`
- `src/proof_of_monk/adapters/twitter.py`
- `src/proof_of_monk/adapters/file.py`

**Estimated time**: 2 days

---

## Phase 2: Quality & Testing (Week 3)

### 2.1 Test Infrastructure

**Tasks**:
- [ ] Create `tests/conftest.py` with fixtures
- [ ] Add fixtures for:
  - Test database (in-memory SQLite)
  - Sample documents
  - Mock adapters
- [ ] Organize tests:
  ```
  tests/
  ├── conftest.py
  ├── unit/
  │   ├── core/
  │   │   ├── test_database.py
  │   │   ├── test_search.py
  │   │   └── test_indexer.py
  │   └── adapters/
  │       ├── test_twitter_adapter.py
  │       └── test_file_adapter.py
  └── integration/
      ├── test_full_flow.py
      └── test_mcp_tools.py
  ```

**Target**: 60% test coverage

**Estimated time**: 3-4 days

### 2.2 Error Handling & Logging

**Tasks**:
- [ ] Create exception hierarchy:
  ```python
  class ProofOfSelfError(Exception): pass
  class ConfigError(ProofOfSelfError): pass
  class AdapterError(ProofOfSelfError): pass
  class ValidationError(AdapterError): pass
  class DatabaseError(ProofOfSelfError): pass
  ```
- [ ] Replace generic `Exception` catches with specific exceptions
- [ ] Use `logger.exception()` for all error logging
- [ ] Fix logging configuration (remove CRITICAL level)
- [ ] Add file-based logging separate from MCP stdio

**Files to create/modify**:
- `src/proof_of_monk/exceptions.py` (NEW)
- All modules with exception handling

**Estimated time**: 2 days

### 2.3 Configuration System

**Tasks**:
- [ ] Create Pydantic config models:
  ```python
  class Config(BaseSettings):
      db_path: Path = Path("./data/proof-of-monk.db")
      log_level: str = "INFO"
      log_file: Optional[Path] = None
      ...
  ```
- [ ] Support .env files
- [ ] Add config validation
- [ ] Document all config options

**Files to create/modify**:
- `src/proof_of_monk/config.py` (NEW)
- Update all modules to use config

**Estimated time**: 1-2 days

---

## Phase 3: Documentation & Polish (Week 4)

### 3.1 Update Documentation

**Tasks**:
- [ ] Update all docs to reflect universal vision
- [ ] Remove Twitter-centric examples
- [ ] Add diverse use case examples (books, research, notes)
- [ ] Create MCP tools documentation
- [ ] Update quickstart guide
- [ ] Update architecture docs

**Files to modify**:
- All files in `docs/`
- `PROJECT_VISION.md` (already done)
- `README.md` (already done)

**Estimated time**: 2-3 days

### 3.2 CLI Simplification

**Current**: Mix of `index`, `index-inbox`, `stats`, etc.

**Target**: Clean MCP-first interface with minimal CLI.

**Proposed CLI**:
```bash
# Setup only (not for regular use)
proof-of-monk init              # Initialize database
proof-of-monk serve             # Start MCP server (or use via config)

# Admin/debugging (optional)
proof-of-monk stats             # Show database stats
proof-of-monk list              # List indexed content
proof-of-monk vacuum            # Clean up database

# Remove these (use MCP instead):
❌ proof-of-monk index --twitter-archive
❌ proof-of-monk index-inbox
```

**Users should add content via AI**:
```
User: "Claude, add my Twitter archive"
Claude: [Uses add_to_knowledge_base MCP tool]
```

**Tasks**:
- [ ] Simplify CLI to setup/admin only
- [ ] Remove user-facing index commands
- [ ] Update documentation to show AI-first usage

**Files to modify**:
- `src/proof_of_monk/cli.py`

**Estimated time**: 1 day

---

## Phase 4: Enhanced Features (Month 2+)

### 4.1 PDF Support

**Tasks**:
- [ ] Add PyPDF2 or pdfplumber dependency
- [ ] Create PDF adapter
- [ ] Extract text with page numbers
- [ ] Extract metadata (author, title, etc.)
- [ ] Handle multi-page documents

**Estimated time**: 3-4 days

### 4.2 ePub Support

**Tasks**:
- [ ] Add ebooklib dependency
- [ ] Create ePub adapter
- [ ] Extract chapter structure
- [ ] Handle metadata

**Estimated time**: 2-3 days

### 4.3 Web Content

**Tasks**:
- [ ] Add requests + BeautifulSoup dependencies
- [ ] Create web adapter
- [ ] Archive web pages
- [ ] Extract clean text from HTML

**Estimated time**: 2-3 days

### 4.4 Deduplication & Smart Updates

**Tasks**:
- [ ] Implement content hashing
- [ ] Check for duplicates before insert
- [ ] Smart merging of metadata
- [ ] Handle source re-indexing (add only new content)

**Estimated time**: 2-3 days

---

## Critical Changes Summary

### Database
```sql
-- Current (wrong)
tweets (primary) → tweets_fts
documents (secondary) → documents_fts

-- Target (right)
documents (primary) → documents_fts
tweets_view → SELECT * FROM documents WHERE source_type='twitter'
```

### Search
```python
# Current (wrong)
search.search_tweets(query)
search.find_thread(id)
search.find_hot_takes()

# Target (right)
search.search_content(query, source_type="twitter")
search.search_content(query, source_type="pdf")
search.find_conversation(id)  # Works for any content type
```

### MCP Tools
```python
# Current (wrong)
search_tweets(query) → results
search_documents(query) → results
list_thoughts() → results

# Target (right)
search_knowledge_base(query, filters) → results  # Works for everything
save_to_knowledge_base(content, metadata) → id   # Universal save
```

### User Interaction
```python
# Current (wrong)
$ proof-of-monk index --twitter-archive ~/Downloads/twitter-*
$ proof-of-monk index-inbox

# Target (right)
User: "Claude, add my Twitter archive at ~/Downloads/twitter-*"
Claude: [Uses add_to_knowledge_base MCP tool]

User: "Claude, add all PDFs in ~/Books/"
Claude: [Uses add_to_knowledge_base MCP tool]
```

---

## Success Metrics

### Technical
- [ ] 60%+ test coverage
- [ ] All adapters use documents table
- [ ] Zero Twitter-specific search methods (only wrappers)
- [ ] MCP tools work across all content types
- [ ] Database is documents-first

### User Experience
- [ ] Users can add any content type via AI
- [ ] Search works across all sources
- [ ] No CLI required for normal use
- [ ] Clear error messages
- [ ] Fast response times (<100ms for searches)

### Documentation
- [ ] PROJECT_VISION.md is accurate
- [ ] README shows diverse use cases
- [ ] No Twitter-centric examples
- [ ] MCP tools fully documented
- [ ] Architecture is clear

---

## Migration Strategy

### Backward Compatibility

**Keep for now**:
- Existing database tables (tweets, bookmarks, likes)
- Twitter-specific MCP tools (mark as deprecated)
- Existing Twitter adapter

**Add**:
- Database views for unified access
- New universal MCP tools
- Migration path documentation

**Remove later** (v2.0):
- Direct access to Twitter tables
- Twitter-specific tools (replaced by universal)
- Twitter-centric CLI commands

### User Migration

**For existing users**:
1. System auto-migrates database (adds documents table)
2. Twitter tools still work (wrappers)
3. Gradual deprecation warnings
4. Final migration in v2.0

---

## Timeline

**Week 1-2**: Phase 1 (Foundation Refactor)
- Database schema
- Search generalization
- MCP tools refactoring
- Indexer improvements

**Week 3**: Phase 2 (Quality & Testing)
- Test infrastructure
- Error handling
- Configuration system

**Week 4**: Phase 3 (Documentation & Polish)
- Update all docs
- CLI simplification
- Final testing

**Month 2+**: Phase 4 (Enhanced Features)
- PDF, ePub, web support
- Deduplication
- Advanced features

---

## Risks & Mitigations

### Risk: Breaking existing users
**Mitigation**: Keep backward compatibility, gradual migration

### Risk: Scope creep
**Mitigation**: Stick to plan, defer nice-to-haves to later phases

### Risk: Test coverage slips
**Mitigation**: Set minimum coverage requirement, block merges below threshold

### Risk: Performance degradation
**Mitigation**: Benchmark before/after, optimize queries

---

## Next Steps (Immediate)

1. **Review this plan** - Get feedback, adjust
2. **Set up development branch** - `refactor/universal-kb`
3. **Start with database refactoring** - Foundation first
4. **Write tests as you go** - TDD approach
5. **Document changes** - Update ADRs

---

**Goal**: By end of Month 1, have a fully functional universal knowledge base that's obviously NOT a Twitter tool.

**Success**: User can tell Claude "add my books" and it just works.
