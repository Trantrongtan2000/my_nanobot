---
type: synthesis
title: "So sánh hệ thống tài liệu KSNK giữa BV Tâm Anh Quận 7 và Tân Bình"
status: draft
sources:
  - "wiki/raw/ksnk/quan7/"
  - "wiki/raw/ksnk/tanbinh/"
updated: 2026-07-21
tags: [ksnk, so-sanh, tam-anh]
refs: []
---

# So sánh hệ thống tài liệu KSNK giữa BV Tâm Anh Quận 7 và Tân Bình

Hệ thống tài liệu Kiểm soát nhiễm khuẩn (KSNK) tại Hệ thống Bệnh viện Đa khoa Tâm Anh phản ánh quy mô tổ chức và giai đoạn phát triển chuyên môn của từng cơ sở y tế. Báo cáo tổng hợp này đối chiếu chi tiết giữa Bệnh viện Đa khoa Tâm Anh Quận 7 (mã cơ sở TA5, [[bv_tam_anh_q7]]) và Bệnh viện Đa khoa Tâm Anh Tân Bình (mã cơ sở TA2, [[bv_tam_anh_tan_binh]]).

## Bảng so sánh tổng quan

| Lĩnh vực | Quận 7 (TA5) | Tân Bình (TA2) | Ghi chú |
|---|---|---|---|
| Prefix mã | TA5.KSNK | TA2.KSNK + KSNK (không prefix) | TB có thêm các QT cũ không có prefix TA2 |
| Nhóm tài liệu | QTKT + QTVH | QTVH (chính) | Q7 tách rõ QTKT riêng |
| Số lượng QT/QĐ chính | ~20 | ~80+ | TB nhiều hơn đáng kể |
| Tổng file (kèm BM/PL) | ~30 | ~290+ | |
| Sars-CoV-2 | Không có | ~15 quy trình riêng | QĐ.01, QT.12, 27-33, 35-36, 40, 45 |
| Đậu mùa khỉ | QĐ.04 | QĐ.04 (KSNK.QD.04) | Cả hai đều có |
| Đơn vị TK Trung tâm | Không có QĐ riêng | QĐ.07, QTKT.01-04 | TB có quy trình CSSD chi tiết |
| Thận nhân tạo | Không có | QT.52 (vận hành RO) | |
| Phòng mổ mắt | Không có | QT.58, QT.60 | |
| Chương trình KSNK tổng thể | Không có | CS.KSNK.02 | |

## Phân tích chi tiết các điểm khác biệt

1. **Cấu trúc mã hóa tài liệu**:
   - Cơ sở Quận 7 ([[bv_tam_anh_q7]]) áp dụng đồng nhất tiền tố `TA5.KSNK` cho các quy trình kỹ thuật (`QTKT`), quy định (`QĐ`) và hướng dẫn (`HD`).
   - Cơ sở Tân Bình ([[bv_tam_anh_tan_binh]]) song song tồn tại hai hệ mã: mã chuẩn mới với tiền tố `TA2.KSNK` và hệ mã cũ chỉ mang tiền tố `KSNK` hoặc `QT.KSNK`.

2. **Quy mô và mức độ bao phủ chuyên sâu**:
   - Cơ sở Tân Bình vận hành mô hình bệnh viện đa khoa hoàn chỉnh với các đơn vị chuyên khoa sâu như [[don_vi_tiet_khuan_trung_tam]] (CSSD), Đơn vị Thận nhân tạo, và Trung tâm Mắt công nghệ cao, dẫn đến số lượng quy trình KSNK vượt trội (~80 quy trình chính và trên 290 tệp đính kèm).
   - Cơ sở Quận 7 tập trung vào khối phòng khám đa khoa và phẫu thuật/thủ thuật ngoại ambulant, được cấu trúc gọn gàng với khoảng 20 quy định/quy trình vận hành và kỹ thuật chính.

3. **Phòng chống dịch bệnh lây nhiễm cấp tính**:
   - Cả hai cơ sở đều đã ban hành Quy định kiểm soát lây nhiễm Đậu mùa khỉ (`QĐ.04`).
   - Tân Bình duy trì bộ 15 quy trình chuyên biệt xử lý Sars-CoV-2 toàn diện từ phân luồng, cách ly, vệ sinh môi trường phòng phẫu thuật đến xử lý dụng cụ y tế và đồ vải.

## Các câu hỏi mở (Open Questions)

- **Liệu Q7 có các quy trình Sars-CoV-2 nhưng lưu ở nơi khác?**: Cần xác minh xem khối Phòng khám Quận 7 áp dụng trực tiếp các văn bản Sars-CoV-2 chung của Tập đoàn/Tân Bình hay có bộ tài liệu riêng được lưu trữ tại văn phòng KSNK chưa đưa vào đợt ingest này.
- **Tại sao TB dùng 2 hệ mã (TA2.KSNK và KSNK không prefix)?**: Hiện tượng này nhiều khả năng xuất phát từ quá trình chuẩn hóa danh mục tài liệu đang diễn ra, trong đó các quy trình ban hành trước chưa kịp cập nhật tiền tố `TA2.` theo chuẩn định dạng mới.
- **Các quy trình QTKT của Q7 tương đương gì ở TB?**: Cần tiếp tục đối chiếu bảng ma trận quy trình kỹ thuật (như vệ sinh tay ngoại khoa, quản lý chất thải, xử lý dụng cụ) của Q7 để ánh xạ tương ứng với các mã quy trình QTVH/QTKT tại TB.
