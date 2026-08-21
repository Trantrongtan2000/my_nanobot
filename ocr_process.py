#!/usr/bin/env python3
import base64
import json
import os
import re
import sys
import time
from pathlib import Path

import requests


def _load_nanobot_env() -> None:
    for path in (Path.home() / ".nanobot" / ".env", Path.home() / ".nanobot" / "env"):
        if not path.is_file():
            continue
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if k and v and not os.environ.get(k):
                os.environ[k] = v


_load_nanobot_env()

API_KEY = os.environ.get("MISTRAL_API_KEY", "").strip()
if not API_KEY:
    raise SystemExit("Missing MISTRAL_API_KEY (set in ~/.nanobot/.env)")
API_URL = "https://api.mistral.ai/v1/ocr"
MODEL = os.environ.get("MISTRAL_OCR_MODEL", "mistral-ocr-latest")
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

PDF_FILES = [
    {
        "path": "/media/tan/T93/BV QUẬN 7_OCR_WORK_20260712/05_KIEM DINH/2025_pdf/MỤC 7. 14 nhiệt ẩm kế tự ghi.pdf",
        "name": "muc7_14_nhiet_am_ke_tu_ghi"
    },
    {
        "path": "/media/tan/T93/BV QUẬN 7_OCR_WORK_20260712/05_KIEM DINH/2025_pdf/MỤC 10. 14 Nhiệt ẩm kế điện tử UTREL.pdf",
        "name": "muc10_14_nhiet_am_ke_dien_tu_utrel"
    },
    {
        "path": "/media/tan/T93/BV QUẬN 7_OCR_WORK_20260712/05_KIEM DINH/2026/1 nhiệt ẩm kế điện tử UHADO-16.pdf",
        "name": "1_nhiet_am_ke_dien_tu_uhado16"
    }
]

OUTPUT_DIR = "/home/tan/.nanobot/workspace/wiki/raw"

def encode_pdf_to_base64(pdf_path):
    with open(pdf_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def call_mistral_ocr(base64_pdf):
    payload = {
        "model": MODEL,
        "document": {
            "type": "document_url",
            "document_url": f"data:application/pdf;base64,{base64_pdf}"
        }
    }
    response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=120)
    response.raise_for_status()
    return response.json()

def extract_markdown_from_response(response):
    pages = response.get("pages", [])
    markdown_parts = []
    for page in pages:
        markdown_parts.append(page.get("markdown", ""))
    return "\n\n".join(markdown_parts)

def extract_device_entries(markdown_text):
    """Extract device calibration entries from OCR markdown text."""
    entries = []
    
    # Common patterns in Vietnamese calibration records
    # Look for structured data patterns
    lines = markdown_text.split('\n')
    
    current_entry = {}
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Try to identify key-value pairs
        # Pattern: Key: Value or Key：Value
        kv_match = re.match(r'^([^:：]+)[:：]\s*(.+)$', line)
        if kv_match:
            key = kv_match.group(1).strip()
            value = kv_match.group(2).strip()
            
            # Map Vietnamese keys to standard fields
            key_lower = key.lower()
            if any(k in key_lower for k in ['tên', 'đối tượng', 'object', 'thiết bị', 'device']):
                current_entry['object_name'] = value
            elif any(k in key_lower for k in ['serial', 'số serial', 'số hiệu', 'number', 'mã']):
                current_entry['serial_number'] = value
            elif any(k in key_lower for k in ['nơi', 'place', 'bộ phận', 'phòng', 'khoa', 'department', 'địa điểm']):
                current_entry['place'] = value
            elif any(k in key_lower for k in ['ngày hiệu chuẩn', 'date of calibration', 'ngày kiểm định', 'calibration date']):
                current_entry['calibration_date'] = value
            elif any(k in key_lower for k in ['ngày hiệu chuẩn lại', 'recalibration', 'hạn sử dụng', 'next calibration', 'ngày kiểm định lại']):
                current_entry['recalibration_date'] = value
            elif any(k in key_lower for k in ['ghi chú', 'note', 'notes', 'kết quả', 'result']):
                current_entry['notes'] = value
    
    # Also try table-based extraction (markdown tables)
    table_pattern = re.compile(r'\|(.+)\|')
    in_table = False
    headers = []
    for line in lines:
        if line.startswith('|') and line.endswith('|'):
            in_table = True
            cells = [c.strip() for c in line.split('|')[1:-1]]
            if not headers:
                headers = [h.lower() for h in cells]
            else:
                row_data = dict(zip(headers, cells))
                entry = {}
                for h, v in row_data.items():
                    if any(k in h for k in ['tên', 'đối tượng', 'object', 'thiết bị']):
                        entry['object_name'] = v
                    elif any(k in h for k in ['serial', 'số serial', 'số hiệu', 'number', 'mã']):
                        entry['serial_number'] = v
                    elif any(k in h for k in ['nơi', 'place', 'bộ phận', 'phòng', 'khoa', 'department', 'địa điểm']):
                        entry['place'] = v
                    elif any(k in h for k in ['ngày hiệu chuẩn', 'date of calibration', 'ngày kiểm định']):
                        entry['calibration_date'] = v
                    elif any(k in h for k in ['ngày hiệu chuẩn lại', 'recalibration', 'hạn sử dụng', 'next calibration', 'ngày kiểm định lại']):
                        entry['recalibration_date'] = v
                    elif any(k in h for k in ['ghi chú', 'note', 'notes', 'kết quả', 'result']):
                        entry['notes'] = v
                if entry:
                    entries.append(entry)
        elif in_table and not line.startswith('|'):
            in_table = False
            headers = []
    
    # If we found entries from tables, return those
    if entries:
        return entries
    
    # Otherwise, try to parse as sequential entries
    # Look for patterns like "1. Tên thiết bị: ..." or numbered entries
    entry_pattern = re.compile(r'(\d+)[\.\:\)]\s*(.+)')
    for line in lines:
        match = entry_pattern.match(line)
        if match:
            if current_entry:
                entries.append(current_entry)
            current_entry = {'raw_line': match.group(2)}
        elif current_entry:
            # Try to parse key-value from this line
            kv_match = re.match(r'^([^:：]+)[:：]\s*(.+)$', line)
            if kv_match:
                key = kv_match.group(1).strip().lower()
                value = kv_match.group(2).strip()
                if any(k in key for k in ['tên', 'đối tượng', 'object', 'thiết bị']):
                    current_entry['object_name'] = value
                elif any(k in key for k in ['serial', 'số serial', 'số hiệu', 'number', 'mã']):
                    current_entry['serial_number'] = value
                elif any(k in key for k in ['nơi', 'place', 'bộ phận', 'phòng', 'khoa', 'department', 'địa điểm']):
                    current_entry['place'] = value
                elif any(k in key for k in ['ngày hiệu chuẩn', 'date of calibration', 'ngày kiểm định']):
                    current_entry['calibration_date'] = value
                elif any(k in key for k in ['ngày hiệu chuẩn lại', 'recalibration', 'hạn sử dụng', 'next calibration', 'ngày kiểm định lại']):
                    current_entry['recalibration_date'] = value
                elif any(k in key for k in ['ghi chú', 'note', 'notes', 'kết quả', 'result']):
                    current_entry['notes'] = value
    
    if current_entry:
        entries.append(current_entry)
    
    # If still no structured entries, return raw text chunks as fallback
    if not entries:
        # Split by double newlines or page breaks
        chunks = re.split(r'\n\s*\n', markdown_text)
        for i, chunk in enumerate(chunks):
            chunk = chunk.strip()
            if len(chunk) > 50:  # Only substantial chunks
                entries.append({
                    'chunk_index': i,
                    'raw_text': chunk[:500]
                })
    
    return entries

def process_pdf(pdf_info):
    print(f"Processing: {pdf_info['name']}...")
    base64_pdf = encode_pdf_to_base64(pdf_info['path'])
    print(f"  Encoded ({len(base64_pdf)} chars), calling API...")
    
    response = call_mistral_ocr(base64_pdf)
    markdown = extract_markdown_from_response(response)
    
    # Save full markdown
    md_path = os.path.join(OUTPUT_DIR, f"mistral_ocr_{pdf_info['name']}.md")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(markdown)
    print(f"  Saved markdown to {md_path}")
    
    # Extract entries
    entries = extract_device_entries(markdown)
    
    # Save summary
    summary = {
        "pdf_name": pdf_info['name'],
        "pdf_path": pdf_info['path'],
        "page_count": len(response.get("pages", [])),
        "entries_count": len(entries),
        "entries": entries
    }
    
    summary_path = os.path.join(OUTPUT_DIR, f"mistral_ocr_{pdf_info['name']}_summary.json")
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"  Saved summary to {summary_path} ({len(entries)} entries)")
    
    return summary

def main():
    all_summaries = []
    for pdf_info in PDF_FILES:
        try:
            summary = process_pdf(pdf_info)
            all_summaries.append(summary)
            time.sleep(1)  # Rate limiting
        except Exception as e:
            print(f"Error processing {pdf_info['name']}: {e}")
            all_summaries.append({
                "pdf_name": pdf_info['name'],
                "error": str(e)
            })
    
    # Output all summaries as JSON to stdout
    print("\n=== FINAL SUMMARIES ===")
    print(json.dumps(all_summaries, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()