# Hướng dẫn kết nối Notion

## 1. Tạo Notion Integration (Token)

1. Vào https://www.notion.so/my-integrations → **New integration**
2. Đặt tên (vd: `nanobot-mcp`), chọn workspace
3. Chọn capabilities cần thiết:
   - **Read content** — đọc page/database
   - **Update content** — ghi/sửa nội dung
   - **Insert content** — thêm block/page
4. Copy **Internal Integration Token** (dạng `ntn_...` hoặc `secret_...`) — giữ bí mật, không đưa vào chat/wiki/commit

## 2. Share trang với Integration

Mỗi page/database muốn bot truy cập phải share riêng:

1. Mở page trong Notion → **•••** (menu trên cùng) → **Connections** → **Connect to**
2. Chọn integration vừa tạo (vd: `nanobot-mcp`)
3. Làm lại cho từng page/database cần dùng

## 3. Cấu hình MCP server (nanobot)

Thêm vào cấu hình MCP của nanobot (ví dụ `.env` hoặc config gateway):

```env
NOTION_API_KEY=ntn_xxx
```

Hoặc dạng MCP config JSON:

```json
{
  "mcpServers": {
    "notion": {
      "command": "npx",
      "args": ["-y", "@notionhq/notion-mcp-server"],
      "env": {
        "NOTION_API_KEY": "ntn_xxx"
      }
    }
  }
}
```

Khởi động lại nanobot sau khi thêm: `systemctl --user restart nanobot`

## 4. Kiểm tra kết nối

- Gửi lệnh `/status` hoặc hỏi bot: *"kiểm tra kết nối Notion"*
- Bot trả về danh sách workspace/trang truy cập được là thành công

## 5. Lấy Page ID / Database ID

Mỗi trang Notion có ID dạng UUID:

- Mở trang → URL có dạng `https://www.notion.so/ten-trang-3ae0c9978722819f9ad1d12bdb3e1312`
- Phần `3ae0c9978722819f9ad1d12bdb3e1312` chính là **page ID**
- Database ID: vào database → URL tương tự, lấy UUID ở giữa

## 6. Lưu ý bảo mật

- Không bao giờ paste token vào chat, wiki, memory, commit
- Token có quyền đọc/ghi toàn bộ page được share — chỉ share đúng trang cần thiết
- Muốn thu hồi: https://www.notion.so/my-integrations → **Delete/Revoke**

## 7. Lỗi thường gặp

| Lỗi | Nguyên nhân | Xử lý |
|------|-------------|-------|
| `404 page not found` | Chưa share page với integration | Share lại ở bước 2 |
| `400 validation_error` | Gọi sai endpoint (vd: tạo database qua API cũ) | Dùng đúng endpoint / bản API mới |
| `401 unauthorized` | Token sai hoặc hết hạn | Tạo lại token |
| `409 conflict` | Vượt giới hạn block/dung lượng | Giảm nội dung, tạo database thay page |
