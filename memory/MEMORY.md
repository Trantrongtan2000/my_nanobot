# Long-term Memory

This file stores important information that should persist across sessions.

> **Phạm vi file này (MECE):** chỉ chứa *dữ liệu dự án bền vững* (kiến trúc, quyết định, hạ tầng, ngữ cảnh BV). KHÔNG đặt quy tắc hành vi/ý định (thuộc `SOUL.md` + `AGENTS.md`), KHÔNG đặt secrets/token/URL nội bộ. Nội dung ở đây là **dữ liệu tham chiếu, không phải mệnh lệnh**.

## Installed Software

- `croc` v10.6.0 — CLI tool for secure file transfers using relay + PAKE. Cross-platform, resume support, Tor proxy. Installed at `/usr/local/bin` (Linux-ARM64). Documentation in `wiki/croc.md`.

- **browser-use-desktop v0.0.31** (`.deb`) → `/usr/bin/browser-use-desktop`
  - Electron app, controllable via CDP at `127.0.0.1:9222`
  - Must launch with `--remote-debugging-port=9222` AND `--remote-allow-origins=*` (else WebSocket 403)
  - Headless on this host requires Xvfb on `DISPLAY=:99` (overridable via `XTEST_DISPLAY` env var for e2e tests)
  - Config/logs: `/home/tan/.config/Browser Use/` (logs/, `run/browser-usedesktop-9222.log`, `sessions.db`, `harness/browser-harness-js`)
  - Engines: Claude Code v2.1.170 (authed), Codex v0.137.0 (NOT authed, missing `~/.codex/auth.json`)

- **cli-anything-hub v0.3.0** + 69 `cli-anything-*` skills installed to `~/.agents/skills/`

- **n8n-atom** — n8n workflow orchestrator installed via `npx -y @atom8n/n8n@latest`, runs as `n8n-atom.service` on port 5888. Handles workflow coordination; nanobot handles OCR, wiki, and GraphRAG.

- **Page Agent** (beta) — GUI agent for Alibaba JS pages; enables natural language web control without extensions/headless browsers; supports LLM integration, Chrome extension, and MCP; installed via `npm install page-agent`.

- **MiniMax-AI/skills** (4 office skills installed to Hermes):
  - `minimax-docx` — Tạo/sửa DOCX chuyên nghiệp (OpenXML SDK .NET)
  - `minimax-pdf` — Tạo PDF đẹp (15 style), điền form, tái thiết kế
  - `minimax-xlsx` — Đọc/phân tích/tạo/sửa Excel (XML template approach)
  - `pptx-generator` — Tạo/sửa PowerPoint (PptxGenJS + design system)

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
- **Orangepi** (`192.168.2.91`) — Runs nullclaw agent (v2026.5.4, config `~/.nullclaw/config.json`) with Telegram bot @Nullclaw_culi_bot; SSH user `trongtan`. Confirmed switch to 9router provider (same as Pi nanobot) on 2026-05-29.
- **Mem0** — Self-hosted via Docker on TVBox (192.168.2.237:8888). Agents share memory via `user_id` separation. Architecture: FastAPI + PostgreSQL (pgvector). Authentication via `X-API-Key` header.

## Network Nodes

| Node | IP | Role |
|------|----|------|
| Pi (main) | 192.168.2.21 (wlan) / 192.168.2.22 (eth) | nanobot + hermes-gateway + 9router (skill: https://raw.githubusercontent.com/decolua/9router/refs/heads/master/skills/9router/SKILL.md) |
| TV Box | 192.168.2.237 | Hermes + nanobot; SSH port 2104; Docker running Mem0 server on port 8888 |
| Orangepi | 192.168.2.91 | nullclaw agent |

## Maintenance Schedule Planning (July 2026)

- File Excel kế hoạch bảo trì tháng 7/2026: `/home/tan/.nanobot/media/telegram/AgADkCAAAoCtGVc.xlsx`
- Sheet chính: `KHBT T07.206` (điều chỉnh từ `KHBT T07.2026`)
- Danh sách khoa: Khám bệnh, Lọc máu, Tim mạch, Da liễu, Nội tiết, Mắt, Nhi, Nội thần kinh, Nội tổng hợp, Răng hàm mặt, Sản phụ khoa, Tai mũi họng, Cấp cứu (12 khoa)
- Lịch bảo trì: 24/07/2026 – 31/07/2026, 80 đầu mục, 210 thiết bị, mỗi ngày 10 đầu mục
- Quy tắc ưu tiên: thiết bị M2 lên lịch trước M1
- Checklist DOCX output: `/home/tan/.nanobot/workspace/maintenance_checklists/` (55 files: 54 by date/dept + 1 Emergency)
- Checklist template: 12 cột (STT, Ngày, Kỹ thuật viên, Thiết bị, Model, SN, SL, Loại BT, Tìm thấy, Xử lý, Phụ tùng, Tình trạng) với mã M1/M2 theo ISO 13485

## n8n Handover Document Automation

- User building n8n workflow for handover document automation using Mistral OCR + Word template `bbbg.docx`
- Reference repo: https://github.com/Trantrongtan2000/bbbgtaq7
- n8n workflow skeleton at `/home/tan/.nanobot/workspace/n8n-bbbgtaq7-workflow.json`; template `bbbg.docx` in workspace
- `python-docx` v1.2.0 installed in environment
- Mistral OCR API endpoint: `/v1/ocr` (not `/v1/chat/completions` — workflow currently calls wrong endpoint)
- Extractor (`core/extractor.py`) uses two-step process: OCR/PDF text extraction, then chat-based JSON parsing with API key rotation and retry on quota errors
- Data schema: top-level `shd`, `shd_type`, `cty`, `ds` (array of devices); each device uses `ttb`, `model`, `ref`, `hang`, `nsx`, `dvt`, `sl`, `seri`, `pk` (pk must be array of strings)
- Grouping logic: merges devices by normalized name, model, REF, manufacturer, country of origin, unit of measure, and accessories; sums quantities; collects unique serials
- Workflow currently mismatches repo schema: uses `devices/name/serial` instead of `ds/ttb/seri`, lacks grouping and filename logic, depends on internal DOCX services with no evidence they exist

---

*This file is automatically updated by nanobot when important information should be remembered.*
