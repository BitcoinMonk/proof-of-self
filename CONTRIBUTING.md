# Contributing to Proof-of-Self

**Status**: 🔴 Not accepting contributions yet - in active refactoring (Phase 1)

We're currently transforming from a Twitter-focused tool to a universal knowledge base. Once Phase 1 refactoring is complete, we'll open for community contributions.

---

## Current Focus (Phase 1 - November 2025)

We're completing foundational work:
- Rebranding from "proof-of-monk" to "Proof-of-Self"
- Refactoring database to documents-first architecture
- Creating universal MCP tools (not Twitter-specific)
- Adding PDF support with chunking
- Removing Twitter-centric CLI commands

**Timeline**: 2-3 weeks

---

## Future Contribution Opportunities (Phase 2+)

Once Phase 1 is complete, we'll need help with:

### High Priority
- **Content Adapters**: ePub, email (mbox/maildir), web bookmarks
- **Testing**: Unit tests, integration tests (current coverage ~10%)
- **Documentation**: Setup guides, tutorials, usage examples
- **Bug Reports**: Real-world usage issues
- **Performance Testing**: Large dataset optimization

### Medium Priority
- **Search Improvements**: Query quality, ranking algorithms
- **Metadata Extraction**: Better title/author/tag detection
- **CLI Tools**: Admin utilities for debugging/stats

### Long-Term
- **Semantic Search**: If Phase 2 testing shows it's needed
- **Knowledge Graph**: If valuable after real-world use
- **Multi-Device Support**: Home server setup, mobile apps

---

## Development Philosophy

### Core Principles

1. **Universal, Not Twitter-Specific**
   - Any content type is first-class
   - No bias toward particular sources
   - Generic tools that work for all content

2. **Privacy First, Always**
   - All data stays local
   - No cloud services required
   - No telemetry or tracking
   - User controls everything

3. **MCP-First Interaction**
   - AI is the interface (not CLI)
   - User talks to Claude/GPT
   - Minimal CLI for setup/admin only

4. **Simple & Maintainable**
   - Avoid over-engineering
   - Clear, readable code
   - Good documentation
   - Sensible defaults

5. **Well-Tested**
   - New features need tests
   - Target: 60%+ coverage
   - Integration tests for happy paths
   - Unit tests for core logic

---

## How to Prepare

If you're interested in contributing later:

1. **⭐ Star the repo** to stay updated on progress
2. **📖 Read the core docs**:
   - [PROJECT_VISION.md](PROJECT_VISION.md) - Understand the vision
   - [ARCHITECTURE.md](ARCHITECTURE.md) - Technical decisions
   - [ROADMAP.md](ROADMAP.md) - Development phases
3. **👀 Watch for updates** - We'll announce when we're ready for contributors
4. **💬 Join discussions** (when we enable them) - Ask questions, share ideas

---

## Contributing Guidelines (When Ready)

### Good First Issues

We'll label issues with:
- `good-first-issue` - New contributors welcome
- `help-wanted` - We need help with this
- `adapter` - New data source adapter needed
- `documentation` - Docs improvements
- `testing` - Test coverage gaps

### Adapter Development

**What is an adapter?**
Adapters parse different content types (PDFs, ePubs, emails) and yield standardized document records for indexing.

**Adapter structure**:
```python
from proof_of_self.adapters.base import BaseAdapter

class EmailAdapter(BaseAdapter):
    """Parse mbox/maildir email archives"""

    def validate_source(self) -> bool:
        """Check if source is valid email archive"""
        pass

    def parse(self) -> Iterator[Dict[str, Any]]:
        """
        Yield document records:
        {
            "source_type": "email",
            "content_type": "message",
            "title": subject,
            "author": from_address,
            "content": body,
            "metadata": {...},
            "created_at": timestamp
        }
        """
        pass
```

**Needed adapters**:
- ePub/mobi (ebook formats)
- Email (mbox, maildir)
- Web bookmarks (HTML exports, Pocket)
- Org-mode files
- Jupyter notebooks

### Code Style

- **Python 3.10+** required
- **Black** for formatting (line length 100)
- **Type hints** on all functions
- **Docstrings** for public APIs
- **Tests** for new features

### Testing Requirements

- Unit tests for new functions/classes
- Integration test for end-to-end adapter flow
- Test with real data samples (include in `tests/fixtures/`)
- Minimum 60% coverage for new code

### Pull Request Process

1. Fork the repo
2. Create feature branch (`git checkout -b feature/email-adapter`)
3. Write code + tests
4. Run tests (`pytest`)
5. Format code (`black src/`)
6. Submit PR with clear description

**PR template** (coming soon):
- What does this add/fix?
- How was it tested?
- Any breaking changes?
- Documentation updated?

---

## Code of Conduct

**Be excellent to each other.**

This project is about empowering individuals with their own data and AI. Let's keep the community:
- **Respectful**: Treat everyone with kindness
- **Helpful**: Support newcomers, share knowledge
- **Focused**: Stay on-topic, productive discussions
- **Privacy-conscious**: Never suggest compromising user privacy

**Unacceptable**:
- Harassment, discrimination, personal attacks
- Spam, off-topic promotions
- Privacy violations (suggesting cloud services for core features)
- Destructive criticism without constructive suggestions

---

## Questions?

- **Technical questions**: Open an issue (when ready)
- **Feature ideas**: Discussions section (when enabled)
- **Security issues**: Contact maintainers directly (email TBD)

---

## Timeline

- **Phase 1 (Now - Dec 2025)**: Foundation refactoring (no external contributions)
- **Phase 2 (Q1 2026)**: Real-world testing (may accept specific contributions)
- **Phase 3 (Q2 2026)**: Open for contributions (adapter development, testing, docs)

**Check back in Q1 2026** when Phase 1 is complete!

---

**Thank you for your interest in Proof-of-Self!**

*A universal personal knowledge base: privacy-first, AI-accessible, locally-controlled.*
