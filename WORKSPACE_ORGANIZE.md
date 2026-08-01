# 🏠 Workspace Reorganization Log

**Ngày:** 2026-07-20  
**Người thực hiện:** nanobot (trongtan2104)  

## Tóm tắt

- Import 26 UpNote HTML note → Markdown → Notion page
- Tái cấu trúc workspace thành hub + category folders
- Archive nội dung rác cũ

## Cấu trúc mới

```
🏠 Home (de3a34a2… parent Quick Note)
├── 📚 01 · Học tập / IT (9 notes)
├── 🤖 02 · AI Agent & Tools (7 notes)
├── 🖥️ 03 · Homelab & Hardware (5 notes)
├── 🏥 04 · Công việc / Kiểm định (1 note)
├── 🔑 05 · Secrets & Config (2 notes)
├── 📎 06 · Tài liệu tham khảo (2 notes)
└── 📥 99 · Inbox (0 notes)
```

## Scripts

- `/home/tan/.nanobot/workspace/import_upnote.py` — HTML → Markdown → Notion
  - Chạy: `python3 /home/tan/.nanobot/workspace/import_upnote.py`
  - Cần: `NOTION_TOKEN` env (xem `.nanobot/config.json`)

## MCP Setup

Nanobot đã kích hoạt:

```json
"tools": {
  "mcpServers": {
    "tinyfish": { "command": "python3", "args": ["…/tinyfish_mcp.py"], "env": {"TINYFISH_API_KEY":"…"} },
    "notion": { "command": "npx", "args": ["-y","@notionhq/notion-mcp-server"], "env": {"NOTION_TOKEN":"${NOTION_TOKEN}"} }
  }
}
```

Token lấy từ env: `NOTION_TOKEN` — set trong `~/.bashrc` hoặc `.nanobot/.env`.

## Quy ước Notion

Xem AGENTS.md phần “Notion Presentation Rules”.

## Đã xong

- 26/26 note đã chuyển thành công
- 0 lỗi
- 8 page rác đã archive (workspace-level garbage)
