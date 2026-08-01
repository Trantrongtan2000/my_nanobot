---
name: doc-ocr-organize
description: >
  OCR PDF/image documents for work (biên bản, giấy tờ thiết bị y tế).
  PDF is always rendered to page images first; OCR extracts text; then
  mistral-small-2603 reorganizes markdown if structure is messy.
  Use when user asks OCR, đọc PDF/ảnh, trích biên bản, sắp xếp lại nội dung OCR,
  mistral ocr, document AI.
---

# doc-ocr-organize

Pipeline bắt buộc:

1. **PDF → ảnh** (mỗi trang PNG) — luôn render để lưu vết + OCR ổn định.
2. **OCR** lấy text/markdown thô (`mistral-ocr-latest` / `MISTRAL_OCR_MODEL`).
3. **Organize** bằng chat model **`mistral-small-2603`** — sắp xếp lại nếu layout/OCR lộn xộn; không bịa số liệu.

## API key (bắt buộc)

Script đọc key theo thứ tự:

1. Process env: `MISTRAL_API_KEY` (+ optional `MISTRAL_API_KEY_2`, `MISTRAL_API_KEY_3`)
2. Auto-load file (nếu env trống): `C:\Users\tantt\.nanobot\.env` hoặc `~/.nanobot/.env` / `~/.nanobot/env`

Trên máy này key nằm trong `C:\Users\tantt\.nanobot\.env`:

```env
MISTRAL_API_KEY=...
MISTRAL_OCR_MODEL=mistral-ocr-latest
MISTRAL_ORGANIZE_MODEL=mistral-small-2603
```

Gateway phải load `.env` (wrapper `start-gateway.ps1`) để `exec` kế thừa env. Nếu vẫn báo missing key: restart gateway hoặc set User env `MISTRAL_API_KEY`.

**Không** hardcode key trong script/skill. **Không** paste key vào chat/Telegram/Notion.

Endpoint: `https://api.mistral.ai/v1/ocr` (docs: Document AI / OCR Processor).

## Script (Windows)

```powershell
python C:\Users\tantt\.nanobot\workspace\skills\doc-ocr-organize\scripts\doc_ocr_organize.py `
  "D:\path\to\file.pdf" `
  -o C:\Users\tantt\.nanobot\workspace\wiki\raw\ocr_out `
  --dpi 200 `
  --organize-model mistral-small-2603
```

Image:

```powershell
python C:\Users\tantt\.nanobot\workspace\skills\doc-ocr-organize\scripts\doc_ocr_organize.py `
  scan.png -o C:\Users\tantt\.nanobot\media\ocr_img
```

Linux/Pi (legacy):

```bash
python3 ~/.nanobot/workspace/skills/doc-ocr-organize/scripts/doc_ocr_organize.py \
  /path/to/file.pdf -o /tmp/out_ocr --dpi 200
```

## Flags

| Flag | Ý nghĩa |
|------|---------|
| `--no-organize` | Chỉ OCR, không gọi small model |
| `--ocr-mode images` | OCR từng trang ảnh (chậm, khi document mode lỗi) |
| `--ocr-mode document` | (default) OCR cả PDF một request + vẫn render ảnh |
| `--via-orfree` | Organize qua 9router `ORFREE_BASE` (default `http://127.0.0.1:20128/v1`) |
| `--hint "..."` | Gợi ý ngữ cảnh (vd. biên bản kiểm định BV Q7) |
| `--dpi 200` | Độ phân giải render PDF |

## Env reference

```text
MISTRAL_API_KEY          # required for OCR (+ organize default path)
MISTRAL_API_KEY_2/3      # optional rotate on 429
MISTRAL_OCR_MODEL        # default mistral-ocr-latest
MISTRAL_ORGANIZE_MODEL   # default mistral-small-2603
MISTRAL_API_URL          # default https://api.mistral.ai/v1
ORFREE_BASE              # if --via-orfree
ORFREE_API_KEY / NANOBOT_ORFREE_KEY
```

## Output (`-o DIR`)

- `images/page-001.png` … — trang đã render
- `ocr_raw.json` / `ocr_raw.md` — OCR thô
- `organized.md` — bản đã sắp xếp (hoặc copy thô nếu `--no-organize`)
- `meta.json` — đường dẫn + model dùng

## Agent rules

- Chạy script bằng `exec` (timeout ≥ 180s cho PDF nhiều trang). Trên Windows: `python` (không bắt buộc `python3`).
- Trước khi chạy: nếu lo missing key, kiểm tra nhanh  
  `python -c "from pathlib import Path; import os; p=Path.home()/'.nanobot'/'.env'; print('env_file', p.is_file()); print('key_set', bool(os.environ.get('MISTRAL_API_KEY')))"`  
  — script tự load `.env` nên thường không cần export tay.
- Sau khi xong: `read_file` `organized.md` (hoặc head) rồi trả user tóm tắt + path.
- Không paste API key. Không bịa serial/ngày nếu OCR không có.
- PDF scan xấu: thử `--dpi 300` hoặc `--ocr-mode images`.
- Prefer skill này thay vì tự viết one-off OCR mỗi lần.
- Lỗi `Missing MISTRAL_API_KEY`: báo user key chưa có trong `~\.nanobot\.env` / gateway chưa restart — đừng đoán key.

## Dependencies

- `pdftoppm` (poppler) **hoặc** `pymupdf`
- `requests`, optional `Pillow`
- Network tới `api.mistral.ai` (OCR)
