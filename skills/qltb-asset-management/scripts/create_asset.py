#!/usr/bin/env python3
"""
Create QLTB asset from wiki entity.
Inspired by Snipe-IT.
"""

import argparse
import json
import os
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = "/home/tan/.nanobot/workspace/data/qltb_assets.db"

def init_db():
    """Initialize SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_tag TEXT UNIQUE NOT NULL,
            serial_number TEXT,
            model TEXT,
            manufacturer TEXT,
            ref TEXT,
            department TEXT,
            location TEXT,
            custodian TEXT,
            status TEXT DEFAULT 'active',
            purchase_date TEXT,
            warranty_expiry TEXT,
            calibration_date TEXT,
            calibration_expiry TEXT,
            calibration_label TEXT,
            notes TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_tag TEXT,
            action TEXT,
            field TEXT,
            old_value TEXT,
            new_value TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def load_entity(entity_path):
    """Load wiki entity from markdown file."""
    with open(entity_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    entity_data = {}
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    entity_data[key.strip()] = value.strip().strip('"')
    return entity_data

def create_asset(entity_data):
    """Create asset in database."""
    init_db()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Generate asset_tag if not exists
    asset_tag = entity_data.get('asset_tag')
    if not asset_tag:
        serial = entity_data.get('serial', 'UNKNOWN')
        asset_tag = f"TA5.HT.{serial[-6:]}"
    
    now = datetime.now().isoformat()
    
    cursor.execute('''
        INSERT OR REPLACE INTO assets (
            asset_tag, serial_number, model, manufacturer, ref,
            department, location, custodian, status,
            purchase_date, warranty_expiry, calibration_date,
            calibration_expiry, calibration_label, notes,
            created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        asset_tag,
        entity_data.get('serial'),
        entity_data.get('model'),
        entity_data.get('manufacturer'),
        entity_data.get('ref'),
        entity_data.get('department'),
        entity_data.get('location'),
        entity_data.get('custodian'),
        entity_data.get('status', 'active'),
        entity_data.get('purchase_date'),
        entity_data.get('warranty_expiry'),
        entity_data.get('calibration_date'),
        entity_data.get('calibration_expiry'),
        entity_data.get('calibration_label'),
        entity_data.get('notes'),
        now,
        now
    ))
    
    conn.commit()
    conn.close()
    
    return asset_tag

def main():
    parser = argparse.ArgumentParser(description='Create QLTB asset from wiki entity')
    parser.add_argument('--entity', required=True, help='Path to wiki entity markdown file')
    parser.add_argument('--asset-tag', help='Custom asset tag')
    
    args = parser.parse_args()
    
    entity_data = load_entity(args.entity)
    
    if args.asset_tag:
        entity_data['asset_tag'] = args.asset_tag
    
    asset_tag = create_asset(entity_data)
    print(f"Asset created: {asset_tag}")

if __name__ == '__main__':
    main()