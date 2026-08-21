import os
import pandas as pd
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Read master Excel
p = r'C:\Users\tantt\.nanobot\media\telegram\AgADRiIAAsd8GFc.xltm'
df = pd.read_excel(p, sheet_name='2. Ban giao lap dat')
df['SN'] = df['SN'].astype(str).str.strip()
df = df[(df['SN'] != 'nan') & (df['SN'] != 'Không có')]

# Get all serial numbers
sns = df['SN'].tolist()
print(f'Total devices in master Excel: {len(sns)}')

# Check wiki entities - read actual SNs from file content
wiki_entities_path = r'C:\Users\tantt\.nanobot\workspace\wiki\entities'
wiki_files = [f for f in os.listdir(wiki_entities_path) if f.endswith('.md')]
print(f'Wiki entities files: {len(wiki_files)}')

# Extract SNs from wiki file content
wiki_sns = []
for f in wiki_files:
    fpath = os.path.join(wiki_entities_path, f)
    try:
        with open(fpath, 'r', encoding='utf-8') as fh:
            content = fh.read()
            # Look for serial_no: or SN: pattern
            for line in content.split('\n'):
                if 'serial_no' in line.lower() or 'sn:' in line.lower():
                    parts = line.split(':')
                    if len(parts) >= 2:
                        sn = parts[1].strip().strip('"').strip("'")
                        if sn and sn != '':
                            wiki_sns.append(sn)
                            break
    except:
        pass

print(f'Wiki entities SNs from content: {len(wiki_sns)}')
for sn in wiki_sns:
    print(f'  {sn}')

# Find missing in wiki
missing_in_wiki = []
for sn in sns:
    if sn not in wiki_sns:
        missing_in_wiki.append(sn)

print(f'\nMissing in wiki entities: {len(missing_in_wiki)}')
for sn in missing_in_wiki[:20]:
    print(f'  {sn}')
if len(missing_in_wiki) > 20:
    print(f'  ... and {len(missing_in_wiki) - 20} more')

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

print(f'\n=== OCR MD CHECK ===')
print(f'Found OCR docs for {len(found_in_ocr)} missing SNs')
for sn, paths in found_in_ocr.items():
    print(f'{sn}: {len(paths)} files')
    for p in paths[:2]:
        print(f'  {p}')
    if len(paths) > 2:
        print(f'  ... and {len(paths) - 2} more')
