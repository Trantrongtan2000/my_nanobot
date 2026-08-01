#!/usr/bin/env python3
"""Extract XN + NT calibration devices and cross-ref handover docs."""
from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path

BASE = Path("/media/tan/T93/BV QUẬN 7_OCR_WORK_20260712")
KD = BASE / "05_KIEM DINH"
CSV_PATH = KD / "danh_sach_thiet_bi_toi_han_v2.csv"
OUT = Path("/home/tan/.nanobot/workspace/wiki/raw/bvq7_xn_nt_kiem_dinh_20260719.json")
OUT.parent.mkdir(parents=True, exist_ok=True)

HANDOVER_DIRS = [
    BASE / "02_HOP DONG MUA SAM" / "Biên bản bàn giao nội bộ" / "Xét nghiệm",
    BASE / "02_HOP DONG MUA SAM" / "Biên bản bàn giao nội bộ" / "Nhà thuốc",
    BASE / "2024" / "SCAN BÀN GIAO NỘI BỘ" / "Xét nghiệm",
    BASE / "2024" / "SCAN BÀN GIAO NỘI BỘ" / "Nhà thuốc",
]


def find_cert_md(cert_name: str) -> str | None:
    if not cert_name:
        return None
    matches = list(KD.rglob(f"*{cert_name}*"))
    mds = [m for m in matches if m.suffix.lower() == ".md"]
    # Prefer 2025_pdf / 2026_pdf
    for pref in ("2025_pdf", "2026_pdf", "wiki"):
        for m in mds:
            if pref in str(m):
                return str(m)
    return str(mds[0]) if mds else None


def find_cert_pdf(cert_name: str) -> str | None:
    if not cert_name:
        return None
    matches = list(KD.rglob(f"*{cert_name}*"))
    pdfs = [m for m in matches if m.suffix.lower() == ".pdf"]
    for pref in ("2025_pdf", "2026_pdf", "pdf-worktree"):
        for m in pdfs:
            if pref in str(m):
                return str(m)
    return str(pdfs[0]) if pdfs else None


def list_handover_files() -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for d in HANDOVER_DIRS:
        key = str(d.relative_to(BASE)) if d.exists() else str(d)
        files = []
        if d.exists():
            for f in sorted(d.rglob("*")):
                if f.is_file() and f.suffix.lower() in {".pdf", ".md", ".docx", ".doc", ".xlsx", ".xls", ".jpg", ".jpeg", ".png"}:
                    files.append(str(f.relative_to(BASE)))
        out[key] = files
    return out


def parse_cert_md_devices(md_path: str) -> list[dict]:
    """Best-effort extract serials / object names from OCR markdown."""
    p = Path(md_path)
    if not p.exists():
        return []
    text = p.read_text(encoding="utf-8", errors="replace")
    devices = []
    # Serial patterns common in VICS certs
    serials = re.findall(
        r"(?:Serial\s*No|Số\s*(?:máy|S/?N)|Mã\s*QL)[^\n:]*[:/]\s*([A-Za-z0-9\-_/]+)",
        text,
        flags=re.I,
    )
    objects = re.findall(
        r"(?:Object|Tên đối tượng đo)[^\n:]*[:]\s*([^\n]+)",
        text,
        flags=re.I,
    )
    places = re.findall(
        r"(?:Place|Nơi sử dụng)[^\n:]*[:]\s*([^\n]+)",
        text,
        flags=re.I,
    )
    numbers = re.findall(
        r"(?:Number|Số\s*\(Number\))[^\n:]*[:]\s*([^\n]+)",
        text,
        flags=re.I,
    )
    recal = re.findall(
        r"(?:Recalibration recommended|Ngày hiệu chuẩn kiến nghị)[^\n:]*[:]\s*([^\n]+)",
        text,
        flags=re.I,
    )
    return [{
        "serials_found": serials[:50],
        "objects_found": [o.strip() for o in objects[:20]],
        "places_found": [p.strip() for p in places[:20]],
        "cert_numbers": [n.strip() for n in numbers[:20]],
        "recal_dates": [r.strip() for r in recal[:20]],
        "chars": len(text),
    }]


def main() -> None:
    with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    xn = [r for r in rows if "XÉT NGHIỆM" in r.get("Khoa / Phòng", "").upper()]
    nt = [r for r in rows if "NHÀ THUỐC" in r.get("Khoa / Phòng", "").upper()]

    cert_cache: dict[str, dict] = {}

    def pack(r: dict) -> dict:
        cert = (r.get("Tên file chứng nhận hiện tại") or "").strip()
        if cert and cert not in cert_cache:
            md = find_cert_md(cert)
            pdf = find_cert_pdf(cert)
            ocr = parse_cert_md_devices(md) if md else []
            cert_cache[cert] = {"md": md, "pdf": pdf, "ocr_extract": ocr}
        info = cert_cache.get(cert, {})
        return {
            "stt": r.get("STT"),
            "ten": r.get("Tên thiết bị y tế"),
            "model": r.get("Model"),
            "serial": r.get("Số S/N"),
            "khoa": r.get("Khoa / Phòng"),
            "han_master": r.get("Ngày đến hạn (Master)"),
            "trang_thai": r.get("Trạng thái trên hệ thống"),
            "cert_file": cert,
            "cert_md": info.get("md"),
            "cert_pdf": info.get("pdf"),
        }

    xn_devs = [pack(r) for r in xn]
    nt_devs = [pack(r) for r in nt]
    handover = list_handover_files()

    # Group by equipment type
    by_type_xn: dict[str, list] = defaultdict(list)
    for d in xn_devs:
        by_type_xn[d["ten"] or "?"].append(d)
    by_type_nt: dict[str, list] = defaultdict(list)
    for d in nt_devs:
        by_type_nt[d["ten"] or "?"].append(d)

    result = {
        "source_csv": str(CSV_PATH),
        "extracted_at": "2026-07-19",
        "counts": {"xet_nghiem": len(xn_devs), "nha_thuoc": len(nt_devs), "certs_unique": len(cert_cache)},
        "xet_nghiem": xn_devs,
        "nha_thuoc": nt_devs,
        "by_type_xet_nghiem": {k: len(v) for k, v in sorted(by_type_xn.items())},
        "by_type_nha_thuoc": {k: len(v) for k, v in sorted(by_type_nt.items())},
        "certs": cert_cache,
        "handover_files": handover,
        "notes": [
            "OCR markdown already exists for all 8 unique cert files under 05_KIEM DINH/*_pdf.",
            "Handover folders may contain PDFs without OCR; listed for inventory cross-check.",
            "Master expiry mostly 2026-07-31 for current batch.",
        ],
    }

    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"XN={len(xn_devs)} NT={len(nt_devs)} certs={len(cert_cache)}")
    print("\n=== BY TYPE XN ===")
    for k, n in sorted(by_type_xn.items(), key=lambda x: -len(x[1])):
        print(f"  {len(n):2d}  {k}")
    print("\n=== BY TYPE NT ===")
    for k, n in sorted(by_type_nt.items(), key=lambda x: -len(x[1])):
        print(f"  {len(n):2d}  {k}")
    print("\n=== CERTS ===")
    for name, info in cert_cache.items():
        print(f"  MD={'Y' if info.get('md') else 'N'} PDF={'Y' if info.get('pdf') else 'N'}  {name[:70]}")
    print("\n=== HANDOVER FILE COUNTS ===")
    for k, files in handover.items():
        print(f"  {len(files):3d}  {k}")
        for f in files[:8]:
            print(f"       - {f}")
        if len(files) > 8:
            print(f"       ... +{len(files)-8} more")
    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()
