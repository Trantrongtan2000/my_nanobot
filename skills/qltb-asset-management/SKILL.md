---
name: qltb-asset-management
description: >
  Quản lý tài sản thiết bị y tế (inspired by Snipe-IT). Theo dõi lifecycle, bảo trì, QR code, API.
---

# QLTB Asset Management

Quản lý tài sản thiết bị y tế toàn diện, dựa trên pattern Snipe-IT.

## Tính năng (inspired by Snipe-IT)

1. **Asset Registry** — Đăng ký thiết bị: model, serial, REF, nhà sản xuất, khoa, vị trí, người quản lý
2. **Lifecycle Tracking** — Tiếp nhận → Kiểm định → Bảo trì → Chuyển giao → Thanh lý
3. **Maintenance Management** — Lịch bảo trì định kỳ, lịch sử bảo trì, checklist, KPI (MTBF, MTTR, uptime)
4. **Calibration Management** — Hạn kiểm định, tem HC, cảnh báo < 30 ngày
5. **QR Code & Label** — Tạo QR code, in nhãn nhiệt, quét kiểm kê
6. **RBAC** — Admin, Kỹ sư, Quản lý khoa, Xét nghiệm (viewer)
7. **Audit Log** — Lịch sử thay đổi đầy đủ
8. **REST API** — Tích hợp với nanobot, wiki, Notion, hệ thống khác
9. **Import/Export** — Excel batch import/export
10. **Dashboard** — Thống kê theo khoa, trạng thái, sắp hết hạn HC

## Data Model

```yaml
# Entity fields (mapping từ wiki entity)
asset_tag: "TA5.HT.001"           # Mã tài sản (prefix khoa + serial)
serial_number: "2204010109"       # Serial number
model: "TE-LF630N03"              # Model
manufacturer: "TERUMO"            # Nhà sản xuất
ref: "TF-LF630N03"                # REF
department: "Khoa Cấp cứu"        # Khoa/phòng
location: "MÁY SỐ 10"             # Vị trí cụ thể
custodian: "Nguyễn Văn A"         # Người quản lý
status: "active"                  # active | maintenance | retired | transferred
purchase_date: "2022-01-15"       # Ngày mua
warranty_expiry: "2025-01-15"     # Hết bảo hành
calibration_date: "2026-07-15"    # Ngày kiểm định gần nhất
calibration_expiry: "2027-07-15"  # Hạn kiểm định
calibration_label: "116284"       # Số tem HC
qr_code: "base64_png"             # QR code image
notes: "..."                      # Ghi chú
```

## Workflow

```bash
# 1. Tạo asset từ wiki entity
python3 ~/.nanobot/workspace/skills/qltb-asset-management/scripts/create_asset.py \
  --entity wiki/entities/device_xxx.md

# 2. Cập nhật trạng thái bảo trì
python3 ~/.nanobot/workspace/skills/qltb-asset-management/scripts/update_status.py \
  --asset TA5.HT.001 --status maintenance --note "Bảo trì định kỳ Q3"

# 3. Tạo lịch bảo trì
python3 ~/.nanobot/workspace/skills/qltb-asset-management/scripts/schedule_maintenance.py \
  --asset TA5.HT.001 --interval-months 6 --next-date 2027-01-15

# 4. Cảnh báo hạn HC
python3 ~/.nanobot/workspace/skills/qltb-asset-management/scripts/check_calibration.py \
  --days-warning 30

# 5. Xuất báo cáo
python3 ~/.nanobot/workspace/skills/qltb-asset-management/scripts/export_report.py \
  --format excel --output reports/qltb_20260722.xlsx
```

## Scripts

- `create_asset.py` — Tạo asset từ wiki entity
- `update_status.py` — Cập nhật trạng thái
- `schedule_maintenance.py` — Lập lịch bảo trì
- `check_calibration.py` — Kiểm tra hạn HC, cảnh báo
- `generate_qr.py` — Tạo QR code cho asset
- `export_report.py` — Xuất báo cáo Excel/CSV
- `import_excel.py` — Import hàng loạt từ Excel
- `sync_wiki.py` — Đồng bộ 2 chiều với wiki entities
- `sync_notion.py` — Đồng bộ với Notion (nếu có)

## Storage

- SQLite: `~/.nanobot/workspace/data/qltb_assets.db`
- Hoặc JSON: `~/.nanobot/workspace/data/qltb_assets.json`
- QR images: `~/.nanobot/workspace/data/qr_codes/`

## API (FastAPI)

```
GET    /assets                    # Danh sách asset
GET    /assets/{asset_tag}        # Chi tiết asset
POST   /assets                    # Tạo asset mới
PUT    /assets/{asset_tag}        # Cập nhật asset
DELETE /assets/{asset_tag}        # Xóa asset (soft delete)
GET    /assets/{asset_tag}/qr     # QR code image
GET    /assets/{asset_tag}/history # Lịch sử thay đổi
GET    /reports/calibration-due   # Cảnh báo hạn HC
GET    /reports/maintenance-due   # Cảnh báo bảo trì
GET    /dashboard/stats           # Thống kê dashboard
```

## Agent rules

- Mọi thay đổi asset phải ghi audit log
- Không xóa cứng asset — chỉ soft delete (status = retired)
- Cảnh báo hạn HC < 30 ngày: tự động tạo issue/notification
- Đồng bộ 2 chiều với wiki entities (entity-creator skill)
- API key authentication cho nanobot integration