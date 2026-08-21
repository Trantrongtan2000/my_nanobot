#!/usr/bin/env python3
# Clean device_registry.csv into LLM Wiki-ready device inventory
import csv, re, json
from pathlib import Path
from collections import Counter, defaultdict

src = Path(r'G:\BV QUẬN 7_OCR_WORK_20260712\_ocr_handover_assets\device_registry.csv')
out_dir = Path(r'C:\Users\tantt\.nanobot\workspace')
out_csv = out_dir / 'devices_cleaned.csv'
out_json = out_dir / 'devices_cleaned.json'

with src.open(encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

# Filter: keep rows with at least equipment_name OR model OR serial_no
# Drop pure doc rows and empty rows
def is_device_row(r):
    return any(r.get(k, '').strip() for k in ['equipment_name', 'model', 'serial_no'])

devices = [r for r in rows if is_device_row(r)]

# Standardize department names
def std_dept(d):
    d = d.strip()
    if not d:
        return 'Không rõ'
    # Drop BBBG filename leaks
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

for r in devices:
    r['department'] = std_dept(r.get('department', ''))

# Deduplicate by serial_no + model + equipment_name
seen = set()
unique = []
for r in devices:
    key = (r.get('serial_no','').strip(), r.get('model','').strip(), r.get('equipment_name','').strip())
    if key not in seen:
        seen.add(key)
        unique.append(r)

# Write cleaned CSV
fieldnames = ['asset_code', 'asset_tag', 'model', 'serial_no', 'manufacturer', 'origin_country', 'equipment_name', 'category', 'department', 'status', 'handover_date', 'form_code', 'contract_no', 'pdf_path', 'md_path', 'ocr_status', 'quality']
with out_csv.open('w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(unique)

# Write cleaned JSON
with out_json.open('w', encoding='utf-8') as f:
    json.dump(unique, f, ensure_ascii=False, indent=2)

print(f'Cleaned: {len(devices)} -> {len(unique)} devices')
print(f'CSV: {out_csv}')
print(f'JSON: {out_json}')

# Summary by department
dept_counts = Counter(r.get('department','') for r in unique)
print('\nBY DEPARTMENT:')
for dept, cnt in dept_counts.most_common():
    print(f'  {dept}: {cnt}')

# Show devices with missing key fields
missing = [r for r in unique if not r.get('serial_no','').strip() or not r.get('equipment_name','').strip()]
print(f'\nMISSING serial/name: {len(missing)}')
for r in missing[:10]:
    print(' ', r.get('asset_code',''), '|', r.get('equipment_name','')[:30], '|', r.get('serial_no',''), '|', r.get('department',''))
