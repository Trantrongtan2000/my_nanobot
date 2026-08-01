---
name: subagent-delegation
description: Subagent delegation workflow — spawn background subagents for heavy tasks, review results, fix incomplete work. Use for multi-step tasks that would take more than one tool round.
---

# Subagent Delegation Workflow

## Khi nào dùng `spawn`

Dùng `spawn` tool cho các task:
- **Nặng thời gian**: web search, multi-file analysis, long research, Notion queries, OCR
- **Nhiều bước**: code changes, batch processing, multi-file edits
- **Có thể chạy độc lập**: không cần user input trung gian

**Đừng dùng** cho: read 1 file, answer trực tiếp, simple lookup

## Cách viết task description

Task phải **tự chứa** (self-contained):
- Mô tả rõ output cuối cùng cần gì
- Liệt kê file paths, tools, constraints
- Chỉ định format kết quả

Ví dụ:
```
Task: Analyze all Python files in /home/tan/project/src/ for security vulnerabilities.
- Check for SQL injection, XSS, hardcoded secrets
- Output: JSON list of findings with file:line and severity
- Use grep tool for pattern matching
- Report in Vietnamese
```

## Workflow 3 bước

### 1. Spawn subagent
```
spawn(task="...", label="security-audit")
```
- `label` ngắn gọn để hiển thị
- Nhận thông báo "đã giao subagent xử lý, sẽ báo khi xong"

### 2. Review kết quả
Subagent sẽ báo về khi hoàn thành. Kiểm tra:
- **Đủ output?** — có đáp án đầy đủ chưa?
- **Đúng format?** — format yêu cầu có đúng không?
- **Có lỗi?** — tool failures, missing data?

### 3. Fix nếu chưa hoàn thành
Nếu kết quả chưa đủ:
- **Phân tích nguyên nhân**: subagent miss gì? thiếu context?
- **Spawn lại** với task mở rộng: thêm context, constraint, hoặc cách tiếp cận khác
- **Hoặc tự làm**: nếu task nhỏ, chuyển sang dùng tool trực tiếp

## Concurrency

- `maxConcurrentSubagents: 1` (đã cấu hình) — chỉ chạy 1 subagent tại thời điểm
- Nếu đạt giới hạn: chờ subagent hiện tại hoàn thành rồi mới spawn mới

## Ví dụ thực tế

**Task nhiều bước:**
1. `spawn(task="Research ISO 13485 medical device software requirements from official sources, create wiki entity pages with citations")`
2. Nhận kết quả: 5 entity pages created, 3 missing citations
3. `spawn(task="Add citations to the 3 missing entity pages: wiki/entities/iso_13485_*.md. Use sources from wiki/raw/")`
4. Nhận kết quả: all citations added
5. Báo user: "Đã tạo 5 entity pages ISO 13485, đã bổ sung citations"
