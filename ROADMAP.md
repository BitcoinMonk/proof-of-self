# Proof-of-Self: Development Roadmap

**Version**: 1.0
**Last Updated**: November 16, 2025
**Status**: Active Roadmap

This roadmap outlines the development path for Proof-of-Self from current state to a mature, universal personal knowledge base.

---

## Vision

Build a **universal personal knowledge base** that:
- Works with ANY content type (Twitter, books, notes, PDFs, emails)
- Is accessible via MCP tools by any AI assistant
- Maintains privacy-first, local-only architecture
- Scales to 100k+ documents with excellent performance
- Eventually supports multi-device access (long-term)

---

## Current State (November 2025)

### What Works ✅
- SQLite + FTS5 full-text search
- Twitter archive adapter and indexing
- Basic MCP server infrastructure
- 8,349 tweets successfully indexed in test database

### What's Wrong ❌
- Architecture is Twitter-centric (65-70% of code)
- Database schema has tweets/bookmarks/likes as primary tables
- MCP tools are Twitter-specific
- CLI-focused instead of MCP-first
- Documentation emphasizes Twitter usage

### Decision Point
**Chosen approach**: Refactor first, then enhance

---

## Phase 1: Universal Foundation (2-3 Weeks)

**Goal**: Transform from Twitter-focused to truly universal architecture

**Priority**: CRITICAL - Must complete before adding features

### Week 1: Database & Schema Refactoring

**Tasks**:
1. **Create universal schema**
   - Implement `documents` table as primary store
   - Implement `chunks` table for large documents
   - Add FTS5 indexes for both tables
   - Add triggers for automatic index updates

2. **Migrate existing data**
   - Copy tweets → documents table
   - Mark old tables for deprecation
   - Verify data integrity

3. **Implement chunking system**
   - Semantic chunking algorithm (500-1000 tokens)
   - 10-20% overlap between chunks
   - Metadata preservation for chunks

**Deliverable**: Documents-first database schema working with test data

### Week 2: Universal MCP Tools

**Tasks**:
1. **Implement generic MCP tools**
   - `add_to_knowledge_base(path, metadata)` - Add any content
   - `search_knowledge_base(query, filters)` - Universal search
   - `save_to_knowledge_base(content, metadata)` - Save created content
   - `list_sources(filters)` - Browse indexed content
   - `get_content(id)` - Retrieve specific item

2. **Refactor adapters**
   - Ensure all adapters yield universal document format
   - Twitter adapter outputs standard documents
   - Test with diverse content types

3. **Deprecate Twitter-specific tools**
   - Mark `search_tweets()`, `find_thread()`, etc. as deprecated
   - Create thin wrappers pointing to universal tools
   - Add deprecation warnings

**Deliverable**: Generic MCP tools that work with any content type

### Week 3: PDF Support & Testing

**Tasks**:
1. **Implement PDF adapter**
   - PyMuPDF for text extraction
   - Metadata extraction (title, author, pages)
   - Page-level chunking for large books

2. **Complete rebrand**
   - Rename all "proof-of-monk" → "proof-of-self" in code
   - Update package name in pyproject.toml
   - Update all imports and references

3. **Testing at scale**
   - Index 100+ PDFs (books, papers)
   - Index 10k+ tweets
   - Verify search works across all content
   - Measure performance (search < 50ms target)

4. **Minimal CLI**
   - Keep: `proof-of-self init`, `stats`, `serve`
   - Remove: `index --twitter-archive`, `index-inbox`
   - Update help text for MCP-first usage

**Deliverable**: Working universal knowledge base you can USE

---

## Phase 2: Real-World Testing & Iteration (1-2 Months)

**Goal**: Use it daily, refine based on actual needs

**Priority**: HIGH - Learn what actually matters

### Month 1: Daily Use & Content Diversity

**Activities**:
1. **Add diverse content**
   - Index personal Twitter archive
   - Index 100+ books (fiction, non-fiction, technical)
   - Index personal notes (markdown files)
   - Index research papers (PDFs)

2. **Use with Claude daily**
   - "Claude, add this PDF"
   - "What did I write about X?"
   - "Help me draft Y based on my knowledge"
   - "Save this draft to my knowledge base"

3. **Identify pain points**
   - Where does search fail?
   - What queries don't work well?
   - What features are missing?
   - What's confusing or frustrating?

**Deliverable**: Real-world usage insights + pain points documented

### Month 2: More Adapters & Refinements

**Tasks**:
1. **Implement ePub adapter**
   - ebooklib for extraction
   - Chapter structure preservation
   - Metadata (author, title, publisher)

2. **Implement email adapter** (if needed)
   - mbox/maildir parsing
   - Thread reconstruction
   - Subject/sender indexing

3. **Implement web bookmark adapter** (if needed)
   - Browser export formats
   - Pocket export
   - Archive web pages with content

4. **Refine search**
   - Improve ranking based on usage
   - Add metadata filtering
   - Optimize query performance

5. **Improve metadata extraction**
   - Better PDF metadata detection
   - Frontmatter parsing for markdown
   - Automatic tagging suggestions

**Deliverable**: Multiple content types working well, refined based on experience

---

## Phase 3: Advanced Features (3-6 Months)

**Goal**: Add sophisticated features that demonstrably add value

**Priority**: MEDIUM - Only if Phase 2 proves the foundation

### Enhancement 1: Semantic Search (Optional)

**When**: Only if keyword search proves insufficient

**Tasks**:
1. **Set up ChromaDB**
   - Local vector database
   - all-MiniLM-L6-v2 embeddings (22MB model)
   - Generate embeddings for all content

2. **Implement hybrid search**
   - Combine FTS5 (keyword) + ChromaDB (semantic)
   - Reciprocal Rank Fusion for result merging
   - A/B test vs keyword-only

3. **Add semantic tools**
   - `find_similar(content_id)` - Find related content
   - `explore_topic(topic)` - Semantic topic exploration
   - Toggle semantic search on/off

**Decision Criteria**:
- [ ] Keyword search frequently misses relevant content
- [ ] Users search with vague/conceptual queries
- [ ] "Find similar" adds clear value
- [ ] Willing to accept 2x storage + indexing time

**Deliverable**: Hybrid search that measurably improves results

### Enhancement 2: Knowledge Graph (Ambitious)

**When**: Only if core system is rock-solid and semantic search exists

**Tasks**:
1. **Entity extraction**
   - Extract people, concepts, places from content
   - Store in graph structure (NetworkX + SQLite)
   - Build relationship edges (mentions, relates-to, part-of)

2. **Graph navigation**
   - `explore_connections(entity)` - See all related content
   - `trace_idea(keyword, timeline)` - Track concept evolution
   - `suggest_consolidation()` - Find clusters worth organizing

3. **Visualization** (optional)
   - D3.js interactive graph
   - Export to Obsidian graph format
   - Timeline view of ideas

**Deliverable**: Discover forgotten connections across all knowledge

### Enhancement 3: Perspective Extraction

**When**: After significant content indexed (10k+ items)

**Tasks**:
1. **Analyze writings by topic**
   - Identify recurring themes
   - Extract your positions/viewpoints
   - Summarize consistent arguments

2. **Perspective tools**
   - `get_perspective(topic)` - "What do you think about X?"
   - `track_evolution(topic, timeline)` - "How has your view changed?"
   - `find_contradictions(topic)` - "Where do you disagree with past self?"

**Deliverable**: AI understands YOUR perspectives and can reference them

---

## Phase 4: Multi-Device / Home Server (Long-Term Vision)

**Goal**: Access knowledge base from any device on local network

**Priority**: LOW - Nice to have, not essential

**When**: After Phase 3, if single-device limitations become pain point

### Architecture Changes

**Add**:
- HTTP API alongside MCP
- Network transport for MCP protocol
- Mobile-friendly web interface
- REST endpoints for thought capture
- WebSocket for real-time updates

**Maintain**:
- Privacy-first (local network only)
- Optional Tailscale for secure remote
- SQLite WAL mode for concurrent access
- No cloud requirements

### Deployment Options

**Option 1: Desktop as Server**
- Current desktop runs MCP + HTTP server
- Other devices connect on local network
- mDNS discovery (proof-of-self.local)

**Option 2: Dedicated Home Server**
- Raspberry Pi / NAS / mini PC
- Always-on service
- 24/7 accessibility within home

**Option 3: Hybrid**
- Desktop for development/heavy use
- Server for always-on mobile access
- Sync between instances

**Deliverable**: Multi-device access while maintaining privacy

---

## Feature Decision Matrix

### Implement Next If...

**Semantic Search**:
- ✅ Core keyword search working perfectly
- ✅ 10k+ documents indexed
- ✅ Common queries: "I know I thought about X somewhere"
- ✅ Willing to accept complexity increase

**Knowledge Graph**:
- ✅ Semantic search implemented and valuable
- ✅ Frequently need "show me everything about X"
- ✅ Want to discover forgotten connections
- ✅ Enjoy data visualization

**Multi-Device**:
- ✅ Using from multiple locations daily
- ✅ Want mobile thought capture
- ✅ Comfortable with home server setup
- ✅ Privacy maintained (local network)

### Don't Implement If...

**Semantic Search**:
- ❌ Keyword search works fine for your use cases
- ❌ < 1,000 documents indexed
- ❌ Don't want 2x storage overhead
- ❌ Want to keep system simple

**Knowledge Graph**:
- ❌ Semantic search doesn't add value
- ❌ Don't need entity-based navigation
- ❌ Prefer simple search interface
- ❌ Want to minimize complexity

**Multi-Device**:
- ❌ Single device works fine
- ❌ Don't want home server complexity
- ❌ Privacy concerns about network exposure
- ❌ Prefer desktop-only for focus

---

## Success Metrics

### Phase 1 Success Criteria

- [ ] Database schema is documents-first
- [ ] Universal MCP tools implemented
- [ ] Twitter is just another source_type
- [ ] Can index and search PDFs
- [ ] Search < 50ms for 100k documents
- [ ] Complete "proof-of-self" rebrand
- [ ] All documentation consistent
- [ ] Test coverage > 60%

### Phase 2 Success Criteria

- [ ] Using daily for 2+ months
- [ ] 100+ books indexed
- [ ] 10k+ various documents indexed
- [ ] Search quality meets needs
- [ ] No major pain points
- [ ] At least 3 content types in use
- [ ] Performance acceptable

### Phase 3 Success Criteria (Optional)

- [ ] Semantic search adds measurable value
- [ ] Knowledge graph reveals insights
- [ ] Perspective extraction accurate
- [ ] Advanced features used regularly
- [ ] Still maintains privacy
- [ ] Performance remains good

### Phase 4 Success Criteria (Future)

- [ ] Accessible from 3+ devices
- [ ] Mobile capture working well
- [ ] No privacy compromises
- [ ] Concurrent access works
- [ ] Still feels like "your" system

---

## Timeline Estimates

**Phase 1: Universal Foundation**
- Weeks 1-3: Implementation
- Week 4: Buffer for issues
- **Total**: 3-4 weeks

**Phase 2: Real-World Testing**
- Month 1: Daily use + content diversity
- Month 2: More adapters + refinements
- **Total**: 2 months

**Phase 3: Advanced Features**
- Semantic search: 3-4 weeks
- Knowledge graph: 4-6 weeks
- Perspective extraction: 2-3 weeks
- **Total**: 3-4 months (if doing all)

**Phase 4: Multi-Device**
- Architecture changes: 2-3 weeks
- Mobile interface: 4-6 weeks
- Testing + refinement: 2 weeks
- **Total**: 2-3 months

**Overall to Phase 3**: 6-8 months of focused work

---

## Not On Roadmap

Things we're explicitly NOT doing:

### ❌ Cloud Services
- No cloud sync
- No cloud embeddings
- No external APIs for core features
- Maintain 100% local-only

### ❌ Social Features
- No sharing
- No collaborative editing
- No multi-user (except multi-device same user)
- This is personal knowledge, not social

### ❌ AI Generation Features
- No auto-summarization (AI assistant does this)
- No auto-tagging (keep user-directed)
- No predictive features
- AI helps via MCP, not baked in

### ❌ Complex Configuration
- No YAML config files
- No complex settings
- Simple environment variables only
- Sensible defaults everywhere

### ❌ Enterprise Features
- No multi-tenancy
- No role-based access control
- No audit logs (beyond basic activity tracking)
- Not building for organizations

---

## Pivot Points

Points where we might change direction:

**After Phase 1**:
- If refactoring breaks too much → rollback and iterate
- If universal architecture too complex → simplify
- If performance degrades → optimize before proceeding

**After Phase 2**:
- If keyword search perfect → skip semantic search
- If content types insufficient → add more adapters
- If usage patterns unexpected → adjust Phase 3 priorities

**During Phase 3**:
- If semantic search doesn't help → deprecate it
- If knowledge graph not valuable → skip it
- If simple system preferred → stop at Phase 2

**Key Principle**: Only add complexity if it demonstrably adds value

---

## Contributing

**Phase 1-2**: Not accepting contributions (foundational work)

**Phase 3+**: May open for contributions
- New adapters (email, chat logs, etc.)
- UI improvements
- Documentation
- Bug fixes
- Performance optimizations

See `CONTRIBUTING.md` for guidelines when we're ready.

---

## Communication

### Roadmap Updates
- Review after each phase completion
- Update based on learnings
- Maintain single source of truth
- Archive old roadmaps (no conflicting versions)

### Decision Documentation
- Major decisions → update ARCHITECTURE.md
- Pivots → update this roadmap
- Deprecated features → update docs/archive/DEPRECATED.md
- Keep history for context

---

## References

- **ARCHITECTURE.md** - Technical architecture and decisions
- **PROJECT_VISION.md** - Overall vision and philosophy
- **docs/archive/DEPRECATED.md** - What was deprecated and why
- **CHANGELOG.md** - Version history

---

**This roadmap is a living document.** It will evolve as we build and learn. The key is maintaining a clear, single source of truth for where the project is headed.

**Current Status**: Beginning Phase 1 (Universal Foundation)

**Next Milestone**: Complete documents-first refactoring (Week 1)

---

*Last updated: November 16, 2025*
