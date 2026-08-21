---
type: entity
title: "Tủ lạnh bảo quản thuốc — Pharmacy Refrigerator"
created: 2026-07-19
updated: 2026-07-19
tags: [refrigerator, pharmacy, GPP, GSP, temperature, storage]
---

## Overview

Tủ lạnh bảo quản thuốc (pharmacy/medical refrigerator) là thiết bị chuyên dụng duy trì nhiệt độ ổn định trong khoảng **2–8 °C** để bảo quản thuốc, vắc-xin, insulin và các sản phẩm y tế nhạy cảm với nhiệt.

## Yêu cầu theo GPP/GSP

- Duy trì nhiệt độ **2–8 °C** (bảo quản lạnh) hoặc **8–15 °C** (bảo quản mát)
- Có thiết bị ghi nhiệt độ tự động ([[entities/logtag.md]] hoặc tương đương)
- Có cảnh báo khi nhiệt độ vượt ngưỡng
- Có ghi chép nhiệt độ hàng ngày
- Kiểm định định kỳ

## Kiểm định tủ lạnh nhà thuốc

### Kiểm tra hàng ngày

- Kiểm tra nhiệt độ hiển thị (2–8 °C)
- Kiểm tra LogTag hoạt động bình thường
- Ghi chép nhiệt độ vào nhật ký

### Kiểm tra định kỳ

| Hạng mục | Tần suất |
|---|---|
| Vệ sinh tủ lạnh | Hàng tháng |
| Kiểm tra gioăng cửa | Hàng tháng |
| So sánh LogTag với nhiệt kế chuẩn | 6 tháng/lần |
| Hiệu chuẩn LogTag | 12 tháng/lần |
| Kiểm tra dây nguồn | 6 tháng/lần |

### Kiểm định (Verification)

1. **Kiểm tra nhiệt độ tủ**: đặt LogTag hoặc nhiệt kế chuẩn ở vị trí trung tâm ngăn lạnh
2. **Theo dõi**: ghi nhiệt độ trong ít nhất 30 phút, so sánh với ngưỡng 2–8 °C
3. **Đánh giá**: nhiệt độ ổn định trong ngưỡng cho phép
4. **Kết luận**: tủ đạt/không đạt yêu cầu bảo quản

### Xử lý khi mất điện

- Chuyển thuốc lạnh sang thùng đá tạm thời
- Kiểm tra nhiệt độ mỗi giờ
- Dùng máy phát điện nếu có
- Ghi nhận thời gian mất điện và nhiệt độ trong quá trình đó

## Related

- [[topics/medical-equipment-verification.md]] — kiểm định thiết bị y tế
- [[entities/mpr-715f.md]] — Sanyo MPR-715F
- [[entities/pharmacy-refrigerator.md]] — tủ lạnh bảo quản thuốc

## Tài liệu
- **Wiki entity:** [[entities/pharmacy-refrigerator]]
- **OCR chứng nhận:** [[raw/ocr_ksnk_qt05/q7/organized]]
