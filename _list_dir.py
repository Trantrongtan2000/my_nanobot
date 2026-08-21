import os
path = r'C:\Users\tantt\Downloads\New folder (3)\Tân Bình\20. KIỂM SOÁT NHIỄM KHUẨN\QTVH\TA2.KSNK.QT.05_Quy trình vệ sinh trang thiết bị'
try:
    print(os.listdir(path))
except Exception as e:
    print(f'Error: {e}')
