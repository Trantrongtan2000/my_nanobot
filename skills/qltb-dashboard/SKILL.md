---
name: qltb-dashboard
description: >
  Dashboard & báo cáo KPI cho QLTB: uptime, MTBF, MTTR, PM compliance, calibration due.
---

# QLTB Dashboard & KPI Reporting

Dashboard thống kê và báo cáo KPI cho quản lý thiết bị y tế.

## KPIs theo dõi

| KPI | Công thức | Mục tiêu | Cảnh báo |
|---|---|---|---|
| **Uptime** | (Thời gian hoạt động / Tổng thời gian) × 100% | ≥ 95% | < 90% |
| **MTBF** | Tổng giờ hoạt động / Số sự cố | Tăng dần | Giảm so với kỳ trước |
| **MTTR** | Tổng giờ sửa chữa / Số sự cố | ≤ 4h | > 8h |
| **PM Compliance** | (Số PM đúng hạn / Tổng PM kế hoạch) × 100% | 100% | < 95% |
| **Calibration Due** | Số thiết bị hết hạn HC / Tổng thiết bị | 0 | > 0 |
| **Calibration Warning** | Số thiết bị < 30 ngày hết hạn / Tổng | 0 | > 5 |

## Data Sources

- Asset registry (qltb-asset-management)
- Incident records (MEIMS QT.05)
- Maintenance records (MEIMS QT.06)
- Calibration records (wiki entities + lab_checklist.json)

## Workflow

```bash
# 1. Tính KPI cho 1 khoa
python3 ~/.nanobot/workspace/skills/qltb-dashboard/scripts/calculate_kpi.py \
  --department "Khoa Cấp cứu" \
  --period 2026-07 \
  --output reports/kpi_cap_cuu_202607.json

# 2. Tạo dashboard HTML
python3 ~/.nanobot/workspace/skills/qltb-dashboard/scripts/generate_dashboard.py \
  --period 2026-07 \
  --output dashboard/qltb_202607.html

# 3. Cảnh báo tự động
python3 ~/.nanobot/workspace/skills/qltb-dashboard/scripts/check_alerts.py \
  --config config/alerts.yaml \
  --notify telegram

# 4. Xuất báo cáo Excel cho quản lý
python3 ~/.nanobot/workspace/skills/qltb-dashboard/scripts/export_excel.py \
  --period 2026-07 \
  --output reports/qltb_monthly_202607.xlsx
```

## Dashboard Components

1. **Overview Cards** — Tổng thiết bị, active, maintenance, retired, calibration due
2. **Department Breakdown** — Biểu đồ cột: thiết bị theo khoa
3. **Status Distribution** — Pie chart: active/maintenance/retired/transferred
4. **Calibration Timeline** — Gantt chart: hạn HC 30/60/90 ngày
5. **Maintenance Calendar** — Lịch bảo trì tháng
6. **KPI Trends** — Line chart: uptime, MTBF, MTTR, PM compliance 12 tháng
7. **Top Issues** — Top 10 thiết bị nhiều sự cố nhất
8. **Alert Panel** — Cảnh báo real-time

## Alert Rules (config/alerts.yaml)

```yaml
alerts:
  - name: "Calibration Due"
    condition: "calibration_expiry <= today + 30 days"
    severity: "warning"
    channels: ["telegram", "email"]
    template: "⚠️ {count} thiết bị sắp hết hạn HC (< 30 ngày)"

  - name: "Calibration Overdue"
    condition: "calibration_expiry < today"
    severity: "critical"
    channels: ["telegram", "email", "sms"]
    template: "🔴 {count} thiết bị QUÁ HẠN HC"

  - name: "Maintenance Overdue"
    condition: "next_maintenance < today"
    severity: "warning"
    channels: ["telegram"]
    template: "🟡 {count} thiết bị trễ bảo trì"

  - name: "Low Uptime"
    condition: "uptime < 90%"
    severity: "critical"
    channels: ["telegram", "email"]
    template: "🔴 {department} uptime {uptime}% (< 90%)"

  - name: "PM Non-compliance"
    condition: "pm_compliance < 95%"
    severity: "warning"
    channels: ["telegram"]
    template: "🟡 {department} PM compliance {pm_compliance}% (< 95%)"
```

## Output Formats

- **HTML Dashboard** — Interactive, Chart.js, real-time update
- **Excel Report** — Chi tiết cho quản lý, có pivot table
- **PDF Summary** — 1 trang, gửi leadership
- **JSON API** — Cho nanobot/Notion integration
- **Telegram Bot** — Cảnh báo real-time, query KPI

## Agent rules

- Tính KPI hàng ngày (cron 02:00)
- Cảnh báo real-time khi có sự cố mới (webhook từ MEIMS)
- Lưu lịch sử KPI để trend analysis
- Không bịa dữ liệu — nếu thiếu data, ghi "insufficient data"
- Dashboard phải load < 3s