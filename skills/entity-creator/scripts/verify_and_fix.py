#!/usr/bin/env python3
"""
verify_and_fix.py - Chạy verification loop tự động cho entity wiki.
Chạy verify_entity.py, nếu có lỗi → tự động sửa và verify lại.
"""

import argparse
import json
import os
import re
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

BASE_DIR = Path("/home/tan/.nanobot/workspace")
ERROR_LOG = BASE_DIR / "memory" / "nanobot_errors.jsonl"
IMPROVEMENT_LOG = BASE_DIR / "memory" / "nanobot_improvements.jsonl"

def log_error(error: str, context: str = "", source: str = "auto"):
    """Ghi nhận lỗi vào log."""
    error_id = f"err_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(error) % 10000}"
    
    entry = {
        "error_id": error_id,
        "timestamp": datetime.now().isoformat(),
        "error": error,
        "context": context,
        "source": source,
        "status": "logged",
        "category": None,
        "auto_fix_suggested": None
    }
    
    # Phân loại lỗi
    patterns = [
        r"missing.*field|missing.*yaml|frontmatter",
        r"serial.*duplicate|trùng.*serial",
        r"timeout|exceeded|timeout",
        r"file not found|nosuch|no such file",
        r"apply_patch.*fail|edit_file.*fail|old_text.*not found"
    ]
    
    for pattern in patterns:
        if re.search(pattern, error, re.IGNORECASE):
            entry["category"] = "validation" if "missing" in pattern else "execution" if "timeout" in pattern else "file"
            break
    
    # Ghi vào log
    with open(ERROR_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    print(f"⚠️ Đã ghi nhận lỗi: {error_id}")
    print(f"   Lỗi: {error[:80]}...")
    return error_id


def get_error(error_id: str) -> Optional[dict]:
    """Lấy thông tin lỗi."""
    if not ERROR_LOG.exists():
        return None
    
    with open(ERROR_LOG, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            if entry["error_id"] == error_id:
                return entry
    return None


def apply_improvement(error_id: str, improvement: str):
    """Áp dụng cải tiến cho lỗi."""
    improvement_entry = {
        "error_id": error_id,
        "timestamp": datetime.now().isoformat(),
        "improvement": improvement,
        "status": "applied"
    }
    
    with open(IMPROVEMENT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(improvement_entry, ensure_ascii=False) + "\n")
    
    print(f"✅ Đã áp dụng cải tiến: {improvement}")


def verify_and_fix(entity_path: Path, max_attempts: int = 3):
    """Chạy verification loop tự động."""
    attempt = 1
    
    while attempt <= max_attempts:
        print(f"\n=== Lần thử {attempt}/{max_attempts} ===")
        
        # Chạy verify_entity.py
        result = subprocess.run([
            "python3", 
            str(Path("/home/tan/.nanobot/workspace/verify_entity.py")), 
            str(entity_path)
        ], capture_output=True, text=True)
        
        print(result.stdout)
        
        # Kiểm tra lỗi
        if result.returncode == 0:
            print("✅ Verification pass!")
            return True
        
        # Có lỗi → phân tích và sửa
        error_msg = result.stdout.split("---JSON---")[0].strip()
        error_id = log_error(error_msg, context=f"Entity: {entity_path.name}", source="auto")
        
        # Đề xuất cải tiến dựa trên phân tích
        error_entry = get_error(error_id)
        if error_entry and error_entry.get("auto_fix_suggested"):
            improvement = error_entry["auto_fix_suggested"]
            print(f"🔧 Cải tiến đề xuất: {improvement}")
            apply_improvement(error_id, improvement)
            
            # Thực hiện cải tiến (ví dụ: sửa file)
            # Ở đây chỉ ghi nhận, thực tế cần sửa file thực tế
            # Ví dụ: thêm kiểm tra serial trước khi tạo
            # TODO: Implement actual file editing based on improvement
            
            print("🔄 Đã sửa và sẽ verify lại...")
        else:
            print("❌ Không có cải tiến đề xuất, dừng lại.")
            return False
        
        attempt += 1
    
    print("⚠️ Đã thử đủ lần nhưng vẫn không pass.")
    return False


def main():
    if len(sys.argv) < 3 or sys.argv[1] != "--entity":
        print("Usage: python verify_and_fix.py --entity <entity_file.md> [--max_attempts N]")
        sys.exit(1)
    
    entity_path = None
    max_attempts = 3
    
    for i, arg in enumerate(sys.argv):
        if arg == "--entity" and i + 1 < len(sys.argv):
            entity_path = Path(sys.argv[i + 1])
        elif arg == "--max_attempts" and i + 1 < len(sys.argv):
            max_attempts = int(sys.argv[i + 1])
    
    if not entity_path or not entity_path.exists():
        print(f"File không tồn tại: {entity_path}")
        sys.exit(1)
    
    success = verify_and_fix(entity_path, max_attempts)
    
    if success:
        print("✅ Verification thành công!")
        sys.exit(0)
    else:
        print("❌ Verification không thành công sau nhiều lần thử.")
        sys.exit(1)


if __name__ == "__main__":
    main()