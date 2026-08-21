import os
base = r'C:\Users\tantt\Downloads\New folder (3)'
keywords = ['thính lực', 'nhĩ lượng', 'oae', 'tiền đình', 'QT.05', 'vệ sinh']
for dp, dn, fn in os.walk(base):
    for f in fn:
        fl = f.lower()
        if any(k in fl for k in keywords):
            print(os.path.join(dp, f))
