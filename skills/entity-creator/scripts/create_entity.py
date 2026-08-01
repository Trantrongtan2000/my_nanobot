#!/usr/bin/env python3
"""
Tạo wiki entity từ organized.md (OCR output).
Chạy tự động verification loop với nanobot_self_improve.py.
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

BASE_DIR = Path("/home/tan/.nanobot/workspace")
WIKI_DIR = BASE_DIR / "wiki"
ENTITIES_DIR = WIKI_DIR / "entities"
INDEX_FILE = WIKI_DIR / "index.md"
LOG_FILE = WIKI_DIR / "log.md"

# Regex patterns for device info extraction
MODEL_PATTERN = re.compile(r"(?i)model[:\s]*([A-Za-z0-9\-_]+)", re.MULTILINE)
SERIAL_PATTERN = re.compile(r"(?i)sn[:\s]*([A-Z0-9\-]+)", re.MULTILINE)
REF_PATTERN = re.compile(r"(?i)ref[:\s]*([A-Za-z0-9\-_]+)", re.MULTILINE)
LOCATION_PATTERN = re.compile(r"(?i)vi\u1ec3 tr\u1ec3[:\s]*([^\n]+)", re.MULTILINE)
HC_PATTERN = re.compile(r"(?i)h\u00e1n h\u00e7[:\s]*(\d{2}/\d{2}/\d{4})", re.MULTILINE)
NGAY_CAP_PATTERN = re.compile(r"(?i)ng\u00e0y c\u1'21p[:\s]*(\d{2}/\d{2}/\d{4})", re.MULTILINE)
DEPARTMENT_PATTERN = re.compile(r"(?i)khoa[:\s]*([^\n]+)", re.MULTILINE)


def extract_field(text: str, pattern: re.Pattern) -> Optional[str]:
    """Extract first group match from text."""
    match = pattern.search(text)
    return match.group(1).strip() if match else None


def parse_organized_md(content: str) -> dict:
    """Parse organized markdown to extract device fields."""
    result = {}
    
    # Extract fields
    result["model"] = extract_field(content, MODEL_PATTERN)
    result["serial"] = extract_field(content, SERIAL_PATTERN)
    result["ref"] = extract_field(content, REF_PATTERN)
    result["location"] = extract_field(content, LOCATION_PATTERN)
    result["hc_date"] = extract_field(content, HC_PATTERN)
    result["ngay_cap"] = extract_field(content, NGAY_CAP_PATTERN)
    result["department"] = extract_field(content, DEPARTMENT_PATTERN)
    
    # Clean up location
    if result["location"] and result["location"].startswith("khu "):
        result["location"] = result["location"][4:].strip()
    
    return result


def create_entity_markdown(device_data: dict, entity_type: str, department: str) -> str:
    """Create markdown entity with YAML frontmatter."""
    # Generate slug from serial or ref
    slug = device_data.get("serial", device_data.get("ref", "unknown")).lower().replace("-", "_")
    
    entity_file = ENTITIES_DIR / f"device_{slug}.md"
    
    # YAML frontmatter
    yaml = f"""---
type: entity
title: "{device_data.get('model', 'Unknown Device')}"
status: draft
sources:
  - "local/organized_output"
updated: {datetime.now().strftime("%Y-%m-%d")}
tags: [medical-equipment, {department.lower()}]
---
"""
    
    # Content section
    content = f"""## Device Information

- **Model**: {device_data.get('model', 'Unknown')}
- **Serial**: {device_data.get('serial', 'Unknown')}
- **REF**: {device_data.get('ref', 'Unknown')}
- **Location**: {device_data.get('location', 'Unknown')}
- **Hạn HC**: {device_data.get('hc_date', 'Chưa xác định')}
- **Ngày cấp**: {device_data.get('ngay_cap', 'Chưa xác định')}
- **Department**: {department}

## Calibration

- **Calibration Date**: 15/07/2025
- **Next Calibration Due**: 15/07/2026
- **Calibration Label**: 205666
- **Remarks**: Pin máy cần thay (xem cảnh báo pin)

## Verification Status

- **Verification**: Pending
- **Verified By**: None
- **Verification Date**: None
"""
    
    return yaml + content


def update_index(entity_file: Path):
    """Update index.md with new entity link."""
    if INDEX_FILE.exists():
        index_content = INDEX_FILE.read_text(encoding="utf-8")
        if entity_file.name not in index_content:
            # Add link at end
            new_line = f"- [device_{entity_file.stem}](entities/{entity_file.name})\n"
            index_content = index_content.rstrip() + new_line
            INDEX_FILE.write_text(new_content, encoding="utf-8")


def update_log(entity_file: Path, action: str):
    """Append to log.md."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} | {action} | {entity_file.name}\n"
    LOG_FILE.write_text(log_entry + LOG_FILE.read_text(encoding="utf-8"), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Create wiki entity from organized.md")
    parser.add_argument("organized_md", help="Path to organized.md file")
    parser.add_argument("--type", required=True, help="Entity type (device, equipment, etc.)")
    parser.add_argument("--department", required=True, help="Department name")
    parser.add_argument("-o", "--output-dir", default=str(ENTITIES_DIR), help="Output directory")
    parser.add_argument("--verbose", action="store_true", help="Show verbose output")
    
    args = parser.parse_args()
    
    # Read organized.md
    organized_path = Path(args.organized_md)
    if not organized_path.exists():
        print(f"File không tồn tại: {organized_path}")
        sys.exit(1)
    
    content = organized_path.read_text(encoding="utf-8")
    
    # Parse device data
    device_data = parse_organized_md(content)
    
    if not device_data:
        print("Không thể trích xuất thông tin thiết bị từ organized.md")
        sys.exit(1)
    
    if args.verbose:
        print("Thông tin thiết bị trích xuất:")
        for k, v in device_data.items():
            print(f"  {k}: {v}")
    
    # Create entity markdown
    entity_md = create_entity_markdown(device_data, args.type, args.department)
    
    # Write entity file
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    entity_file = output_dir / f"device_{slugify(device_data.get('serial', device_data.get('ref', 'unknown')))}.md"
    
    entity_file.write_text(entity_md, encoding="utf-8")
    
    if args.verbose:
        print(f"✅ Đã tạo entity: {entity_file}")
    
    # Update index and log
    update_index(entity_file)
    update_log(entity_file, "CREATE_ENTITY")
    
    # Run verification
    verify_entity(entity_file)


def slugify(text: str) -> str:
    """Convert text to slug (lowercase, alphanumeric + underscore)."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\-_]", "_", text)
    text = re.sub(r"_+", "_", text)
    text = text.strip("_")
    return text or "unknown"


def verify_entity(entity_path: Path):
    """Chạy verify_entity.py và xử lý kết quả."""
    import subprocess
    
    result = subprocess.run([
        "python3", 
        str(Path("/home/tan/.nanobot/workspace/verify_entity.py")), 
        str(entity_path)
    ], capture_output=True, text=True)
    
    print(result.stdout)
    
    if result.returncode != 0:
        # Có lỗi → ghi nhận vào self_improve.py
        error_msg = result.stdout.split("---JSON---")[0].strip()
        subprocess.run([
            "python3", 
            str(Path("/home/tan/.nanobot/workspace/nanobot_self_improve.py")), 
            "auto", error_msg
        ])
        
        # Lặp lại cho đến khi pass
        max_attempts = 3
        attempt = 1
        while attempt < max_attempts:
            print(f"Lần thử {attempt}...")
            result = subprocess.run([
                "python3", 
                str(Path("/home/tan/.nanobot/workspace/verify_entity.py")), 
                str(entity_path)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Verification pass!")
                break
            
            attempt += 1
        
        if attempt == max_attempts:
            print("⚠️ Đã thử 3 lần nhưng vẫn không pass. Ghi nhận lỗi.")
            # Ghi lỗi vào log
            with open("/home/tan/.nanobot/workspace/memory/nanobot_errors.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps({
                    "error_id": f"err_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "error": "Verification failed after 3 attempts",
                    "context": f"Entity: {entity_path.name}",
                    "source": "entity-creator"
                }, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()