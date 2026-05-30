"""Base de données pour l'historique des scans"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

class ScanDatabase:
    def __init__(self):
        self.db_path = Path(__file__).parent.parent.parent / "data" / "scans.db"
        self.db_path.parent.mkdir(exist_ok=True)
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id TEXT UNIQUE,
                target TEXT,
                scanner TEXT,
                results TEXT,
                status TEXT,
                created_at TIMESTAMP,
                completed_at TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def save_scan(self, scan_id, target, scanner, results, status):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO scans (scan_id, target, scanner, results, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (scan_id, target, scanner, json.dumps(results), status, datetime.now()))
        conn.commit()
        conn.close()
    
    def get_scan(self, scan_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT target, scanner, results, status, created_at FROM scans WHERE scan_id = ?', (scan_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'target': row[0],
                'scanner': row[1],
                'results': json.loads(row[2]) if row[2] else None,
                'status': row[3],
                'created_at': row[4]
            }
        return None
    
    def get_all_scans(self, limit=50):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT scan_id, target, scanner, status, created_at FROM scans ORDER BY created_at DESC LIMIT ?', (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [{'scan_id': r[0], 'target': r[1], 'scanner': r[2], 'status': r[3], 'created_at': r[4]} for r in rows]