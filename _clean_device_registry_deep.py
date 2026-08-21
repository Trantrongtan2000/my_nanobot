#!/usr/bin/env python3
# Deep clean device_registry.csv: fix paths, parse filenames, infer departments
import csv, re, json, os
from pathlib import Path
from collections import Counter, defaultdict

src = Path(r'G:\BV QUẬN 7_OCR_WORK_20260712\_ocr_handover_assets\device_registry.csv')
out_dir = Path(r'C:\Users\tantt\.nanobot\workspace')
out_csv = out_dir / 'devices_cleaned.csv'
out_json = out_dir / 'devices_cleaned.json'
base = Path(r'G:\BV QUẬN 7_OCR_WORK_20260712')

with src.open(encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

print(f'Raw rows: {len(rows)}')

# Fix md_path typo: md\md\ -> md\
def fix_md_path(p):
    if not p:
        return ''
    p = p.replace('md\\md\\', 'md\\').replace('md/md/', 'md/')
    return p

# Parse filename to extract info
def parse_filename(fname):
    info = {
        'equipment_name': '',
        'model': '',
        'serial_no': '',
        'manufacturer': '',
        'asset_code': '',
        'qty': 1
    }
    if not fname:
        return info
    
    # Remove .md/.pdf extension
    base_name = fname.replace('.md', '').replace('.pdf', '')
    
    # Pattern: BBBG NB_<info>_<asset_code>.md
    # Or: BBBG NB_<model>_<serial>_CT <manufacturer>.md
    # Or: <department>/<year>/BBBG NB_<info>_<asset_code>.md
    
    # Extract asset code (usually at end, format like Q726040027 or 25070520)
    m = re.search(r'[_-]([A-Z]?\d{6,})\.?$', base_name)
    if m:
        info['asset_code'] = m.group(1)
    
    # Extract serial (SN <serial>)
    m = re.search(r'SN\s+([A-Z0-9]+)', base_name, re.IGNORECASE)
    if m:
        info['serial_no'] = m.group(1)
    
    # Extract model (usually after NB_ and before _ or CT)
    # Pattern: NB_<model>_... or NB_<model>+...
    m = re.search(r'NB[_\s]+([A-Za-z0-9\-\+\.]+)', base_name)
    if m:
        model_candidate = m.group(1).strip()
        # Remove trailing numbers that might be asset codes
        model_candidate = re.sub(r'[\_\-\+].*$', '', model_candidate)
        if model_candidate:
            info['model'] = model_candidate
    
    # Extract manufacturer (CT <manufacturer>)
    m = re.search(r'CT\s+([A-Za-z\s]+?)(?:\s+SN|\s+_|$)', base_name, re.IGNORECASE)
    if m:
        info['manufacturer'] = m.group(1).strip()
    
    # Extract equipment name from the middle part
    # Remove prefixes and suffixes
    name_part = base_name
    name_part = re.sub(r'^BBBG\s+NB_?', '', name_part, flags=re.IGNORECASE)
    name_part = re.sub(r'_CT\s+.*$', '', name_part)
    name_part = re.sub(r'_SN\s+.*$', '', name_part)
    name_part = re.sub(r'_\d+$', '', name_part)
    name_part = re.sub(r'[\_\-\+]+', ' ', name_part)
    name_part = name_part.strip()
    
    # Clean up common patterns
    name_part = re.sub(r'^\d+x\s*', '', name_part)  # Remove leading "8x "
    name_part = re.sub(r'\s+', ' ', name_part)
    
    if name_part and len(name_part) > 3:
        info['equipment_name'] = name_part.title()
    
    return info

# Infer department from md_path folder structure
def infer_dept_from_path(md_path):
    if not md_path:
        return ''
    p = md_path.replace('md\\md\\', 'md\\')
    parts = p.split('\\')
    # Look for department folder in path
    for part in parts:
        part_lower = part.lower()
        if 'cấp cứu' in part_lower and ('lọc' in part_lower or 'thận' in part_lower):
            return 'Khoa Cấp cứu - Lọc thận'
        if 'cấp cứu' in part_lower:
            return 'Khoa Cấp cứu'
        if 'thận nhân tạo' in part_lower or 'thận' in part_lower:
            return 'Khoa Thận nhân tạo'
        if 'xét nghiệm' in part_lower:
            return 'Khoa Xét nghiệm'
        if 'nhà thuốc' in part_lower or 'nha thuoc' in part_lower:
            return 'Nhà thuốc'
        if 'khám bệnh' in part_lower:
            return 'Khoa Khám bệnh'
    return ''

# Standardize department
def std_dept(d):
    d = d.strip()
    if not d:
        return 'Không rõ'
    if d.startswith('BBBG') or d.startswith('BB '):
        return 'Không rõ'
    d = d.replace('–', '-').replace('—', '-')
    if 'Cấp cứu' in d and ('Lọc' in d or 'Thận' in d or 'Lọc máu' in d):
        return 'Khoa Cấp cứu - Lọc thận'
    if d in ['P.TTB Q7', 'Phòng Trang Thiết Bị Y Tế', 'Phòng Trang thiết bị y tế - Phòng Khám ĐK Tâm Anh Q.7', 'Phòng Trang thiết bị y tế']:
        return 'Phòng Trang thiết bị Y tế'
    if d == 'Khoa Cấp Cứu':
        return 'Khoa Cấp cứu'
    if d == 'Khoa Thận Nhân Tạo':
        return 'Khoa Thận nhân tạo'
    if d == 'Khoa Khám Bệnh':
        return 'Khoa Khám bệnh'
    return d

# Process rows
cleaned = []
for r in rows:
    # Skip pure empty rows
    if not any(r.get(k, '').strip() for k in ['equipment_name', 'model', 'serial_no', 'asset_code']):
        continue
    
    # Fix md_path
    md_path = fix_md_path(r.get('md_path', ''))
    r['md_path'] = md_path
    
    # Infer department from path if missing/BBBG
    dept = r.get('department', '').strip()
    if not dept or dept.startswith('BBBG') or dept.startswith('BB '):
        dept = infer_dept_from_path(md_path)
    
    # If still no dept, try to infer from filename
    if not dept or dept == 'Không rõ':
        fname = os.path.basename(md_path) if md_path else ''
        if 'cấp cứu' in fname.lower() or 'thận' in fname.lower():
            dept = 'Khoa Cấp cứu - Lọc thận'
    
    r['department'] = std_dept(dept)
    
    # Parse filename for additional info
    fname = os.path.basename(md_path) if md_path else ''
    parsed = parse_filename(fname)
    
    # Fill missing fields from filename parsing
    if not r.get('equipment_name', '').strip() and parsed['equipment_name']:
        r['equipment_name'] = parsed['equipment_name']
    if not r.get('model', '').strip() and parsed['model']:
        r['model'] = parsed['model']
    if not r.get('serial_no', '').strip() and parsed['serial_no']:
        r['serial_no'] = parsed['serial_no']
    if not r.get('asset_code', '').strip() and parsed['asset_code']:
        r['asset_code'] = parsed['asset_code']
    
    # Clean up
    r['equipment_name'] = r.get('equipment_name', '').strip().title()
    r['model'] = r.get('model', '').strip().upper()
    r['serial_no'] = r.get('serial_no', '').strip().upper()
    r['asset_code'] = r.get('asset_code', '').strip().upper()
    
    cleaned.append(r)

# Deduplicate by asset_code, then serial_no, then equipment_name+model
def dedup_key(r):
    if r.get('asset_code'):
        return ('asset', r['asset_code'])
    if r.get('serial_no'):
        return ('serial', r['serial_no'])
    return ('name', r.get('equipment_name', '').lower(), r.get('model', '').lower())

seen = set()
deduped = []
for r in cleaned:
    key = dedup_key(r)
    if key not in seen:
        seen.add(key)
        deduped.append(r)

print(f'After dedup: {len(deduped)}')

# Write cleaned CSV
fieldnames = ['asset_code', 'asset_tag', 'model', 'serial_no', 'manufacturer', 'origin_country', 'equipment_name', 'category', 'department', 'status', 'handover_date', 'form_code', 'contract_no', 'pdf_path', 'md_path', 'ocr_status', 'quality']
with out_csv.open('w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(deduped)

# Write cleaned JSON
with out_json.open('w', encoding='utf-8') as f:
    json.dump(deduped, f, ensure_ascii=False, indent=2)

# Summary
dept_counts = Counter(r.get('department','') for r in deduped)
print('\nBY DEPARTMENT:')
for dept, cnt in dept_counts.most_common():
    print(f'  {dept}: {cnt}')

# Devices with good data
good = [r for r in deduped if r.get('serial_no') and r.get('equipment_name')]
print(f'\nDevices with name + serial: {len(good)}')
for r in good:
    print(f"  {r.get('asset_code','')} | {r.get('equipment_name','')[:40]} | {r.get('model','')} | {r.get('serial_no','')} | {r.get('department','')}")

# Devices missing key fields
missing = [r for r in deduped if not r.get('serial_no') or not r.get('equipment_name')]
print(f'\nDevices missing name/serial: {len(missing)}')
for r in missing:
    print(f"  {r.get('asset_code','')} | {r.get('equipment_name','')[:30]} | {r.get('serial_no','')} | {r.get('department','')} | {r.get('md_path','')[:60]}")
