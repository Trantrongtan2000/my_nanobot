#!/usr/bin/env python3
"""
Feedback agent cho wiki entity verification.
Chạy sau mỗi lần tạo entity mới để kiểm tra độc lập và đề xuất cải tiến.
"""

import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

WIKI_DIR = Path("/home/tan/.nanobot/workspace/wiki")
ENTITIES_DIR = WIKI_DIR / "entities"
INDEX_FILE = WIKI_DIR / "index.md"
LOG_FILE = WIKI_DIR / "log.md"

REQUIRED_FIELDS = ["type:", "title:", "status:", "sources:", "updated:", "tags:"]
SERIAL_PATTERN = re.compile(r"S/N[:\s]*([A-Z0-9\-]+)", re.IGNORECASE)
HC_PATTERN = re.compile(r"Hạn HC[:\s]*(\d{2}/\d{2}/\d{4})", re.IGNORECASE)
NGAY_CAP_PATTERN = re.compile(r"Ngày cấp[:\s]*(\d{2}/\d{2}/\d{4})", re.IGNORECASE)


def parse_yaml_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from markdown file."""
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}
    
    yaml_content = match.group(1)
    result = {}
    for line in yaml_content.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def check_required_fields(yaml_data: dict) -> list[str]:
    """Check if all required fields are present."""
    missing = []
    for field in REQUIRED_FIELDS:
        if field not in yaml_data:
            missing.append(field.rstrip(":"))
    return missing


def check_serial_uniqueness(serial: str, current_file: str) -> Optional[str]:
    """Check if serial number already exists in other entities."""
    if not serial:
        return None
    
    for entity_file in ENTITIES_DIR.glob("*.md"):
        if entity_file.name == current_file:
            continue
        
        content = entity_file.read_text(encoding="utf-8")
        match = SERIAL_PATTERN.search(content)
        if match and match.group(1) == serial:
            return entity_file.name
    return None


def check_hc_expiry(hc_date_str: str) -> Optional[str]:
    """Check if HC expiry is within 30 days."""
    if not hc_date_str:
        return None
    
    try:
        hc_date = datetime.strptime(hc_date_str, "%d/%m/%Y")
        days_left = (hc_date - datetime.now()).days
        if days_left < 0:
            return f"Hạn HC đã qua hạn {abs(days_left)} ngày"
        elif days_left < 30:
            return f"⚠️ CẢNH BÁO: Hạn HC trong vòng {days_left} ngày"
    except ValueError:
        return None
    return None


def verify_entity(entity_path: Path) -> dict:
    """Verify a single entity file."""
    result = {
        "file": entity_path.name,
        "valid": True,
        "errors": [],
        "warnings": [],
        "suggestions": []
    }
    
    content = entity_path.read_text(encoding="utf-8")
    yaml_data = parse_yaml_frontmatter(content)
    
    # Check required fields
    missing = check_required_fields(yaml_data)
    if missing:
        result["errors"].append(f"Thiếu field: {', '.join(missing)}")
        result["valid"] = False
    
    # Check serial uniqueness
    serial_match = SERIAL_PATTERN.search(content)
    if serial_match:
        duplicate = check_serial_uniqueness(serial_match.group(1), entity_path.name)
        if duplicate:
            result["warnings"].append(f"Serial {serial_match.group(1)} trùng với {duplicate}")
    
    # Check HC expiry
    hc_match = HC_PATTERN.search(content)
    if hc_match:
        hc_status = check_hc_expiry(hc_match.group(1))
        if hc_status:
            result["warnings"].append(hc_status)
    
    # Check if in index
    if INDEX_FILE.exists():
        index_content = INDEX_FILE.read_text(encoding="utf-8")
        if entity_path.name not in index_content:
            result["suggestions"].append("Thêm vào index.md")
    
    return result


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python verify_entity.py <entity_file.md>")
        sys.exit(1)
    
    entity_path = Path(sys.argv[1])
    if not entity_path.exists():
        print(f"File không tồn tại: {entity_path}")
        sys.exit(1)
    
    result = verify_entity(entity_path)
    
    print(f"\n=== KẾT QUẢ KIỂM TRA: {result['file']} ===\n")
    
    if result["valid"]:
        print("✅ Entity hợp lệ")
    else:
        print("❌ Entity có lỗi")
    
    if result["errors"]:
        print("\nLỗi:")
        for err in result["errors"]:
            print(f"  - {err}")
    
    if result["warnings"]:
        print("\nCảnh báo:")
        for warn in result["warnings"]:
            print(f"  - {warn}")
    
    if result["suggestions"]:
        print("\nGợi ý cải tiến:")
        for sug in result["suggestions"]:
            print(f"  - {sug}")
    
    # Output JSON for subagent processing
    print("\n---JSON---")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()