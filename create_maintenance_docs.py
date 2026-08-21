#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import os

NODE = r"D:\node-v24.14.0-win-x64\node.exe"
OFFICECLI_JS = r"C:\Users\tantt\AppData\Local\pnpm\global\v11\6980-19f5a76a79b\node_modules\@officecli\officecli\officecli.js"

def run_officecli(args):
    cmd = [NODE, OFFICECLI_JS] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR running: {' '.join(cmd)}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        raise subprocess.CalledProcessError(result.returncode, cmd)
    return result

departments = {
    "Cap_cuu": [
        ("Ban mo JS-003", ["4002802549", "4002802550"]),
        ("Den mo treo Solarmax Led 160+80", ["ELO2401001", "ELO2401002"]),
        ("Noi so sinh SK-AD2", ["SK372021"]),
        ("Xe day do cap cuu SC32-EMG", ["BM23-P5202", "BM23-P5205"]),
        ("Xe day y dung cu SC32PRO", ["BM23-P5192", "BM24-P1256", "BM24-P1266"]),
    ],
    "Cap_cuu_Loc_mau": [
        ("He thong loc nuoc RO ban cong nghiep", ["RO BCN"]),
    ],
    "Tim_mach": [
        ("BO luu dien UPS C2K-LCD", ["240813-27090104"]),
        ("BO luu dien UPS 11TG2", ["230208-26590031", "230208-26590036", "230208-26590037", "230208-26590038", "230919-74920087"]),
        ("May hut dich di dong New Askir", ["36376"]),
        ("Monitor benh nhan 4 thong so van chuyen Carescape V100", ["SH623240013SA", "SH623100222SA"]),
        ("Xe day do cap cuu SC32-EMG", ["BM24-P0821"]),
    ],
    "Da_lieu": [
        ("Can xong hoi MNH 303", ["1", "2", "3"]),
        ("Den Led anh sang sinh hoc Celluma Pro", ["CEOL24050044", "CEOL24050045"]),
        ("Den soi da MNH", ["1", "2", "3", "4"]),
        ("May dieu tri da bang Laser Q-Switched M031-3A/2 QX", ["24001852"]),
        ("May hut khoi khu mui BlueEva", ["BES10B0B6", "BES10B0B7"]),
        ("May laser SCANXEL", ["MSSCN2404001", "MSSCN2404002"]),
        ("May phan tich da A-one Standard", ["A1D 240002", "A1D 240003"]),
        ("May xit hoi lanh Cryo6", ["2320015782", "2320015785"]),
        ("Thiet bi cham soc da da nang APD-2000", ["APD2002402008", "APD2002402009"]),
        ("Xe day y dung cu SC32PRO", ["BM24-P0702"]),
    ],
    "Noi_tiet": [
        ("Can phan tich thanh phan co the BSM370", ["S9823000760"]),
        ("Monitor benh nhan 4 thong so van chuyen Carescape V100", ["SH624020128SA"]),
    ],
    "Mat": [
        ("Bang thu thi luc TSLC 2000", ["BK0811", "BK0433", "BK0055"]),
        ("Dao mo dien cao tan ZEUS-150", ["A07C0AT0484"]),
        ("Den mo di dong KL05L.ILED", [""]),
        ("Kinh soi goc tien phong 3 guong V3MIR", ["LOT: CEO5058"]),
        ("Kinh soi goc tien phong 4 guong VG4", ["LOT: CEO4193"]),
        ("Kinh Volk V90C", ["LOT: CD08208"]),
        ("Kinh Volk VDGTLWF", ["LOT: CEO4004"]),
        ("May cat lop vong mac Cirrus HD-OCT", ["840-26613"]),
        ("May chup mau day mat Kowa Nonmyd AF", ["32111500377"]),
        ("May do khuc xa tu dong ARKM-200", ["2092948"]),
        ("May do nhan ap SNT-700", ["22080970"]),
        ("Nhan ap ke SHIOTS PMS", ["LOT: 20240067"]),
        ("Sinh hien vi kham 700GL", ["2092267", "2094650", "2092268"]),
    ],
    "Nhi": [
        ("May hut dich di dong New Askir", ["38456"]),
        ("May pha rung tim TEC-5621", ["10416"]),
        ("Xe day do cap cuu SC32-EMG", ["BM23-P5203"]),
    ],
    "Noi_than_kinh": [
        ("May dien co 12 kenh SIERRA SUMMIT", ["19027206AC0624043"]),
        ("May dien nao 32 kenh ARC ESSENTIA-E3", ["19029003E3A0624030"]),
    ],
    "Noi_tong_hop": [
        ("Bom tiem dien TE-SS830", ["220510005"]),
        ("May do chuc nang ho hattp FeNO+", ["240318-04-3852"]),
    ],
    "Rang_ham_mat": [
        ("Den tay trang rang ZME-3000", ["68776"]),
        ("Ghe kham nha khoa SK-IA", ["A-10ND0651", "A-10ND0652"]),
        ("May cao voi rang sieu am PYON 2 PB-200", ["04156", "04161"]),
        ("May khoan xuong nha khoa Piezotome Cube", ["218920005"]),
        ("May tra dau bao duong Assistina 301 plus", ["118738"]),
        ("May tram rang KER-910860-1", ["423063045", "423081788"]),
        ("Xe day y dung cu SC32PRO", ["BM24-P0704", "BM24-P0711"]),
    ],
    "San_phu_khoa": [
        ("Ban chuyen dung A99-5", ["SKPRR24024-2-001", "SKPRR24024-2-002"]),
        ("Ban kham san phu khoa Examline 740", ["665", "666", "671"]),
        ("Doppler SR2", ["(21)777C602899724", "(21)777C602900524", "(21)777C602900324", "(21)777C602900724", "(21)777C602900424", "(21)777C602900624"]),
        ("Ghe kham san phu khoa Francy", ["F0000103", "F0000100", "F0000101", "F0000099", "F0000095", "F0000097", "F0000096", "F0000102"]),
        ("May ap lanh san khoa CR-201", ["4147", "4148"]),
        ("May monitor san khoa Team3A-B", ["(21)777AB70589524", "(21)777AB70589424", "(21)777AB70590524", "(21)777AB70590724", "(21)777AB70590624", "(21)777AB70589724"]),
        ("May sieu am mau Voluson P6", ["VP6803351"]),
        ("May sieu am mau Voluson P8", ["VP8206609"]),
        ("May soi co tu cung KP 3000", ["35277", "35278"]),
        ("Monitor benh nhan 4 thong so Carescape V100", ["SH624020107SA", "SH624340024SA"]),
        ("BO luu dien UPS 11TG2", ["230204-02290094"]),
        ("BO luu dien UPS N/A", ["230919-74920072"]),
        ("Xe day y dung cu SC32PRO", ["BM23-P5187", "BM23-P5188", "BM23-P5194", "BM23-P5195", "BM24-P0705", "BM24-P0706", "BM24-P0708", "BM24-P0709", "BM24-P1266", "BM24-P1267", "BM24-P1740", "BM24-P1742"]),
    ],
    "Tai_mui_hong": [
        ("He thong VNG VisualEyes 525", ["1053505", "1053506"]),
        ("He thong vHIT VisualEyes EyeSeeCam", ["1053507", "1053508"]),
        ("May do am oc tai R140 TE", ["R14O24C000405"]),
        ("May do nhi luong RS-H1", ["00690033"]),
        ("May do thinh luc AA-M1C1", ["00590060"]),
    ],
}

dept_display = {
    "Cap_cuu": "Cấp cứu",
    "Cap_cuu_Loc_mau": "Cấp cứu - Lọc máu",
    "Tim_mach": "Tim mạch",
    "Da_lieu": "Da liễu",
    "Noi_tiet": "Nội tiết",
    "Mat": "Mắt",
    "Nhi": "Nhi",
    "Noi_than_kinh": "Nội thần kinh",
    "Noi_tong_hop": "Nội tổng hợp",
    "Rang_ham_mat": "Răng hàm mặt",
    "San_phu_khoa": "Sản phụ khoa",
    "Tai_mui_hong": "Tai mũi họng",
}

base_path = r"C:\Users\tantt\.nanobot\workspace"

for dept_key, items in departments.items():
    file_name = os.path.join(base_path, f"Lich_bao_tri_24_7_{dept_key}.docx")
    dept_name = dept_display[dept_key]
    
    # Flatten: each (device, serial) becomes a row
    rows = []
    for device, serials in items:
        for serial in serials:
            rows.append((device, serial))
    
    # Create file
    run_officecli(["create", file_name, "--force"])
    
    # Add title
    run_officecli([
        "add", file_name, "/body",
        "--type", "paragraph",
        "--prop", "text=LỊCH BẢO TRÌ THIẾT BỊ Y TẾ",
        "--prop", "style=Heading1",
        "--prop", "size=18pt",
        "--prop", "bold=true",
        "--prop", "align=center",
        "--prop", "spaceAfter=6pt"
    ])
    
    run_officecli([
        "add", file_name, "/body",
        "--type", "paragraph",
        "--prop", f"text=Khoa: {dept_name} | Ngày: 24/07/2026 (Thứ 6)",
        "--prop", "style=Heading2",
        "--prop", "size=14pt",
        "--prop", "bold=true",
        "--prop", "align=center",
        "--prop", "spaceAfter=12pt"
    ])
    
    # Add table
    row_count = len(rows) + 1
    run_officecli([
        "add", file_name, "/body",
        "--type", "table",
        "--prop", f"rows={row_count}",
        "--prop", "cols=4",
        "--prop", "width=100%"
    ])
    
    # Header row
    run_officecli([
        "set", file_name, "/body/tbl[1]/tr[1]",
        "--prop", "header=true",
        "--prop", "c1=STT",
        "--prop", "c2=Tên thiết bị",
        "--prop", "c3=Số serial",
        "--prop", "c4=Ghi chú"
    ])
    
    # Format header
    for col in range(1, 5):
        run_officecli([
            "set", file_name, f"/body/tbl[1]/tr[1]/tc[{col}]",
            "--prop", "fill=1F4E79"
        ])
        run_officecli([
            "set", file_name, f"/body/tbl[1]/tr[1]/tc[{col}]/p[1]/r[1]",
            "--prop", "bold=true",
            "--prop", "color=FFFFFF"
        ])
    
    # Data rows - each serial on its own row
    for i, (device, serial) in enumerate(rows):
        row_num = i + 2
        stt = i + 1
        run_officecli([
            "set", file_name, f"/body/tbl[1]/tr[{row_num}]",
            "--prop", f"c1={stt}",
            "--prop", f"c2={device}",
            "--prop", f"c3={serial}",
            "--prop", "c4="
        ])
    
    # Set column widths
    run_officecli([
        "set", file_name, "/body/tbl[1]/tr[1]/tc[1]",
        "--prop", "width=800"
    ])
    run_officecli([
        "set", file_name, "/body/tbl[1]/tr[1]/tc[2]",
        "--prop", "width=3500"
    ])
    run_officecli([
        "set", file_name, "/body/tbl[1]/tr[1]/tc[3]",
        "--prop", "width=2500"
    ])
    run_officecli([
        "set", file_name, "/body/tbl[1]/tr[1]/tc[4]",
        "--prop", "width=2000"
    ])
    
    # Add footer
    run_officecli([
        "add", file_name, "/",
        "--type", "footer",
        "--prop", "type=default",
        "--prop", "text=Trang ",
        "--prop", "align=center",
        "--prop", "size=9pt"
    ])
    run_officecli([
        "add", file_name, "/footer[1]/p[1]",
        "--type", "field",
        "--prop", "fieldType=page"
    ])
    
    # Save
    run_officecli(["save", file_name])
    print(f"Created: {file_name} ({len(rows)} rows)")

print("\nAll files created successfully!")
