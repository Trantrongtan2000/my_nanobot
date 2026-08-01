#!/usr/bin/env python3
"""Update asset status with audit log."""

import argparse
import sqlite3
from datetime import datetime

DB_PATH = "/home/tan/.nanobot/workspace/data/qltb_assets.db"

def update_status(asset_tag, status, note=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get current status
    cursor.execute("SELECT status FROM assets WHERE asset_tag = ?", (asset_tag,))
    row = cursor.fetchone()
    if not row:
        print(f"Asset not found: {asset_tag}")
        return False
    
    old_status = row[0]
    now = datetime.now().isoformat()
    
    # Update status
    cursor.execute(
        "UPDATE assets SET status = ?, notes = ?, updated_at = ? WHERE asset_tag = ?",
        (status, note, now, asset_tag)
    )
    
    # Audit log
    cursor.execute('''
        INSERT INTO audit_log (asset_tag, action, field, old_value, new_value, timestamp)
        VALUES (?, 'status_change', 'status', ?, ?, ?)
    ''', (asset_tag, old_status, status, now))
    
    conn.commit()
    conn.close()
    print(f"Updated {asset_tag}: {old_status} → {status}")
    return True

def main():
    parser = argparse.ArgumentParser(description='Update QLTB asset status')
    parser.add_argument('--asset', required=True, help='Asset tag')
    parser.add_argument('--status', required=True, 
                        choices=['active', 'maintenance', 'retired', 'transferred'],
                        help='New status')
    parser.add_argument('--note', help='Note for this change')
    
    args = parser.parse_args()
    update_status(args.asset, args.status, args.note)

if __name__ == '__main__':
    main()
