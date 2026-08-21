import os
entity_dir = r'C:\Users\tantt\.nanobot\workspace\wiki\entities'
for f in sorted(os.listdir(entity_dir)):
    if f.endswith('.md'):
        print(f.replace('.md', ''))
