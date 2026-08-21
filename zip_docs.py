import zipfile, os, glob

files = glob.glob(r'C:\Users\tantt\.nanobot\workspace\Lich_bao_tri_24_7_*.docx')
zip_path = r'C:\Users\tantt\.nanobot\workspace\Lich_bao_tri_24_7.zip'

with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for f in files:
        try:
            zf.write(f, os.path.basename(f))
            print('Added:', os.path.basename(f))
        except Exception as e:
            print('Skip', os.path.basename(f), ':', e)

print('Zip size:', os.path.getsize(zip_path))
