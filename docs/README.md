# Proof-of-Self Documentation

**Welcome!** This is the documentation hub for Proof-of-Self, a universal personal knowledge base accessible via MCP.

---

## 🎯 Start Here

**New to the project?** Read these in order:

1. **[../README.md](../README.md)** - Project overview, quick example, current status
2. **[../PROJECT_VISION.md](../PROJECT_VISION.md)** - Complete vision and philosophy
3. **[../ARCHITECTURE.md](../ARCHITECTURE.md)** - Technical architecture and decisions
4. **[../ROADMAP.md](../ROADMAP.md)** - Development phases and timeline

---

## 📚 Core Documentation

### Essential Files (Root Directory)

| Document | Purpose |
|----------|---------|
| **[README.md](../README.md)** | Project overview, installation, usage examples |
| **[PROJECT_VISION.md](../PROJECT_VISION.md)** | Complete vision: what this is, why it matters, how it works |
| **[ARCHITECTURE.md](../ARCHITECTURE.md)** | Technical architecture, storage decisions, schema design |
| **[ROADMAP.md](../ROADMAP.md)** | Development phases (Phase 1-3+), timeline, priorities |
| **[CHANGELOG.md](../CHANGELOG.md)** | Version history and major changes |
| **[CONTRIBUTING.md](../CONTRIBUTING.md)** | How to contribute (opens Phase 2+) |
| **[LICENSE](../LICENSE)** | MIT License |

---

## 🗂️ Documentation Structure

```
proof-of-self/
├── README.md                 # Project overview
├── PROJECT_VISION.md         # Vision document
├── ARCHITECTURE.md           # Technical architecture
├── ROADMAP.md                # Development roadmap
├── CHANGELOG.md              # Version history
├── CONTRIBUTING.md           # Contribution guidelines
├── LICENSE                   # MIT License
│
└── docs/
    ├── README.md             # This file (documentation index)
    │
    └── archive/              # Historical/deprecated documentation
        ├── DEPRECATED.md     # What was deprecated and why
        ├── roadmap.md        # Old roadmap (phase conflicts)
        ├── status.md         # Old status snapshot
        ├── quickstart.md     # Old Twitter-focused guide
        ├── setup.md          # Old setup instructions
        ├── architecture.md   # Old structure doc
        ├── AUDIT_REPORT.md   # Nov 16 audit findings
        ├── REFACTORING_PLAN.md  # Superseded refactoring plan
        ├── AUDIT_COMPLETE.md    # Audit summary
        └── inbox-guide.md    # Deprecated inbox feature
```

---

## 📖 Reading Guide

### For New Users

**Want to understand the vision?**
1. Read [README.md](../README.md) - 5 minutes
2. Read [PROJECT_VISION.md](../PROJECT_VISION.md) - 15 minutes
3. Check [Current Status](#current-status) below

**Want to install and use it?**
- **Note**: We're in Phase 1 refactoring (Nov 2025)
- Setup guides coming after Phase 1 completes
- Current code is Twitter-focused (being refactored)

### For Developers

**Want to contribute?**
1. Read [CONTRIBUTING.md](../CONTRIBUTING.md)
2. Read [ARCHITECTURE.md](../ARCHITECTURE.md)
3. Check [ROADMAP.md](../ROADMAP.md) for current phase
4. **Status**: Not accepting contributions until Phase 1 complete

**Want to understand technical decisions?**
1. Read [ARCHITECTURE.md](../ARCHITECTURE.md) - Storage, search, MCP tools
2. Read [archive/DEPRECATED.md](archive/DEPRECATED.md) - What changed and why
3. Read [CHANGELOG.md](../CHANGELOG.md) - Version history

### For Contributors (Future)

**Phase 2+ (Q1 2026)** - We'll need:
- Content adapters (ePub, email, web bookmarks)
- Testing (current coverage ~10%)
- Documentation improvements
- Bug reports from real-world usage

See [CONTRIBUTING.md](../CONTRIBUTING.md) for details.

---

## 🚦 Current Status

**Phase**: Phase 1 - Universal Foundation (Nov-Dec 2025)

**What's Happening**:
- Rebranding from "proof-of-monk" to "Proof-of-Self"
- Refactoring database to documents-first (Twitter as one source among many)
- Creating universal MCP tools (not Twitter-specific)
- Adding PDF support with chunking
- Removing Twitter-centric CLI commands

**Timeline**: 2-3 weeks

**What Works Now**:
- ✅ SQLite + FTS5 full-text search
- ✅ MCP server infrastructure
- ✅ Twitter archive adapter (test data)
- ✅ 8,349 tweets successfully indexed

**Coming in Phase 1**:
- 🚧 Documents-first database schema
- 🚧 Universal MCP tools
- 🚧 PDF adapter with chunking
- 🚧 Complete rebrand in code

See [ROADMAP.md](../ROADMAP.md) for detailed plan.

---

## 📝 Quick Links

### Documentation
- [Project README](../README.md)
- [Vision Document](../PROJECT_VISION.md)
- [Architecture](../ARCHITECTURE.md)
- [Roadmap](../ROADMAP.md)
- [Changelog](../CHANGELOG.md)
- [Contributing](../CONTRIBUTING.md)

### Archive (Historical)
- [Deprecated Features](archive/DEPRECATED.md)
- [Old Audit Report](archive/AUDIT_REPORT.md)
- [Old Roadmap](archive/roadmap.md)
- [Old Setup Guides](archive/)

---

## ❓ Common Questions

**Q: Is this ready to use?**
A: Not yet. We're in Phase 1 refactoring (2-3 weeks). Check [ROADMAP.md](../ROADMAP.md) for timeline.

**Q: Can I contribute?**
A: Not yet. We'll open for contributions after Phase 1. See [CONTRIBUTING.md](../CONTRIBUTING.md).

**Q: Is this still Twitter-focused?**
A: No! We're actively refactoring to be universal. Twitter was just the test dataset. See [CHANGELOG.md](../CHANGELOG.md) v0.2.0.

**Q: What's the difference from proof-of-monk?**
A: "Proof-of-Self" is the rebrand emphasizing universal knowledge base (not Twitter-specific). Same project, clearer direction.

**Q: Will old documentation come back?**
A: No. Archived docs in `archive/` are for historical reference only. New docs reflect current direction.

**Q: What happened to the inbox feature / consciousness streams?**
A: Deprecated/deferred. See [archive/DEPRECATED.md](archive/DEPRECATED.md) for full list and reasoning.

---

## 🎓 Learning Path

**Complete beginner to the project:**
1. [README.md](../README.md) - What is this?
2. [PROJECT_VISION.md](../PROJECT_VISION.md) - Why does this exist?
3. Wait for Phase 1 to complete for setup guides

**Developer interested in contributing:**
1. [ARCHITECTURE.md](../ARCHITECTURE.md) - How does it work?
2. [CONTRIBUTING.md](../CONTRIBUTING.md) - When can I help?
3. [ROADMAP.md](../ROADMAP.md) - What's the plan?

**Researcher/technical deep-dive:**
1. [ARCHITECTURE.md](../ARCHITECTURE.md) - Technical decisions
2. [archive/AUDIT_REPORT.md](archive/AUDIT_REPORT.md) - Code audit findings
3. [archive/DEPRECATED.md](archive/DEPRECATED.md) - What changed and why

---

## 🔄 Documentation Updates

**Last Updated**: November 16, 2025 (v0.2.0 - Architecture Reset)

**Major Changes**:
- Complete documentation overhaul
- Archived old Twitter-focused docs
- Created new ARCHITECTURE.md and unified ROADMAP.md
- Updated all links and navigation
- Clarified current status and direction

**Next Update**: After Phase 1 completion (Dec 2025)
- New setup guides for universal approach
- MCP tools documentation
- Real-world usage examples

---

## 📞 Contact

- **Issues**: [GitHub Issues](https://github.com/your-username/proof-of-self/issues) (when ready)
- **Discussions**: Coming in Phase 2+
- **Security**: Contact maintainers directly (email TBD)

---

**Thank you for your interest in Proof-of-Self!**

*A universal personal knowledge base: your knowledge, accessible to AI, private and under your control.*
