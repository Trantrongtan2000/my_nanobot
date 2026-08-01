#!/usr/bin/env python3
"""Check calibration expiry. Warn if < 30 days."""

import argparse
import sqlite3
from datetime import datetime, timedelta

DB_PATH = "/home/tan/.nanobot/workspace/data/qltb_assets.db"

def check_calibration(days_warning=30):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    today = datetime.now().date()
    warning_date = today + timedelta(days=days_warning)
    
    # Overdue
    cursor.execute('''
        SELECT asset_tag, serial_number, model, department, calibration_expiry
        FROM assets 
        WHERE calibration_expiry IS NOT NULL 
          AND date(calibration_expiry) < date(?)
          AND status != 'retired'
        ORDER BY calibration_expiry
    ''', (today.isoformat(),))
    overdue = cursor.fetchall()
    
    # Warning (< 30 days)
    cursor.execute('''
        SELECT asset_tag, serial_number, model, department, calibration_expiry
        FROM assets 
        WHERE calibration_expiry IS NOT NULL 
          AND date(calibration_expiry) >= date(?)
          AND date(calibration_expiry) <= date(?)
          AND status != 'retired'
        ORDER BY calibration_expiry
    ''', (today.isoformat(), warning_date.isoformat(),))
    warning = cursor.fetchall()
    
    # No calibration date
    cursor.execute('''
        SELECT asset_tag, serial_number, model, department
        FROM assets 
        WHERE calibration_expiry IS NULL 
          AND status != 'retired'
    ''')
    no_date = cursor.fetchall()
    
    conn.close()
    
    # Report
    if overdue:
        print(f"🔴 QUÁ HẠN HC ({len(overdue)} thiết bị):")
        for row in overdue:
            print(f"  {row[0]} | {row[2]} | {row[3]} | hết hạn: {row[4]}")
    
    if warning:
        print(f"⚠️ SẮP HẾT HẠN HC < {days_warning} ngày ({len(warning)} thiết bị):")
        for row in warning:
            print(f"  {row[0]} | {row[2]} | {row[3]} | hết hạn: {row[4]}")
    
    if no_date:
        print(f"❓ CHƯA CÓ NGÀY HC ({len(no_date)} thiết bị):")
        for row in no_date:
            print(f"  {row[0]} | {row[2]} | {row[3]}")
    
    if not overdue and not warning and not no_date:
        print("✅ Tất cả thiết bị đều còn hạn HC.")
    
    return {
        "overdue": overdue,
        "warning": warning,
        "no_date": no_date
    }

def main():
    parser = argparse.ArgumentParser(description='Check calibration expiry')
    parser.add_argument('--days-warning', type=int, default=30, 
                        help='Warning threshold in days (default: 30)')
    args = parser.parse_args()
    check_calibration(args.days_warning)

if __name__ == '__main__':
    main()
