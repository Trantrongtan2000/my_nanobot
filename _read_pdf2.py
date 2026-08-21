import os
import fitz

files = [
    r'C:\Users\tantt\Downloads\New folder (3)\Quận 7\20. KIỂM SOÁT NHIỄM KHUẨN\QTVH\TA5.KSNK.QT.05_Quy trình vệ sinh trang thiết bị y tế\TA5.KSNK.QT.05_Quy trình vệ sinh trang thiết bị y tế.pdf',
    r'C:\Users\tantt\Downloads\New folder (3)\Tân Bình\20. KIỂM SOÁT NHIỄM KHUẨN\QTVH\TA2.KSNK.QT.05_Quy trình vệ sinh trang thiết bị\TA2.KSNK.QT.05_Quy trình vệ sinh trang thiết bị.pdf',
]

for path in files:
    label = 'Q7' if 'Quận 7' in path else 'TB'
    print(f'\n=== {label}: {os.path.basename(path)} ===')
    if not os.path.exists(path):
        print('FILE NOT FOUND')
        continue
    doc = fitz.open(path)
    has_text = False
    for i in range(min(15, len(doc))):
        page = doc.load_page(i)
        text = page.get_text()
        if text.strip():
            has_text = True
            print(f'--- Page {i+1} ---')
            print(text.strip()[:1500])
    if not has_text:
        print('No text layer (scan-only)')
    doc.close()
