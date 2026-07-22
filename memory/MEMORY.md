# Long-term Memory

This file stores important information that should persist across sessions.

## Installed Software

- **browser-use-desktop v0.0.31** (`.deb`) → `/usr/bin/browser-use-desktop`
  - Electron app, controllable via CDP at `127.0.0.1:9222`
  - Must launch with `--remote-debugging-port=9222` AND `--remote-allow-origins=*` (else WebSocket 403)
  - Headless on this host requires Xvfb on `DISPLAY=:99` (overridable via `XTEST_DISPLAY` env var for e2e tests)
  - Config/logs: `/home/tan/.config/Browser Use/` (logs/, `run/browser-usedesktop-9222.log`, `sessions.db`, `harness/browser-harness-js`)
  - Engines: Claude Code v2.1.170 (authed), Codex v0.137.0 (NOT authed, missing `~/.codex/auth.json`)

- **cli-anything-hub v0.3.0** + 69 `cli-anything-*` skills installed to `~/.agents/skills/`

## CLI-Anything Harness Convention

- Package layout: `cli_anything/<product>/` with `core/{process,cdp,state}.py`, `utils/{format,repl_skin}.py`, `tests/`, `skills/SKILL.md`, top-level `<PRODUCT>.md` overview
- Use `cli-anything-harness` skill (see `skills/cli-anything-harness/SKILL.md`) for the full workflow

## 9Remote (Remote Access TUI)

- Installed: server at `/home/tan/.npm-global/lib/node_modules/9remote/dist/server.cjs`; config dir `/home/tan/.9remote/`; approved devices in `state/approvedDevices.json`
- **Binds to IPv6 `[::1]:2208` only (NOT IPv4)** — cloudflared must use `--url http://[::1]:2208` else requests get 403
- Auth: API key + machine ID `b3063f652df75827`; session cookie ~30 min
- Startup: launch app in a tmux session (TUI blocks), then `cloudflared tunnel --url http://[::1]:2208 --no-autoupdate`; extract URL from `INF |  https://...trycloudflare.com |` log line
- Shutdown: `pkill -f 'cloudflared.*2208'` then `pkill -f '9remote --tray'`

## Safety Guard Gotchas

- The `fetch` tool blocks `127.0.0.1`/`localhost` URLs and all private IP ranges (192.168.x.x) — must use subprocess/Python for local CDP/HTTP
- IP whitelisting available via config (requires nanobot restart)

## cli-anything Skills Lacking Global Install Support

Shotcut, SiYuan, WireMock, Zoom, Zotero, 3MF, Tigris, VideoCaptioner, WaveTone, Web Yu-PRI, UnrealInsights, Slay the Spire II (13 total)

## Workspace

- `/home/tan/.nanobot/workspace`

## Google Workspace Integration

- `workspace-mcp` v1.21.1 server runs locally (port 8000, 45 tools, 12 services: Gmail, Drive, Calendar, Docs, Sheets, Slides, Chat, Tasks, Contacts, Forms, Search).
- Auth: `--single-user` mode with pre-created OAuth token. Credentials dir: `~/.google_workspace_mcp/credentials/`. Requires `WORKSPACE_MCP_HOST=0.0.0.0` for LAN access.
- All scopes active (Gmail, Calendar, Chat, Drive, Docs, Sheets, Slides, Contacts, Tasks, Forms, Search) — re-authorized with full scopes 2026-06-03.
- Drive layout (Jun 2026 snapshot): ~1.2TB / 5TB used; root folders `REVIEW_LATER`, `STUDY`, `PERSONAL`, `WORK`, `Root_Leftovers`.
- Constraint: files owned by others in Shared Drives cannot be deleted by the user's token.

## Active Projects

- **hospital-mail-tracker** — tracks `@tahospital.vn` emails using LLM Wiki 3-layer pattern.
  - Layout: `hospital-mail-tracker/` with `AGENTS.md` (schema), `filters.yaml` (rules), `tracker.py` (core), `emails.json`, `raw/` (immutable snapshots), `wiki/` (`index.md`, `log.md`).
  - Cron: daily 07:30 checks previous day's mail, sends Telegram summary. Urgent flag for TATB equipment / MRI / CT notices.
  - Filters exclude "TIN BUỒN" (death notices) from urgent alerts per user preference.
  - By default fetches only email metadata (snippet); full body fetched on demand via `read <id>` or `readall`.
  - Source emails stored under `/home/tan/.nanobot/workspace/hospital-emails.json`.

- **Device Wiki** (`kb/wiki/devices/`) — 38 ultrasound device pages for Tâm Anh Q7 from Excel, with AETitle registry (51 devices). Uses LLM Wiki 3-layer pattern (`raw/`, `wiki/`, `AGENTS.md`).

- **Central Orchestrator** (`/home/tan/central-orchestrator/`) — CrewAI multi-agent system connecting nanobot + Hermes on two nodes (192.168.2.22 and 192.168.2.237), both running Hermes + nanobot.
  - Architecture: Hermes handles planning/coordination (calls Node 1), Nanobot handles code/GPU-heavy tasks (calls Node 2). Both agents run on both nodes.
  - Node 2 (192.168.2.237) is a TV box; SSH access via port 2104 (root/tvbox).
  - Config in `.env`: `NODE1_BASE_URL`, `NODE2_BASE_URL`, `SHARED_MODEL_NAME=MiniMax-M2.7`.
  - Structure: `main.py` (entry), `bot.py` (Telegram handler), `orchestrator.py` (CrewAI logic), `agents.py` (agent defs), `requirements.txt`, `.env.example`.
  - Hermes and nanobot originally shared the same Telegram token causing polling conflicts; separate tokens assigned per bot.

## Tâm Anh Hospital Context

- User interfaces with Tâm Anh Hospital system (Q7, Q8, HCM; Viện Nghiên Cứu Tâm Anh).
- Internal email domain: `@tahospital.vn`. Key senders: `ta5.pttbyt`/`ta5.pkhth` (TTBYT Q7), `khth` (KHHĐ), `hanhchinh`, `cntt`, `nhansu`, `phongdieuduong`, `huonglt2` (KSK coordination).
- User builds tools around hospital ops (mail tracking, equipment reports like `MÁY SIÊU ÂM Q7`, `TBYTQ7_BCCL`).

## Agent Ecosystem

- **AgentMemory MCP** installed (port 3111, viewer 3114). `bm25-only` mode (no embeddings API key).
- **Pi Agent** (Qwen local via Ollama): web search fixed by replacing `@ollama/pi-web-search` with `pi-web-access` (Exa MCP).
- Skills installed from ClawHub: self-improving-agent, skill-vetter, vibesec, markitdown.
- **Mistral OCR workflow** (on Hermes): PDF → images → Mistral OCR → markdown. Used for biomedical document processing.
- **Hermes Gateway** — Messaging gateway service handling Telegram bot communication and MCP server coordination.
- **Dedicated-agent direction** — User wants separate agents for OCR, Wiki, GraphRAG, Maintenance, and Safety management; Wiki agent was selected first, with the others not yet created.
- **Orangepi** (`192.168.2.91`) — Runs nullclaw agent with Telegram bot @Nullclaw_culi_bot; SSH user `trongtan`.
- **Mem0** — Evaluated as universal memory layer for AI agents (self-hosted via Docker); agents share memory via `user_id` separation. Not currently deployed.

## Network Nodes

| Node | IP | Role |
|------|----|------|
| Pi (main) | 192.168.2.21 (wlan) / 192.168.2.22 (eth) | nanobot + hermes-gateway + 9router |
| TV Box | 192.168.2.237 | Hermes + nanobot; SSH port 2104 |
| Orangepi | 192.168.2.91 | nullclaw agent |

---

*This file is automatically updated by nanobot when important information should be remembered.*
