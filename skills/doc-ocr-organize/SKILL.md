---
name: doc-ocr-organize
description: >
  OCR PDF/image documents for work (biên bản, giấy tờ thiết bị y tế).
  PDF is always rendered to page images first; OCR extracts text; then
  mistral-small-2603 reorganizes markdown if structure is messy.
  Use when user asks OCR, đọc PDF/ảnh, trích biên bản, sắp xếp lại nội dung OCR.
---

# doc-ocr-organize

Pipeline bắt buộc:

1. **PDF → ảnh** (mỗi trang PNG) — luôn render để lưu vết + OCR ổn định.
2. **OCR** lấy text/markdown thô (`mistral-ocr-latest`).
3. **Organize** bằng chat model **`mistral-small-2603`** — sắp xếp lại nếu layout/OCR lộn xộn; không bịa số liệu.

## Script

```bash
python3 ~/.nanobot/workspace/skills/doc-ocr-organize/scripts/doc_ocr_organize.py \
  /path/to/file.pdf \
  -o /tmp/out_ocr \
  --dpi 200 \
  --organize-model mistral-small-2603
```

Image:

```bash
python3 ~/.nanobot/workspace/skills/doc-ocr-organize/scripts/doc_ocr_organize.py scan.png -o /tmp/out_img
```

Flags hữu ích:

| Flag | Ý nghĩa |
|------|---------|
| `--no-organize` | Chỉ OCR, không gọi small model |
| `--ocr-mode images` | OCR từng trang ảnh (chậm, khi document mode lỗi) |
| `--ocr-mode document` | (default) OCR cả PDF một request + vẫn render ảnh |
| `--via-orfree` | Organize qua 9router `ORFREE_BASE` (default `http://127.0.0.1:20128/v1`) |
| `--hint "..."` | Gợi ý ngữ cảnh (vd. biên bản kiểm định BV Q7) |
| `--dpi 200` | Độ phân giải render PDF |

## Env

```bash
export MISTRAL_API_KEY=...          # bắt buộc cho OCR (+ organize mặc định)
# optional rotate:
export MISTRAL_API_KEY_2=...
export MISTRAL_API_KEY_3=...

# nếu --via-orfree:
export ORFREE_BASE=http://127.0.0.1:20128/v1
export NANOBOT_ORFREE_KEY=sk-...    # hoặc ORFREE_API_KEY
```

Trên Pi nanobot: thêm `MISTRAL_API_KEY` vào `~/.nanobot/env` nếu chưa có.

## Output (`-o DIR`)

- `images/page-001.png` … — trang đã render
- `ocr_raw.json` / `ocr_raw.md` — OCR thô
- `organized.md` — bản đã sắp xếp (hoặc copy thô nếu `--no-organize`)
- `meta.json` — đường dẫn + model dùng

## Agent rules

- Chạy script bằng `exec` (timeout ≥ 180s cho PDF nhiều trang).
- Sau khi xong: `read_file` `organized.md` (hoặc head) rồi trả user tóm tắt + path.
- Không paste API key. Không bịa serial/ngày nếu OCR không có.
- PDF scan xấu: thử `--dpi 300` hoặc `--ocr-mode images`.
- Prefer skill này thay vì tự viết one-off OCR mỗi lần.

## Dependencies

- `pdftoppm` (poppler-utils) **hoặc** `pymupdf`
- `requests`, optional `Pillow`
- Network tới `api.mistral.ai` (OCR)
