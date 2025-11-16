# Proof-of-Self: Architecture

**Version**: 1.0
**Date**: November 16, 2025
**Status**: Definitive architecture after research and refocus

This document defines the architecture for Proof-of-Self, a universal personal knowledge base accessible via MCP tools.

---

## Core Principles

1. **Universal, not Twitter-specific** - Any content type is first-class
2. **MCP-first** - AI is the interface, not CLI
3. **Privacy-first** - All data local, no cloud services
4. **Simple & maintainable** - Avoid over-engineering
5. **Scalable to personal scale** - 100k+ documents, not enterprise scale

---

## Architecture Overview

```
┌──────────────────────────────────────────────────┐
│                   USER                           │
│         (Talks to Claude/GPT via MCP)            │
└────────────────────┬─────────────────────────────┘
                     │
                     ↓
┌──────────────────────────────────────────────────┐
│              MCP TOOLS LAYER                     │
│  • add_to_knowledge_base(path, metadata)         │
│  • search_knowledge_base(query, filters)         │
│  • save_to_knowledge_base(content, metadata)     │
│  • list_sources(filters)                         │
│  • get_content(id)                               │
└────────────────────┬─────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        ↓                         ↓
┌─────────────────┐     ┌──────────────────┐
│  STORAGE LAYER  │     │   SEARCH LAYER   │
├─────────────────┤     ├──────────────────┤
│                 │     │ Phase 1:         │
│ SQLite Database │◄────┤ • FTS5 keyword   │
│ • documents     │     │ • BM25 ranking   │
│ • chunks        │     │ • Metadata filter│
│ • metadata      │     │                  │
│ • FTS5 indexes  │     │ Phase 2+:        │
│                 │     │ • ChromaDB       │
│ File System     │     │   (optional)     │
│ • Original PDFs │     │ • Hybrid RRF     │
│ • Markdown      │     │ • Semantic       │
│ • Archives      │     └──────────────────┘
└─────────────────┘
        ↑
        │
┌───────┴──────────┐
│  ADAPTER LAYER   │
│ • Twitter        │
│ • PDF (PyMuPDF)  │
│ • Markdown       │
│ • ePub (future)  │
│ • Email (future) │
└──────────────────┘
```

---

## Storage Layer

### Database: SQLite + FTS5

**Why SQLite?**
- Perfect for personal knowledge bases (100k+ documents)
- Single-file portability
- Zero configuration
- Fast full-text search with FTS5
- Privacy-first (local-only)
- Proven at scale

**Performance Benchmarks**:
- 10k-100k documents: Sub-20ms queries
- FTS5 index: 45-50% of content size
- Query speed: 100k SELECT/s possible
- Database size: 1-5 GB for 100k docs

**When NOT to use SQLite**:
- Multiple concurrent writers (not an issue for single-user)
- Distributed systems (not applicable)
- Enterprise-scale multi-tenancy (not our use case)

### Schema Design: Documents-First

```sql
-- PRIMARY TABLE: Universal document storage
CREATE TABLE documents (
    id TEXT PRIMARY KEY,              -- SHA256 hash of content + source
    source_type TEXT NOT NULL,        -- 'twitter', 'pdf', 'markdown', 'user'
    content_type TEXT NOT NULL,       -- 'tweet', 'book', 'note', 'article'
    title TEXT,
    author TEXT,
    content TEXT,                     -- Full content or NULL if file-referenced
    source_path TEXT,                 -- Path to original file (if applicable)
    is_chunked BOOLEAN DEFAULT FALSE, -- True if large doc with chunks
    metadata TEXT,                    -- JSON blob for source-specific metadata
    created_at TIMESTAMP,
    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CHUNKS TABLE: For large documents (books, long PDFs)
CREATE TABLE chunks (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    metadata TEXT,                    -- JSON: page numbers, section, etc.
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    UNIQUE(document_id, chunk_index)
);

-- FTS5 INDEXES: Fast full-text search
CREATE VIRTUAL TABLE documents_fts USING fts5(
    id UNINDEXED,
    title,
    author,
    content,
    content=documents,
    content_rowid=rowid
);

CREATE VIRTUAL TABLE chunks_fts USING fts5(
    id UNINDEXED,
    content,
    content=chunks,
    content_rowid=rowid
);

-- TRIGGERS: Keep FTS5 in sync
CREATE TRIGGER documents_ai AFTER INSERT ON documents BEGIN
    INSERT INTO documents_fts(rowid, id, title, author, content)
    VALUES (new.rowid, new.id, new.title, new.author, new.content);
END;

CREATE TRIGGER chunks_ai AFTER INSERT ON chunks BEGIN
    INSERT INTO chunks_fts(rowid, id, content)
    VALUES (new.rowid, new.id, new.content);
END;

-- (Similar UPDATE and DELETE triggers)
```

### Hybrid Storage Strategy

**Decision Matrix**:

| Document Size | Storage Strategy | Rationale |
|--------------|------------------|-----------|
| < 5,000 words | Full content in `documents.content` | Fast, simple, no chunking needed |
| 5,000 - 50,000 words | Chunked + full content in DB | Precise retrieval, keep original |
| > 50,000 words | Chunked + file reference | Avoid DB bloat, preserve original |

**Chunking Strategy**:
- **Chunk size**: 500-1000 tokens (2000-4000 characters)
- **Overlap**: 10-20% (100-200 tokens)
- **Method**: Semantic chunking (respect sentence/paragraph boundaries)
- **Metadata**: Each chunk carries hierarchical context (book → chapter → section)

**Example: 300-page book**
```python
{
    "document": {
        "id": "book_on_writing_king",
        "title": "On Writing",
        "author": "Stephen King",
        "is_chunked": True,
        "source_path": "/knowledge/books/on-writing.pdf",
        "content": None  # Large, referenced
    },
    "chunks": [
        {
            "id": "chunk_001",
            "chunk_index": 0,
            "content": "First 500 tokens...",
            "metadata": {
                "chapter": "Introduction",
                "page_range": "1-3"
            }
        },
        # ... 200+ chunks total
    ]
}
```

---

## Search Layer

### Phase 1: FTS5 Keyword Search (CURRENT)

**Technology**: SQLite FTS5 with BM25 ranking

**Capabilities**:
- Full-text keyword search
- Boolean operators (AND, OR, NOT)
- Phrase search ("exact match")
- Prefix search (datam*)
- Proximity search (words NEAR each other)
- BM25 relevance ranking

**Performance**:
- < 50ms for complex queries on 100k documents
- Sub-20ms for simple keyword queries

**Query Examples**:
```sql
-- Simple keyword
SELECT * FROM documents_fts
WHERE documents_fts MATCH 'bitcoin'
ORDER BY rank LIMIT 10;

-- Boolean query
WHERE documents_fts MATCH 'bitcoin AND (mining OR nodes)'

-- Phrase search
WHERE documents_fts MATCH '"proof of work"'

-- With metadata filters
SELECT d.* FROM documents d
JOIN documents_fts fts ON d.id = fts.id
WHERE fts MATCH 'dialogue'
  AND d.source_type = 'pdf'
  AND d.author = 'Stephen King'
ORDER BY rank LIMIT 10;
```

**Search Strategy**:
1. Search both `documents_fts` and `chunks_fts`
2. For chunk matches, return parent document + surrounding context
3. Rank by BM25 relevance score
4. Apply metadata filters (date, source, author, tags)

### Phase 2+: Optional Semantic Search

**When to implement**: Only if Phase 1 search proves insufficient

**Technology**: ChromaDB (local vector database)

**Approach**:
```python
# Hybrid search combining keyword + semantic
def search_knowledge_base(query: str, strategy: str = "hybrid"):
    if strategy == "keyword":
        return fts5_search(query)

    elif strategy == "semantic":
        return chromadb_search(query)

    elif strategy == "hybrid":
        # Both strategies, combined with RRF
        keyword_results = fts5_search(query)
        semantic_results = chromadb_search(query)
        return reciprocal_rank_fusion(keyword_results, semantic_results)
```

**Embedding Model**: all-MiniLM-L6-v2
- Size: 22MB (tiny, fits in memory)
- Dimensions: 384
- Speed: ~25 minutes for 75k documents
- Quality: Excellent for personal use

**Decision Criteria for Adding Semantic Search**:
- [ ] FTS5 keyword search insufficient for common queries
- [ ] User frequently searches with vague/conceptual queries
- [ ] "Find similar" feature adds clear value
- [ ] Willing to accept 2x storage overhead (FTS5 + embeddings)
- [ ] Willing to accept indexing time increase (embedding generation)

---

## Adapter Layer

### Base Adapter Interface

```python
from abc import ABC, abstractmethod
from typing import Iterator, Dict, Any

class BaseAdapter(ABC):
    """Base class for all data source adapters"""

    @abstractmethod
    def parse(self) -> Iterator[Dict[str, Any]]:
        """
        Parse source and yield document records

        Yields:
            {
                "source_type": "twitter",
                "content_type": "tweet",
                "title": Optional[str],
                "author": Optional[str],
                "content": str,
                "metadata": Dict[str, Any],
                "created_at": timestamp
            }
        """
        pass

    @abstractmethod
    def validate_source(self) -> bool:
        """Verify source is valid and accessible"""
        pass
```

### Implemented Adapters

**1. Twitter Adapter**
- Parses: `tweets.js`, `bookmarks.js`, `likes.js`
- Extracts: Hashtags, mentions, URLs, engagement metrics
- Handles: Replies, retweets, threads

**2. Markdown Adapter**
- Parses: `.md`, `.markdown` files
- Extracts: Frontmatter metadata, headings, content
- Handles: Nested directory structures

**3. PDF Adapter** (Phase 1)
- Tool: PyMuPDF (fast, accurate)
- Extracts: Text, page numbers, metadata (author, title)
- Chunks: Large PDFs into searchable pieces

### Future Adapters (Phase 2+)

**4. ePub Adapter**
- Library: ebooklib
- Extracts: Chapter structure, TOC, metadata

**5. Email Adapter**
- Formats: mbox, maildir
- Extracts: Subject, from/to, body, threads

**6. Web Bookmark Adapter**
- Formats: HTML exports from browsers, Pocket
- Extracts: Title, URL, saved content

---

## MCP Tools Layer

### Universal Tools (Phase 1)

```python
@server.call_tool()
async def add_to_knowledge_base(
    path: str,
    source_type: Optional[str] = None,
    metadata: Optional[Dict] = None
) -> str:
    """
    Add content to knowledge base

    AI locates file, determines type, indexes it
    User: "Claude, add my Twitter archive"
    User: "Add this PDF: ~/Books/on-writing.pdf"
    """
    # Auto-detect source type if not specified
    # Choose appropriate adapter
    # Index content
    # Return status + stats
```

```python
@server.call_tool()
async def search_knowledge_base(
    query: str,
    source_type: Optional[str] = None,
    content_type: Optional[str] = None,
    date_range: Optional[Tuple[str, str]] = None,
    limit: int = 10
) -> List[Dict]:
    """
    Universal search across all content

    Searches both documents and chunks
    Returns relevant excerpts with context
    """
    # FTS5 keyword search
    # Apply metadata filters
    # Return ranked results
```

```python
@server.call_tool()
async def save_to_knowledge_base(
    content: str,
    title: str,
    category: str,
    tags: List[str] = []
) -> str:
    """
    Save newly created content

    User + AI create something together
    Save it back to knowledge base
    """
    # Create document record
    # Index for search
    # Return ID
```

```python
@server.call_tool()
async def list_sources(
    source_type: Optional[str] = None,
    limit: int = 20
) -> List[Dict]:
    """
    List what's in knowledge base

    Browse indexed content by type
    Get statistics
    """
    # Query documents table
    # Group by source_type
    # Return summaries
```

```python
@server.call_tool()
async def get_content(
    content_id: str
) -> Dict:
    """
    Retrieve specific content by ID

    Get full document with metadata
    """
    # Fetch from documents table
    # Include chunks if applicable
    # Return complete record
```

### Deprecated Tools (Phase Out)

Twitter-specific tools will be thin wrappers temporarily:

```python
@server.call_tool()
async def search_tweets(query: str, **kwargs):
    """DEPRECATED: Use search_knowledge_base() instead"""
    return await search_knowledge_base(
        query,
        source_type="twitter",
        **kwargs
    )
```

**Timeline**: Remove entirely in Phase 2 after migration

---

## Content Processing Pipeline

```
1. User Request
   User: "Add my book collection"
   │
   ↓
2. AI Uses MCP Tool
   add_to_knowledge_base(path="~/Books/")
   │
   ↓
3. Adapter Selection
   Detect: PDF files
   Choose: PDFAdapter
   │
   ↓
4. Content Extraction
   PyMuPDF: Extract text + metadata
   │
   ↓
5. Chunking Decision
   300-page book → YES, chunk it
   Semantic chunking (500-1000 tokens)
   │
   ↓
6. Storage
   • Create document record (metadata + file ref)
   • Create 200+ chunk records
   • Insert into SQLite
   • FTS5 triggers auto-index
   │
   ↓
7. Response
   "Indexed: On Writing by Stephen King
    Pages: 300, Chunks: 247
    Time: 2.3 seconds"
```

---

## Performance Considerations

### Database Optimizations

```sql
-- Batch inserts within transactions
BEGIN TRANSACTION;
INSERT INTO documents VALUES (...);
INSERT INTO documents VALUES (...);
-- ... 100+ inserts
COMMIT;

-- Defer FTS5 updates during bulk insert
PRAGMA defer_foreign_keys = ON;
-- bulk insert
PRAGMA defer_foreign_keys = OFF;

-- Optimize after large ingestion
PRAGMA optimize;

-- WAL mode for better concurrency (Phase 2)
PRAGMA journal_mode = WAL;
```

### Indexing Performance

**Targets**:
- 100 documents/minute (mixed content)
- 1000 tweets/minute
- 10 PDFs/minute (with extraction)
- < 2 seconds per 300-page book

**Optimizations**:
- Batch processing (100-1000 at a time)
- Async embedding generation (Phase 2)
- Incremental updates (hash-based change detection)

### Search Performance

**Targets**:
- < 50ms for keyword queries (100k docs)
- < 100ms for filtered searches
- < 200ms for hybrid semantic + keyword (Phase 2)

**Optimizations**:
- Proper indexes on metadata columns
- Limit result sets (pagination)
- Cache common queries (if needed)

---

## Scaling Limits

### What SQLite Handles Well

**Document Count**:
- ✅ 10k documents: Instant
- ✅ 100k documents: Fast (<20ms)
- ✅ 1M documents: Usable (<100ms)
- ⚠️ 10M documents: Consider optimizations

**Database Size**:
- ✅ 1-100 GB: SQLite sweet spot
- ⚠️ 100-500 GB: Still works, monitor performance
- ❌ > 500 GB: Consider distributed approach (not personal use case)

**Content Size**:
- ✅ Short docs (<10k words): Store full text
- ✅ Medium docs (10k-100k words): Chunk + store
- ✅ Large docs (>100k words): Chunk + file reference
- ✅ Books library (1000 books): ~5 GB, excellent performance

### When to Consider Alternatives

**Triggers**:
- Search queries consistently > 500ms
- Database size > 100 GB
- Concurrent write conflicts (not expected for single-user)
- Need distributed access (Phase 3 home-server feature)

**Options at that scale**:
- PostgreSQL + pgvector (multi-device)
- Sharding by content type (unlikely needed)
- Dedicated vector DB (Chroma, Weaviate)

**Expected for personal use**: Never hit these limits

---

## Deployment Architecture

### Phase 1: Desktop Single-User

```
┌─────────────────────────┐
│   User's Desktop        │
│                         │
│  ┌──────────────────┐  │
│  │  Claude Desktop  │  │
│  │  (MCP Client)    │  │
│  └────────┬─────────┘  │
│           │ stdio       │
│           ↓             │
│  ┌──────────────────┐  │
│  │  proof-of-self   │  │
│  │  (MCP Server)    │  │
│  └────────┬─────────┘  │
│           │             │
│           ↓             │
│  ┌──────────────────┐  │
│  │  SQLite DB       │  │
│  │  + Files         │  │
│  └──────────────────┘  │
└─────────────────────────┘
```

**Characteristics**:
- Single Python process
- MCP over stdio
- Local-only
- Zero network exposure

### Phase 3+: Home Server Multi-Device (Future)

```
┌────────────────┐    ┌────────────────┐    ┌────────────────┐
│  Desktop       │    │  Laptop        │    │  Phone/Tablet  │
│  Claude Desktop│    │  Claude Code   │    │  Web Client    │
└───────┬────────┘    └───────┬────────┘    └───────┬────────┘
        │                     │                     │
        │ MCP (stdio)         │ MCP (HTTP)          │ HTTP API
        └─────────────────────┴─────────────────────┘
                              │
                              ↓
                ┌──────────────────────────┐
                │   Home Server            │
                │   (Raspberry Pi/NAS)     │
                │                          │
                │  ┌────────────────────┐ │
                │  │  proof-of-self     │ │
                │  │  (MCP + HTTP API)  │ │
                │  └──────────┬─────────┘ │
                │             ↓           │
                │  ┌────────────────────┐ │
                │  │  SQLite DB + Files │ │
                │  └────────────────────┘ │
                └──────────────────────────┘
                    Local network only
```

**Characteristics**:
- MCP server exposes HTTP transport
- REST API for mobile clients
- mDNS discovery (homeserver.local)
- Optional Tailscale for secure remote access
- SQLite WAL mode for concurrent reads
- Still privacy-first (no cloud)

---

## Security & Privacy

### Privacy Guarantees

1. **Local-only by default**
   - All data stays on user's machine
   - No external API calls for core functionality
   - No telemetry or analytics

2. **Optional features are opt-in**
   - If adding cloud embeddings (don't!), make it explicit
   - If adding sync, user controls it
   - Never surprise the user

3. **Audit trail**
   - Log all MCP tool calls (optional)
   - Track what was indexed when
   - User can review all activity

### Data Protection

1. **No secrets in database**
   - Redact phone numbers, emails, IPs if requested
   - Don't index credentials accidentally
   - Warn if indexing .env files

2. **File references, not copies**
   - Original files stay where user put them
   - Database points to files, doesn't duplicate
   - User controls file permissions

3. **Backups**
   - Single database file = easy backup
   - User can backup to encrypted storage
   - Document backup procedures

---

## Testing Strategy

### Unit Tests
- [ ] Database operations (CRUD)
- [ ] FTS5 search queries
- [ ] Chunking algorithms
- [ ] Each adapter's parsing logic
- [ ] Metadata extraction

### Integration Tests
- [ ] Full pipeline (add → index → search)
- [ ] Large document handling (300+ pages)
- [ ] Multiple content types together
- [ ] MCP tool responses

### Performance Tests
- [ ] 100k document indexing time
- [ ] Search latency benchmarks
- [ ] Database size growth
- [ ] Memory usage

### Real-World Tests
- [ ] Index 100+ diverse PDFs
- [ ] Index personal Twitter archive
- [ ] Index markdown notes collection
- [ ] Complex search queries
- [ ] Verify search quality

**Target**: 60% test coverage minimum before Phase 2

---

## Migration Path

### From Current Twitter-First to Universal

**Step 1: Schema Migration**
```sql
-- Add universal fields to existing tables
ALTER TABLE tweets ADD COLUMN universal_source_type TEXT DEFAULT 'twitter';
ALTER TABLE tweets ADD COLUMN universal_content_type TEXT DEFAULT 'tweet';

-- Create new documents table
CREATE TABLE documents (...);

-- Create migration script to copy tweets → documents
-- tweets.tweet_id → documents.id
-- tweets.text → documents.content
-- tweets.source = 'twitter'
```

**Step 2: Dual-Write Period**
- New content goes to `documents` table
- Old content stays in `tweets` table
- Search queries both tables
- Gradual migration script

**Step 3: Full Migration**
- All content in `documents`
- Old tables become views (backward compat)
- Update all code to use `documents`

**Step 4: Cleanup**
- Remove old tables (after verification)
- Remove Twitter-specific code
- Update documentation

---

## Decision Log

### Why SQLite over PostgreSQL?
**Decision**: Use SQLite
**Reasoning**: Personal scale (100k docs), zero config, local-only, proven performance
**Trade-off**: Less concurrency (acceptable for single-user)

### Why FTS5 over Vector Search?
**Decision**: FTS5 first, vector optional later
**Reasoning**: Keyword search works well for personal knowledge (you know what you wrote), simpler, faster
**Trade-off**: Less semantic understanding (can add later if needed)

### Why Hybrid Storage (DB + Files)?
**Decision**: Use both
**Reasoning**: DB for search/metadata, files for human-readability, best of both
**Trade-off**: Two systems to manage (acceptable complexity)

### Why Documents-First Schema?
**Decision**: Generic `documents` table
**Reasoning**: Universal architecture, Twitter just another source type
**Trade-off**: Refactoring work needed (worth it for long-term)

### Why MCP-First Interaction?
**Decision**: AI is the interface
**Reasoning**: Aligns with project vision, better UX ("talk to Claude" vs "run commands")
**Trade-off**: Requires AI assistant (acceptable for target users)

---

## Future Considerations

### Phase 2 Enhancements
- Semantic search (if keyword search insufficient)
- More adapters (ePub, email, web)
- Better metadata extraction
- Perspective analysis ("what do I think about X?")

### Phase 3 Advanced Features
- Knowledge graph (entity extraction, relationships)
- Temporal tracking (idea evolution over time)
- Visual explorer (graph visualization)
- Consolidation suggestions

### Phase 3+ Home Server
- Multi-device access (desktop, laptop, phone)
- Network API (MCP + HTTP)
- Concurrent access (SQLite WAL mode)
- Mobile apps for thought capture

---

## References

### Internal Documentation
- `PROJECT_VISION.md` - Overall vision and philosophy
- `ROADMAP.md` - Development phases and timeline
- `docs/archive/DEPRECATED.md` - What was deprecated and why

### External Resources
- [SQLite FTS5](https://www.sqlite.org/fts5.html) - Full-text search documentation
- [ChromaDB](https://docs.trychroma.com/) - Vector database (if implementing Phase 2)
- [sentence-transformers](https://www.sbert.net/) - Embedding models
- [PyMuPDF](https://pymupdf.readthedocs.io/) - PDF text extraction
- [MCP Specification](https://modelcontextprotocol.io/) - Model Context Protocol

---

**Last Updated**: November 16, 2025
**Next Review**: After Phase 1 completion

This architecture balances simplicity, performance, and future extensibility. It's designed for personal-scale knowledge management with privacy and user control as core values.
