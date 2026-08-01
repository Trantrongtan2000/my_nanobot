---
type: topic
title: "Kiểm định thiết bị y tế — Medical Equipment Verification"
created: 2026-07-19
updated: 2026-07-20
tags: [medical, verification, calibration, pharmacy, GPP, GSP]
---

## Overview

Wiki ghi lại quy trình, tiêu chuẩn và thiết bị liên quan đến **kiểm định thiết bị y tế**, tập trung vào nhà thuốc và kho bảo quản thuốc.

## Phạm vi

- **Nhà thuốc (GPP)**: tủ lạnh bảo quản thuốc, LogTag, nhiệt kế, ẩm kế
- **Kho GSP**: kho bảo quản thuốc, hệ thống giám sát nhiệt độ/độ ẩm
- **Thiết bị khác**: tủ ấm, máy lạnh, thiết bị đo lường

## Vị trí nhà thuốc

Cơ sở có 3 tầng, mỗi tầng một nhà thuốc:

| Tên đầy đủ | Viết tắt | Tầng |
|---|---|---|
| Nhà thuốc trệt | NT trệt | Trệt (Ground) |
| Nhà thuốc 1 | NT1 | Lầu 1 |
| Nhà thuốc 2 | NT2 | Lầu 3 |

> Viết tắt thường dùng trên thiết bị: **NT1**, **NT2**. Nhà thuốc trệt có thể ghi "NT trệt" hoặc "Trệt".

## Quy định pháp lý Việt Nam

| Văn bản | Nội dung chính |
|---|---|
| **Thông tư 02/2018/TT-BYT** | Thực hành tốt cơ sở bán lẻ thuốc (GPP) |
| **Thông tư 36/2018/TT-BYT** | Thực hành tốt bảo quản thuốc (GSP) |
| **Thông tư 11/2018/TT-BYT** | Xử lý thuốc hết hạn, hư hỏng |
| **Nghị định 54/2017/NĐ-CP** | Quản lý thuốc kê đơn, thuốc độc |

### Yêu cầu nhiệt độ bảo quản

| Loại | Nhiệt độ | Độ ẩm |
|---|---|---|
| Nhiệt độ phòng | 15–30 °C | ≤75% |
| Bảo quản lạnh | 2–8 °C | ≤75% |
| Bảo quản mát | 8–15 °C | ≤75% |

## Thiết bị nhà thuốc

- [[entities/logtag.md]] — LogTag: thiết bị ghi nhiệt độ/độ ẩm tự động
- [[entities/pharmacy-refrigerator.md]] — Tủ lạnh bảo quản thuốc
- [[entities/mpr-715f.md]] — PHCbi MPR-715F (tủ lạnh dược phẩm)
- [[entities/mpr-s313.md]] — PHCbi MPR-S313-PK (tủ lạnh dược phẩm nhỏ)

## Danh mục thiết bị theo vị trí

Tổng: **23 thiết bị** (Trệt 12, Tầng 1 6, Tầng 3 5).

### Tầng Trệt (12 thiết bị)

| # | Thiết bị | Model | Serial | Tem HC | Hạn |
|---|---|---|---|---|---|
| 1 | TỦ LẠNH SỐ 4 | MPR-715F-PE | 231090072 | 201177 | 31/07/2026 |
| 2 | TỦ LẠNH SỐ 3 | MPR-S313-PK | 23090064 | 201178 | 31/07/2026 |
| 3 | TỦ LẠNH SỐ 1 | MPR-S313-PK | 21110338 | 200743 | 30/09/2026 |
| 4 | TỦ LẠNH SỐ 2 | MPR-S313-PK | 21030056 | 200742 | 30/09/2026 |
| 5 | LogTag WiFi trệt - Tủ Lạnh 2 | UTREL30-WIFI | A0A50034017C | 205756 | 14/07/2027 |
| 6 | LogTag WiFi trệt - Tủ Lạnh 1 | UTREL30-WIFI | A0A5003405BT | 205757 | 14/07/2027 |
| 7 | LogTag 1 (không WiFi) | UTRED-16F | A0A7001776U5 | 200745 | 30/09/2026 |
| 8 | LogTag 2 (không WiFi) | UTRED-16F | A0A700194590 | 200744 | 30/09/2026 |
| 9 | LogTag UHADO-16 | UHADO-16 | — | 201181 | 31/07/2026 |
| 10 | LogTag UTRED-16F hành trình | UTRED-16F | A0480057337T | 201146 | 27/03/2027 |
| 11 | LogTag UTRID-16R | UTRID-16R | 6045142461 | DK134 | 31/10/2026 |
| 12 | LogTag SmartTech | UHADO-16 | A0C1042582WT | 205758 | 14/07/2027 |

### Tầng 1 — NT1 (6 thiết bị)

| # | Thiết bị | Model | Serial | Tem HC | Hạn |
|---|---|---|---|---|---|
| 1 | TỦ LẠNH 01 | MPR-715F-PE | 231190097 | 205750 | 14/07/2027 |
| 2 | TỦ LẠNH 02 | MPR-715F-PE | 231090071 | 205751 | 14/07/2027 |
| 3 | LogTag WiFi 1 | UTREL30-WIFI | A0A5003388X5 | 205752 | 14/07/2027 |
| 4 | LogTag WiFi 2 | UTREL30-WIFI | — | 201143 | 27/03/2027 |
| 5 | LogTag WiFi 3 | UTREL30-WIFI | A0A50033406L5 | 205753 | 14/07/2027 |
| 6 | LogTag UHADO-16 (NT1) | UHADO-16 | A0C1042585QT | 201186 | 31/07/2026 |

**Ảnh tư liệu NT1:**
| File | Mô tả |
|---|---|
| `images/nt1/tulanh01_label.jpg` | Nhãn tủ lạnh 01 NT1 |
| `images/nt1/tulanh02_label.jpg` | Nhãn tủ lạnh 02 NT1 |
| `images/nt1/tulanh02_serial.jpg` | Serial plate Tủ lạnh 02 (S/N 231090071) |
| `images/nt1/logtag_wifi_tl1.jpg` | LogTag gắn Tủ lạnh 1 — UTREL30-WIFI |
| `images/nt1/logtag_smarttech_sticker.jpg` | Sticker LogTag SmartTech VN |
| `images/nt1/tem201186.jpg` | Tem hiệu chuẩn 201186 (UHADO-16) |

### Tầng 3 — NT2 (5 thiết bị)

**Ảnh tư liệu NT2:**
| File | Mô tả |
|---|---|
| `images/nt2/logtag_wifi_tl1.jpg` | LogTag WiFi Tủ lạnh 1 — S/N A0A5003402HT, tem 206166 |
| `images/nt2/logtag_wifi_tl2.jpg` | LogTag WiFi Tủ lạnh 2 — S/N A0A5003371QT, tem 206167 |
| `images/nt2/logtag_smarttech_nt2.jpg` | LogTag SmartTech NT2 — S/N A0C1042579L5 |
| `images/nt2/tem201191.jpg` | Tem HC 201191 — HC: 01-07-25 → 01-07-26 |
| `images/nt2/tulanh1_label.jpg` | Nhãn tủ lạnh 1 NT2 |
| `images/nt2/tulanh2_label.jpg` | Nhãn tủ lạnh 2 NT2 |

| # | Thiết bị | Model | Serial | Tem HC | Hạn |
|---|---|---|---|---|---|
| 1 | Tủ lạnh 1 | MPR-S313-PK | 23090063 | 205768 | 14/07/2027 |
| 2 | Tủ lạnh 2 | MPR-S313-PK | 23090062 | 206165 | 14/07/2027 |
| 3 | LogTag WiFi - Tủ lạnh 2 | UTREL30-WIFI | A0A5003371QT | 206167 | 14/07/2027 |
| 4 | LogTag WiFi - Tủ lạnh 1 | UTREL30-WIFI | A0A5003402HT | 206166 | 14/07/2027 |
| 5 | LogTag SmartTech (NT2) | SmartTech/UHADO-16 | A0C1042579L5 | 206168 | 08/02/2027 |

---

## Quy trình kiểm định chung

1. **Kiểm tra thiết bị**: xác nhận thiết bị hoạt động, không hư hỏng
2. **Kiểm tra cảm biến**: so sánh với thiết bị chuẩn (hiệu chuẩn)
3. **Ghi nhận kết quả**: lưu biên bản kiểm định, chứng chỉ hiệu chuẩn
4. **Đánh giá**: thiết bị đạt/không đạt yêu cầu
5. **Xử lý**: hiệu chỉnh, thay thế hoặc đưa ra khỏi sử dụng nếu không đạt

## Kiểm định LogTag

### Kiểm tra định kỳ

| Hạng mục | Tần suất |
|---|---|
| Đối chiếu nhiệt độ LogTag với nhiệt kế chuẩn | 6 tháng/lần |
| Hiệu chuẩn LogTag (gửi lab) | 12 tháng/lần |
| Kiểm tra pin, tình trạng vật lý | 6 tháng/lần |
| Đối chiếu chứng chỉ hiệu chuẩn | 12 tháng/lần |

### Quy trình kiểm tra nhanh (tại chỗ)

1. Đặt LogTag và nhiệt kế chuẩn cạnh nhau trong cùng môi trường
2. Đợi 15–30 phút cho ổn định
3. So sánh nhiệt độ hiển thị / đã ghi
4. Sai số cho phép: ±0.5 °C (với nhiệt kế chuẩn)
5. Nếu sai số > ±1 °C → cần hiệu chuẩn lại hoặc thay thế

### Ghi nhận kết quả

Mỗi lần kiểm định cần ghi:
- Ngày kiểm định
- Thiết bị (model, serial)
- Vị trí (NT trệt / NT1 / NT2)
- Kết quả đo (LogTag vs chuẩn)
- Kết luận (Đạt / Không đạt)
- Người thực hiện

## Tem kiểm định

Sau khi kiểm định, thiết bị phải được dán **tem kiểm định** (verification/calibration sticker) để chứng nhận đã qua kiểm tra và cho biết trạng thái hiện tại.

### Thông tin trên tem

| Thông tin | Mô tả |
|---|---|
| **Trạng thái** | Đạt / Không đạt |
| **Ngày kiểm định** | Ngày thực hiện kiểm định |
| **Hạn kiểm định tiếp** | Ngày hết hạn (thường 12 tháng sau) |
| **Số tem** | Mã số tem riêng |
| **Đơn vị kiểm định** | Tên tổ chức thực hiện |
| **Mã thiết bị** | Serial / mã định danh thiết bị |

### Quy tắc dán tem

- Dán ở vị trí **dễ thấy** trên thiết bị (cửa tủ lạnh, mặt trước LogTag)
- Không che phủ thông tin quan trọng (serial, model, nút bấm)
- **Không dán chồng** tem cũ — gỡ tem cũ trước khi dán tem mới
- Nếu thiết bị **không đạt** → gỡ tem cũ, không dán tem mới, đánh dấu "Không đạt"

### Tem theo trạng thái

| Trạng thái | Màu tem | Ý nghĩa |
|---|---|---|
| **Đạt** | Xanh lá / Xanh dương | Thiết bị hoạt động đúng, cho phép sử dụng |
| **Không đạt** | Đỏ / Vàng | Thiết bị sai số lớn, cần hiệu chuẩn lại hoặc thay thế |
| **Đang kiểm định** | Trắng / Vàng nhạt | Đang trong quá trình kiểm định |

### Kiểm tra tem định kỳ

- Kiểm tra tem còn hiệu lực khi kiểm tra hàng ngày
- Nếu tem hết hạn → lập tức kiểm định lại
- Nếu tem bị rách, mờ → dán lại tem mới với thông tin cập nhật

## Cần kiểm tra (tồn đọng)

Tất cả đã xử lý xong. Không còn mục tồn đọng.

- [x] **T3_TL2** (Tủ lạnh 2, Tầng 3) — S/N 23090062 ✅
- [x] **LogTag SmartTech (NT2)** — tem 201191 (HC: 01-07-25 → 01-07-26) ✅
- [x] **Tem 201186 trùng**: ảnh tem 20/07/26 xác nhận trên UHADO-16 → gán cho NT1, xoá khỏi T3 ✅
- [x] **S/N A0C1042582WT trùng**: T3 WiFi TL1 S/N thực tế là A0A5003402HT nên không trùng nữa ✅
