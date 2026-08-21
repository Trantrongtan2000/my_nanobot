import os
import re
from datetime import datetime

entity_dir = r'C:\Users\tantt\.nanobot\workspace\wiki\entities'
output_file = r'C:\Users\tantt\.nanobot\workspace\master_data.html'

# Department mapping with display names
dept_names = {
    'bvq7_cap_cuu': 'Cấp cứu',
    'bvq7_cap_cuu_loc_mau': 'Cấp cứu - Đơn vị lọc máu',
    'bvq7_chan_doan_hinh_anh': 'Chẩn đoán hình ảnh',
    'bvq7_da_lieu': 'Da liễu',
    'bvq7_he_thong_bao_goi_y_ta': 'Hệ thống báo gọi y tá',
    'bvq7_he_thong_khi': 'Hệ thống khí',
    'bvq7_khac': 'Khác',
    'bvq7_kham_benh': 'Khám bệnh',
    'bvq7_khoa_xet_nghiem': 'Khoa Xét nghiệm',
    'bvq7_kiem_soat_can_nang': 'Kiểm soát cân nặng',
    'bvq7_kiem_soat_nhiem_khuan': 'Kiểm soát nhiễm khuẩn',
    'bvq7_mat': 'Mắt',
    'bvq7_nha_khi': 'Nhà khí',
    'bvq7_nha_thuoc': 'Nhà thuốc',
    'bvq7_nhi': 'Nhi',
    'bvq7_noi_soi_tieu_hoa': 'Nội soi tiêu hóa',
    'bvq7_noi_than_kinh': 'Nội thần kinh',
    'bvq7_noi_tiet': 'Nội tiết',
    'bvq7_noi_tong_hop': 'Nội tổng hợp',
    'bvq7_phuc_hoi_chuc_nang': 'Phục hồi chức năng',
    'bvq7_rang_ham_mat': 'Răng hàm mặt',
    'bvq7_san_khoa': 'Sản phụ khoa',
    'bvq7_sieu_am_bao_thai': 'Siêu âm bào thai',
    'bvq7_tai_mui_hong': 'Tai mũi họng',
    'bvq7_tim_mach': 'Tim mạch',
    'bvq7_trung_tam_tim_mach': 'Trung tâm tim mạch',
    'bvq7_ung_buou': 'Ung bướu',
}

def parse_entity(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    name = os.path.basename(filepath).replace('.md', '')
    dept_name = dept_names.get(name, name)
    
    # Extract device count
    count_match = re.search(r'\*\*Số thiết bị:\*\*\s*(\d+)', content)
    count = int(count_match.group(1)) if count_match else 0
    
    # Extract table rows
    devices = []
    in_table = False
    for line in content.split('\n'):
        if line.startswith('|') and 'STT' not in line and '---' not in line:
            parts = [p.strip() for p in line.split('|')]
            parts = [p for p in parts if p]  # remove empty
            if len(parts) >= 5:
                devices.append({
                    'stt': parts[0],
                    'sn': parts[1],
                    'ten': parts[2],
                    'model': parts[3],
                    'phong': parts[4],
                    'han': parts[5] if len(parts) > 5 else ''
                })
    
    return {
        'name': name,
        'dept_name': dept_name,
        'count': count,
        'devices': devices
    }

# Parse all entities
entities = []
for f in sorted(os.listdir(entity_dir)):
    if f.endswith('.md'):
        entities.append(parse_entity(os.path.join(entity_dir, f)))

# Sort departments alphabetically by Vietnamese name
entities.sort(key=lambda x: x['dept_name'])

# Generate HTML
html = f'''<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Master Data - BV Quận 7 Thiết bị Y tế</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .summary {{
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .department {{
            background-color: white;
            margin-bottom: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .dept-header {{
            background-color: #3498db;
            color: white;
            padding: 12px 15px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .dept-header:hover {{
            background-color: #2980b9;
        }}
        .dept-content {{
            padding: 15px;
            display: none;
        }}
        .dept-content.active {{
            display: block;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            font-size: 13px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 6px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        .count-badge {{
            background-color: #e74c3c;
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 12px;
        }}
        .footer {{
            margin-top: 20px;
            padding: 10px;
            text-align: center;
            color: #7f8c8d;
            font-size: 12px;
        }}
        .no-data {{
            color: #7f8c8d;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Master Data - Thiết bị Y tế BV Quận 7</h1>
        <p>Được tạo từ wiki entities | Ngày: {datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
    </div>
    
    <div class="summary">
        <strong>Tổng quan:</strong> {len(entities)} khoa/phòng | {sum(e['count'] for e in entities)} thiết bị
    </div>
'''

for entity in entities:
    html += f'''
    <div class="department">
        <div class="dept-header" onclick="toggleDept(this)">
            <span><strong>{entity['dept_name']}</strong></span>
            <span class="count-badge">{entity['count']} TB</span>
        </div>
        <div class="dept-content">
            <p><em>Wiki entity: {entity['name']}</em></p>
'''
    if entity['devices']:
        html += '''
            <table>
                <tr>
                    <th>#</th>
                    <th>S/N</th>
                    <th>Tên thiết bị</th>
                    <th>Model</th>
                    <th>Phòng</th>
                    <th>Hạn CN</th>
                </tr>
'''
        for i, dev in enumerate(entity['devices'], 1):
            html += f'                <tr><td>{dev["stt"]}</td><td>{dev["sn"]}</td><td>{dev["ten"]}</td><td>{dev["model"]}</td><td>{dev["phong"]}</td><td>{dev["han"]}</td></tr>\n'
        html += '            </table>\n'
    else:
        html += '            <p class="no-data">Chi tiết thiết bị xem wiki entity.</p>\n'
    
    html += '        </div>\n    </div>\n'

html += '''
    <div class="footer">
        Generated from wiki entities | Master Excel: G:/05_KIEM DINH/data/Kiểm định Master Test.xlsx
    </div>
    
    <script>
        function toggleDept(header) {
            const content = header.nextElementSibling;
            content.classList.toggle('active');
        }
        // Open first department by default
        document.querySelector('.dept-content').classList.add('active');
    </script>
</body>
</html>
'''

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'HTML created: {output_file}')
print(f'Total departments: {len(entities)}')
print(f'Total devices: {sum(e["count"] for e in entities)}')
