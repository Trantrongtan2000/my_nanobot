# -*- coding: utf-8 -*-
import hashlib, json, os, re, sys
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

ROOT = Path(sys.argv[1])
MD_ROOT = ROOT / "md"
OUT = ROOT / "_ocr_handover_assets"
OUT.mkdir(exist_ok=True)

KEY_MAP = {
    "source_pdf": "source_pdf",
    "pdf_path": "pdf_path",
    "md_path": "md_path",
    "doc_type": "doc_type",
    "doc_type_label": "doc_type_label",
    "pages": "pages",
    "form_code": "form_code",
    "handover_date": "handover_date",
    "department": "department",
    "party_giver": "party_giver",
    "party_receiver": "party_receiver",
    "party_a": "party_a",
    "party_b": "party_b",
    "contract_no": "contract_no",
    "ref_no": "ref_no",
    "model": "model",
    "serial_no": "serial_no",
    "serial_number": "serial_no",
    "manufacturer": "manufacturer",
    "origin_country": "origin_country",
    "equipment_name": "equipment_name",
    "equipment_count": "equipment_count",
    "equipment_list": "equipment_list",
    "ocr_model": "ocr_model",
    "ocr_time": "ocr_time",
    "ocr_at": "ocr_time",
}

JSON_SERIAL_KEYS = {"serial_no", "serial_number", "model", "manufacturer", "name"}
ITEM_HEADER_CANDIDATES = [
    ["stt", "ten thiet bi", "dvt", "so luong", "ghi chu"],
    ["stt", "ten thiet bi", "model", "hang san xuat", "quoc gia sx", "serial_no", "so luong", "ghi chu"],
    ["stt", "ten thiet bi", "model", "serial_no", "hang", "so luong", "ghi chu"],
    ["stt", "ten thiet bi", "dvt", "so luong"],
    ["stt", "ten thiet bi", "ghi chu"],
]

def safe_strip(value):
    if value is None:
        return ""
    return str(value).strip()

def remove_accents(text: str) -> str:
    text = text.replace("đ", "d").replace("Đ", "D")
    return "".join(ch for ch in text if ch.isascii() or ch.isspace())

def normalize_rel(rel):
    return str(rel).replace("\\", "/")

def find_md_target(root: Path, rel_target: str) -> Path:
    rel_norm = remove_accents(rel_target).lower()
    rel_norm = re.sub(r"\s+", " ", rel_norm)
    rel_norm = re.sub(r"[^a-z0-9/\\_.\- ]", "", rel_norm)
    for dp, dns, fns in os.walk(root):
        dp_rel = remove_accents(str(Path(dp).relative_to(root))).replace("\\", "/").lower()
        dp_rel = re.sub(r"\s+", " ", dp_rel)
        dp_rel = re.sub(r"[^a-z0-9/_.\- ]", "", dp_rel)
        for fn in fns:
            if not fn.lower().endswith(".md"):
                continue
            full_candidate = f"{dp_rel}/{fn}".lower()
            full_candidate = re.sub(r"\s+", " ", full_candidate)
            full_candidate = re.sub(r"[^a-z0-9/_.\- ]", "", full_candidate)
            name_only = re.sub(r"[^a-z0-9_.\- ]", "", fn.lower())
            if full_candidate == rel_norm or name_only == rel_norm:
                return Path(dp) / fn
    return None

def is_yaml_frontmatter(lines):
    return bool(lines) and lines[0].lstrip().startswith("---")

def load_yaml_frontmatter(text):
    data = {}
    for line in text.splitlines():
        if not line.strip() or line.strip() == "---":
            continue
        match = re.match(r"\s*([A-Za-z0-9_]+)\s*:\s*(.*)", line)
        if not match:
            continue
        key, value = match.group(1), match.group(2).strip()
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        data[key] = value
    return data

def parse_frontmatter(path):
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError as exc:
        print(f"skip {path}: {exc}", file=sys.stderr)
        return {}
    lines = text.splitlines()
    if not lines or not is_yaml_frontmatter(lines):
        return {}
    end_idx = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_idx = idx
            break
    if end_idx is None:
        return {}
    data = load_yaml_frontmatter("\n".join(lines[1:end_idx]))
    normalized = {}
    for key, value in data.items():
        normalized[KEY_MAP.get(key, key)] = value
    return normalized

def walk_handover_md():
    for dirpath, _, filenames in os.walk(MD_ROOT):
        dp = Path(dirpath)
        for filename in filenames:
            if not filename.lower().endswith(".md"):
                continue
            path = dp / filename
            name = filename.lower()
            rel = normalize_rel(path.relative_to(ROOT))
            if any(name.startswith(prefix) for prefix in ("bbbg", "bbth")):
                yield path, rel, "filename_prefix"
                continue
            if any(token in name for token in ("bàn giao", "thu hồi", "ban giao", "thu hoi")) or "bbgnb" in name:
                yield path, rel, "filename_token"
                continue

def load_manifest_map():
    path_map = {}
    manifest_path = ROOT / "_ocr_manifest.jsonl"
    if manifest_path.exists():
        for line in manifest_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            pdf = rec.get("pdf")
            md = rec.get("md")
            if not pdf:
                continue
            path_map[str(pdf)] = {
                "status": rec.get("status", ""),
                "pages": rec.get("pages", ""),
                "error": rec.get("error", ""),
                "md": md,
            }
    return path_map

def split_items_table(text):
    lower = text.lower()
    markers = ["**Nội dung**", "Nội dung", "Theo hợp đồng số:", "nội dung"]
    start_idx = None
    for marker in markers:
        idx = lower.find(marker.lower())
        if idx != -1:
            start_idx = idx
            break
    if start_idx is None:
        return None
    snippet = text[start_idx: start_idx + 4000]
    match = re.search(r"(\|[^\n]*STT[^\n]*\|.*?)(?:\n\n|\Z)", snippet, re.S)
    if not match:
        return None
    table_block = match.group(1)
    lines = [ln.strip() for ln in table_block.splitlines() if ln.strip().startswith("|")]
    if len(lines) < 3:
        return None
    rows = []
    for line in lines[2:]:
        cols = [c.strip() for c in line.strip("|").split("|")]
        rows.append(cols)
    return rows

def normalize_header(header):
    return re.sub(r"[^a-z0-9]+", "_", header.strip().lower()).strip("_")

def parse_table_rows(rows):
    if not rows:
        return []
    header_candidates = [[" ".join(normalize_header(c) for c in col).strip() for col in zip(*rows[:2])] if len(rows) > 1 else None]
    headers = [normalize_header(h) for h in rows[0]]
    parsed = []
    for cols in rows[1:]:
        if len(cols) < len(headers):
            cols += [""] * (len(headers) - len(cols))
        row = {normalize_header(h): c for h, c in zip(headers, cols)}
        parsed.append(row)
        notes = row.get("ghi_chu", "")
        for key in ["so_seri", "serial_no", "sn", "ma_serial", "serial"]:
            if key not in row or not row.get(key):
                m = re.search(r"(?:số\s*seri|s/n|seri|sn|serial)[\s:.#\-]*([A-Z0-9][\w./\-]{3,})", notes, re.IGNORECASE)
                if m:
                    row[key] = m.group(1).strip()
                    break
    return parsed

def choose_best_equipment_item(meta):
    equips = meta.get("equipment_list") if isinstance(meta.get("equipment_list"), list) else []
    if not equips:
        return {}
    scored = []
    for idx, item in enumerate(equips):
        score = 0
        for key in JSON_SERIAL_KEYS:
            if str(item.get(key, "")).strip():
                score += 2
        if str(item.get("item_type", "")).lower().startswith("main"):
            score += 5
        scored.append((score, idx, item))
    scored.sort(reverse=True)
    return scored[0][2] if scored else equips[0]

def parse_equipment_list_item(item, fallback_meta):
    row = {
        "item_sequence": safe_strip(item.get("stt", "")),
        "item_name": safe_strip(item.get("name") or fallback_meta.get("equipment_name")),
        "item_model": safe_strip(item.get("model") or fallback_meta.get("model")),
        "item_manufacturer": safe_strip(item.get("manufacturer") or fallback_meta.get("manufacturer")),
        "item_origin_country": safe_strip(item.get("origin_country") or fallback_meta.get("origin_country")),
        "item_serial_no": safe_strip(item.get("serial_no") or item.get("serial_number") or fallback_meta.get("serial_no")),
        "item_quantity": safe_strip(item.get("qty") or fallback_meta.get("equipment_count")),
        "item_unit": safe_strip(item.get("unit")),
        "item_type": safe_strip(item.get("item_type")),
    }
    if "Model" in row["item_name"]:
        m = re.search(r"Model:\s*([^\-]+)", row["item_name"], re.IGNORECASE)
        if m and not row["item_model"]:
            row["item_model"] = m.group(1).strip()
    if not row["item_serial_no"]:
        m = re.search(r"Số seri:\s*([^\s]+)", row["item_name"], re.IGNORECASE)
        if m:
            row["item_serial_no"] = m.group(1).strip()
    return row

def parse_plain_section(text):
    lower = text.lower()
    patterns = {
        "plain_contract": r"(?:theo\s+hợp\s+đồng\s+số|hợp\s+đồng\s+số|hợp\s+đồng)[\s:#]*([A-Za-z0-9../\-]+)",
        "plain_department": r"bên\s+giao:.*?(khoa|phòng|p\.ttb)[^\n]{0,40}",
        "plain_receiver": r"bên\s+nhận:.*?\n\s*([^\n]{5,120})",
        "plain_giver": r"bên\s+giao:.*?\n\s*([^\n]{5,120})",
        "plain_date": r"(?:tp\.?\s*hcm|hà nội|ngày)[\s,]*([0-9]{1,2}\s+tháng\s+\d+\s+năm\s+\d{4})",
    }
    data = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, lower, re.IGNORECASE)
        data[key] = match.group(1).strip() if match else ""
    return data

def derive_location_from_rel(rel):
    rel = str(rel)
    if rel.startswith("md/"):
        rel = rel[3:]
    parts = rel.split("/")
    best = ""
    for part in parts[-4:]:
        cleaned = part.replace("_", " ").strip()
        if any(token in cleaned.lower() for token in ["khoa", "phòng", "p.", "trung tâm", "bộ phận", "khoa", "phòng khám"]):
            best = cleaned
    return best

def derive_doc_status(text):
    lower = text.lower()
    if "thu hồi" in lower or "(thu hồi)" in lower or "thu hoi" in lower:
        return "recovery"
    return "handover"

def derive_asset_class_from_name(name: str):
    name = name.lower()
    if any(token in name for token in ["máy chạy thận", "thận nhân tạo", "lọc máu", "lọc thận"]):
        return "hemodialysis"
    if any(token in name for token in ["x-quang", "ct ", "mri", "siêu âm", "chẩn đoán hình ảnh"]):
        return "imaging"
    if any(token in name for token in ["nội soi", "soi"]):
        return "endoscopy"
    if any(token in name for token in ["bơm tiêm", "bơm", "tiêm"]):
        return "infusion_pump"
    if any(token in name for token in ["máy thở", "thở"]):
        return "ventilator"
    if any(token in name for token in ["máy điện tim", "điện tim", "tim"]):
        return "cardiac"
    if any(token in name for token in ["rửa", "dung cụ", "linh kiện", "dây", "cáp", "ống"]):
        return "surgical_consumables"
    return "general_medical"

master_rows = []
item_rows = []
quality_rows = []
errors = defaultdict(int)
success = 0
manifest_map = load_manifest_map()

for path, rel, detection in walk_handover_md():
    meta = parse_frontmatter(path)
    md_rel = normalize_rel(path.relative_to(ROOT))
    pdf_rel = safe_strip(meta.get("source_pdf") or meta.get("pdf_path"))
    md_rel_meta = safe_strip(meta.get("md_path"))
    if not pdf_rel:
        pdf_rel = str(path.relative_to(ROOT)).replace("\\", "/").replace("md/", "", 1)
    if not md_rel_meta:
        md_rel_meta = md_rel
    pdf_meta = manifest_map.get(pdf_rel) or manifest_map.get(str(path.relative_to(ROOT)).replace("\\", "/").replace("md/", "", 1)) or {}
    ocr_time = safe_strip(meta.get("ocr_time") or meta.get("ocr_at"))
    if not ocr_time:
        ocr_time = safe_strip(pdf_meta.get("md", ""))
    text = ""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError as exc:
        errors["read_error"] += 1
        quality_rows.append({"md_path": md_rel, "pdf": pdf_rel, "quality": "read_error", "detail": str(exc)})
        continue
    linked_table_path = None
    for m in re.finditer(r'\[tbl-\d+\.md\]\(([^\)]+)\)', text):
        cand = find_md_target(ROOT, m.group(1))
        if cand and cand.exists():
            linked_table_path = cand
            break
    table_text = ""
    if linked_table_path:
        try:
            table_text = linked_table_path.read_text(encoding="utf-8", errors="ignore")
        except OSError as exc:
            errors["linked_table_read_error"] += 1
    raw_rows = split_items_table(text) or split_items_table(table_text) or []
    table_rows = parse_table_rows(raw_rows)
    plain = parse_plain_section(text)
    doc_type = "handover" if derive_doc_status(text) == "handover" else "recovery"
    page_count = safe_strip(meta.get("pages") or pdf_meta.get("pages", ""))
    try:
        page_count = str(int(page_count))
    except (TypeError, ValueError):
        page_count = safe_strip(page_count)

    master = {
        "md_path": md_rel,
        "source_pdf": pdf_rel,
        "ocr_status": pdf_meta.get("status", ""),
        "document_type": doc_type,
        "document_type_label": safe_strip(meta.get("doc_type_label")),
        "form_code": safe_strip(meta.get("form_code", "")),
        "handover_date": safe_strip(meta.get("handover_date")),
        "department": safe_strip(meta.get("department") or derive_location_from_rel(rel)),
        "party_giver": safe_strip(meta.get("party_giver") or plain.get("plain_giver")),
        "party_receiver": safe_strip(meta.get("party_receiver") or plain.get("plain_receiver")),
        "party_a": safe_strip(meta.get("party_a")),
        "party_b": safe_strip(meta.get("party_b")),
        "contract_no": safe_strip(meta.get("contract_no") or plain.get("plain_contract")),
        "ref_no": safe_strip(meta.get("ref_no")),
        "ocr_model": safe_strip(meta.get("ocr_model")),
        "ocr_time": ocr_time,
        "pages": page_count,
        "equipment_count": safe_strip(meta.get("equipment_count")),
        "equipment_name": safe_strip(meta.get("equipment_name")),
        "model": safe_strip(meta.get("model")),
        "serial_no": safe_strip(meta.get("serial_no")),
        "manufacturer": safe_strip(meta.get("manufacturer")),
        "origin_country": safe_strip(meta.get("origin_country")),
        "derived_department": safe_strip(derive_location_from_rel(rel)),
        "derived_asset_class": safe_strip(derive_asset_class_from_name(safe_strip(meta.get("equipment_name")))),
        "best_item_source": "equipment_list" if meta.get("equipment_list") else ("table" if table_rows else "plain"),
        "quality_flag": "rich" if meta.get("model") or meta.get("serial_no") or meta.get("equipment_list") or table_rows else "light",
        "lang": "vi",
    }
    master_rows.append(master)
    success += 1
    best_item = choose_best_equipment_item(meta) if isinstance(meta.get("equipment_list"), list) and meta.get("equipment_list") else {}
    if not best_item and table_rows:
        best_item = table_rows[0]
    if not best_item:
        best_item = {"name": master["equipment_name"], "model": master["model"], "serial_no": master["serial_no"], "manufacturer": master["manufacturer"], "qty": master["equipment_count"]}

    if table_rows:
        seen = set()
        for idx, row in enumerate(table_rows, start=1):
            parsed = parse_equipment_list_item(row, master)
            dedup_key = (parsed["item_name"].lower(), parsed["item_model"].lower(), parsed["item_serial_no"].lower(), parsed["item_quantity"], parsed["item_unit"])
            if dedup_key in seen:
                continue
            seen.add(dedup_key)
            item_rows.append({
                "md_path": md_rel,
                "source_pdf": master["source_pdf"],
                "document_type": master["document_type"],
                "handover_date": master["handover_date"],
                "department": master["department"],
                "party_giver": master["party_giver"],
                "party_receiver": master["party_receiver"],
                "contract_no": master["contract_no"],
                "ref_no": master["ref_no"],
                "item_sequence": str(idx),
                "item_name": parsed["item_name"],
                "item_model": parsed["item_model"],
                "item_manufacturer": parsed["item_manufacturer"],
                "item_origin_country": parsed["item_origin_country"],
                "item_serial_no": parsed["item_serial_no"],
                "item_quantity": parsed["item_quantity"],
                "item_unit": parsed["item_unit"],
                "item_type": parsed["item_type"],
                "best_item_source": "table",
                "quality_flag": master["quality_flag"],
            })
    elif best_item:
        parsed = parse_equipment_list_item(best_item, master)
        item_rows.append({
            "md_path": md_rel,
            "source_pdf": master["source_pdf"],
            "document_type": master["document_type"],
            "handover_date": master["handover_date"],
            "department": master["department"],
            "party_giver": master["party_giver"],
            "party_receiver": master["party_receiver"],
            "contract_no": master["contract_no"],
            "ref_no": master["ref_no"],
            "item_sequence": "1",
            "item_name": parsed["item_name"],
            "item_model": parsed["item_model"],
            "item_manufacturer": parsed["item_manufacturer"],
            "item_origin_country": parsed["item_origin_country"],
            "item_serial_no": parsed["item_serial_no"],
            "item_quantity": parsed["item_quantity"],
            "item_unit": parsed["item_unit"],
            "item_type": parsed["item_type"],
            "best_item_source": "equipment_list",
            "quality_flag": master["quality_flag"],
        })

    if pdf_meta.get("status") and pdf_meta.get("status") != "ocr_ok":
        quality_rows.append({
            "md_path": md_rel,
            "pdf": pdf_rel,
            "quality": pdf_meta.get("status"),
            "detail": safe_strip(pdf_meta.get("error") or f"redirected={pdf_rel != md_rel_meta}"),
            "pages": page_count,
        })
        errors[pdf_meta.get("status", "other")] += 1

master_csv = OUT / "handover_master.csv"
item_csv = OUT / "handover_items_long.csv"
quality_csv = OUT / "handover_quality_issues.csv"
master_jsonl = OUT / "handover_master.jsonl"

master_fields = [
    "md_path", "source_pdf", "ocr_status", "document_type", "document_type_label", "form_code",
    "handover_date", "department", "party_giver", "party_receiver", "party_a", "party_b",
    "contract_no", "ref_no", "ocr_model", "ocr_time", "pages", "equipment_count", "equipment_name",
    "model", "serial_no", "manufacturer", "origin_country", "derived_department", "derived_asset_class",
    "best_item_source", "quality_flag", "lang"
]
with master_csv.open("w", encoding="utf-8-sig", newline="") as f:
    import csv
    w = csv.DictWriter(f, fieldnames=master_fields)
    w.writeheader()
    w.writerows(master_rows)

item_fields = [
    "md_path", "source_pdf", "document_type", "handover_date", "department", "party_giver", "party_receiver",
    "contract_no", "ref_no", "item_sequence", "item_name", "item_model", "item_manufacturer",
    "item_origin_country", "item_serial_no", "item_quantity", "item_unit", "item_type", "best_item_source", "quality_flag"
]
with item_csv.open("w", encoding="utf-8-sig", newline="") as f:
    import csv
    w = csv.DictWriter(f, fieldnames=item_fields)
    w.writeheader()
    w.writerows(item_rows)

quality_fields = ["md_path", "pdf", "quality", "detail", "pages"]
with quality_csv.open("w", encoding="utf-8-sig", newline="") as f:
    import csv
    w = csv.DictWriter(f, fieldnames=quality_fields)
    w.writeheader()
    w.writerows(quality_rows)

with master_jsonl.open("w", encoding="utf-8") as f:
    for row in master_rows:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

print(f"handover_md={success} item_rows={len(item_rows)} docs={len(master_rows)} quality={len(quality_rows)} errors={dict(errors)}")
print(f"master={master_csv}")
print(f"items={item_csv}")
print(f"quality={quality_csv}")
print(f"jsonl={master_jsonl}")
