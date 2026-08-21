import os
import re

entity_dir = r'C:\Users\tantt\.nanobot\workspace\wiki\entities'
synthesis_dir = r'C:\Users\tantt\.nanobot\workspace\wiki\synthesis'
raw_dir = r'C:\Users\tantt\.nanobot\workspace\wiki\raw'

# Categorize files
departments = [
    'bvq7_cap_cuu', 'bvq7_cap_cuu_loc_mau', 'bvq7_chan_doan_hinh_anh',
    'bvq7_da_lieu', 'bvq7_he_thong_bao_goi_y_ta', 'bvq7_he_thong_khi',
    'bvq7_khac', 'bvq7_kham_benh', 'bvq7_kiem_soat_can_nang',
    'bvq7_kiem_soat_nhiem_khuan', 'bvq7_mat', 'bvq7_nha_khi',
    'bvq7_nhi', 'bvq7_noi_soi_tieu_hoa', 'bvq7_noi_than_kinh',
    'bvq7_noi_tiet', 'bvq7_noi_tong_hop', 'bvq7_phuc_hoi_chuc_nang',
    'bvq7_rang_ham_mat', 'bvq7_san_khoa', 'bvq7_sieu_am_bao_thai',
    'bvq7_tai_mui_hong', 'bvq7_tim_mach', 'bvq7_trung_tam_tim_mach',
    'bvq7_ung_buou'
]

devices = [
    'blood-pressure-monitor', 'logtag', 'mpr-715f', 'omron_hem8712_20240456768vg',
    'patient-scale', 'pharmacy-refrigerator', 'resonance_r14o', 'rion_aa-m1c1', 'rion_rs-h1'
]

others = ['don_vi_tiet_khuan_trung_tam', 'ksnk_tam_anh', 'tam-anh-clinic-q7']
hospitals = ['bv_tam_anh_q7', 'bv_tam_anh_tan_binh']

# XN/NT departments that have synthesis page
xn_nt_deps = ['bvq7_khoa_xet_nghiem', 'bvq7_nha_thuoc']  # already has docs

def add_docs_section(filepath, category, name):
    with open(filepath, 'r', encoding='utf-8') as fh:
        content = fh.read()
    
    if '## Tài liệu' in content or '## Documents' in content:
        return False
    
    # Find where to insert (before ## Việc còn mở or at end)
    insert_pos = content.find('## Việc còn mở')
    if insert_pos == -1:
        insert_pos = len(content)
    
    docs_section = '\n## Tài liệu\n'
    
    if category == 'department':
        docs_section += '- **Master Excel:** `G:/05_KIEM DINH/data/Kiểm định Master Test.xlsx`\n'
        if name in ['bvq7_khoa_xet_nghiem', 'bvq7_nha_thuoc']:
            docs_section += '- **Tổng hợp kiểm định:** [[synthesis/bvq7_xn_nt_kiem_dinh_20260719]]\n'
        docs_section += '- **KSNK:** [[synthesis/ksnk_quy_trinh_hub]]\n'
        docs_section += '- **Raw OCR:** [[raw/ksnk/extracts/docx/]]\n'
    elif category == 'device':
        docs_section += '- **Wiki entity:** [[entities/{}]]\n'.format(name)
        if name == 'resonance_r14o':
            docs_section += '- **Manual:** [[raw/manuals/Resonance_R14O_user_handbook]]\n'
            docs_section += '- **OCR:** [[raw/manuals/Resonance_R14O_ocr]]\n'
        elif name == 'rion_aa-m1c1':
            docs_section += '- **Manual:** [[raw/manuals/Rion_AA-M1C1_instruction_manual]]\n'
        elif name == 'rion_rs-h1':
            docs_section += '- **Manual:** [[raw/manuals/Resonance_R14O_user_handbook]] (tham khảo)\n'
        elif name == 'omron_hem8712_20240456768vg':
            docs_section += '- **OCR nguồn:** Telegram OCR 2026-07-20\n'
        elif name == 'logtag':
            docs_section += '- **OCR chứng nhận:** [[raw/ocr_ksnk_qt05/q7/organized]]\n'
        elif name == 'mpr-715f':
            docs_section += '- **OCR chứng nhận:** [[raw/ocr_ksnk_qt05/q7/organized]]\n'
        elif name == 'pharmacy-refrigerator':
            docs_section += '- **OCR chứng nhận:** [[raw/ocr_ksnk_qt05/q7/organized]]\n'
        elif name == 'blood-pressure-monitor':
            docs_section += '- **OCR chứng nhận:** [[raw/ocr_ksnk_qt05/q7/organized]]\n'
        elif name == 'patient-scale':
            docs_section += '- **OCR chứng nhận:** [[raw/ocr_ksnk_qt05/q7/organized]]\n'
    elif category == 'hospital':
        docs_section += '- **Master Excel:** `G:/05_KIEM DINH/data/Kiểm định Master Test.xlsx`\n'
        docs_section += '- **Tổng hợp kiểm định:** [[synthesis/bvq7_xn_nt_kiem_dinh_20260719]]\n'
    elif category == 'other':
        if name == 'ksnk_tam_anh':
            docs_section += '- **KSNK Hub:** [[synthesis/ksnk_quy_trinh_hub]]\n'
            docs_section += '- **Gói Q7:** [[synthesis/ksnk_q7_goi_quy_trinh]]\n'
            docs_section += '- **Raw catalog:** [[raw/ksnk/catalog]]\n'
            docs_section += '- **DOCX extracts:** [[raw/ksnk/extracts/docx/]]\n'
        elif name == 'don_vi_tiet_khuan_trung_tam':
            docs_section += '- **KSNK Hub:** [[synthesis/ksnk_quy_trinh_hub]]\n'
        elif name == 'tam-anh-clinic-q7':
            docs_section += '- **Master Excel:** `G:/05_KIEM DINH/data/Kiểm định Master Test.xlsx`\n'
            docs_section += '- **Tổng hợp kiểm định:** [[synthesis/bvq7_xn_nt_kiem_dinh_20260719]]\n'
    
    new_content = content[:insert_pos] + docs_section + content[insert_pos:]
    
    with open(filepath, 'w', encoding='utf-8') as fh:
        fh.write(new_content)
    return True

# Process all files
count = 0
for f in sorted(os.listdir(entity_dir)):
    if not f.endswith('.md'):
        continue
    name = f.replace('.md', '')
    filepath = os.path.join(entity_dir, f)
    
    if name in departments:
        if add_docs_section(filepath, 'department', name):
            count += 1
            print(f'Added docs to dept: {name}')
    elif name in devices:
        if add_docs_section(filepath, 'device', name):
            count += 1
            print(f'Added docs to device: {name}')
    elif name in hospitals:
        if add_docs_section(filepath, 'hospital', name):
            count += 1
            print(f'Added docs to hospital: {name}')
    elif name in others:
        if add_docs_section(filepath, 'other', name):
            count += 1
            print(f'Added docs to other: {name}')

print(f'\nTotal updated: {count}')
