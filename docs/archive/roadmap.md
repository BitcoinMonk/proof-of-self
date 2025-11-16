# Proof-of-Monk Development Roadmap

**Vision**: Building "Proof-of-Self" - A privacy-first personal AI consciousness that absorbs all your intellectual work and discovers connections across everything you think about.

This document outlines the technical plan for building Proof-of-Monk, from MVP to generalized "Proof-of-Self."

---

## Architecture Overview

```
┌─────────────────────────────────────────┐
│    proof-of-monk (Personal AI Agent)    │
└─────────────────────────────────────────┘
            │
            ├─── Consciousness Directory
            │    ├─ streams/ (daily raw thoughts)
            │    ├─ memory/ (consolidated topics)
            │    ├─ knowledge/ (external sources)
            │    └─ artifacts/ (published work)
            │
            ├─── Data Adapters (pluggable)
            │    ├─ Twitter Archive (Phase 1 ✅)
            │    ├─ Markdown files (Phase 2)
            │    ├─ PDFs & Documents (Phase 2)
            │    └─ [Future: Email, Chat logs, etc.]
            │
            ├─── Hybrid Storage
            │    ├─ SQLite Database
            │    │  ├─ Structured data & metadata
            │    │  ├─ Full-text search (FTS5)
            │    │  └─ Vector embeddings (Phase 2)
            │    └─ Filesystem
            │       ├─ Long-form content
            │       └─ Human-readable files
            │
            ├─── Search & Discovery
            │    ├─ Keyword search (FTS5) ✅
            │    ├─ Semantic search (Phase 2)
            │    └─ Knowledge graph (Phase 3)
            │
            └─── MCP Server
                 ├─ Generic search/query tools
                 ├─ Consciousness stream tools
                 └─ Privacy-first, model-agnostic
```

---

## Phase 1: MVP - Twitter as Test Data Source ✅ COMPLETE

**Goal**: Prove the concept works with one data source (Twitter archives).

**Status**: Complete (November 2025)

### What We Built

**Core Infrastructure:**
- SQLite + FTS5 full-text search
- Twitter adapter (tweets, bookmarks, likes)
- 7 MCP tools for Claude integration
- CLI for indexing and stats
- Successfully indexed 8,349+ tweets

**Key Insight**: Twitter archives work great as test data because they're:
- Structured and timestamped
- Representative of intellectual output
- Easy to export from Twitter
- Rich with engagement metadata

**Architecture Decision**: Hybrid database + files approach validated:
- Database excellent for queries, metadata, relationships
- Files better for long-form, human-readable content
- Both needed for "consciousness directory" concept

---

## Phase 1.5: Consciousness Streams 🚧 IN PROGRESS

**Goal**: Add file-based thought capture that grows continuously. Make it easy to dump ANY content into your consciousness.

**Timeline**: Late November 2025 (2-3 hours)

### The "Consciousness Directory" Concept

Mirrors natural thought flow:

```
~/.local/share/proof-of-monk/consciousness/
├── streams/          # Daily raw thoughts (date-based markdown)
│   ├── 2025/
│   │   └── 11/
│   │       ├── 15-stream.md    # Today's thoughts
│   │       └── 15-meta.json    # Tags, timestamps
│   └── .index/       # Hash-based change detection
│
├── memory/           # Consolidated topic files
│   ├── bitcoin/
│   │   ├── mining.md
│   │   └── datum.md
│   ├── drafts/       # Article drafts
│   └── ideas/        # Seeds for future work
│
├── knowledge/        # External data sources
│   ├── twitter-archive/    # Imported Twitter data
│   ├── bookmarks/          # Saved articles
│   └── research/           # Papers, PDFs
│
└── artifacts/        # Published outputs
    ├── articles/
    └── threads/
```

### What We're Building

**1. Database Extensions**:
```sql
ALTER TABLE thoughts ADD COLUMN file_path TEXT;
ALTER TABLE thoughts ADD COLUMN content_type TEXT;  -- 'short'|'long'|'stream'
ALTER TABLE thoughts ADD COLUMN source_type TEXT;   -- 'thought'|'tweet'|'article'|'research'
```

**2. New Module**: `src/proof_of_monk/core/consciousness.py`
```python
class ConsciousnessStream:
    """Manages daily thought streams and file-based knowledge capture"""

    def stream_entry(content, tags):
        """Append to today's stream file + index in DB"""

    def save_research(content, title, source_url):
        """Save research article to knowledge/research/"""

    def create_memory(topic, content):
        """Create consolidated topic file in memory/"""
```

**3. New MCP Tools**:
- `stream_thought(content, tags)` - Dump anything to today's stream
- `save_research(title, content, url)` - Save articles/papers to research folder
- `search_consciousness(query, date_range)` - Search across all consciousness
- `list_streams(date_range)` - Browse daily streams

**4. Smart Routing**:
- Short content (<1000 chars) → database only
- Long content (>1000 chars) → file + database reference
- Daily stream entries → markdown file + indexed entries

### Use Case Example

```
You: "I want to research this Ocean TIDES mining article"
[Saves to consciousness/knowledge/research/ocean-tides-mining.md]

You: "Find my tweets about mining centralization"
[Searches Twitter archive + today's research notes]
Returns: 5 tweets + "By the way, here's that TIDES article you saved today"

You: "I want to write about solo mining with DATUM"
[Creates consciousness/memory/drafts/datum-solo-mining.md]
[Agent suggests: "Your tweets about pool centralization and today's TIDES research are relevant"]
```

### Deliverable

- Can dump thoughts/research to files with one command
- Files automatically indexed and searchable
- Search works across database AND files seamlessly
- Twitter remains accessible as first knowledge source
- Foundation ready for Phase 2 (semantic search)

---

## Phase 2: Semantic Search & RAG Architecture

**Goal**: Add vector embeddings for "I know I thought about this somewhere" discovery.

**Timeline**: January 2026 (3-4 weeks)

### Week 1: SQLite-Vec Integration

**Add Vector Search to SQLite**:
```sql
-- New tables for embeddings
CREATE TABLE IF NOT EXISTS content_embeddings (
    content_id TEXT PRIMARY KEY,
    content_type TEXT,  -- 'tweet'|'thought'|'article'|'research'
    embedding BLOB,     -- 384-dim vector (all-MiniLM-L6-v2)
    model_version TEXT,
    created_at TIMESTAMP
);

CREATE INDEX idx_embeddings_type ON content_embeddings(content_type);
```

**Install SQLite-Vec**:
- Lightweight vector search extension
- ~100KB binary, runs everywhere
- Seamless SQLite integration
- Handles 100k+ vectors easily

### Week 2: Embedding Generation

**Local Embedding Model**:
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
# 384 dimensions, 80MB, fast on CPU
```

**Or Lighter Alternative**:
```python
from fastembed import TextEmbedding
model = TextEmbedding("sentence-transformers/all-MiniLM-L6-v2")
# ONNX runtime, no PyTorch dependency
```

**Generate Embeddings For**:
- All existing tweets
- All thoughts and stream entries
- All research articles
- All drafts and published work

**Background Service**:
- Async embedding generation (non-blocking)
- Hash-based change detection (only re-embed if changed)
- Incremental updates (no full reindexing)

### Week 3: Hybrid Search Implementation

**Combine FTS5 + Vector Similarity**:
```python
def hybrid_search(query, search_type='hybrid'):
    results = []

    if search_type in ['keyword', 'hybrid']:
        # FTS5 keyword search
        keyword_results = db.fts_search(query)
        results.extend(keyword_results)

    if search_type in ['semantic', 'hybrid']:
        # Vector similarity search
        query_embedding = model.encode(query)
        semantic_results = db.vector_search(query_embedding)
        results.extend(semantic_results)

    # RRF (Reciprocal Rank Fusion) for ranking
    return rank_fusion(results)
```

**New MCP Tools**:
- `find_connections(query)` - Semantic search across ALL data types
- `find_similar(content_id, content_type)` - "Show me similar thoughts/tweets"
- `explore_topic(topic)` - Timeline view of everything about a topic

### Week 4: Optimization & Polish

**Performance**:
- Benchmark hybrid search (<200ms target)
- Optimize vector similarity queries
- Add result caching
- Parallel embedding generation

**User Experience**:
- Progress indicators for embedding generation
- "Indexing..." status in search results
- Suggestion system ("Did you mean...?")

### Deliverable

RAG-style discovery:
- "I know I thought about this somewhere" → finds it semantically
- "What else did I say related to X?" → discovers forgotten connections
- "Show me everything about Y" → tweets + thoughts + research + drafts
- Works 100% locally, no cloud services required

---

## Phase 3: Knowledge Graph & Advanced Discovery

**Goal**: Entity extraction, relationship mapping, automated consolidation.

**Timeline**: Q1 2026 (4-6 weeks)

### Entity Extraction

**Extract From All Content**:
```python
# Using spaCy (local NER) or embeddings
entities = extract_entities(content)
# Returns: ["DATUM", "mining", "Ocean pool", "TIDES", "FPPS"]

# Store in graph
graph.add_entity(entity, entity_type, source_content_id)
graph.add_relationship(entity1, entity2, relationship_type)
```

**Knowledge Graph Storage**:
```sql
CREATE TABLE knowledge_graph_nodes (
    id INTEGER PRIMARY KEY,
    entity TEXT UNIQUE,
    entity_type TEXT,  -- 'concept'|'person'|'project'|'technology'
    first_mentioned TIMESTAMP,
    mention_count INTEGER
);

CREATE TABLE knowledge_graph_edges (
    from_entity TEXT,
    to_entity TEXT,
    relationship TEXT,  -- 'relates_to'|'part_of'|'builds_on'
    strength REAL,      -- Based on co-occurrence
    FOREIGN KEY (from_entity) REFERENCES knowledge_graph_nodes(entity),
    FOREIGN KEY (to_entity) REFERENCES knowledge_graph_nodes(entity)
);
```

### Graph-Based Discovery

**New MCP Tools**:
```python
@server.call_tool()
async def explore_connections(entity: str):
    """Show all content connected to this concept"""
    # Returns tweets, thoughts, articles mentioning entity
    # Plus: related entities, timeline, connection strength

@server.call_tool()
async def trace_idea(keyword: str, start_date: str):
    """Timeline of your thinking about a concept"""
    # Chronological view:
    # 2024-03: First tweet about X
    # 2024-05: Research article saved
    # 2024-07: Thread expanding on X
    # 2024-09: Article published

@server.call_tool()
async def suggest_consolidation():
    """Analyze recent streams and suggest memory files"""
    # "You've written 15 entries about 'mining centralization'
    #  in the past week. Create a memory file?"
```

### Automated Consolidation

**Stream → Memory Workflow**:
```python
class ConsolidationService:
    async def analyze_streams(days=7):
        """Find clusters in recent streams"""
        entries = get_recent_stream_entries(days)

        # Cluster by semantic similarity
        clusters = cluster_embeddings(entries)

        # Suggest memory file for each cluster
        for cluster in clusters:
            suggest_memory_file(
                topic=cluster.main_topic,
                entries=cluster.entries,
                path=f"memory/topics/{cluster.main_topic}.md"
            )
```

### Visualization & Export

**Graph Visualization**:
- Export to Obsidian format (markdown with WikiLinks)
- Export to Roam Research format
- D3.js interactive graph (optional web UI)

**Timeline View**:
- "Evolution of your thinking on X"
- Chronological display across all data sources
- Highlight key moments (viral tweets, published articles)

### Deliverable

**The Full "Proof-of-Self" Vision**:
- Agent knows everything you've ever thought about
- Discovers connections you forgot
- Suggests consolidations ("You should write about this")
- Traces idea evolution over time
- Works across ALL data sources (not just Twitter)
- 100% private, local-only, you own everything

---

## Technical Decisions

### Why Hybrid Database + Files?

**SQLite Strengths**:
- Fast queries and relationships
- ACID transactions
- FTS5 full-text search
- Handles structured metadata beautifully
- Works with 8,000+ tweets easily

**File System Strengths**:
- Human-readable (markdown, text)
- Version control friendly (git)
- Direct editing in any editor
- Portable backups
- Natural for long-form content

**Integration**: Database indexes files via `file_path` column. Best of both worlds.

### Why SQLite-Vec? (not FAISS or Chroma)

- Seamless SQLite integration (one database file)
- 100KB binary size (tiny)
- Runs everywhere (Linux/Mac/Windows/WASM)
- Single-file portability
- Sufficient for personal use (100k+ vectors)
- No separate vector database to manage

### Why all-MiniLM-L6-v2?

- Industry standard embedding model
- 384 dimensions (good balance)
- 80MB model size (small)
- Fast on CPU (~50ms per encoding)
- Well-supported in sentence-transformers
- Proven track record for semantic search

### Why Local-Only Embeddings?

- Privacy first - data never leaves your machine
- No API costs or rate limits
- Works offline
- Full ownership of your AI
- Auditable and transparent

### Why MCP?

- Standard protocol from Anthropic
- Works with Claude Desktop/Code out of the box
- Extensible to other AI assistants
- Tool-based architecture is clean
- Keeps data local (no cloud required)

---

## Key Principles

1. **Privacy First**: Data never leaves your machine unless you explicitly choose
2. **Continuous Growth**: Each session adds knowledge, no full rebuilds
3. **Extensibility**: Easy to add new data sources via adapters
4. **Local-First**: Embeddings, search, everything runs locally
5. **Transparency**: Open source, auditable, no black boxes
6. **Ownership**: Your data, your AI, your rules

---

## Success Metrics

**Phase 1 Success** ✅:
- ✅ Indexed 8,349+ tweets in < 1 minute
- ✅ Search returns results in < 100ms
- ✅ Works with Claude Code
- ✅ Other people can install and use it

**Phase 1.5 Success**:
- Can dump thoughts to files with one command
- Files automatically indexed and searchable
- Hybrid search works across DB + files
- Foundation ready for semantic search

**Phase 2 Success**:
- Semantic search returns relevant results (no keyword match needed)
- "I know I thought about this" queries work
- Hybrid search outperforms pure keyword
- Works with 10,000+ items (tweets + thoughts + research)

**Phase 3 Success**:
- Knowledge graph connects related concepts
- Consolidation suggestions >70% useful
- Timeline shows evolution of thinking
- Exports work with Obsidian/Roam
- "Proof-of-Self" vision fully realized

---

## Timeline

- **Phase 1 MVP**: ✅ Complete (November 2025)
- **Phase 1.5 Consciousness Streams**: Late November 2025 (2-3 hours)
- **Phase 2 Semantic Search**: January 2026 (3-4 weeks)
- **Phase 3 Knowledge Graph**: Q1 2026 (4-6 weeks)
- **Community Growth**: Ongoing (2026+)

---

## Future Data Source Adapters (Phase 2+)

**High Priority**:
- Markdown files / Obsidian vaults
- PDF documents
- Web bookmarks (HTML, Pocket exports)
- Voice notes (transcription + indexing)

**Medium Priority**:
- Email archives (mbox, maildir)
- Chat logs (Signal, Telegram exports)
- Code repositories (git commits, comments)
- Meeting notes (calendar + notes integration)

**Experimental**:
- Browser history
- Location data (with privacy controls)
- Health/fitness data
- Financial data (extremely careful with privacy)

---

## Similar Projects & Inspiration

- [Obsidian](https://obsidian.md/) - Local-first notes, excellent but not AI-native
- [Mem.ai](https://mem.ai/) - Similar concept, but cloud-based and closed
- [Notion AI](https://www.notion.so/product/ai) - Cloud, not privacy-first
- [Logseq](https://logseq.com/) - Knowledge graph, local-first
- [MCP Servers](https://github.com/modelcontextprotocol/servers) - Official examples
- [Simon Willison's Datasette](https://datasette.io/) - Data exploration philosophy

---

## Getting Involved

**For Users**:
1. ⭐ Star the repo
2. Try it with your Twitter archive (Phase 1)
3. Report issues and share feedback
4. Request features you want

**For Contributors** (opening in Phase 2):
1. Write new data source adapters
2. Improve search algorithms
3. Build visualization tools
4. Write documentation and guides
5. Help others in discussions

---

**This roadmap is a living document. It will evolve as we build and learn.**

Last updated: 2025-11-15
