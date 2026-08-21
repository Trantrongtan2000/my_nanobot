import os
import pandas as pd

# Read master Excel
p = r'C:\Users\tantt\.nanobot\media\telegram\AgADRiIAAsd8GFc.xltm'
df = pd.read_excel(p, sheet_name='2. Ban giao lap dat')
df['SN'] = df['SN'].astype(str).str.strip()
df = df[(df['SN'] != 'nan') & (df['SN'] != 'Không có')]

# Get all serial numbers
sns = df['SN'].tolist()
print(f'Total devices in master Excel: {len(sns)}')

# Check wiki entities
wiki_entities_path = r'C:\Users\tantt\.nanobot\workspace\wiki\entities'
wiki_files = os.listdir(wiki_entities_path)
wiki_sns = []
for f in wiki_files:
    if f.endswith('.md'):
        sn_part = f.split('_')[-1].replace('.md', '')
        wiki_sns.append(sn_part)

print(f'Wiki entities files: {len(wiki_files)}')
print(f'Wiki entities SNs: {len(wiki_sns)}')

# Find missing in wiki
missing_in_wiki = []
for sn in sns:
    if sn not in wiki_sns:
        missing_in_wiki.append(sn)

print(f'Missing in wiki entities: {len(missing_in_wiki)}')
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