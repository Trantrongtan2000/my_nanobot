---
type: entity
title: "LogTag — Temperature Data Logger"
created: 2026-07-19
updated: 2026-08-10
tags: [logtag, data-logger, temperature, humidity, calibration, pharmacy]
device_sn: "AOA1005236US"
model: "UTRED30-WIFI"
mac_address: "00:80:E1:C4:1E:BD"
location: "Bệnh viện Quận 7"
source: "Mistral OCR v4"
---

## Overview

**LogTag** là thiết bị ghi nhiệt độ/độ ẩm tự động (data logger) dùng trong bảo quản thuốc, vắc-xin, thực phẩm và nhiều ngành khác. Mỗi LogTag có serial number riêng, có thể hiệu chuẩn (calibrated) và điều chỉnh (adjusted).

## Các dòng LogTag phổ biến

| Dòng | Đặc điểm |
|---|---|
| **TRED30-16R** | Đầu dò ngoài ST100 (blue sleeve), ghi nhiệt độ |
| **TREL30-16** | Đầu dò ngoài ST10 (green sleeve), ghi nhiệt độ |
| **TRID30-7** | Ghi nhiệt độ, 3 kênh |
| **HAXO-8** | Ghi nhiệt độ + độ ẩm |
| **UHADO-16** | Ghi nhiệt độ + độ ẩm, độ chính xác cao |
| **TREX** | Đầu dò ngoài, chịu nhiệt cao |

## Thiết bị cụ thể (cập nhật 2026-08-10)

### LogTag UTRED30-WIFI — SN: AOA1005236US

**Thông số từ thiết bị:**
- **Serial Number**: `AOA1005236US`
- **Model**: `UTR/D10-WIFI` / `UTRED30-WIFI`
- **MAC Address**: `00:80:E1:C4:1E:BD`
- **Distributor**: SmartTech Co. (www.smarttechco.com.vn)
- **Battery Status**: Low ⚠️ → **Đã thay pin** ✓ (2026-08-10)
- **Certificate of Calibration**: Có (Certificate of Calibration)

**Cấu hình logging:**
- **Record readings continuously**: overwrite oldest when memory full
- **Số ngày ghi**: ≥ 56 Days
- **Số lần đọc tối đa**: 16129 (max)
- **Chu kỳ đọc**: mỗi 5 phút
- **Begin recording after**: 0 phút delay (bắt đầu ngay)

**Cài đặt Wifi:**
- **SSID**: Leave Wifi settings unchanged (chưa cấu hình)
- Hoạt động trong nhiều tháng: THANG 01–05/2026

**Trạng thái bảo mật:**
- ☐ Configure requires a password
- ☐ Download requires a password

## Hiệu chuẩn (Calibration)

### Nguyên tắc

- LogTag có serial number riêng, có thể hiệu chuẩn
- Khuyến nghị gửi đến phòng lab có chứng nhận (traceable calibration)
- Có thể dùng phần mềm **LogTag Calibrate** để điều chỉnh (dành cho lab được ủy quyền)
- Đầu dò ngoài phải hiệu chuẩn cùng LogTag (calibrated bundle)

### Chứng chỉ hiệu chuẩn

- Có sẵn qua **LogTag Analyzer 3** cho LogTag sản xuất từ tháng 4/2019
- Hiệu lực: **12 tháng** từ ngày cấu hình đầu tiên
- Hạn cuối cấp chứng chỉ: **18 tháng** từ ngày sản xuất
- Chỉ áp dụng cho LogTag cấu hình lần đầu bằng LogTag Analyzer 3

### Khi nào cần hiệu chuẩn lại

- Sau khi **thay pin** (mở vỏ có thể ảnh hưởng đến cảm biến)
- Khi nghi ngờ độ chính xác (sai lệch so với thiết bị chuẩn)
- Định kỳ theo yêu cầu GPP/GSP (thường 12 tháng/lần)
- Sau khi tiếp xúc với hóa chất, dung môi

### Phần mềm

- **LogTag Analyzer 3**: cấu hình, đọc dữ liệu, in chứng chỉ hiệu chuẩn
- **LogTag Calibrate**: điều chỉnh hiệu chuẩn (dành cho lab được ủy quyền)

## Lưu ý

- LogTag có serial number riêng → cần quản lý danh sách thiết bị
- Sau thay pin → nên hiệu chuẩn lại
- Hóa chất tẩy rửa (cồn isopropyl) có thể ảnh hưởng cảm biến độ ẩm
- Không ngâm LogTag trong dung dịch — chỉ lau bề mặt
