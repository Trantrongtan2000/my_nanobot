---
type: entity
title: "Snipe-IT"
status: draft
sources:
  - "https://snipeitapp.com/"
  - "https://snipe-it.readme.io/docs/introduction"
updated: 2026-07-22
tags: [asset-management, itam, open-source, rest-api, meims]
refs:
  - "[[docuflow-studio]]"
---

# Snipe-IT

**Free Open Source IT Asset Management System**

## Tổng quan
Snipe-IT là hệ thống quản lý tài sản IT mã nguồn mở, giúp:
- Quản lý tài sản, phần mềm, giấy phép, phụ kiện, linh kiện
- Theo dõi ai có tài sản nào, lịch sử bảo trì, audit log
- Hỗ trợ nhiều khu vực, bảo mật cao
- API REST mạnh, tích hợp linh hoạt

## Thống kê (từ website)
- 20,889,000+ tài sản được quản lý
- 10,140,000+ người dùng
- 6,010 khách hàng
- 13 năm phát triển
- 330+ contributors, 12,000+ commits

## Tính năng nổi bật
- REST API mạnh (JSON), dễ tích hợp
- Quản lý giấy phép phần mềm
- Theo dõi lịch sử bảo trì, audit log
- Hỗ trợ barcode, QR code
- Nhiều tùy chọn triển khai: self-hosted, cloud, Docker

## Công nghệ
- Xây dựng trên Laravel (PHP)
- CSDL: MySQL/SQLite
- Web-based, chạy trên web server

## Ứng dụng cho MEIMS/QLTB
- **Quản lý tài sản y tế** (thiết bị, phần mềm, giấy phép)
- **Theo dõi vị trí, người chịu trách nhiệm, lịch bảo trì**
- **Tích hợp với hệ thống báo cáo KPI** (uptime, MTBF, MTTR)
- **API REST** để tích hợp với nanobot, wiki, Notion

## Open questions
- So sánh với DocuFlow Studio: Snipe-IT tập trung asset management, DocuFlow tập trung tài liệu
- Tích hợp với hệ thống kiểm định BYT hiện tại như thế nào?
- Có cần custom field cho thiết bị y tế (hạn kiểm định, người bảo trì) không?