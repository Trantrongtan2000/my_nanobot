2026-07-21 | updated `wiki/synthesis/bvq7_xn_nt_kiem_dinh_20260719.md` — tổng hợp lại Nhà thuốc: 14 thiết bị (9 CSV + 5 UTREL30), cập nhật ngày 2026-07-21, thêm refs UTREL30
2026-07-21 | gửi danh sách thiết bị nhà thuốc (9 CSV + 5 UTREL30) qua Telegram
2026-07-21 | field update Nhà thuốc T1: UTREL30 A0A5003406L5 tem 26A/N 484 ngày 14/07/2026 → hạn 14/07/2027; raw ảnh `wiki/raw/nha_thuoc_t1_utrel30_A0A5003406L5_20260714.jpg`; cập nhật entities bvq7_nha_thuoc + bvq7_nha_thuoc_utrel30

2026-07-21 | field Nhà thuốc T1 #2: LogTag mã TS 205753 (dự kiến UHADO-16 A0C1042585QT), tem 26A/N 484 ngày 14/07/2026 → hạn 14/07/2027, 28.8°C/61%RH; raw `wiki/raw/nha_thuoc_t1_logtag_205753_20260714.jpg`; cập nhật bvq7_nha_thuoc — lưu ý trùng số tem với UTREL30 T1

2026-07-21 | correction: ảnh mã TS 205753 là cùng UTREL30 A0A5003406L5 (không phải UHADO A0C1042585QT); gộp 2 ảnh field T1 vào 1 thiết bị; cập nhật bvq7_nha_thuoc + bvq7_nha_thuoc_utrel30

2026-07-21 | correction: 205753 là tem kiểm định (không phải mã TS); cập nhật bvq7_nha_thuoc + bvq7_nha_thuoc_utrel30 cho UTREL30 A0A5003406L5

2026-07-21 | correction: KD/HC là một — UTREL30 A0A5003406L5 tem 205753 (26A/N 484), 14/07/2026 → 14/07/2027; bỏ tách tem KD vs tem HC

2026-07-21 | correction: tem KD/HC UTREL30 A0A5003406L5 chỉ là 205753 (bỏ 26A/N 484); cập nhật bvq7_nha_thuoc + bvq7_nha_thuoc_utrel30

## 2026-07-21 — ingest KSNK
- Source: `C:\Users\tantt\Downloads\New folder (3)`
- Catalog: `raw/ksnk/catalog.md` (299 files)
- Main SOP PDF extracted: 76 → concepts: 57
- Hub: `synthesis/ksnk_quy_trinh_hub.md`
- Entity: `entities/ksnk_tam_anh.md`
- Note: no full binary copy; text extract ≤12 pages/PDF
- Weak text-layer: 76 docs


## 2026-07-21 — enrich KSNK DOCX
- DOCX extracted: 190 → `raw/ksnk/extracts/docx/`
- Concept pages enriched: 26
- Q7 package map: `synthesis/ksnk_q7_goi_quy_trinh.md` (19 packages)
- PDF mains remain scan-only (no local OCR engine / no Mistral key in env)
- 2026-07-21: Ingest KSNK corpus from BV Tâm Anh Q7 (TA5) + Tân Bình (TA2). Created topic page, 3 entities, 8 concepts, 1 synthesis. Source: C:\Users\tantt\Downloads\New folder (3). Total 323 files (~960MB).


- 2026-07-22: OCR TA5.KSNK.QT.05 (Q7, 54 trang) và TA2.KSNK.QT.05 (Tân Bình, 95 trang); tạo synthesis `synthesis/phong_do_thinh_luc_ve_sinh_ttb_20260722.md`. Đã xác định quy trình chung và giới hạn áp dụng cho RS-H1; chưa có manual AA-MAC1/OAE.
- 2026-07-22: Bổ sung manual OAE Resonance `raw/manuals/AgADrygAAuJYCVc.pdf`; cập nhật tổng hợp phòng đo thính lực. Không chốt Cidex OPA/thời gian 5 phút nếu chưa xác nhận đúng IFU/model.
 - 2026-07-22: Bổ sung manual Rion AA-M1C1 `raw/manuals/Rion_AA-M1C1_instruction_manual.pdf`; cập nhật hướng dẫn vệ sinh tai nghe, nút bấm phản hồi, vỏ máy và LCD. Cần xác minh model thực tế do nguồn trước ghi AA-MAC1.
 - 2026-07-24: OCR bổ sung 3 thiết bị ENT từ `_ocr_verify/`: Resonance R14O (`r14o/organized.md`), Rion AA-M1C1 (`rion/organized.md`), Rion RS-H1 (`rs-h1/organized.md`). Tạo entity wiki tương ứng và cập nhật index + synthesis phòng đo thính lực.
2026-07-24 | completed verification of all entities, updated index with missing UTREL30 devices, linked 5 LogTag UTREL30 to master CSV.
2026-07-24 | verified special SNs from master Excel: 10 Team3A-B monitors (SẢN PHỤ KHOA + CẤP CỨU), 3 SR2 dopplers (SẢN PHỤ KHOA), 1 UPS SLC-3000-TWIN PR02CO (NHÀ THUỐC).
2026-07-24 | created `wiki/entities/bvq7_san_khoa.md` (11 TB: 6 Team3A-B + 5 SR2) and `wiki/entities/bvq7_cap_cuu.md` (1 TB: Team3A-B).
2026-07-24 | updated `wiki/entities/bvq7_nha_thuoc.md` — bổ sung UPS `0000507245-004` vào danh sách thiết bị Nhà thuốc.
2026-07-24 | batch-created 23 department entity files from master Excel for all remaining departments (CHẨN ĐOÁN HÌNH ẢNH, NỘI SOI TIÊU HÓA, KHÁM BỆNH, etc.), covering 903 devices total.
2026-07-24 | updated `wiki/index.md` — thêm 23 entity files mới vào Entities section.
2026-07-24 | fixed broken wikilinks: ENT entity files `[[wiki/raw/ocr_ksnk_qt05]]` → `[[raw/ocr_ksnk_qt05/q7/organized.md]]`; synthesis `bvq7_xn_nt_kiem_dinh_20260719.md` refs `[[wiki/...]]` → `[[entities/...]]`/`[[topics/...]]`, removed deleted `bvq7_nha_thuoc_utrel30`.
2026-07-24 | added `## Tài liệu` sections to `bvq7_khoa_xet_nghiem.md` and `bvq7_nha_thuoc.md` linking to synthesis + raw JSON OCR data.
2026-07-24 | verified entity counts: XN 65, Nhà thuốc 17, Sản 49, Cấp cứu 144, plus 23 other departments from master Excel (903 devices total).
2026-07-24 | added `## Tài liệu` sections to all 39 remaining entity files (departments, devices, hospitals, KSNK) linking to master Excel, synthesis pages, raw OCR, and manuals.

## 2026-07-25 — Mistral OCR KSNK
- ok=57 skip=0 fail=0
- out: `raw/ksnk/ocr/`
- model: mistral-ocr-latest
