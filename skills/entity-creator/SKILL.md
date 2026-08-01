---
name: entity-creator
description: >
  Tạo và verify wiki entity từ OCR output. Tự động chạy verification loop
  (verify_entity.py + nanobot_self_improve.py) cho đến khi entity pass.
  Use khi có organized.md từ doc-ocr-organize và cần tạo entity thiết bị y tế.
---

# entity-creator

Workflow tự động tạo entity với self-improvement loop:

## Pipeline

1. **Input**: `organized.md` từ doc-ocr-organize (hoặc file markdown thô)
2. **Extract**: Trích xuất thông tin thiết bị (model, serial, REF, vị trí, hạn HC, v.v.)
3. **Create**: Tạo entity markdown theo format wiki (YAML frontmatter + content)
4. **Verify**: Chạy `verify_entity.py` trên entity mới
5. **Improve**: Nếu fail → ghi nhận lỗi vào `nanobot_self_improve.py` → sửa entity → verify lại
6. **Commit**: Cập nhật `index.md` và `log.md`
7. **Report**: Trả về kết quả + path entity

## Scripts

```bash
# Tạo entity từ organized.md
python3 /home/tan/.nanobot/workspace/skills/entity-creator/scripts/create_entity.py \
  /path/to/organized.md \
  --type device \
  --department "Khoa Xét nghiệm" \
  -o /home/tan/.nanobot/workspace/wiki/entities/

# Chạy verification loop cho entity đã có
python3 /home/tan/.nanobot/workspace/skills/entity-creator/scripts/verify_and_fix.py \
  /home/tan/.nanobot/workspace/wiki/entities/device_xxx.md
```

## Env

```bash
export MISTRAL_API_KEY=...          # cho OCR (nếu cần re-OCR)
export ORFREE_BASE=http://127.0.0.1:20128/v1
export NANOBOT_ORFREE_KEY=sk-...
```

## Output

- Entity file: `wiki/entities/<slug>.md`
- Updated: `wiki/index.md`, `wiki/log.md`
- Error log: `memory/nanobot_errors.jsonl`
- Improvement log: `memory/nanobot_improvements.jsonl`

## Agent rules

- **Luôn chạy verify** sau khi tạo entity (bắt buộc).
- **Không bỏ qua** lỗi/warning từ verify_entity.py.
- **Ghi nhận mọi lỗi** vào nanobot_self_improve.py để học tập.
- **Lặp lại** verify cho đến khi pass (tối đa 3 vòng).
- **Cập nhật index.md + log.md** sau khi entity pass verification.
- **Không bịa** serial/ngày/hạn HC nếu OCR không có — để trống hoặc ghi "chưa xác định".

## Dependencies

- `verify_entity.py` (workspace root)
- `nanobot_self_improve.py` (workspace root)
- `doc-ocr-organize` skill (cho OCR input)
- Python 3.10+, `requests`, `pyyaml` (optional)

## Example

```bash
# 1. OCR PDF
python3 ~/.nanobot/workspace/skills/doc-ocr-organize/scripts/doc_ocr_organize.py \
  /mnt/sda1/BV_QUAN_7/device.pdf -o /tmp/ocr_out

# 2. Tạo entity từ organized.md
python3 ~/.nanobot/workspace/skills/entity-creator/scripts/create_entity.py \
  /tmp/ocr_out/organized.md \
  --type device \
  --department "Khoa Cấp cứu" \
  -o ~/.nanobot/workspace/wiki/entities/

# Kết quả: entity đã tạo, verified, indexed
```