import os

base = r'C:\Users\tantt\Downloads\New folder (3)'
for dp, dn, fn in os.walk(base):
    for f in fn:
        if 'TA2.KSNK.QT.05' in f and f.endswith('.pdf'):
            print(os.path.join(dp, f))
        if 'TA5.KSNK.QT.05' in f and f.endswith('.pdf'):
            print(os.path.join(dp, f))
