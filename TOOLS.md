# Tools (Raspberry Pi)

## Built-in

| Need | Prefer |
|------|--------|
| Read / write / edit files | `read_file`, `write_file`, `edit_file` / `apply_patch` |
| Search text / files | `grep`, `find_files`, `list_dir` |
| Shell | `exec` (bash on this host) |
| Web search / fetch | TinyFish MCP first; else `web_search` / `web_fetch` |
| Reminders / schedules | `cron` (not MEMORY.md) |
| Long work | `/goal` + `complete_goal` when done |
| Subagents | `spawn` sparingly; keep parent context lean |

## MCP

| Server | Use for |
|--------|---------|
| `notion` | Notion pages (markdown API preferred; see AGENTS.md) |
| `tinyfish` | `tinyfish_search`, `tinyfish_fetch_content`, `tinyfish_batch_create`, automation runs |

If an MCP tool is missing at runtime, fall back to built-ins and say so once — do not loop reconnects.

## Host paths

- Workspace: `/home/tan/.nanobot/workspace`
- Config: `/home/tan/.nanobot/config.json`
- 9router LLM: `http://127.0.0.1:20128/v1`
- Services: `systemctl --user {nanobot,9router,9router-tunnel}`

## Skills

Load via `read_file` on `skills/<name>/SKILL.md` when needed:

- `ponytail` — lazy ladder (always-on via SOUL)
- `ponytail-review` — over-engineering review
- `ponytail-debt` — harvest `ponytail:` shortcut markers
- `ponytail-audit` — whole-repo complexity audit
- `tinyfish-mcp` — TinyFish stdio details
- `doc-ocr-organize` — OCR batch organize
- `cli-anything-harness` — CDP/CLI harness pattern
- `skill-creator` — scaffold new skills
- `entity-creator` — create/verify entity wiki pages
- `wiki-manager` — LLM wiki management
- `mistral-ocr` — Mistral OCR API, key rotation, auto-chunking
- `officecli-docx` — Word docs
- `agent-patterns` — study notes from system-prompt collections
- `code-review-graph` — graph MCP workflow (blast radius / impact / search)
- `crg-build-graph`, `crg-review-changes`, `crg-explore-codebase`, `crg-refactor-safely`, `crg-debug-issue` — upstream CRG skills

## Scripts in workspace

- `import_upnote.py` — UpNote HTML → Notion (`NOTION_TOKEN`)
- `ocr_process.py` — OCR processing helpers
- `verify_entity.py` — entity verification (self-improvement loop)
- `nanobot_self_improve.py` — learn from errors and improve

## Shell notes (Linux/Pi)

- Shell is bash.
- Destructive: `rm -rf`, disk wipes — confirm first.
- Never dump secrets from `.env` / config into chat or Notion.
