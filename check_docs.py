import os
entity_dir = r'C:\Users\tantt\.nanobot\workspace\wiki\entities'
no_docs = []
for f in sorted(os.listdir(entity_dir)):
    if f.endswith('.md'):
        path = os.path.join(entity_dir, f)
        with open(path, 'r', encoding='utf-8') as fh:
            content = fh.read()
        if '## Tài liệu' not in content and '## Documents' not in content:
            no_docs.append(f.replace('.md', ''))
print(f'No Tài liệu section: {len(no_docs)}')
for n in no_docs:
    print(f'  - {n}')
