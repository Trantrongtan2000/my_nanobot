import os
import re
entity_dir = r'C:\Users\tantt\.nanobot\workspace\wiki\entities'
for f in sorted(os.listdir(entity_dir)):
    if f.endswith('.md'):
        with open(os.path.join(entity_dir, f), 'r', encoding='utf-8') as fh:
            content = fh.read()
            rows = [line for line in content.split('\n') if line.strip().startswith('|') and 'SN' not in line and '---' not in line and 'STT' not in line]
            print(f"{f}: {len(rows)}")