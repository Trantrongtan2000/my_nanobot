import os
base = r'C:\Users\tantt\Downloads\New folder (3)'
for dp, dn, fn in os.walk(base):
    if 'TA2.KSNK.QT.05' in dp:
        print('DIR:', dp)
        for f in fn:
            print('  FILE:', f)
        break
