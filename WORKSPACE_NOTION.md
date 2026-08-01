# 🏠 Workspace Notion — Hướng dẫn cho Agent

## Thông tin kết nối

**Notion Token:**
```
ntn_b33821509461YDidRoXi87DjYhyxp3c4CkSYr1PrZkL9x3
```

**Cách dùng:**
```bash
export NOTION_TOKEN="ntn_b33821509461YDidRoXi87DjYhyxp3c4CkSYr1PrZkL9x3"
# hoặc thêm vào ~/.bashrc / .nanobot/.env
```

**MCP Config (nanobot):**
```json
{
  "mcpServers": {
    "notion": {
      "command": "npx",
      "args": ["-y", "@notionhq/notion-mcp-server"],
      "env": { "NOTION_TOKEN": "${NOTION_TOKEN}" },
      "tool_timeout": 60
    }
  }
}
```

---

## Tổng quan cấu trúc

### Parent page: Quick Note
**ID:** `de3a34a2-81ce-4c49-84cf-b6b69a507fa6`  
**URL:** https://www.notion.so/de3a34a281ce4c4984cfb6b69a507fa6

### Home hub
**ID:** `3a30c997-8722-817d-b8d6-fea5c234bd61`  
**URL:** https://www.notion.so/3a30c9978722817db8d6fea5c234bd61

### Category folders (dưới Home)

| Emoji | Thư mục | Page ID | Số note |
|---|---|---|---|
| 📚 | 01 · Học tập / IT | 3a30c997-8722-8197-9a8b-dab964819b6f | 9 |
| 🤖 | 02 · AI Agent & Tools | 3a30c997-8722-81e3-bdd5-bc6a1cf3b728 | 7 |
| 🖥️ | 03 · Homelab & Hardware | 3a30c997-8722-8136-9b8f-e19ec0a22c03 | 5 |
| 🏥 | 04 · Công việc / Kiểm định | 3a30c997-8722-8115-9a79-daad9d142af8 | 1 |
| 🔑 | 05 · Secrets & Config | 3a30c997-8722-81e0-b52a-dec6b7a9f12d | 2 |
| 📎 | 06 · Tài liệu tham khảo | 3a30c997-8722-819e-8da3-e4d16857d95b | 2 |
| 📥 | 99 · Inbox | 3a30c997-8722-8189-801d-f21517a3439e | 0 |

---

## Quy tắc Notion Presentation

Khi ghi nội dung lên Notion (MCP tool hoặc API):

### 1. Dùng Markdown API (ưu tiên)
```bash
# Tạo page với markdown body
POST /v1/pages
{
  "parent": {"page_id": "<parent-id>"},
  "properties": {"title": [{"text": {"content": "Title"}}]},
  "markdown": "# Heading\n\n- list\n**bold** [link](url)"
}

# Cập nhật nội dung
PATCH /v1/pages/{id}/markdown
{
  "type": "replace_content",
  "replace_content": {"new_str": "nội dung markdown mới"}
}
```
Header: `Notion-Version: 2026-03-11`

### 2. Cấu trúc nội dung
- `#` / `##` / `###` cho section (max H3)
- `-` / `1.` cho list
- `**bold**` cho label
- `` `code` `` cho đường dẫn / ID
- Link: `[label ngắn](url)` — không paste URL thô
- Table markdown khi so sánh ≥3 field
- `---` divider hạn chế

### 3. Title
- ≤80 ký tự, không URL thô
- `httpsgithub.comfoo…` → `github.com · foo`
- `Scribd.pdf (1.27 MB)` → bỏ suffix
- LaTeX → `Công thức / ghi chú toán`

### 4. Bulk Import UpNote
```bash
export NOTION_TOKEN="ntn_b33821509461YDidRoXi87DjYhyxp3c4CkSYr1PrZkL9x3"
python3 /home/tan/.nanobot/workspace/import_upnote.py
```
Script đọc HTML → Markdown → Notion (tự động replace nếu page đã tồn tại).

### 5. Kiểm tra sau ghi
```bash
# Đọc markdown để verify
GET /v1/pages/{id}/markdown
```
Nếu cấu trúc flat/broken → replace bằng markdown API, không append block lẻ.

### 6. Tuyệt đối không paste secrets vào Notion page
Token / API key chỉ để trong **🔑 Secrets & Config** folder.

---

## Script đã dùng

### import_upnote.py
- Đường dẫn: `/home/tan/.nanobot/workspace/import_upnote.py`
- Chức năng: Đọc 26 file HTML từ UpNote export, convert thành Notion page với markdown sạch
- Pipeline: UpNote HTML → HTMLParser → Markdown → Notion POST page with markdown body
- Hỗ trợ: heading, list, bold, italic, link, code block, table, divider
- Tự động clean title (URL, pdf noise, fbclid tracking)
- Replace markdown body cho page đã tồn tại (không duplicate)

### Cấu trúc Notion hiện tại

```
NOTION WORKSPACE
├── Quick Note (inbox gốc)
│   └── 🏠 Home (hub trung tâm)
│       ├── 📚 Học tập / IT (9 notes)
│       │   ├── BÀI 1 TÍNH TOÁN ĐỊA CHỈ IP VÀ CHIA MẠNG CON
│       │   ├── DÀN Ý BÀI GIẢNG NHẬP MÔN LẬP TRÌNH (BUỔI 1)
│       │   ├── DÀN Ý BÀI GIẢNG NHẬP MÔN LẬP TRÌNH - BUỔI 3
│       │   ├── DÀN Ý BÀI GIẢNG THUẬT TOÁN & BIỂU DIỄN THUẬT TOÁN
│       │   ├── Cheat Sheet IT005 — Mạng máy tính
│       │   ├── Thuyết trình Toán
│       │   ├── IT001 — Buổi 4 (tóm tắt)
│       │   ├── Công thức / ghi chú toán
│       │   └── Đề cương ôn Cơ sở dữ liệu
│       ├── 🤖 AI Agent & Tools (7 notes)
│       │   ├── Hệ sinh thái AI Agent & Multi-Agent
│       │   ├── Claw đang tìm hiểu
│       │   ├── Prompt dài vs Skills
│       │   ├── Skill
│       │   ├── NotebookLM — Hướng dẫn TV
│       │   ├── Tự động accept
│       │   └── Workflow
│       ├── 🖥️ Homelab & Hardware (5 notes)
│       │   ├── Máy chơi game
│       │   ├── SBC in home
│       │   ├── Cuộn chuột mượt
│       │   ├── GameHub Lite (releases)
│       │   └── TensorLake
│       ├── 🏥 Công việc / Kiểm định (1 note)
│       ├── 🔑 Secrets & Config (2 notes)
│       │   ├── API key
│       │   └── Pastebin note
│       └── 📎 Tài liệu tham khảo (2 notes)
│           ├── Tài liệu Harvard
│           └── Từ khóa thường dùng
│
├── Getting Started (template — không đụng)
├── Personal Home (template — không đụng)
├── Reading List (template — không đụng)
│
└── Databases (template Notion mặc định)
    ├── People
    ├── Tasks
    ├── Projects
    ├── Class Notes
    ├── Media
    ├── Journal
    ├── Travel Plans
    ├── Recipes
    └── Task List
```

---

## Lưu ý

- **Token này là internal integration**, có quyền đọc/ghi toàn bộ workspace. Chia sẻ cẩn thận.
- Move page API (PATCH parent) không hoạt động thực tế với internal integration → copy + archive là workaround.
- Version header `2026-03-11` cho markdown endpoints, `2022-06-28` cho block/rest API cũ.
- MCP server `@notionhq/notion-mcp-server` expose 24 tools.

---

*Generated by nanobot · 2026-07-20*
