---
name: ocr-pipeline
description: Auto-OCR pipeline for images and PDFs sent via Telegram or in workspace. Uses Mistral OCR. Use when processing document images, PDF invoices, equipment manuals, or calibration certificates.
---

# Image & Document Handling (auto-OCR)

## Auto-OCR Flow

- User sends image(s) → **auto OCR** qua `doc-ocr-organize` skill trước khi trả lời. Không đợi nhắc.
- PDF/image trong workspace, hoặc ảnh nhúng trong tin nhắn → pipeline: `doc_ocr_organize.py --no-organize` → đọc kết quả → nếu có thông tin thiết bị mới → cập nhật wiki entities.
- `MISTRAL_API_KEY` đã có trong `.env`; export vào env trước khi gọi script.
- Script timeout ≥ 180s cho PDF nhiều trang.
- Sau OCR: tóm tắt nội dung + path file output + cập nhật wiki nếu phát hiện thiết bị mới.
- Chỉ bỏ qua OCR nếu ảnh là sticker, meme, hoặc user chủ động nói "không cần OCR".

## Commands

```bash
# OCR single image/PDF
python3 ~/.nanobot/workspace/skills/doc-ocr-organize/scripts/doc_ocr_organize.py <path> --no-organize

# Batch OCR for BV Quận 7 corpus
# Check progress/manifest before restarting
python3 ~/.nanobot/workspace/skills/doc-ocr-organize/scripts/doc_ocr_organize.py <dir> --batch
```
