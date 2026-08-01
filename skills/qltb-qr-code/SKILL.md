---
name: qltb-qr-code
description: >
  Tạo, quản lý, quét QR code cho thiết bị y tế. Dùng cho nhãn tài sản, kiểm kê, tra cứu nhanh.
---

# QLTB QR Code Management

Quản lý QR code cho thiết bị y tế, dùng cho nhãn in nhiệt, kiểm kê, tra cứu.

## Tính năng

1. **Generate QR** — Tạo QR code từ asset data (asset_tag, serial, model, department)
2. **Label Template** — Template nhãn in nhiệt (A6, A7, 50x30mm, 70x40mm)
3. **Batch Generate** — Tạo hàng loạt QR cho danh sách asset
4. **Scan & Lookup** — Quét QR → tra cứu asset info (web/mobile)
5. **Print Integration** — Xuất PDF sẵn sàng in nhiệt

## QR Data Format

```json
{
  "asset_tag": "TA5.HT.001",
  "serial": "2204010109",
  "model": "TE-LF630N03",
  "manufacturer": "TERUMO",
  "department": "Khoa Cấp cứu",
  "location": "MÁY SỐ 10",
  "calibration_expiry": "2027-07-15",
  "url": "https://qltb.tahospital.vn/asset/TA5.HT.001"
}
```

## Workflow

```bash
# 1. Tạo QR cho 1 asset
python3 ~/.nanobot/workspace/skills/qltb-qr-code/scripts/generate_qr.py \
  --asset-tag TA5.HT.001 \
  --serial 2204010109 \
  --model TE-LF630N03 \
  --department "Khoa Cấp cứu" \
  --output data/qr_codes/TA5.HT.001.png

# 2. Tạo hàng loạt từ CSV/JSON
python3 ~/.nanobot/workspace/skills/qltb-qr-code/scripts/batch_generate.py \
  --input data/assets.csv \
  --output-dir data/qr_codes/

# 3. Tạo PDF nhãn in nhiệt (A6, 4 nhãn/trang)
python3 ~/.nanobot/workspace/skills/qltb-qr-code/scripts/create_label_pdf.py \
  --input data/qr_codes/ \
  --template thermal_a6 \
  --output labels/nhan_qr_20260722.pdf

# 4. Tra cứu qua QR (web endpoint)
# GET /qr/lookup?data=<qr_content>
```

## Label Templates

| Template | Kích thước | Nhãn/trang | Dùng cho |
|---|---|---|---|
| `thermal_50x30` | 50x30mm | 24 | Nhãn nhỏ, thiết bị nhỏ |
| `thermal_70x40` | 70x40mm | 12 | Nhãn chuẩn, thiết bị trung bình |
| `thermal_a6` | A6 (105x148mm) | 4 | Nhãn lớn, nhiều info |
| `thermal_a7` | A7 (74x105mm) | 8 | Nhãn vừa |

## QR Content Options

- **Minimal**: `asset_tag` only (tra cứu qua API)
- **Standard**: asset_tag + serial + model + department
- **Full**: Tất cả fields + URL tra cứu web
- **Custom**: Theo cấu hình

## Dependencies

- `qrcode[pil]` — Tạo QR code
- `reportlab` — Tạo PDF nhãn
- `pillow` — Xử lý ảnh
- `pandas` — Đọc CSV/Excel (batch)

## Agent rules

- QR code phải chứa `asset_tag` tối thiểu
- URL tra cứu phải trỏ về hệ thống QLTB (nếu có) hoặc wiki entity
- Nhãn in nhiệt: font size ≥ 8pt, QR ≥ 15mm
- Batch generate: validate input trước khi tạo
- Lưu QR images vào `data/qr_codes/{asset_tag}.png`