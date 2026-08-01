#!/usr/bin/env python3
"""
Nanobot Self-Improvement Loop (SIA-inspired)

Feedback agent cho chính Nanobot:
1. Ghi nhận lỗi (tool failure, wrong output, user correction)
2. Phân tích nguyên nhân gốc rễ
3. Đề xuất cải tiến (update prompt, thêm validation, sửa tool pattern)
4. Áp dụng cải tiến
5. Theo dõi hiệu quả (cùng loại lỗi còn lặp lại?)

Usage:
  python nanobot_self_improve.py log --error "..." --context "..." --fix_attempt "..."
  python nanobot_self_improve.py reflect --error_id <id>
  python nanobot_self_improve.py apply --error_id <id> --improvement "..."
  python nanobot_self_improve.py report
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

BASE_DIR = Path("/home/tan/.nanobot/workspace")
ERROR_LOG = BASE_DIR / "memory" / "nanobot_errors.jsonl"
IMPROVEMENT_LOG = BASE_DIR / "memory" / "nanobot_improvements.jsonl"
SKILLS_DIR = BASE_DIR / "skills"
AGENTS_FILE = BASE_DIR / "AGENTS.md"

# Các pattern lỗi thường gặp và cải tiến tự động
ERROR_PATTERNS = [
    {
        "pattern": r"missing.*field|missing.*yaml|frontmatter",
        "category": "validation",
        "auto_fix": "Thêm bước kiểm tra YAML frontmatter trước khi tạo file",
        "improvement": "Sử dụng verify_entity.py để kiểm tra sau khi tạo entity"
    },
    {
        "pattern": r"serial.*duplicate|trùng.*serial",
        "category": "data_integrity",
        "auto_fix": "Thêm bước kiểm tra serial uniqueness trước khi ghi",
        "improvement": "Chạy verify_entity.py trước khi commit entity mới"
    },
    {
        "pattern": r"timeout|timed out|exceeded.*timeout",
        "category": "tool_execution",
        "auto_fix": "Tăng timeout hoặc chia nhỏ task",
        "improvement": "Sử dụng subagent cho task > 3 tool calls"
    },
    {
        "pattern": r"file not found|FileNotFound|No such file",
        "category": "path_resolution",
        "auto_fix": "Luôn dùng find_files trước khi read_file",
        "improvement": "Thêm bước find_files trước read_file/edit_file"
    },
    {
        "pattern": r"apply_patch.*fail|edit_file.*fail|old_text.*not found",
        "category": "file_editing",
        "auto_fix": "Đọc lại file với force=True trước khi edit",
        "improvement": "Luôn read_file trước khi apply_patch/edit_file"
    },
    {
        "pattern": r"SSRF|blocked.*url|internal.*url",
        "category": "security",
        "auto_fix": "Dùng web_fetch thay vì curl cho URLs",
        "improvement": "Không bao giờ dùng curl cho internal URLs"
    },
    {
        "pattern": r"API.*key|token.*exposed|secret.*leaked",
        "category": "security",
        "auto_fix": "Xóa key khỏi output, dùng .env",
        "improvement": "Thêm bước kiểm tra secrets trước khi output"
    },
    {
        "pattern": r"wiki.*orphan|missing.*index|broken.*link",
        "category": "knowledge_base",
        "auto_fix": "Cập nhật index.md và log.md sau khi tạo entity",
        "improvement": "Thêm bước cập nhật index.md + log.md vào workflow tạo entity"
    },
    {
        "pattern": "prompt.*too long|context.*window|exceed.*limit",
        "category": "context_management",
        "auto_fix": "Tóm tắt context, dùng head_limit",
        "improvement": "Sử dụng grep head_limit thay vì dump full file"
    }
]


def log_error(error: str, context: str = "", fix_attempt: str = "", source: str = "manual") -> str:
    """Ghi nhận lỗi mới vào log."""
    error_id = f"err_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(error) % 10000}"
    
    entry = {
        "error_id": error_id,
        "timestamp": datetime.now().isoformat(),
        "error": error,
        "context": context,
        "fix_attempt": fix_attempt,
        "source": source,
        "status": "logged",
        "category": None,
        "auto_fix_suggested": None,
        "applied": False,
        "resolved": False
    }
    
    # Phân loại lỗi tự động
    for pattern_info in ERROR_PATTERNS:
        if re.search(pattern_info["pattern"], error, re.IGNORECASE):
            entry["category"] = pattern_info["category"]
            entry["auto_fix_suggested"] = pattern_info["auto_fix"]
            entry["improvement_suggested"] = pattern_info["improvement"]
            break
    
    ERROR_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(ERROR_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    print(f"✅ Đã ghi nhận lỗi: {error_id}")
    print(f"   Phân loại: {entry['category'] or 'chưa phân loại'}")
    if entry.get("auto_fix_suggested"):
        print(f"   Đề xuất sửa: {entry['auto_fix_suggested']}")
    
    return error_id


def get_error(error_id: str) -> Optional[dict]:
    """Tìm lỗi theo ID."""
    if not ERROR_LOG.exists():
        return None
    
    with open(ERROR_LOG, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            if entry["error_id"] == error_id:
                return entry
    return None


def reflect_error(error_id: str) -> dict:
    """Phân tích lỗi và đề xuất cải tiến chi tiết."""
    error_entry = get_error(error_id)
    if not error_entry:
        print(f"Không tìm thấy lỗi: {error_id}")
        return {}
    
    print(f"\n=== PHÂN TÍCH LỖI: {error_id} ===\n")
    print(f"Lỗi: {error_entry['error']}")
    print(f"Bối cảnh: {error_entry['context']}")
    print(f"Fix attempt: {error_entry['fix_attempt']}")
    
    analysis = {
        "error_id": error_id,
        "root_cause": None,
        "improvement_plan": [],
        "preventive_measures": [],
        "related_errors": []
    }
    
    # Tìm lỗi tương tự
    if ERROR_LOG.exists():
        with open(ERROR_LOG, "r", encoding="utf-8") as f:
            for line in f:
                entry = json.loads(line)
                if entry["error_id"] != error_id and entry.get("category") == error_entry.get("category"):
                    analysis["related_errors"].append(entry["error_id"])
    
    # Phân tích nguyên nhân gốc rễ
    error_text = error_entry["error"].lower()
    context_text = error_entry["context"].lower()
    
    if "missing" in error_text or "field" in error_text:
        analysis["root_cause"] = "Thiếu bước validation trước khi thực hiện"
        analysis["improvement_plan"] = [
            "Thêm pre-check validation trước khi tạo/sửa file",
            "Sử dụng verify_entity.py hoặc script tương tự",
            "Kiểm tra required fields trong YAML frontmatter"
        ]
        analysis["preventive_measures"] = [
            "Luôn chạy validation script sau mỗi lần tạo entity",
            "Thêm checklist validation vào workflow"
        ]
    elif "timeout" in error_text or "exceed" in error_text:
        analysis["root_cause"] = "Task quá phức tạp cho single tool call"
        analysis["improvement_plan"] = [
            "Chia nhỏ task thành các bước nhỏ hơn",
            "Sử dụng subagent cho task > 3 tool calls",
            "Tăng timeout nếu cần thiết"
        ]
        analysis["preventive_measures"] = [
            "Đánh giá độ phức tạp task trước khi thực hiện",
            "Sử dụng subagent cho task nặng"
        ]
    elif "file not found" in error_text or "nosuch" in error_text:
        analysis["root_cause"] = "Path resolution sai hoặc file chưa tồn tại"
        analysis["improvement_plan"] = [
            "Luôn dùng find_files trước khi read_file",
            "Kiểm tra file tồn tại trước khi edit",
            "Sử dụng force=True khi read_file để bypass cache"
        ]
        analysis["preventive_measures"] = [
            "Thêm bước find_files vào workflow",
            "Verify file path trước khi thao tác"
        ]
    elif "duplicate" in error_text or "trùng" in error_text:
        analysis["root_cause"] = "Thiếu bước kiểm tra uniqueness"
        analysis["improvement_plan"] = [
            "Thêm bước kiểm tra serial uniqueness",
            "Sử dụng verify_entity.py trước khi commit",
            "Tạo registry cho serial numbers"
        ]
        analysis["preventive_measures"] = [
            "Kiểm tra duplicate trước khi tạo entity mới",
            "Duy trì serial registry"
        ]
    else:
        analysis["root_cause"] = "Chưa phân tích được nguyên nhân cụ thể"
        analysis["improvement_plan"] = [
            "Ghi nhận thêm context chi tiết",
            "Thử fix khác và ghi nhận kết quả"
        ]
    
    # Thêm đề xuất từ pattern matching
    if error_entry.get("auto_fix_suggested"):
        analysis["improvement_plan"].append(error_entry["auto_fix_suggested"])
    
    print(f"\nNguyên nhân gốc rễ: {analysis['root_cause']}")
    print(f"\nKế hoạch cải tiến:")
    for i, plan in enumerate(analysis["improvement_plan"], 1):
        print(f"  {i}. {plan}")
    print(f"\nBiện pháp phòng ngừa:")
    for measure in analysis["preventive_measures"]:
        print(f"  - {measure}")
    
    if analysis["related_errors"]:
        print(f"\nLỗi tương tự: {', '.join(analysis['related_errors'])}")
    
    return analysis


def apply_improvement(error_id: str, improvement: str) -> bool:
    """Áp dụng cải tiến cho lỗi cụ thể."""
    error_entry = get_error(error_id)
    if not error_entry:
        print(f"Không tìm thấy lỗi: {error_id}")
        return False
    
    improvement_entry = {
        "error_id": error_id,
        "timestamp": datetime.now().isoformat(),
        "improvement": improvement,
        "status": "applied",
        "verified": False
    }
    
    IMPROVEMENT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(IMPROVEMENT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(improvement_entry, ensure_ascii=False) + "\n")
    
    # Cập nhật trạng thái lỗi
    _update_error_status(error_id, applied=True)
    
    print(f"✅ Đã áp dụng cải tiến cho {error_id}")
    print(f"   Cải tiến: {improvement}")
    
    return True


def _update_error_status(error_id: str, **kwargs):
    """Cập nhật trạng thái lỗi."""
    if not ERROR_LOG.exists():
        return
    
    entries = []
    with open(ERROR_LOG, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            if entry["error_id"] == error_id:
                entry.update(kwargs)
            entries.append(entry)
    
    with open(ERROR_LOG, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def generate_report() -> str:
    """Tạo báo cáo tổng quan về lỗi và cải tiến."""
    if not ERROR_LOG.exists():
        return "Chưa có lỗi nào được ghi nhận."
    
    total_errors = 0
    resolved_errors = 0
    category_counts = {}
    
    with open(ERROR_LOG, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            total_errors += 1
            if entry.get("resolved"):
                resolved_errors += 1
            cat = entry.get("category") or "chưa phân loại"
            category_counts[cat] = category_counts.get(cat, 0) + 1
    
    total_improvements = 0
    if IMPROVEMENT_LOG.exists():
        with open(IMPROVEMENT_LOG, "r", encoding="utf-8") as f:
            total_improvements = sum(1 for _ in f)
    
    report = f"""
=== BÁO CÁO TỰ CẢI TIẾN NANOBOT ===
Tổng lỗi: {total_errors}
Đã giải quyết: {resolved_errors}
    Tỷ lệ giải quyết: {(f'{resolved_errors/total_errors*100:.1f}' if total_errors else '0')}%
Tổng cải tiến: {total_improvements}

Phân loại lỗi:
"""
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        report += f"  - {cat}: {count}\n"
    
    report += "\nLỗi chưa giải quyết:\n"
    with open(ERROR_LOG, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            if not entry.get("resolved"):
                report += f"  - {entry['error_id']}: {entry['error'][:80]}...\n"
    
    return report


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "log":
        if len(sys.argv) < 3:
            print("Usage: python nanobot_self_improve.py log --error \"...\" --context \"...\"")
            sys.exit(1)
        
        error = sys.argv[2] if sys.argv[2] != "--error" else sys.argv[3]
        context = ""
        fix_attempt = ""
        source = "manual"
        
        for i, arg in enumerate(sys.argv):
            if arg == "--context" and i + 1 < len(sys.argv):
                context = sys.argv[i + 1]
            elif arg == "--fix" and i + 1 < len(sys.argv):
                fix_attempt = sys.argv[i + 1]
            elif arg == "--source" and i + 1 < len(sys.argv):
                source = sys.argv[i + 1]
        
        error_id = log_error(error, context, fix_attempt, source)
        print(f"\nID lỗi: {error_id}")
        print(f"Chạy: python nanobot_self_improve.py reflect --error_id {error_id}")
    
    elif command == "reflect":
        if len(sys.argv) < 4 or sys.argv[2] != "--error_id":
            print("Usage: python nanobot_self_improve.py reflect --error_id <id>")
            sys.exit(1)
        
        error_id = sys.argv[3]
        reflect_error(error_id)
    
    elif command == "apply":
        if len(sys.argv) < 5 or sys.argv[2] != "--error_id":
            print("Usage: python nanobot_self_improve.py apply --error_id <id> --improvement \"...\"")
            sys.exit(1)
        
        error_id = sys.argv[3]
        improvement = sys.argv[4] if sys.argv[4] != "--improvement" else sys.argv[5]
        apply_improvement(error_id, improvement)
    
    elif command == "report":
        print(generate_report())
    
    elif command == "auto":
        """Tự động: log + reflect + suggest fix"""
        if len(sys.argv) < 3:
            print("Usage: python nanobot_self_improve.py auto \"error message\"")
            sys.exit(1)
        
        error_msg = " ".join(sys.argv[2:])
        error_id = log_error(error_msg, source="auto")
        reflect_error(error_id)
        print(f"\nĐể áp dụng cải tiến: python nanobot_self_improve.py apply --error_id {error_id} --improvement \"...\"")
    
    else:
        print(f"Lệnh không xác định: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()