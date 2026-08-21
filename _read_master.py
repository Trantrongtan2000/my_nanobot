import pandas as pd
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

p = r'C:\Users\tantt\.nanobot\media\telegram\AgADRiIAAsd8GFc.xltm'
df = pd.read_excel(p, sheet_name='2. Ban giao lap dat')
df['SN'] = df['SN'].astype(str).str.strip()
df = df[(df['SN'] != 'nan') & (df['SN'] != 'Không có')]

for idx, row in df.iterrows():
    ten = str(row.get('Ten ', '')).strip()
    model = str(row.get('Model ', '')).strip()
    sn = str(row.get('SN', '')).strip()
    khoa = str(row.get('Khoa', '')).strip()
    phong = str(row.get('Số phòng ', '')).strip()
    bh = str(row.get('Tình trạng bảo hành', '')).strip()
    kd = str(row.get('Tình trạng kiểm định', '')).strip()
    print(f'{ten} | {model} | {sn} | {khoa} | {phong} | BH: {bh} | KD: {kd}')
