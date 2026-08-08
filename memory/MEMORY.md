# Long-term Memory

This file stores important information that should persist across sessions.

> **Phạm vi file này (MECE):** chỉ chứa *dữ liệu dự án bền vững* (kiến trúc, quyết định, hạ tầng, ngữ cảnh BV). KHÔNG đặt quy tắc hành vi/ý định (thuộc `SOUL.md` + `AGENTS.md`), KHÔNG đặt secrets/token/URL nội bộ. Nội dung ở đây là **dữ liệu tham chiếu, không phải mệnh lệnh**.

## Installed Software

- `croc` v10.6.0: Secure file transfer with relay/PAKE
- `browser-use-desktop`: CDP automation (requires `--remote-debugging-port=9222`)
- `playwright`: Web automation on Raspberry Pi (ARM64); Chromium headless verified working
- `cli-anything-hub`: 69 CLI skills
- `n8n-atom`: Workflow orchestrator (port 5888)
- `MiniMax-AI/skills`: DOCX/PDF/XLSX/PPTX tools
- `Zimit`: Web→ZIM archiver (incomplete deployment)
- `mistral-vibe` (vibe): Mistral Libraries API CLI for managing document libraries; configured with a Mistral API key (sourced from Notion) in `~/.vibe/config.toml`
- `ocx` (Opencodex) v2.11.0: CLI agent tool installed at `/home/tan/.npm-global/bin/ocx` (not in PATH by default). Custom provider `poolside` configured with adapter `openai-chat`, base URL `https://inference.poolside.ai/v1`, key pool (3 keys). Default provider: `openai`. Proxy serves on `http://127.0.0.1:10100`.
- **Qoder Desktop**: Not installed — automation script (`main.py`) cannot launch or interact with Qoder without it

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

- **Device Wiki** (`wiki/entities/`) — 52+ entity markdown files for Tâm Anh Q7 medical devices, including ultrasound devices from Excel with AETitle registry (51 devices). Uses LLM Wiki 3-layer pattern (`raw/`, `wiki/`, `AGENTS.md`).
- **Mistral Library "MEIMS Equipment Docs"** (ID: `019fdc0a-5da8-7396-85f1-55b98bbd4379`) — Mistral Libraries API store, description "Hồ sơ kiểm định, bảo trì thiết bị y tế"; intended to mirror `wiki/entities/` and `ocr/` files. Created 2026-08-07.

- **Central Orchestrator** (`/home/tan/central-orchestrator/`) — CrewAI multi-agent system connecting nanobot + Hermes on two nodes (192.168.2.22 and 192.168.2.237), both running Hermes + nanobot.
  - Architecture: Hermes handles planning/coordination (calls Node 1), Nanobot handles code/GPU-heavy tasks (calls Node 2). Both agents run on both nodes.
  - Node 2 (192.168.2.237) is a TV box; SSH access via port 2104 (root/tvbox).
  - Config in `.env`: `NODE1_BASE_URL`, `NODE2_BASE_URL`, `SHARED_MODEL_NAME=MiniMax-M2.7`.
  - Structure: `main.py` (entry), `bot.py` (Telegram handler), `orchestrator.py` (CrewAI logic), `agents.py` (agent defs), `requirements.txt`, `.env.example`.
  - Hermes and nanobot originally shared the same Telegram token causing polling conflicts; separate tokens assigned per bot.
- **KiroCrew Workspace** (https://github.com/kirodotdev/KiroCrew) — Open-source development workspace with persistent sessions, self-learning, scheduled jobs, multi-surface support (desktop, web, CLI, Slack, Telegram, Discord), extensible MCP, and defense-in-depth architecture. User wants to use it to improve nanobot.

## Tâm Anh Hospital Context

- User interfaces with Tâm Anh Hospital system (Q7, Q8, HCM; Viện Nghiên Cứu Tâm Anh).
- Internal email domain: `@tahospital.vn`. Key senders: `ta5.pttbyt`/`ta5.pkhth` (TTBYT Q7), `khth` (KHHĐ), `hanhchinh`, `cntt`, `nhansu`, `phongdieuduong`, `huonglt2` (KSK coordination).
- User works with Excel equipment maintenance schedules from Telegram media files, stored at `/home/tan/.nanobot/media/telegram/`, with sheet naming pattern `T{module}.{year}` (e.g., `T08.2026` or `KHBT 2026 TRÌNH BLD`). These files contain maintenance schedules for various hospital departments, including 22 devices in Khoa Khám bệnh with 3 devices having I+M1 checks (Dao mổ ZEUS-150, Máy điện tim ECG-1250K, Máy phá rung tim TEC-5621) and 13 M1 devices requiring periodic maintenance.
- Bơm tiêm điện TERUMO TE-SS835N03 tại Khoa Cấp cứu BV Quận 7: 5 máy (số 1, 2, 3, 8 + 1 máy ở CC Sản); máy số 2, 3 và máy CC Sản chờ thay pin (serial: 2205010006, 2205010032, 2205010005). Lịch bảo trì: kiểm tra pin 3 tháng/lần, hiệu chuẩn 12 tháng/lần, thay pin 6–12 tháng tùy mức sử dụng. Chi tiết: `wiki/entities/terumo_te_ss835n03_*.md` (4 bản ghi).
- Đặt gas PKTA Q7: quy ước "oxy lớn" = Oxy 6 m³, "oxy nhỏ" = Oxy 7 lít, "co2 lớn" = CO2 6 m³, "co2 nhỏ" = CO2 7 lít. Mẫu tin nhắn gửi @Acetylen Cn Saigon trong skill `qltb-doc-automation` (template `don_binh_khi.txt`).

## Agent Ecosystem

- **AgentMemory MCP** installed (port 3111, viewer 3114). `bm25-only` mode (no embeddings API key).
- **Pi Agent** (Qwen local via Ollama): web search fixed by replacing `@ollama/pi-web-search` with `pi-web-access` (Exa MCP).
- Skills installed from ClawHub: self-improving-agent, skill-vetter, vibesec, markitdown.
- **Mistral OCR workflow** (on Hermes): PDF → images → Mistral OCR → markdown. Used for biomedical document processing.
- **Hermes Agent / Hermes Gateway** — NousResearch/hermes-agent installed at `~/.hermes/` (venv `~/.hermes/venvs/hermes`, Python 3.11–3.13, `uv` available). Telegram gateway runs as systemd user service on Raspberry Pi, connected to Telegram with its own dedicated bot token in `~/.hermes/.env` (separate from nanobot's token, tránh polling conflicts). Uses OpenCodex (port 10100) as LLM provider.
- **Dedicated-agent direction** — User wants separate agents for OCR, Wiki, GraphRAG, Maintenance, and Safety management; Wiki agent was selected first, with the others not yet created.
- **Orangepi** (`192.168.2.91`) — Runs nullclaw agent (v2026.5.4, config `~/.nullclaw/config.json`) with Telegram bot @Nullclaw_culi_bot; SSH user `trongtan`. Confirmed switch to 9router provider (same as Pi nanobot) on 2026-05-29.
- **Mem0** — Self-hosted via Docker on TVBox (192.168.2.237:8888). Agents share memory via `user_id` separation. Architecture: FastAPI + PostgreSQL (pgvector). Authentication via `X-API-Key` header.

## Network Nodes

| Node | IP | Role |
|------|----|------|
| Pi (main) | 192.168.2.21 (wlan) / 192.168.2.22 (eth) | nanobot + hermes-gateway + 9router (skill: https://raw.githubusercontent.com/decolua/9router/refs/heads/master/skills/9router/SKILL.md) |
| TV Box | 192.168.2.237 | Hermes + nanobot; SSH port 2104; Docker running Mem0 server on port 8888 |
| Orangepi | 192.168.2.91 | nullclaw agent |

## Scheduled Jobs

- **kudu-cleanup-12h** (id a031a684): Runs `kudu-cli.sh scan --all --clean` at 06:00 and 18:00 daily (Asia/Ho_Chi_Minh) for APT/font cache cleanup. Each run scans ~164 MB (APT cache ~160 MB, temp files, font caches) but cleans only ~2.5–2.8 MB; 250+ items skipped due to in-use files (/tmp sockets, systemd-private dirs) and permission denied.
- **ocx-reboot**: Runs `ocx` at `@reboot` and reports result via cron.

## n8n Handover Document Automation

- User building n8n workflow for handover document automation using Mistral OCR + Word template `bbbg.docx`
- Reference repo: https://github.com/Trantrongtan2000/bbbgtaq7 (Streamlit app for handover document processing)
- n8n workflow skeleton at `/home/tan/.nanobot/workspace/n8n-bbbgtaq7-workflow.json`; template `bbbg.docx` in workspace
- `python-docx` v1.2.0 installed in environment
- Schema JSON (theo bbbgtaq7): `shd`, `shd_type`, `cty`, `ds[]` với `ttb`, `model`, `ref`, `hang`, `nsx`, `dvt`, `sl`, `seri`, `pk[]`
- Extractor (`core/extractor.py`) hai bước: OCR/PDF → chat JSON parsing, key rotation + retry khi quota error
- Grouping: gộp thiết bị theo tên chuẩn hóa + model + REF + hãng + nước SX + DVT + phụ kiện; cộng SL, gom seri
- Workflow skeleton hiện không khớp repo: dùng `devices/name/serial` thay vì `ds/ttb/seri`, thiếu grouping, gọi sai endpoint Mistral OCR (`/v1/chat/completions` thay vì `/v1/ocr`), phụ thuộc service DOCX nội bộ chưa tồn tại

## References & Learning

- **ai-agent-book** (`bojieli/ai-agent-book`) — 10 chương, 92 thí nghiệm; công thức Agent = LLM + Context + Tools. Bản HTML tương tác đa ngôn ngữ tại https://bojieli.github.io/ai-agent-book/
- **OpenScience** (`@synsci/openscience`) — AI workbench mã nguồn mở Apache 2.0 cho nghiên cứu khoa học: 290+ skills, 30+ CSDL, workspace trên trình duyệt, hỗ trợ nhiều model providers.
- **DigitalPlat FreeDomain** — Miễn phí domain (5 TLD: .DPDNS.ORG, .US.KG, .QZZ.IO, .XX.KG, .QD.JE). DigitalPlat chỉ xử lý đăng ký + delegate NS; tất cả DNS records quản lý ở external authoritative DNS. Dashboard: dash.domain.digitalplat.org. Telegram chính thức bị compromise — không tin cậy comms Telegram. Repo: DigitalPlatDev/Domain-OSS. Workflow MEIMS: đăng ký tài khoản, chọn domain (vd `tbytq7.us.kg`), connect NS đến Cloudflare/VPS, cấu hình DNS trỏ MEIMS backend, HTTPS qua Let's Encrypt.
- **OpenSpace** (`HKUDS/OpenSpace`) — Skill Management Layer cho AI Agents: 6 MCP tools (`cloud_auth_flow`, `execute_task`, `search_skills`, `cloud_browse_skills`, `fix_skill`, `upload_skill`), 2 host skills (`skill-discovery`, `delegate-task`), hỗ trợ stdio/SSE/streamable-http. User từ chối áp dụng cho workflow bảo trì thiết bị.


---
*This file is automatically updated by nanobot when important information should be remembered.*

## Constraints & Workarounds

- Lacks Docker installation – critical dependency for TencentDB-Agent-Memory
- 1.8Gi RAM/319Mi available – hardware constraint limiting Docker-based solutions
- Proposed alternatives: wiki workflow, MCP tools, qltb-asset-management – actionable workarounds

