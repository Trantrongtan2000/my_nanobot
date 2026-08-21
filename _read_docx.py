import os
import sys

# Add the docx reading capability
try:
    from docx import Document
except ImportError:
    print("python-docx not installed")
    sys.exit(1)

base = r'C:\Users\tantt\Downloads\New folder (3)\Tân Bình\20. KIỂM SOÁT NHIỄM KHUẨN\QTVH\TA2.KSNK.QT.05_Quy trình vệ sinh trang thiết bị'
files = [
    'BK02_TA2.KSNK.QT.05_Bảng kiểm vệ sinh trang thiết bị y tế.docx',
    'PL02_TA2.KSNK.QT.05_Hóa chất khử khuẩn trang thiết bị y tế.docx',
]

for f in files:
    path = os.path.join(base, f)
    print(f'\n=== {f} ===')
    try:
        doc = Document(path)
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                print(text)
    except Exception as e:
        print(f'Error reading {f}: {e}')
