import fitz, os
path = r'C:\Users\tantt\Downloads\New folder (3)\Tân Bình\20. KIỂM SOÁT NHIỄM KHUẨN\QTVH\TA2.KSNK.QT.05_Quy trình vệ sinh trang thiết bị\TA2.KSNK.QT.05_Quy trình vệ sinh trang thiết bị.pdf'
doc = fitz.open(path)
print('pages', len(doc))
for i, page in enumerate(doc):
    text = page.get_text()
    if text.strip():
        print(f'--- Page {i+1} ---')
        print(text.strip()[:2000])
