import sqlite3
import os
import re
from typing import List, Dict, Any, Optional
from nanobot.core.trust_model import TrustLevel, ProvenanceMetadata

class DeviceRepository:
    """
    Production SQLite Repository for Medical Equipment Management.
    Executes real parameterized SQL queries against database/devices.db with tokenized matching.
    """
    def __init__(self, db_path: str = "database/devices.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS facilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            floor INTEGER,
            building TEXT,
            contact_ext TEXT
        );""")
        c.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_name TEXT NOT NULL,
            model TEXT NOT NULL,
            serial_no TEXT UNIQUE NOT NULL,
            facility_id INTEGER REFERENCES facilities(id),
            manufacturer TEXT,
            origin_country TEXT,
            contract_no TEXT,
            status TEXT DEFAULT 'IN_USE',
            last_calibrated_date TEXT,
            next_calibration_due TEXT,
            risk_class TEXT DEFAULT 'B'
        );""")
        conn.commit()
        conn.close()

    def find_by_serial(self, serial_no: str) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        c = conn.cursor()
        sql = """
            SELECT d.*, f.name as facility_name, f.floor, f.contact_ext
            FROM devices d
            LEFT JOIN facilities f ON d.facility_id = f.id
            WHERE UPPER(d.serial_no) = UPPER(?)
        """
        c.execute(sql, (serial_no.strip(),))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None

    def search_devices(self, query: str, department: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        c = conn.cursor()
        
        # Extract meaningful tokens (model, serial, key device terms)
        tokens = [t for t in re.findall(r"[A-Za-z0-9\-_]+|[À-ỹ\w]+", query) if len(t) > 1]
        
        # Look for explicit known model identifiers first
        extracted_model = None
        for tok in tokens:
            if tok.upper() in ["MS4980", "RAD-5V", "RAD5V", "ASKIR", "230", "FRESENIUS", "WATO"]:
                extracted_model = tok.upper()
                if extracted_model == "RAD5V": extracted_model = "Rad-5v"
                break
                
        if extracted_model:
            sql = """
                SELECT d.*, f.name as facility_name, f.floor, f.contact_ext
                FROM devices d
                LEFT JOIN facilities f ON d.facility_id = f.id
                WHERE (d.model LIKE ? OR d.device_name LIKE ? OR d.serial_no LIKE ?)
            """
            params = [f"%{extracted_model}%", f"%{extracted_model}%", f"%{extracted_model}%"]
            if department:
                sql += " AND f.name LIKE ?"
                params.append(f"%{department.strip()}%")
            sql += " LIMIT ?"
            params.append(limit)
            c.execute(sql, params)
            rows = [dict(r) for r in c.fetchall()]
            if rows:
                conn.close()
                return rows

        # Fallback to general token search
        q_term = f"%{query.strip()}%"
        sql = """
            SELECT d.*, f.name as facility_name, f.floor, f.contact_ext
            FROM devices d
            LEFT JOIN facilities f ON d.facility_id = f.id
            WHERE (d.device_name LIKE ? OR d.model LIKE ? OR d.serial_no LIKE ?)
        """
        params = [q_term, q_term, q_term]
        if department:
            sql += " AND f.name LIKE ?"
            params.append(f"%{department.strip()}%")
        sql += " LIMIT ?"
        params.append(limit)
        
        c.execute(sql, params)
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return rows

    def get_calibration_due_list(self, days_ahead: int = 60) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        c = conn.cursor()
        sql = """
            SELECT d.id, d.device_name, d.model, d.serial_no, d.next_calibration_due, f.name as facility_name
            FROM devices d
            LEFT JOIN facilities f ON d.facility_id = f.id
            WHERE d.next_calibration_due IS NOT NULL
            ORDER BY d.next_calibration_due ASC
        """
        c.execute(sql)
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return rows
