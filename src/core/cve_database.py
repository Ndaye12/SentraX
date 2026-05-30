#!/usr/bin/env python3
"""Base de donnees CVE pour correlation des vulnerabilites"""

import json
import sqlite3
import os
from datetime import datetime
from pathlib import Path

class CVEDatabase:
    """Base de donnees des vulnerabilites connues"""
    
    def __init__(self):
        self.db_path = Path(__file__).parent.parent.parent / "data" / "cve.db"
        self.init_database()
        self.load_known_vulnerabilities()
    
    def init_database(self):
        """Initialise la base de donnees SQLite"""
        os.makedirs(self.db_path.parent, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table des CVEs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cves (
                id TEXT PRIMARY KEY,
                port INTEGER,
                service TEXT,
                description TEXT,
                severity TEXT,
                cvss_score REAL,
                published_date TEXT,
                exploit_available INTEGER DEFAULT 0
            )
        ''')
        
        # Table des services vulnerables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vulnerable_services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                port INTEGER,
                service TEXT,
                version_pattern TEXT,
                cve_id TEXT,
                FOREIGN KEY (cve_id) REFERENCES cves(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_known_vulnerabilities(self):
        """Charge les CVE connues"""
        # Vulnerabilites connues par port/service
        self.vulnerabilities = {
            21: {
                'service': 'FTP',
                'cves': [
                    {'id': 'CVE-2020-1938', 'name': 'Ghostcat', 'severity': 'CRITICAL', 'cvss': 9.8},
                    {'id': 'CVE-2019-17566', 'name': 'FTP Buffer Overflow', 'severity': 'HIGH', 'cvss': 8.1}
                ]
            },
            22: {
                'service': 'SSH',
                'cves': [
                    {'id': 'CVE-2023-38408', 'name': 'SSH RCE', 'severity': 'CRITICAL', 'cvss': 9.8},
                    {'id': 'CVE-2020-15778', 'name': 'SSH Command Injection', 'severity': 'HIGH', 'cvss': 7.8}
                ]
            },
            80: {
                'service': 'HTTP',
                'cves': [
                    {'id': 'CVE-2021-41773', 'name': 'Apache Path Traversal', 'severity': 'HIGH', 'cvss': 7.5},
                    {'id': 'CVE-2017-5638', 'name': 'Struts2 RCE', 'severity': 'CRITICAL', 'cvss': 9.8},
                    {'id': 'CVE-2014-0160', 'name': 'Heartbleed', 'severity': 'HIGH', 'cvss': 7.5}
                ]
            },
            443: {
                'service': 'HTTPS',
                'cves': [
                    {'id': 'CVE-2014-0160', 'name': 'Heartbleed', 'severity': 'HIGH', 'cvss': 7.5},
                    {'id': 'CVE-2017-7679', 'name': 'Apache Mod_SSL', 'severity': 'MEDIUM', 'cvss': 5.9}
                ]
            },
            3306: {
                'service': 'MySQL',
                'cves': [
                    {'id': 'CVE-2023-21912', 'name': 'MySQL RCE', 'severity': 'HIGH', 'cvss': 7.5},
                    {'id': 'CVE-2018-2696', 'name': 'MySQL Privilege Escalation', 'severity': 'HIGH', 'cvss': 7.2}
                ]
            },
            3389: {
                'service': 'RDP',
                'cves': [
                    {'id': 'CVE-2019-0708', 'name': 'BlueKeep', 'severity': 'CRITICAL', 'cvss': 9.8},
                    {'id': 'CVE-2020-0610', 'name': 'RDP RCE', 'severity': 'HIGH', 'cvss': 8.1}
                ]
            },
            445: {
                'service': 'SMB',
                'cves': [
                    {'id': 'CVE-2017-0144', 'name': 'EternalBlue', 'severity': 'CRITICAL', 'cvss': 9.3},
                    {'id': 'CVE-2020-0796', 'name': 'SMBGhost', 'severity': 'CRITICAL', 'cvss': 9.8}
                ]
            },
            6379: {
                'service': 'Redis',
                'cves': [
                    {'id': 'CVE-2022-0543', 'name': 'Redis RCE', 'severity': 'CRITICAL', 'cvss': 9.8},
                    {'id': 'CVE-2021-32762', 'name': 'Redis Lua Sandbox', 'severity': 'HIGH', 'cvss': 7.2}
                ]
            },
            27017: {
                'service': 'MongoDB',
                'cves': [
                    {'id': 'CVE-2019-20925', 'name': 'MongoDB RCE', 'severity': 'HIGH', 'cvss': 8.1},
                    {'id': 'CVE-2021-20330', 'name': 'MongoDB DoS', 'severity': 'MEDIUM', 'cvss': 6.5}
                ]
            }
        }
        
        # Charger dans la base
        self.save_to_database()
    
    def save_to_database(self):
        """Sauvegarde les vulnerabilites dans la base SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for port, data in self.vulnerabilities.items():
            for cve in data['cves']:
                cursor.execute('''
                    INSERT OR REPLACE INTO cves 
                    (id, port, service, description, severity, cvss_score, published_date, exploit_available)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    cve['id'], port, data['service'], cve['name'],
                    cve['severity'], cve['cvss'], datetime.now().isoformat(), 1
                ))
        
        conn.commit()
        conn.close()
    
    def check_vulnerabilities(self, port, service=None, version=None):
        """Verifie les vulnerabilites pour un port/service"""
        vulnerabilities = []
        
        if port in self.vulnerabilities:
            for cve in self.vulnerabilities[port]['cves']:
                vuln = {
                    'port': port,
                    'service': self.vulnerabilities[port]['service'],
                    'cve_id': cve['id'],
                    'name': cve['name'],
                    'severity': cve['severity'],
                    'cvss_score': cve['cvss'],
                    'risk_level': self.get_risk_level(cve['severity'])
                }
                
                # Verifier la version si disponible
                if version and self.check_version_match(service, version, cve['id']):
                    vuln['version_affected'] = True
                
                vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def get_risk_level(self, severity):
        """Convertit la severite en niveau de risque"""
        levels = {
            'CRITICAL': '🔴 CRITIQUE',
            'HIGH': '🟠 ELEVE',
            'MEDIUM': '🟡 MOYEN',
            'LOW': '🟢 FAIBLE'
        }
        return levels.get(severity, '⚪ INCONNU')
    
    def check_version_match(self, service, version, cve_id):
        """Verifie si la version est affectee par une CVE"""
        # Version pattern matching
        version_patterns = {
            'OpenSSH': {
                'CVE-2023-38408': ['7.2', '7.3', '7.4', '7.5', '7.6', '7.7', '7.8', '7.9'],
                'CVE-2020-15778': ['8.0', '8.1', '8.2', '8.3', '8.4', '8.5', '8.6', '8.7', '8.8', '8.9']
            },
            'Apache': {
                'CVE-2021-41773': ['2.4.49', '2.4.50'],
                'CVE-2017-5638': ['2.3.0', '2.3.1', '2.3.2', '2.3.3']
            }
        }
        
        if service in version_patterns and cve_id in version_patterns[service]:
            affected_versions = version_patterns[service][cve_id]
            for v in affected_versions:
                if v in version:
                    return True
        return False
    
    def get_statistics(self):
        """Retourne les statistiques CVE"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT severity, COUNT(*) FROM cves GROUP BY severity')
        by_severity = dict(cursor.fetchall())
        
        cursor.execute('SELECT COUNT(*) FROM cves')
        total = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_cves': total,
            'by_severity': by_severity
        }

# Singleton pour utilisation globale
cve_db = CVEDatabase()