import os

path = r'C:\Users\tantt\Downloads\New folder (3)\Tân Bình\20. KIỂM SOÁT NHIỄM KHUẨN\QTVH\TA2.KSNK.QT.05_Quy trình vệ sinh trang thiết bị'
print('Exists:', os.path.exists(path))
if os.path.exists(path):
    print('Contents:', os.listdir(path))
else:
    # Try to find it
    base = r'C:\Users\tantt\Downloads\New folder (3)'
    for dp, dn, fn in os.walk(base):
        if 'TA2.KSNK.QT.05' in dp and 'Quy trình vệ sinh trang thiết bị' in dp:
            print('Found dir:', dp)
            print('Files:', fn)
            break
