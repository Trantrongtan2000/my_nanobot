# Skill: wiki-manager

## Mô tả
Agent quản lý wiki thiết bị y tế - tự động xử lý, kiểm tra, đồng bộ với Notion.

## Công dụng
- Tự động tạo/cập nhật entity thiết bị từ OCR output
- Kiểm tra và sửa lỗi wiki (broken links, missing citations)
- Đồng bộ dữ liệu với Notion
- Ghi log thay đổi vào history.jsonl

## Sử dụng
```bash
python3 ~/.nanobot/workspace/skills/wiki-manager/scripts/wiki_manager.py --action <action> [options]
```

## Actions
- `process`: Xử lý file organized.md → tạo entity
- `verify`: Kiểm tra toàn bộ wiki
- `sync-notion`: Đồng bộ với Notion
- `status`: Kiểm tra trạng thái wiki

## Dependencies
- `verify_entity.py`
- `nanobot_self_improve.py`
- Notion MCP (nếu có)