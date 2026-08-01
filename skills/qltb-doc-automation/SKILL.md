# qltb-doc-automation

Tự động tạo tài liệu QLTB (biên bản bàn giao, kiểm định, bảo trì) từ dữ liệu OCR/Excel/wiki entity. Dựa trên pattern DocuFlow Studio và repo [bbbgtaq7](https://github.com/Trantrongtan2000/bbbgtaq7).

## Tính năng

- **Biên bản bàn giao** — Từ JSON OCR hoặc wiki entity + template Word chuẩn BYT
- **Biên bản kiểm định** — Từ chứng từ OCR + template BYT
- **Biên bản bảo trì** — Từ lịch bảo trì + checklist
- **Nhãn QR code tài sản** — In nhiệt, chứa QR + serial + model + khoa
- **Hỗ trợ phụ kiện (pk)** — Mảng strings

## Schema JSON (theo bbbgtaq7)

```json
{
  "shd": "Số hiệu biên bản",
  "shd_type": "Loại biên bản (giao/nhận)",
  "cty": "Công ty/khoa phòng",
  "ds": [
    {
      "ttb": "Tên thiết bị",
      "model": "Model",
      "ref": "Reference",
      "hang": "Hãng sản xuất",
      "nsx": "Nước sản xuất",
      "dvt": "Đơn vị tính",
      "sl": "Số lượng",
      "seri": "Số serial",
      "pk": ["Phụ kiện 1", "Phụ kiện 2"]  // mảng
    }
  ]
}
```

## Workflow

```bash
# 1. Từ JSON OCR (kết quả từ Mistral OCR)
python3 scripts/generate_doc.py \
  --input output/ocr_result.json \
  --template templates/bien_ban_ban_giao.docx \
  --output output/bien_ban_ban_giao_20260727.docx

# 2. Từ wiki entity (vẫn giữ nguyên)
python3 scripts/generate_doc.py \
  --input wiki/entities/device_xxx.md \
  --template templates/bien_ban_ban_giao.docx \
  --output output/bien_ban_ban_giao.docx
```

## Placeholders

| Key | Mô tả | Ví dụ |
|-----|-------|-------|
| shd | Số hiệu biên bản | "BB.2026.001" |
| shd_type | Loại biên bản | "Bàn giao" |
| cty | Công ty / khoa | "Khoa Cấp cứu" |
| ttb | Tên thiết bị | "Máy truyền dịch" |
| model | Model | "TE-LF630N03" |
| serial | Serial | "2204010109" |
| ref | Reference | "TF-LF630N03" |
| hang | Hãng SX | "TERUMO" |
| nsx | Nước SX | "Japan" |
| dvt | Đơn vị tính | "Cái" |
| sl | Số lượng | 1 |
| pk | Phụ kiện (mảng) | ["Dây truyền", "Adapter"] |
| qr_code | QR code base64 | (tự động sinh) |

## Scripts

- `generate_doc.py` — Tạo tài liệu từ JSON hoặc wiki entity
- `generate_qr_label.py` — Tạo nhãn QR in nhiệt (A6/A7)

## Thay đổi từ bbbgtaq7

- Schema JSON: thay thế wiki entity flat fields bằng cấu trúc `shd/shd_type/cty/ds`
- `pk` là mảng strings (không phải chuỗi gộp)
- Tích hợp Mistral OCR: 2 bước OCR → chat extract JSON
- Key rotation: tự động rotate API key khi gặp quota error

## Cài đặt

```bash
pip install python-docx openpyxl qrcode[pil] jinja2

# config.ini (nếu dùng Mistral OCR)
[API]
MISTRAL_API_KEY = YOUR_KEY_HERE
```

## Templates mặc định

- `templates/bien_ban_ban_giao.docx`
- `templates/bien_ban_kiem_dinh.docx`
- `templates/bien_ban_bao_tri.docx`
- `templates/bien_ban_thanh_ly.docx`
- `templates/nhan_qr_thermal.docx`

## Agent rules

- Luôn dùng template Word chuẩn BYT/QCVN
- Không bịa dữ liệu — nếu thiếu field, để trống hoặc ghi "chưa xác định"
- pk phải là mảng, không gộp thành 1 chuỗi
- Tự động tạo QR code: asset tag từ serial + model + khoa
- Ghi log vào `memory/history.jsonl` mỗi lần tạo tài liệu
