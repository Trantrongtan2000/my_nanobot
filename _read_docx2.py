import os
import sys

try:
    from docx import Document
except ImportError:
    print("python-docx not installed")
    sys.exit(1)

base = r'C:\Users\tantt\Downloads\New folder (3)'
target_files = [
    'BK02_TA2.KSNK.QT.05_Bảng kiểm vệ sinh trang thiết bị y tế.docx',
    'PL02_TA2.KSNK.QT.05_Hóa chất khử khuẩn trang thiết bị y tế.docx',
]

found = {}
for dp, dn, fn in os.walk(base):
    for f in fn:
        if f in target_files:
            found[f] = os.path.join(dp, f)

for f in target_files:
    path = found.get(f)
    print(f'\n=== {f} ===')
    if not path:
        print('NOT FOUND')
        continue
    try:
        doc = Document(path)
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                print(text)
    except Exception as e:
        print(f'Error: {e}')
