#!/usr/bin/env python3
"""
Nanobot Session FTS Indexer & Search CLI
Inspired by MiMo CLI (mimocode) session architecture:
- SQLite FTS5 index for instant search across all session histories
- Fast keyword/phrase search without context window bloat
- Session listing, search, and export
"""

import sys
import os
import json
import sqlite3
from pathlib import Path
import argparse

WORKSPACE_DIR = Path("/home/tan/.nanobot/workspace")
SESSIONS_DIR = WORKSPACE_DIR / "sessions"
DB_PATH = WORKSPACE_DIR / "memory" / "session_fts.db"

def init_db(conn):
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS session_meta (
            session_id TEXT PRIMARY KEY,
            file_name TEXT,
            message_count INTEGER,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
            session_id UNINDEXED,
            role UNINDEXED,
            timestamp UNINDEXED,
            content,
            tokenize='porter unicode61'
        )
    """)
    conn.commit()

def index_sessions():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)

    indexed_count = 0
    total_messages = 0

    if not SESSIONS_DIR.exists():
        print(f"Sessions directory not found: {SESSIONS_DIR}")
        return

    for session_file in SESSIONS_DIR.glob("*.jsonl"):
        session_id = session_file.stem
        file_mtime = session_file.stat().st_mtime

        # Clear existing entries for this session before re-indexing
        conn.execute("DELETE FROM messages_fts WHERE session_id = ?", (session_id,))
        conn.execute("DELETE FROM session_meta WHERE session_id = ?", (session_id,))

        msg_count = 0
        with open(session_file, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    role = data.get("role") or data.get("sender") or "unknown"
                    ts = data.get("timestamp") or data.get("created_at") or ""
                    
                    # Extract text content
                    content_text = ""
                    raw_content = data.get("content")
                    if isinstance(raw_content, str):
                        content_text = raw_content
                    elif isinstance(raw_content, list):
                        parts = []
                        for part in raw_content:
                            if isinstance(part, dict) and part.get("type") == "text":
                                parts.append(part.get("text", ""))
                        content_text = "\n".join(parts)

                    tool_calls = data.get("tool_calls")
                    if tool_calls and isinstance(tool_calls, list):
                        for tc in tool_calls:
                            fn = tc.get("function", {})
                            content_text += f"\n[Tool: {fn.get('name')}({fn.get('arguments')})]"

                    if content_text.strip():
                        conn.execute(
                            "INSERT INTO messages_fts (session_id, role, timestamp, content) VALUES (?, ?, ?, ?)",
                            (session_id, str(role), str(ts), content_text)
                        )
                        msg_count += 1
                except json.JSONDecodeError:
                    continue

        conn.execute(
            "INSERT INTO session_meta (session_id, file_name, message_count) VALUES (?, ?, ?)",
            (session_id, session_file.name, msg_count)
        )
        indexed_count += 1
        total_messages += msg_count

    conn.commit()
    conn.close()
    print(f"✓ Indexed {indexed_count} sessions ({total_messages} messages) into {DB_PATH}")

def search_sessions(query: str, limit: int = 10):
    if not DB_PATH.exists():
        print("Database not indexed yet. Running indexer first...")
        index_sessions()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    sql = """
        SELECT session_id, role, timestamp, snippet(messages_fts, 3, '>>>', '<<<', '...', 25)
        FROM messages_fts
        WHERE messages_fts MATCH ?
        ORDER BY rank
        LIMIT ?
    """
    try:
        results = cursor.execute(sql, (query, limit)).fetchall()
        if not results:
            print(f"No results found for query: '{query}'")
            return

        print(f"=== Search Results for '{query}' ({len(results)} matches) ===")
        for res in results:
            sess_id, role, ts, snippet = res
            print(f"[{sess_id}] ({role} | {ts}):")
            print(f"  {snippet}\n")
    except sqlite3.OperationalError as e:
        print(f"Search query error: {e}")
    finally:
        conn.close()

def list_sessions():
    if not DB_PATH.exists():
        index_sessions()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    rows = cursor.execute("SELECT session_id, message_count FROM session_meta ORDER BY message_count DESC").fetchall()
    conn.close()

    print(f"=== Nanobot Sessions ({len(rows)} total) ===")
    for row in rows:
        print(f"- {row[0]}: {row[1]} messages")

def main():
    parser = argparse.ArgumentParser(description="Nanobot Session FTS Search & Management (MiMo style)")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("index", help="Re-index all sessions into SQLite FTS5")
    
    search_parser = subparsers.add_parser("search", help="Search sessions via FTS5")
    search_parser.add_argument("query", type=str, help="Search query / keyword")
    search_parser.add_argument("--limit", type=int, default=10, help="Max results")

    subparsers.add_parser("list", help="List all indexed sessions")

    args = parser.parse_args()

    if args.command == "index":
        index_sessions()
    elif args.command == "search":
        search_sessions(args.query, args.limit)
    elif args.command == "list":
        list_sessions()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
