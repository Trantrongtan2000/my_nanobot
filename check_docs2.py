import os
entity_dir = r'C:\Users\tantt\.nanobot\workspace\wiki\entities'
files = [f for f in os.listdir(entity_dir) if f.endswith('.md')]
print(f'Total entity files: {len(files)}')
missing = []
for f in sorted(files):
    path = os.path.join(entity_dir, f)
    with open(path, 'r', encoding='utf-8') as fh:
        content = fh.read()
    if '## Tài liệu' not in content:
        missing.append(f.replace('.md', ''))
print(f'Missing Tài liệu section: {len(missing)}')
for m in missing:
    print(m)
