import sqlite3
import os
import re
from typing import List, Dict, Any, Optional
from nanobot.core.trust_model import TrustLevel, ProvenanceMetadata

class DeviceRepository:
    """
    Production SQLite Repository for Medical Equipment Management.
    Executes precise tokenized parameterized SQL queries against database/devices.db with multi-word search
    across device models, names, serials, and facility names.
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
        
        # Proper Unicode tokenization
        raw_tokens = re.findall(r"[\w\-]+", query, flags=re.UNICODE)
        stopwords = {
            "tra", "cứu", "tìm", "xem", "cho", "kiểm", "thiết", "bị", "tại", "ở", "khoa",
            "phòng", "của", "các", "những", "danh", "sách", "máy", "vị", "trí", "số", "nằm",
            "đặt", "đang", "hỏi", "biết", "hiện", "có"
        }
        tokens = [t for t in raw_tokens if len(t) >= 2 and t.lower() not in stopwords]
        
        # 1. Multi-token parameterized AND search (including facility name)
        if tokens:
            where_clauses = []
            params = []
            for tok in tokens:
                where_clauses.append("(d.model LIKE ? OR d.device_name LIKE ? OR d.serial_no LIKE ? OR d.manufacturer LIKE ? OR f.name LIKE ?)")
                p = f"%{tok}%"
                params.extend([p, p, p, p, p])
            
            sql = f"""
                SELECT d.*, f.name as facility_name, f.floor, f.contact_ext
                FROM devices d
                LEFT JOIN facilities f ON d.facility_id = f.id
                WHERE {' AND '.join(where_clauses)}
            """
            if department:
                sql += " AND f.name LIKE ?"
                params.append(f"%{department.strip()}%")
            sql += " LIMIT ?"
            params.append(limit)
            
            c.execute(sql, params)
            rows = [dict(r) for r in c.fetchall()]
            conn.close()
            return rows

        # 2. Substring fallback
        q_term = f"%{query.strip()}%"
        sql = """
            SELECT d.*, f.name as facility_name, f.floor, f.contact_ext
            FROM devices d
            LEFT JOIN facilities f ON d.facility_id = f.id
            WHERE (d.device_name LIKE ? OR d.model LIKE ? OR d.serial_no LIKE ? OR f.name LIKE ?)
        """
        params = [q_term, q_term, q_term, q_term]
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
              AND date(d.next_calibration_due) <= date('now', '+' || ? || ' days')
            ORDER BY d.next_calibration_due ASC
        """
        c.execute(sql, (days_ahead,))
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return rows
