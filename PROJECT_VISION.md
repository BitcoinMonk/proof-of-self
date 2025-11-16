# Proof-of-Self: Project Vision

**Version**: 1.0
**Last Updated**: November 16, 2025
**Status**: Definitive Vision

## What This Is

**Proof-of-Self** is your personal AI memory system. It gives AI assistants (Claude, GPT, etc.) access to YOUR knowledge - your writings, your books, your research, your thoughts - so they can help you think and create in YOUR voice.

## The Core Idea

You don't interact with this tool directly. **You talk to your AI, and your AI talks to Proof-of-Self.**

```
You → AI Assistant → Proof-of-Self Knowledge Base
```

Your AI becomes an extension of your memory and perspective, informed by everything you've read, written, and thought about.

## How It Works

### Example Workflow

```
You: "Claude, I just downloaded my Twitter archive. Add it to my proof-of-self."

Claude: [Uses MCP to add archive to knowledge base]
        "Done. I've indexed 5,000 tweets from 2018-2024.
         I can now search your past thoughts on any topic."

---

You: "Someone posted about a protocol called 'Koltur' for Bitcoin.
      What have I said about arbitrary data on Bitcoin?"

Claude: [Searches your knowledge base via MCP]
        "You've written 12 tweets on this. Your consistent view:
         - Skeptical of blockchain bloat
         - Prefer layer-2 solutions for data
         - Cited the inscriptions debate in 2023

         Want me to research Koltur and help draft a response?"

You: "Yes, draft something in my style."

Claude: [Researches Koltur]
        [Drafts response using your known perspective]

        "Here's a draft:
        'Koltur's approach raises the same concerns I had with
         inscriptions. L2 solutions better preserve Bitcoin's core
         value. We shouldn't trade decentralization for features.'

         Sound like you?"

You: "Perfect. Save this as a draft in my knowledge base."

Claude: [Saves draft to knowledge base via MCP]
        "Saved with tags: bitcoin, koltur, draft."
```

## This Is NOT

### Not a Content Creation Tool
- **You don't write in Proof-of-Self**
- You write in your AI chat
- Obsidian/Notion are where you actively write and organize
- Proof-of-Self is where your AI reads from and saves to

### Not a Twitter Tool
- Twitter is just ONE possible data source
- You could just as easily index:
  - Your library of books (PDFs, ePubs)
  - Your research papers
  - Your blog posts
  - Your personal notes
  - Your email archive
  - Anything that represents YOUR knowledge

### Not Cloud-Based
- All data stays on your machine
- Never sent to external services
- You control what gets indexed
- Privacy-first, always

## The Real Use Cases

### The Writer
```
You: "Add my library of writing craft books."
AI: [Indexes PDFs]

You: "What does Stephen King say about dialogue?"
AI: [Searches your indexed books]
    "From 'On Writing', page 127: 'The key to good dialogue
     is to strip away everything except the essential...'"

You: "Help me improve this scene's dialogue."
AI: [Uses King's advice to help you revise]
```

### The Researcher
```
You: "Add all my conference papers from 2020-2024."
AI: [Indexes PDFs]

You: "Find papers where I discussed neural networks and ethics."
AI: [Searches across all your papers]
    "Found 3 papers. Your main argument: algorithmic
     transparency is crucial for accountability..."

You: "I'm writing a grant proposal on AI ethics. Draft an intro."
AI: [Drafts using your past research as context]
```

### The Thinker (Any Domain)
```
You: "Add my notes on philosophy."
AI: [Indexes markdown files]

You: "What have I written about free will?"
AI: [Searches your notes]
    "You've explored compatibilism in 8 notes, often
     referencing Dennett's arguments..."

You: "I want to write an essay. Help me outline my thoughts."
AI: [Creates outline using your existing ideas]
```

## The Architecture

```
┌─────────────────────────────────────────┐
│  Your Personal Data                     │
│  • Twitter archives                     │
│  • Books (PDF, ePub)                    │
│  • Notes (Markdown, text)               │
│  • Research papers                      │
│  • Blog posts                           │
│  • Anything you've read/written         │
└──────────────┬──────────────────────────┘
               │
               │ "Add this to my knowledge base"
               ↓
┌─────────────────────────────────────────┐
│  Proof-of-Self Knowledge Base           │
│  • Local SQLite database                │
│  • Full-text search indexing            │
│  • Unified document storage             │
│  • NO user interface                    │
└──────────────┬──────────────────────────┘
               │
               │ MCP Protocol (tool calls)
               ↓
┌─────────────────────────────────────────┐
│  AI Agent (Claude, GPT, etc.)           │
│  • Your actual interface                │
│  • Searches knowledge base              │
│  • Understands YOUR perspectives        │
│  • Helps create in YOUR voice           │
└──────────────┬──────────────────────────┘
               │
               │ Natural conversation
               ↓
┌─────────────────────────────────────────┐
│  You                                    │
│  • Talk naturally to AI                 │
│  • AI has access to your knowledge      │
│  • Create content collaboratively       │
│  • Save what matters back to KB         │
└─────────────────────────────────────────┘
```

## MCP Tools (AI's Interface to Your Knowledge)

Your AI assistant uses these tools (you don't call them directly):

### Core Tools

```python
# Ingestion (AI adds data when you ask)
add_to_knowledge_base(path: str, source_type: str) → status
# User: "Add my Twitter archive"
# User: "Add this PDF"
# User: "Add all my notes in ~/Documents/research/"

# Search (AI finds relevant content)
search_knowledge_base(
    query: str,
    source_type: Optional[str],  # Filter: "twitter", "pdf", "note"
    date_range: Optional[tuple],
    limit: int
) → list[results]
# AI searches when you ask about a topic

# Save new content (after creating together)
save_to_knowledge_base(
    content: str,
    title: str,
    tags: list[str],
    category: str  # "draft", "idea", "response"
) → id
# User: "Save this draft to my knowledge base"

# List what's indexed (for user awareness)
list_knowledge_base(
    source_type: Optional[str],
    limit: int
) → list[items]
# User: "What's in my knowledge base?"

# Remove content (user control)
remove_from_knowledge_base(id: str) → status
# User: "Remove my Twitter data"
```

### Future Advanced Tools (Phase 2+)

```python
# Perspective extraction
extract_perspective(topic: str) → summary
# Analyzes your writings on a topic
# Summarizes your consistent viewpoints

# Similarity search
find_similar(content_id: str, limit: int) → list[results]
# "Find content similar to this essay"

# Cross-reference
find_connections(concept: str) → graph
# "How have my thoughts on X evolved?"
```

## Data Storage (Answering Your Question)

### How Content Is Stored

Every piece of content gets a unique ID based on its content + source:

```python
# Example: Twitter tweet
{
  "id": "a3f9c2b1...",  # SHA256 hash of content+source
  "source_type": "twitter",
  "content_type": "tweet",
  "title": None,
  "content": "Bitcoin is digital scarcity...",
  "metadata": {
    "tweet_id": "123456",
    "created_at": "2023-05-15",
    "likes": 42,
    ...
  },
  "tags": ["bitcoin", "economics"],
  "indexed_at": "2024-11-16"
}

# Example: Book excerpt
{
  "id": "d7e2a1c4...",
  "source_type": "file",
  "content_type": "pdf",
  "title": "On Writing by Stephen King",
  "content": "The key to good dialogue is...",
  "metadata": {
    "file_path": "~/Books/on-writing.pdf",
    "page": 127,
    "author": "Stephen King",
    ...
  },
  "tags": ["writing", "craft", "dialogue"],
  "indexed_at": "2024-11-16"
}

# Example: New draft you created with AI
{
  "id": "f1b4c8e2...",
  "source_type": "user",
  "content_type": "draft",
  "title": "Response to Koltur Protocol",
  "content": "Koltur's approach raises...",
  "metadata": {
    "created_with": "claude",
    "related_to": ["a3f9c2b1..."],  # Links to tweets
    ...
  },
  "tags": ["bitcoin", "koltur", "draft"],
  "indexed_at": "2024-11-16"
}
```

### Deduplication Strategy

**If you add the same content twice:**

1. **Exact duplicate detected** (same hash)
   - AI: "This content is already in your knowledge base."
   - Option: Update metadata (add new tags, update dates)
   - Prevents clutter

2. **Similar but not identical** (different hash)
   - Gets its own entry
   - Could be a revision or different version
   - Both searchable

3. **Re-indexing a source** (like Twitter archive)
   - Skip content that's already there
   - Add only new content since last index
   - AI: "Added 150 new tweets since last update."

## Development Approach

**Current Phase: Universal Foundation (2-3 weeks)**

We're refactoring from Twitter-focused to truly universal architecture:

### Phase 1: Universal Foundation
**Goal**: Working generic knowledge base

- Refactor database to documents-first (Twitter just another source)
- Implement universal MCP tools
- Add PDF support with chunking
- Complete rebrand to Proof-of-Self
- Test with diverse content types

### Phase 2: Real-World Testing (1-2 months)
**Goal**: Use it daily, learn what matters

- Index diverse content (books, notes, archives)
- Daily usage with Claude
- More adapters (ePub, email, web)
- Refine based on actual needs
- Iterate on search quality

### Phase 3: Advanced Features (3-6 months, optional)
**Goal**: Add sophistication only if needed

- **Semantic search** (if keyword search insufficient)
  - Local embeddings (all-MiniLM-L6-v2)
  - Hybrid keyword + semantic search
  - "Find similar" functionality

- **Knowledge graph** (if valuable)
  - Entity extraction
  - Relationship discovery
  - Idea evolution tracking

- **Perspective extraction** (if useful)
  - Analyze your viewpoints on topics
  - Track opinion changes over time
  - Help AI understand your positions

### Future: Multi-Device (Long-term vision)
**Goal**: Access from any device on local network

- Home server deployment
- Mobile apps for thought capture
- Multi-device sync
- Still privacy-first (local network only)

## Success Criteria

This project succeeds when:

1. **Anyone can use it**
   - Not just Twitter users
   - Not just programmers
   - Writers, researchers, thinkers of all kinds

2. **Any content works**
   - Books, notes, archives, emails, anything text-based
   - No bias toward one source type

3. **Any AI can access it**
   - Works with Claude, GPT, local models
   - Standard MCP protocol
   - Easy integration

4. **It's obviously privacy-first**
   - Data stays local
   - No cloud sync required
   - User controls everything

5. **AI truly understands you**
   - Can recall your past thoughts
   - Drafts in your voice/style
   - Respects your perspectives

## What Makes This Unique

### Not RAG Frameworks (LangChain, etc.)
- Those are for developers to build apps
- This is for anyone to use directly
- No coding required

### Not Vector Databases (Pinecone, etc.)
- Those are infrastructure
- This is a complete tool
- Privacy-first (local-only)

### Not Notion/Obsidian
- Those are for active writing/organizing
- This is for AI memory/context
- Different interaction model

### Not Twitter Archive Viewers
- Twitter is one possible source
- Universal content support
- Not tied to any platform

## Proof-of-Self = Your Knowledge, AI's Memory

The name means:
- **Proof**: Evidence of your knowledge and perspectives
- **Of-Self**: Personal, individual, yours alone
- **For AI**: Machine-readable memory system

Like "proof-of-work" in Bitcoin represents computational effort, "proof-of-self" represents your intellectual journey made accessible to AI.

## Current State (November 2025)

### Project Status: Phase 1 - Universal Foundation

**What Works ✅**
- SQLite + FTS5 full-text search (fast, local)
- MCP server infrastructure
- Twitter archive adapter (test data source)
- 8,349 tweets successfully indexed
- Adapter pattern for extensibility

**Refactoring In Progress 🚧**
- Database: Moving to documents-first schema
- MCP Tools: Creating universal tools (not Twitter-specific)
- Chunking: Implementing for large documents (books)
- Rebrand: Completing "Proof-of-Self" throughout codebase
- Architecture: Following research-based decisions

**Decisions Made ✓**
- **Storage**: SQLite + FTS5 (proven, scales to 100k+ docs)
- **Chunking**: 500-1000 tokens, 10-20% overlap, semantic
- **Semantic search**: Deferred to Phase 3 (if needed)
- **Approach**: Refactor first, then enhance
- **Interface**: MCP-first (AI is the interface, minimal CLI)

See **[ARCHITECTURE.md](ARCHITECTURE.md)** for technical decisions and **[ROADMAP.md](ROADMAP.md)** for detailed plan.

## Design Principles

### 1. AI Is the Interface
User never uses Proof-of-Self directly. They talk to their AI, AI uses MCP tools.

### 2. User-Directed Ingestion
System never auto-scans or surprises. User explicitly: "Add this."

### 3. Privacy Always
All data stays local. No cloud services. No tracking. User in control.

### 4. Source Agnostic
Twitter and PDFs are equally first-class. No bias toward any content type.

### 5. Preserve Context
Metadata matters: dates, sources, connections. Not just raw text.

### 6. AI Understanding
Goal is AI that knows YOUR perspectives, writes in YOUR voice, references YOUR knowledge.

## Call to Action

### If You're a User
1. Try it with your data (when ready)
2. Tell us what content types matter to you
3. Share your use case
4. Help us understand how you think

### If You're a Developer
1. We need adapters for more content types
2. MCP tools are easy to add
3. Privacy-first is non-negotiable
4. Universal design, no shortcuts

### If You're an AI Researcher
1. This is infrastructure for personalized AI
2. Long-term memory without RAG complexity
3. Privacy-preserving by design
4. MCP makes it model-agnostic

## The Vision

Imagine:

**Your AI assistant that:**
- Remembers everything you've read
- Knows everything you've written
- Understands your perspectives
- Writes in your voice
- Never forgets
- Never shares (privacy)
- Works with any AI model

**That's Proof-of-Self.**

Not a Twitter tool.
Not a database.
Not a RAG system.

**Your intellectual self, accessible to AI, private and under your control.**

---

*This is what we're building. Join us.*
