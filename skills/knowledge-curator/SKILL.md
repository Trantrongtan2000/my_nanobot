# Skill: knowledge-curator

## Mô tả
Agent phụ trách mảng kiến thức. Mỗi khi user gửi link hoặc yêu cầu tìm hiểu, tự động ingest vào wiki theo LLM Wiki 3-layer pattern, trích xuất ý tưởng cải thiện nanobot/MEIMS.

## Trigger
- User gửi URL/link
- User yêu cầu "tìm hiểu", "nghiên cứu", "kiểm tra" một chủ đề
- User gửi tài liệu PDF/ảnh cần OCR + ingest

## Workflow

### 1. Ingest nguồn
- URL → fetch content qua `tinyfish_fetch_content` hoặc `web_fetch`
- PDF/ảnh → OCR qua `doc-ocr-organize` skill
- Lưu bản gốc vào `wiki/raw/` (markdown hoặc JSON), ghi metadata: URL/path, ngày ingest, loại nguồn

### 2. Phân loại
Gán 1 trong các loại:
- `regulation` — quy định, thông tư, QCVN
- `standard` — ISO, IEC, ANSI, AAMI
- `manual` — tài liệu kỹ thuật thiết bị
- `service-record` — biên bản, chứng từ
- `research` — bài báo, whitepaper
- `vendor` — thông tin nhà sản xuất
- `user-decision` — quyết định của user
- `tool` — công cụ, framework, library

### 3. Trích xuất
Từ nội dung, rút ra:
- **Claims** — khẳng định có thể kiểm chứng
- **Entities** — thiết bị, tổ chức, tiêu chuẩn, vendor
- **Concepts** — workflow, metric, data model, compliance rule
- **Requirements** — yêu cầu bắt buộc
- **Risks** — rủi ro, cảnh báo
- **Open questions** — câu hỏi chưa có câu trả lời

### 4. Cập nhật wiki
- Kiểm tra `wiki/index.md` trước
- Tạo/cập nhật page trong `wiki/entities/`, `wiki/concepts/`, `wiki/synthesis/`
- Thêm YAML frontmatter (type, title, status, sources, updated, tags, refs)
- Cross-link với `[[wikilinks]]`
- Cập nhật `wiki/index.md` (1 link + 1 dòng tóm tắt)
- Append vào `wiki/log.md` (ngày + hành động + file thay đổi)

### 5. Ý tưởng cải thiện
Nếu nội dung có ý tưởng áp dụng cho nanobot/MEIMS:
- Tạo/cập nhật `wiki/synthesis/nanobot_improvements.md`
- Ghi: nguồn, ý tưởng, cách áp dụng, ưu tiên (high/medium/low)
- Nếu ý tưởng đủ cụ thể → đề xuất tạo skill mới hoặc cập nhật AGENTS.md

### 6. Báo cáo
Trả về user:
- Tóm tắt nội dung (2-3 câu)
- Đường dẫn file wiki đã tạo/cập nhật
- Ý tưởng cải thiện (nếu có)
- Open questions (nếu có)

## Quy tắc
- Không bao giờ ghi đè nguồn gốc trong `wiki/raw/`
- Mọi claim phải có citation (path, URL, section)
- Không invent thông tin — nếu không có trong nguồn, ghi "chưa xác định"
- Contradictions → `status: disputed`, không xóa silently
- Không paste secrets vào wiki
- Wiki là compounding artifact — cập nhật page cũ thay vì tạo trùng
