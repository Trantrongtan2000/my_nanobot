# User Profile

## Basic Information

- **Name**: tan (Telegram: @trongtan2104)
- **Telegram chat ID**: `1449852069`
- **Role**: Kỹ sư thiết bị y tế (Biomedical Equipment Engineer)
- **Main project**: MEIMS / QLTB — phần mềm Quản lý thiết bị y tế
- **Languages**: Vietnamese (primary), technical English
- **Local workstation**: Ubuntu 24.04 x86_64 (groups: ollama, docker, render, wireshark)
- **Remote agent host**: Raspberry Pi `192.168.2.21` (wlan) / `192.168.2.22` (eth), user `tan`

## Domain Knowledge

### Medical equipment management
- Lifecycle: tiếp nhận → kiểm định → bảo trì/định kỳ → cập nhật hồ sơ → thanh lý
- Standards: ISO 13485, ISO 14971, IEC 60601, Circular 30/2015/TT-BYT, QCVN
- Classification: Groups A/B/C (risk), specialty (Imaging, Lab, ICU, OR, …)
- KPIs: uptime, MTBF, MTTR, PM compliance, calibration traceability
- Records: DMR, DHR, service history, calibration certificates

### MEIMS modules (in progress / built)
- QT.04 Commissioning (wizard + OCR prefill)
- QT.05 Incident (+ severity/SLA, RACI stubs)
- QT.06 Maintenance
- QT.07 Disposal
- QT.08 Transfer (state machine)
- Auth/RACI guard (spec + partial backend; frontend enforcement incomplete)
- OCR batch BV Quận 7: large PDF corpus, Mistral OCR scripts — always check manifest/progress before restarting

### Software interests
- CLI tooling & automation, CDP/Electron harnesses
- Agent harness design, local-first LLM Wiki
- 9router / nanobot / opencode stack on Pi
- Remotion for video creation projects

## Preferences

### Communication
- Casual + technical biomedical terms
- **Brief and concise** by default; detail only when asked
- Expert technical level — no beginner hand-holding
- **Thông báo kế hoạch trước khi chạy**: Luôn nêu 1 câu ngắn gọn kế hoạch sẽ làm gì TRƯỚC KHI thực thi bất kỳ tool/lệnh nào.
- Vietnamese default
- **No heartbeat status reports** — disable all heartbeat reporting
- Docx documents: use Heading 1/2, bullet lists, centered titles, italic figure captions

### Response length
- Telegram: 2–3 paragraphs typical
- Tables when comparing ≥3 fields
- No walls of logs — path + short excerpt

## Work Context

- Pi services: `nanobot`, `9router` (`:20128`), `9router-tunnel` (cloudflared quick URL changes on restart)
- Nanobot workspace on Pi: `/home/tan/.nanobot/workspace`
- LLM via 9router model `orfree` (fallback `kilonek`)
- Notion + TinyFish MCP enabled when keys present
- Prior Telegram history with @Pino4_bot loaded into sessions/history for continuity

## Topics of Interest

- Medical equipment lifecycle & regulatory compliance (VN BYT + ISO)
- Calibration & PM optimization, asset tracking
- CLI / agent automation, LLM Wiki knowledge bases
- Hospital ops for BV Quận 7 equipment docs/OCR
- Maintenance checklist generation (DOCX templates, Excel data mapping)

## Special Instructions

- Respond in Vietnamese unless asked otherwise
- No permission theater for single-step safe tasks
- Never store passwords or API tokens in this file
- Use LLM Wiki pattern (raw → entities/concepts/synthesis → index/log)
- Correct Vietnamese biomedical terms: thiết bị y tế, kiểm định, bảo trì dự phòng, hồ sơ thiết bị, etc.
- Do not invent device counts, PO numbers, or regulatory conclusions
- Greeting-only messages: one short reply, no tool spam
