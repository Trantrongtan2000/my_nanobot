---
name: session-fts
description: Index and search Nanobot session history using SQLite FTS5 (inspired by MiMo CLI session architecture). Use to instantly recall details from past chats without blowing LLM context window.
---

# Session FTS Indexing & Search (MiMo-style)

This skill provides fast, full-text search over all Nanobot Telegram and CLI session transcripts using SQLite FTS5.

## Usage

### 1. Re-index all sessions
Run this when new sessions are recorded or to refresh the FTS database:
```bash
python3 /home/tan/.nanobot/workspace/session_fts.py index
```

### 2. Search past conversations
Search for any term, device name, serial number, or topic across past chat sessions:
```bash
python3 /home/tan/.nanobot/workspace/session_fts.py search "<keyword_or_phrase>"
```
Example:
```bash
python3 /home/tan/.nanobot/workspace/session_fts.py search "kiểm định BVQ7"
python3 /home/tan/.nanobot/workspace/session_fts.py search "UHADO-16"
```

### 3. List indexed sessions
```bash
python3 /home/tan/.nanobot/workspace/session_fts.py list
```

## Architecture
- Database location: `/home/tan/.nanobot/workspace/memory/session_fts.db`
- Transcripts indexed from: `/home/tan/.nanobot/workspace/sessions/*.jsonl`
- Search engine: SQLite FTS5 with unicode61 tokenizer.
