import pandas as pd
import os
import re

p = r'C:\Users\tantt\.nanobot\media\telegram\AgADRiIAAsd8GFc.xltm'
df = pd.read_excel(p, sheet_name='2. Ban giao lap dat')
df['SN'] = df['SN'].astype(str).str.strip()
df = df[(df['SN'] != 'nan') & (df['SN'] != 'Không có')]

entities_dir = r'C:\Users\tantt\.nanobot\workspace\wiki\entities'
entity_files = os.listdir(entities_dir)

# Get all serial numbers from entities
entity_sns = set()
for ef in entity_files:
    if ef.endswith('.md'):
        with open(os.path.join(entities_dir, ef), 'r', encoding='utf-8') as f:
            content = f.read()
            # Extract serial numbers from frontmatter
            sn_match = re.search(r'serial_no:\s*["\']?([^"\'\n]+)["\']?', content)
            if sn_match:
                entity_sns.add(sn_match.group(1).strip())

output_lines = []
output_lines.append("=== Devices in Master Excel ===")
for idx, row in df.iterrows():
    ten = str(row.get('Ten ', '')).strip()
    model = str(row.get('Model ', '')).strip()
    sn = str(row.get('SN', '')).strip()
    khoa = str(row.get('Khoa', '')).strip()
    
    # Check if SN exists in any entity
    sn_found = any(sn in e or e in sn for e in entity_sns)
    
    status = "OK" if sn_found else "MISSING"
    output_lines.append(f"{status} | {ten} | {model} | {sn} | {khoa}")

with open(r'C:\Users\tantt\.nanobot\workspace\_check_output.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))

print("Done. Output written to _check_output.txt")