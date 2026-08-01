#!/usr/bin/env python3
"""Agent quản lý wiki thiết bị y tế - tối giản, Ponytail style"""

import argparse
import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/tan/.nanobot/workspace")
SKILL_DIR = Path(__file__).parent

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def log_history(action, details):
    """Ghi log vào memory/history.jsonl"""
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,
        "details": details
    }
    history_path = WORKSPACE / "memory" / "history.jsonl"
    with open(history_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    logger.info(f"Đã ghi log: {action}")

def process_organized(organized_path):
    """Xử lý file organized.md → tạo entity"""
    organized_path = Path(organized_path)
    if not organized_path.exists():
        logger.error(f"File organized.md không tồn tại: {organized_path}")
        return False

    # Gọi entity-creator script
    entity_creator = WORKSPACE / "skills" / "entity-creator" / "scripts" / "create_entity.py"
    if not entity_creator.exists():
        entity_creator = WORKSPACE / "scripts" / "create_entity.py"
    if entity_creator.exists():
        result = subprocess.run(
            [sys.executable, str(entity_creator), str(organized_path),
             "--type", "device", "--department", "Chưa xác định"],
            capture_output=True,
            text=True,
            cwd=str(WORKSPACE)
        )
        if result.returncode == 0:
            log_history("process_organized", f"Đã xử lý {organized_path.name}")
            return True
        else:
            logger.error(f"Lỗi entity-creator: {result.stderr}")
            return False
    else:
        logger.error(f"Script entity-creator không tồn tại: {script_path}")
        return False

def verify_wiki():
    """Kiểm tra toàn bộ wiki"""
    verify_script = WORKSPACE / "verify_entity.py"
    if verify_script.exists():
        result = subprocess.run(
            [sys.executable, str(verify_script), "wiki/entities"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            log_history("verify_wiki", "Đã kiểm tra wiki")
            return True
        else:
            logger.error(f"Lỗi verify_entity: {result.stderr}")
            return False
    else:
        logger.error(f"Script verify_entity không tồn tại: {verify_script}")
        return False

def sync_notion():
    """Đồng bộ với Notion (nếu có)"""
    # TODO: Thêm Notion MCP integration
    logger.info("Đồng bộ Notion chưa được triển khai")
    log_history("sync_notion", "Đã bỏ qua - chưa triển khai")
    return True

def status():
    """Kiểm tra trạng thái wiki"""
    index_path = WORKSPACE / "wiki" / "index.md"
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        logger.info(f"Wiki index có {len(lines)} dòng")
        return True
    else:
        logger.error("Wiki index không tồn tại")
        return False

def main():
    parser = argparse.ArgumentParser(description="Agent quản lý wiki thiết bị y tế")
    parser.add_argument("--action", required=True, choices=["process", "verify", "sync-notion", "status"], help="Hành động cần thực hiện")
    parser.add_argument("--organized", help="Đường dẫn đến file organized.md")

    args = parser.parse_args()

    try:
        if args.action == "process":
            if not args.organized:
                logger.error("Thiếu --organized path")
                return 1
            success = process_organized(args.organized)
        elif args.action == "verify":
            success = verify_wiki()
        elif args.action == "sync-notion":
            success = sync_notion()
        elif args.action == "status":
            success = status()
        else:
            logger.error(f"Hành động không được hỗ trợ: {args.action}")
            return 1

        if success:
            logger.info(f"Đã hoàn thành hành động: {args.action}")
            return 0
        else:
            logger.error(f"Thất bại khi thực hiện hành động: {args.action}")
            return 1
    except Exception as e:
        logger.error(f"Lỗi không mong đợi: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())