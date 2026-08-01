---
type: entity
title: "DocuFlow Studio"
status: draft
sources:
  - "https://github.com/ghuyphan/docuflow-studio"
updated: 2026-07-22
tags: [document-automation, asset-management, handover, qr-code, meims]
refs:
  - "[[snipe-it]]"
---

# DocuFlow Studio

**Modern Enterprise IT Asset Management & Automated Handover Document Generator**

## Tổng quan
DocuFlow Studio là giải pháp open-source full-stack (FastAPI + React + SQLite) tập trung vào:
- Tự động tạo tài liệu Word (biên bản bàn giao) từ mapping Excel serial → template `.docx`
- Tạo nhãn QR code tài sản, serial number, thông tin phòng ban
- Dashboard quản lý tồn kho thời gian thực
- RBAC (Admin, Staff, Viewer) + JWT auth + audit log
- Chạy được Docker, desktop app (Tkinter), web service

## Tính năng chi tiết
- **Automated Word Document Generation**: Điền tự động biên bản bàn giao thiết bị từ Excel mapping serial vào Word template
- **QR Code Asset Tag Generator**: Tạo nhãn in nhiệt có QR code, asset tag, serial number, thông tin phòng ban
- **Camera & Hardware QR Scanner**: Quét QR code tích hợp, lookup nhanh tài sản
- **Smart Inventory Dashboard**: Theo dõi lifecycle tài sản, phân bố theo khoa/phòng, status badges, import/export Excel hàng loạt
- **RBAC**: 3 vai trò (Admin, Staff, Viewer) với JWT authentication, audit log lịch sử thay đổi
- **Cross-Platform**: Docker container, desktop app với system tray, hoặc web service

## Công nghệ
- Backend: Python 3.10+, FastAPI, SQLAlchemy, SQLite, Pydantic, python-docx, openpyxl, PyJWT
- Frontend: React 18, TypeScript, Vite, Glassmorphism UI, Lucide Icons, html5-qrcode
- Desktop: Tkinter GUI, Pystray (System Tray), Uvicorn background server
- Deployment: Docker, Docker Compose, Windows Service / Startup Task scripts

## Ứng dụng cho MEIMS/QLTB
- **Tự động hóa biên bản bàn giao thiết bị y tế** từ dữ liệu OCR/Excel
- **Tạo nhãn QR** cho thiết bị y tế, theo dõi trạng thái bảo trì
- **Dashboard quản lý tài sản** y tế theo khoa/phòng
- **RBAC** phù hợp với phân quyền: Kỹ sư, Quản lý, Xét nghiệm

## Open questions
- Tích hợp với OCR pipeline hiện tại (Mistral OCR) như thế nào?
- Có cần fork và customize template Word cho biên bản kiểm định BYT không?
- So sánh với Snipe-IT: DocuFlow tập trung tài liệu, Snipe-IT tập trung asset management.