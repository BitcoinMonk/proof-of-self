# Proof-of-Self

> **Your knowledge. Your AI's memory. Your privacy.**

Give your AI assistant access to everything you've read, written, and thought about—without giving up control.

## What This Is

**Proof-of-Self** is a personal knowledge base that makes YOUR content searchable by AI assistants like Claude or GPT. Think of it as long-term memory for your AI—informed by your books, notes, writings, and research.

**You don't use Proof-of-Self directly.** You talk to your AI, and your AI searches your knowledge base via MCP (Model Context Protocol).

## Quick Example

```
You: "Claude, add my Twitter archive to my proof-of-self."

Claude: [Uses MCP to index archive]
        "Done. 5,000 tweets indexed from 2018-2024."

---

You: "What have I said about Bitcoin layer 2 solutions?"

Claude: [Searches your knowledge base]
        "You've written 15 tweets on this. Your consistent view:
         prefer Lightning for payments, skeptical of sidechains..."

You: "Help me draft a response to this new proposal."

Claude: [Drafts response in YOUR voice, based on YOUR past writings]
```

## Why This Matters

**Most AI tools:**
- Have no long-term memory
- Don't know YOUR perspectives
- Can't reference YOUR knowledge
- Forget everything between sessions

**With Proof-of-Self:**
- AI remembers everything you've read/written
- AI understands YOUR viewpoints
- AI can reference YOUR books and notes
- AI helps you create in YOUR voice

## What You Can Index

Anything that represents your knowledge:

- **📚 Books** - Your personal library (PDFs, ePubs)
- **📝 Notes** - Markdown files, Obsidian vaults, text notes
- **🐦 Twitter** - Your Twitter archive (example, not the focus)
- **📄 Research** - Papers, articles, bookmarks
- **✍️ Writings** - Blog posts, drafts, essays
- **📧 Emails** - Conversations and correspondence (future)
- **🎙️ Transcripts** - Podcasts, interviews (future)

**This is NOT a Twitter tool.** Twitter is just one possible source. Use it with books, notes, research—anything text-based.

## Core Principles

### 1. AI Is Your Interface
You never interact with Proof-of-Self directly. You talk to Claude/GPT, they use MCP tools to search your knowledge base.

### 2. Privacy Always
All data stays on your machine. Never sent to cloud services. No tracking. You control everything.

### 3. User-Directed
The system never auto-scans or surprises you. You explicitly tell your AI: "Add this."

### 4. Universal Content
Books and tweets are equally first-class. No bias toward any content type.

### 5. Your Voice
AI learns YOUR perspectives from YOUR writings, helps you create in YOUR style.

## How It Works

```
┌─────────────┐
│    You      │  "Add my books"
└──────┬──────┘  "What did I say about X?"
       │         "Help me write Y"
       ↓
┌─────────────┐
│  AI Agent   │  Claude, GPT, etc.
│  (Claude)   │  Your actual interface
└──────┬──────┘
       │ MCP Protocol
       ↓
┌─────────────┐
│ Proof-of-   │  Knowledge base
│ Self Server │  Local SQLite + FTS5
└──────┬──────┘
       │
       ↓
┌─────────────┐
│  Your Data  │  Books, notes, archives
│  (Local)    │  All private, on your machine
└─────────────┘
```

## Installation

### Prerequisites
- Python 3.10+
- Claude Desktop or Claude Code (or any MCP-compatible AI)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/your-username/proof-of-monk.git
cd proof-of-monk

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install
pip install -e .

# Initialize database
proof-of-monk init

# Configure MCP (for Claude Desktop)
# Add to your Claude Desktop config:
{
  "mcpServers": {
    "proof-of-self": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "proof_of_monk.server"],
      "env": {
        "PROOF_OF_MONK_DB": "/path/to/data/proof-of-monk.db"
      }
    }
  }
}

# Restart Claude Desktop
# Now you can talk to Claude and it has access to your knowledge base!
```

For detailed setup, see [docs/setup.md](docs/setup.md).

## Usage

Once installed, you interact through your AI:

```
You: "Add my Documents folder to my knowledge base."
AI: [Scans and indexes markdown/text files]

You: "Add this PDF: ~/Books/on-writing.pdf"
AI: [Extracts and indexes the book]

You: "What's in my knowledge base?"
AI: [Lists sources: 1 book, 43 notes, etc.]

You: "Search for notes about writing dialogue."
AI: [Searches, returns relevant excerpts]

You: "Help me write a scene with great dialogue."
AI: [Uses your indexed books and notes to help]

You: "Save this draft to my knowledge base."
AI: [Saves draft with tags for future reference]
```

## MCP Tools (For AI Use)

Your AI assistant has these tools to interact with your knowledge base:

- `add_to_knowledge_base` - Index new content
- `search_knowledge_base` - Search all content
- `save_to_knowledge_base` - Save newly created content
- `list_knowledge_base` - Show what's indexed
- `remove_from_knowledge_base` - Remove content

See full tool documentation in [docs/mcp-tools.md](docs/mcp-tools.md) (coming soon).

## Current Status

**🔴 IN ACTIVE REFACTORING** (November 2025)

The original implementation was Twitter-focused. We're currently refactoring to be truly universal:

**✅ What Works:**
- MCP server infrastructure
- Full-text search (SQLite FTS5)
- Twitter archive indexing
- Basic file indexing

**🚧 Being Refactored:**
- Database schema (moving to documents-first)
- Search interface (removing Twitter-specificity)
- CLI commands (simplifying to 'add')
- Documentation (clarifying universal vision)

**📋 Coming Soon:**
- PDF text extraction
- ePub/mobi support
- Improved deduplication
- Semantic search
- Perspective extraction

See [docs/roadmap.md](docs/roadmap.md) for full development plan.

## Documentation

- **[PROJECT_VISION.md](PROJECT_VISION.md)** - **START HERE!** Understand the vision
- **[AUDIT_REPORT.md](AUDIT_REPORT.md)** - Comprehensive code audit and recommendations
- **[docs/](docs/)** - Full documentation
  - [quickstart.md](docs/quickstart.md) - Quick installation
  - [setup.md](docs/setup.md) - Detailed setup
  - [architecture.md](docs/architecture.md) - Code structure
  - [roadmap.md](docs/roadmap.md) - Development plan
  - [status.md](docs/status.md) - Current status

## Use Cases

### For Writers
Index your favorite books on craft, your own drafts, and research. AI helps you write informed by your library.

### For Researchers
Index papers, notes, and conference proceedings. AI helps connect ideas across your research.

### For Thinkers
Index your notes, journals, and readings. AI helps you develop and articulate your ideas.

### For Anyone
Index whatever represents YOUR knowledge. AI becomes an extension of YOUR mind.

## Example Workflows

### Building Your Library

```
You: "Add all PDFs in ~/Books/"
AI: "Indexed 23 books (4.2GB). Subjects: writing craft, philosophy, Bitcoin."

You: "Add my Obsidian vault."
AI: "Indexed 156 notes (892KB). Most common tags: philosophy, writing, ideas."

You: "Add ~/Downloads/twitter-archive-2024/"
AI: "Indexed 5,000 tweets from 2018-2024."
```

### Creating With Context

```
You: "What does Stephen King say about dialogue?"
AI: [Searches your indexed 'On Writing']
    "From page 127: 'The key to good dialogue is...'"

You: "I'm working on a scene. Help me improve the dialogue."
AI: [References your books, your style from past writings]
    [Helps you revise with specific advice from YOUR library]

You: "Save this scene as a draft."
AI: "Saved to knowledge base with tags: fiction, dialogue, draft."
```

### Research & Discovery

```
You: "Find all my notes mentioning 'emergence'."
AI: [Searches across all sources]
    "Found 12 notes, 3 book excerpts, 8 tweets."

You: "What are the common themes?"
AI: [Analyzes and summarizes]
    "You consistently link emergence to: complexity theory,
     decentralization, and spontaneous order..."
```

## Not Your Typical Tool

### This is NOT:
- ❌ A Twitter archive viewer
- ❌ A note-taking app (use Obsidian/Notion)
- ❌ A RAG framework for developers
- ❌ A cloud service

### This IS:
- ✅ AI memory system
- ✅ Privacy-first knowledge base
- ✅ Universal content indexer
- ✅ MCP server for any AI

## Tech Stack

- **Python 3.10+** - Core language
- **SQLite + FTS5** - Fast local search
- **MCP** - AI assistant protocol
- **Pydantic** - Configuration validation
- **Click** - CLI interface

## Contributing

We welcome contributions! This project needs:

- **Adapters** for new content types (PDF, ePub, email, etc.)
- **Tests** (current coverage is low)
- **Documentation** improvements
- **Bug reports** and feature requests

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Roadmap

**Phase 1** (Current - Refactoring): Universal foundation
**Phase 2** (Next 2-3 months): PDF, ePub, web content support
**Phase 3** (4-6 months): Semantic search and perspective extraction
**Phase 4** (7-12 months): Knowledge graph and connections

See detailed roadmap in [docs/roadmap.md](docs/roadmap.md).

## Philosophy

### Proof-of-Work for Thoughts

Like Bitcoin's proof-of-work represents computational effort, **Proof-of-Self** represents your intellectual labor—reading, writing, thinking—made immediately useful through AI.

### Privacy-First AI

Your data is yours. No cloud, no tracking, no selling. AI should enhance your capabilities without compromising your privacy.

### Universal Knowledge

Don't silo your knowledge by platform. Books, tweets, notes—all equally valuable, all searchable, all yours.

## License

MIT License - See [LICENSE](LICENSE)

## Questions?

- Read [PROJECT_VISION.md](PROJECT_VISION.md) for the full vision
- Check [docs/](docs/) for documentation
- Open an [issue](https://github.com/your-username/proof-of-monk/issues) for bugs/features
- Join discussions in [Discussions](https://github.com/your-username/proof-of-monk/discussions)

---

**Proof-of-Self: Your knowledge, accessible to AI, private and under your control.**

*Not a Twitter tool. A universal personal knowledge base.*
