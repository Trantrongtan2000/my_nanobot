import os
import pandas as pd
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Read master Excel
p = r'C:\Users\tantt\.nanobot\media\telegram\AgADRiIAAsd8GFc.xltm'
df = pd.read_excel(p, sheet_name='2. Ban giao lap dat')
df['SN'] = df['SN'].astype(str).str.strip()
df = df[(df['SN'] != 'nan') & (df['SN'] != 'Không có')]

# Get all serial numbers from master
sns = df['SN'].tolist()
print(f'Total devices in master Excel: {len(sns)}')

# Check wiki entities - extract SNs from filenames
wiki_entities_path = r'C:\Users\tantt\.nanobot\workspace\wiki\entities'
wiki_files = [f for f in os.listdir(wiki_entities_path) if f.endswith('.md')]
print(f'Wiki entities files: {len(wiki_files)}')

# Extract SNs from filenames using regex patterns
wiki_sns = []
for f in wiki_files:
    # Try different patterns to extract SN from filename
    # Pattern 1: _SN.md (e.g., omron_hem8712_20240456768vg.md)
    match = re.search(r'_([A-Z0-9\-]+)\.md$', f)
    if match:
        sn = match.group(1)
        wiki_sns.append(sn)
        print(f'  {f} -> SN: {sn}')
    else:
        # Pattern 2: just the filename (e.g., mpr-715f.md)
        sn = f.replace('.md', '')
        wiki_sns.append(sn)
        print(f'  {f} -> SN: {sn} (from filename)')

print(f'\\nWiki entities SNs: {len(wiki_sns)}')
for sn in wiki_sns:
    print(f'  {sn}')

# Find missing in wiki
missing_in_wiki = []
for sn in sns:
    if sn not in wiki_sns:
        missing_in_wiki.append(sn)

print(f'\\nMissing in wiki entities: {len(missing_in_wiki)}')
for sn in missing_in_wiki[:30]:
    print(f'  {sn}')
if len(missing_in_wiki) > 30:
    print(f'  ... and {len(missing_in_wiki) - 30} more')

# Check OCR MD for missing SNs
ocr_root = r'G:\BV QUẬN 7_OCR_WORK_20260712\md'
found_in_ocr = {}
for root, dirs, files in os.walk(ocr_root):
    for f in files:
        if f.endswith('.md'):
            fpath = os.path.join(root, f)
            try:
                with open(fpath, 'r', encoding='utf-8') as fh:
                    content = fh.read()
                    for sn in missing_in_wiki:
                        if sn in content:
                            if sn not in found_in_ocr:
                                found_in_ocr[sn] = []
                            found_in_ocr[sn].append(fpath)
            except:
                pass

print(f'\\n=== OCR MD CHECK ===')
print(f'Found OCR docs for {len(found_in_ocr)} missing SNs')
for sn, paths in found_in_ocr.items():
    print(f'{sn}: {len(paths)} files')
    for p in paths[:2]:
        print(f'  {p}')
    if len(paths) > 2:
        print(f'  ... and {len(paths) - 2} more')

# Summary
print(f'\\n=== SUMMARY ===')
print(f'Total devices in master: {len(sns)}')
print(f'Wiki entities coverage: {len(wiki_sns)}/{len(sns)} ({len(wiki_sns)/len(sns)*100:.1f}%)')
print(f'Missing in wiki: {len(missing_in_wiki)}')
print(f'Found in OCR: {len(found_in_ocr)}')
print(f'Need to create wiki entities for: {len(missing_in_wiki) - len(found_in_ocr)} devices')