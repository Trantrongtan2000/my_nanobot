import pandas as pd
p = r'C:\Users\tantt\.nanobot\media\telegram\AgADRiIAAsd8GFc.xltm'
df = pd.read_excel(p, sheet_name='2. Ban giao lap dat')
df['SN'] = df['SN'].astype(str).str.strip()
df = df[(df['SN'] != 'nan') & (df['SN'] != 'Không có')]
print('=== MASTER EXCEL DEVICES ===')
print(f'Total: {len(df)}')
print('Serial numbers:')
for sn in df['SN'].tolist():
    print(f'  {sn}')
