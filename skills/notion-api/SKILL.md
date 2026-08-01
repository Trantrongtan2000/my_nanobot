---
name: notion-api
description: Notion API presentation rules and workspace map. Use when creating, updating, or querying Notion pages via the Notion MCP server or REST API.
---

# Notion API Rules

## Presentation Rules

1. Prefer markdown page API over raw block JSON:
   - Create: `POST /v1/pages` with `"markdown": "..."`.
   - Replace: `PATCH /v1/pages/{id}/markdown` with `{"type":"replace_content","replace_content":{"new_str":"..."}}`.
   - Header `Notion-Version: 2026-03-11` for markdown endpoints.
2. Structure: `#`/`##`/`###` (max H3); lists; `**bold**` labels; `` `code` `` for IDs/paths; markdown tables for ≥3-field compares; sparse `---`.
3. Titles ≤80 chars; clean URL/PDF dumps into short human labels.
4. Bulk UpNote HTML: `python3 /home/tan/.nanobot/workspace/import_upnote.py` (needs `NOTION_TOKEN`).
5. After write: verify retrieve-markdown; replace if flat/broken.
6. Never paste secrets into Notion pages outside Secrets folder.
7. **Never share Notion tokens in chat, code, or guides** — users must obtain personal tokens from Notion integrations and store them in config files.

## Workspace Map

Parent **Quick Note**: `de3a34a2-81ce-4c49-84cf-b6b69a507fa6`
Home hub: `3a30c997-8722-817d-b8d6-fea5c234bd61`

| Folder | Page ID |
|--------|---------|
| 01 Học tập / IT | `3a30c997-8722-8197-9a8b-dab964819b6f` |
| 02 AI Agent & Tools | `3a30c997-8722-81e3-bdd5-bc6a1cf3b728` |
| 03 Homelab & Hardware | `3a30c997-8722-8136-9b8f-e19ec0a22c03` |
| 04 Công việc / Kiểm định | `3a30c997-8722-8115-9a79-daad9d142af8` |
| 05 Secrets & Config | `3a30c997-8722-81e0-b52a-dec6b7a9f12d` |
| 06 Tài liệu tham khảo | `3a30c997-8722-819e-8da3-e4d16857d95b` |
| 99 Inbox | `3a30c997-8722-8189-801d-f21517a3439e` |

Full guide: `WORKSPACE_NOTION.md` in workspace. Never paste tokens into Notion pages outside Secrets folder.
User-facing Vietnamese guide: `huong-dan-ket-noi-notion.md` in workspace (sent via Telegram 2026-08-01).

## Authentication Setup

To obtain a Notion integration token:
1. Go to https://www.notion.so/my-integrations
2. Click "New integration"
3. Copy the "Internal Integration Token"
4. Share the target Notion page with the integration (via Share → Invite)
5. Store the token securely (e.g., in environment variable or secrets manager)

The token is required for scripts like `import_upnote.py` and Notion MCP server operation.

**Security rule:** never share the Notion token in chat, code, wiki, memory, or commits — instruct users to create their own personal token and keep it in a config file / secrets manager.
