# Tools (Windows PC)

Local map for this host. Prefer structured nanobot tools over shell when equivalent.

## Built-in

| Need | Prefer |
|------|--------|
| Read / write / edit files | `read_file`, `write_file`, `edit_file` / `apply_patch` |
| Search text / files | `grep`, `find_files`, `list_dir` |
| Shell | `exec` (PowerShell on this host) |
| Web search / fetch | TinyFish MCP first; else `web_search` / `web_fetch` |
| Reminders / schedules | `cron` (not MEMORY.md) |
| Long work | `/goal` + `complete_goal` when done |
| Subagents | `spawn` sparingly; keep parent context lean |

## MCP

| Server | Use for |
|--------|---------|
| `notion` | Notion pages (markdown API preferred; see AGENTS.md) |
| `tinyfish` | `tinyfish_search`, `tinyfish_fetch_content`, `tinyfish_batch_create`, automation runs |
| `code-review-graph` | Structural graph: callers/callees, impact/blast radius, search, flows (default repo = this workspace) |

If an MCP tool is missing at runtime, fall back to built-ins and say so once — do not loop reconnects.

### code-review-graph ops

```text
code-review-graph status --repo C:\Users\tantt\.nanobot\workspace
code-review-graph update --repo C:\Users\tantt\.nanobot\workspace   # after code edits
code-review-graph build  --repo C:\Users\tantt\.nanobot\workspace   # full rebuild
```

Only **git-tracked** sources are indexed. New Python files: `git add` then `update`.  
Skill: `skills/code-review-graph/SKILL.md` + `skills/crg-*`.

## Host paths

- Workspace: `C:\Users\tantt\.nanobot\workspace`
- Config: `C:\Users\tantt\.nanobot\config.json`
- Gateway health: `http://127.0.0.1:18790/health`
- 9router LLM: `http://127.0.0.1:20128/v1`
- Autostart: Task Scheduler `nanobot-gateway` → `~\.nanobot\start-gateway.ps1`

## Shell notes (Windows)

- Shell is PowerShell. No `&&` on PS 5.1 — use `; if ($?) { … }` or separate calls.
- Prefer `curl.exe` over `curl` alias when needed.
- Destructive: `rm -r`, `Remove-Item -Recurse`, disk wipes — confirm first.
- Never dump secrets from `.env` / config into chat or Notion.

## Skills

Load via `read_file` on `skills/<name>/SKILL.md` when needed:

- `code-review-graph` — graph MCP workflow (blast radius / impact / search)
- `crg-build-graph`, `crg-review-changes`, `crg-explore-codebase`, `crg-refactor-safely`, `crg-debug-issue` — upstream CRG skills
- `agent-patterns` — study notes from system-prompt collections (when rewriting SOUL/AGENTS)
- `ponytail` — lazy ladder (always-on via SOUL; full SKILL + `references/platform-native.md`)
- `ponytail-review` — over-engineering review only
- `ponytail-debt` — harvest `ponytail:` shortcut markers
- `ponytail-audit` — whole-repo complexity audit
- `tinyfish-mcp` — TinyFish stdio details
- `doc-ocr-organize` — OCR batch organize
- `cli-anything-harness` — CDP/CLI harness pattern
- `skill-creator` — scaffold new skills
- `officecli-docx` — Word docs when present
- `mistral-ocr` — Mistral OCR API, key rotation, auto-chunking & document conversion (PDF/images/Word/Excel)

## Scripts in workspace

- `import_upnote.py` — UpNote HTML → Notion (`NOTION_TOKEN`)
- `ocr_process.py` / wiki OCR helpers — check manifest before restarting batches
