# Inbox System Guide

The inbox system provides a simple drop zone for adding content to your Proof-of-Monk knowledge base.

## Quick Start

### 1. Drop files in the inbox

```bash
# Just copy files to the inbox directory
cp ~/Downloads/my-notes.md data/inbox/
cp ~/Downloads/twitter-archive-* data/inbox/
```

### 2. Run the indexing command

```bash
proof-of-monk index-inbox
```

That's it! Your files are now indexed and searchable via MCP tools.

## Directory Structure

```
data/
├── inbox/              # 👈 DROP ZONE - put files here
│   ├── [your files]
│   └── [twitter archives]
├── processed/          # Files move here after indexing
└── proof-of-monk.db    # Your knowledge base
```

## Supported File Types

Currently supported:
- **Markdown** (.md, .markdown)
- **Text files** (.txt)
- **Org mode** (.org)
- **Twitter archives** (full directory structure)

Coming soon:
- PDF files
- HTML/Web pages
- Office documents (docx, xlsx)

## How It Works

1. **You drop files** in `data/inbox/`
2. **Run `proof-of-monk index-inbox`**
   - Scans inbox directory
   - Auto-detects file types
   - Extracts metadata (title, tags, dates)
   - Indexes content for full-text search
   - Moves processed files to `data/processed/`
3. **Everything becomes searchable** via MCP tools

## Markdown Frontmatter

For markdown files, you can add frontmatter to provide metadata:

```markdown
---
title: My Important Notes
tags: bitcoin, research, article-idea
category: draft
---

# Your content here...
```

The indexer will extract:
- **title**: Document title
- **tags**: Array of tags for categorization
- Any other metadata you include

If no frontmatter is provided, the indexer will:
- Use the first `# Heading` as the title
- Use the filename as fallback

## CLI Commands

### Index files from inbox
```bash
proof-of-monk index-inbox
```

### Keep files in inbox (don't move to processed)
```bash
proof-of-monk index-inbox --keep-files
```

### Use custom paths
```bash
proof-of-monk index-inbox \
  --inbox-path ~/my-inbox \
  --db-path ~/my-kb.db \
  --processed-path ~/archived
```

### Check what's indexed
```bash
proof-of-monk stats
```

## Searching Documents with MCP

Once files are indexed, you can search them using MCP tools in Claude:

```
# Search all documents
search_documents(query="bitcoin proof of work")

# Filter by content type
search_documents(query="knowledge base", content_type="markdown")

# List recent documents
list_recent_documents(limit=10)

# Filter recent by type
list_recent_documents(limit=5, content_type="text")
```

## Twitter Archives

To index a Twitter archive:

1. Download your Twitter archive from Twitter
2. Extract the zip file
3. Move the entire folder to `data/inbox/`
4. Run `proof-of-monk index-inbox`

The system will automatically detect it's a Twitter archive and index:
- All your tweets
- Bookmarks
- Likes

## Tips

- **Batch processing**: Drop multiple files, run once
- **Automatic deduplication**: Same content won't be indexed twice (based on content hash)
- **Safe cleanup**: Files move to `processed/` so you can verify indexing worked
- **Keep originals**: The database stores content, but original files are preserved in `processed/`

## Workflow Example

```bash
# Download Twitter archive
mv ~/Downloads/twitter-2025-* data/inbox/

# Add some notes
echo "Bitcoin represents digital scarcity" > data/inbox/bitcoin-notes.md

# Drop research PDF (future)
cp ~/research/whitepaper.pdf data/inbox/

# Index everything
proof-of-monk index-inbox

# Check stats
proof-of-monk stats

# Now use with Claude!
# Claude can search across all your content via MCP
```

## Advanced: Agent Integration

The inbox system was designed with AI agents in mind:

- **Claude can suggest** what to save via `dump_thought` MCP tool
- **You manually drop** larger files (archives, PDFs) into inbox
- **Everything becomes searchable** for Claude to reference

This creates a hybrid human + AI knowledge curation system.

## Troubleshooting

### Files not being indexed?

Check file extension is supported:
```bash
ls -la data/inbox/
```

Run with verbose output (future):
```bash
proof-of-monk index-inbox --verbose
```

### Want to re-index?

Files are deduplicated by content hash, so you can safely re-run indexing. The same content won't create duplicates.

### Files stuck in inbox?

If indexing failed, files stay in inbox. Check errors and run again.

---

**Questions?** Open an issue or check the main README.
