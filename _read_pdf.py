import os
import sys

try:
    import fitz  # PyMuPDF
except ImportError:
    print("PyMuPDF not installed")
    sys.exit(1)

base = r'C:\Users\tantt\Downloads\New folder (3)'
targets = [
    ('Q7', r'Quận 7\20. KIỂM SOÁT NHIỄM KHUẨN\QTVH\TA5.KSNK.QT.05_Quy trình vệ sinh trang thiết bị y tế\TA5.KSNK.QT.05_Quy trình vệ sinh trang thiết bị y tế.pdf'),
    ('TB', r'Tân Bình\20. KIỂM SOÁT NHIỄM KHUẨN\QTVH\TA2.KSNK.QT.05_Quy trình vệ sinh trang thiết bị\TA2.KSNK.QT.05_Quy trình vệ sinh trang thiết bị.pdf'),
]

for label, rel in targets:
    path = os.path.join(base, rel)
    print(f'\n=== {label}: {os.path.basename(path)} ===')
    if not os.path.exists(path):
        print('FILE NOT FOUND')
        continue
    try:
        doc = fitz.open(path)
        for i in range(min(10, len(doc))):
            page = doc.load_page(i)
            text = page.get_text()
            if text.strip():
                print(f'--- Page {i+1} ---')
                print(text.strip()[:2000])
        doc.close()
    except Exception as e:
        print(f'Error: {e}')
