import os
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

wiki_entities_path = r'C:\Users\tantt\.nanobot\workspace\wiki\entities'
files = [f for f in os.listdir(wiki_entities_path) if f.endswith('.md')]

print('Reading wiki entity files for actual SNs:')
wiki_sns = []
for f in files:
    fpath = os.path.join(wiki_entities_path, f)
    try:
        with open(fpath, 'r', encoding='utf-8') as fh:
            content = fh.read()
            # Look for S/N: or serial_no: patterns
            sn_match = re.search(r'[Ss]/\s*N[:：]\s*([^\n]+)', content) or \
                       re.search(r'[Ss]erial[_\s]*[Nn][o\.]?[:：]\s*([^\n]+)', content)
            if sn_match:
                sn = sn_match.group(1).strip()
                wiki_sns.append(sn)
                print(f'  {f} -> SN: {sn}')
            else:
                # Try to find SN in the YAML front matter
                if '---' in content:
                    parts = content.split('---')
                    if len(parts) >= 3:
                        front_matter = parts[1]
                        sn_match = re.search(r'S/N\s*:[^\n]*([^\n]+)', front_matter) or \
                                   re.search(r'serial_no\s*:[^\n]*([^\n]+)', front_matter, re.IGNORECASE)
                        if sn_match:
                            sn = sn_match.group(1).strip()
                            wiki_sns.append(sn)
                            print(f'  {f} -> SN (from front matter): {sn}')
                        else:
                            print(f'  {f} -> No SN found in front matter')
                    else:
                        print(f'  {f} -> No front matter')
                else:
                    print(f'  {f} -> No front matter')
    except Exception as e:
        print(f'  {f} -> Error: {e}')

print(f'\nTotal wiki entities with SNs: {len(wiki_sns)}')
for sn in wiki_sns:
    print(f'  {sn}')
