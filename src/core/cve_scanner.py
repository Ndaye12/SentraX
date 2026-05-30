#!/usr/bin/env python3
"""Scanner de vulnérabilités CVE"""

import re

# Base de données CVE simplifiée
CVE_DATABASE = [
    {
        'id': 'CVE-2017-0144',
        'name': 'EternalBlue',
        'port': 445,
        'service': 'smb',
        'severity': 'CRITICAL',
        'cvss': 9.3,
        'check': lambda banner: 'Windows' in banner and 'SMB' in banner
    },
    {
        'id': 'CVE-2019-0708',
        'name': 'BlueKeep',
        'port': 3389,
        'service': 'rdp',
        'severity': 'CRITICAL',
        'cvss': 9.8,
        'check': lambda banner: 'Windows' in banner
    },
    {
        'id': 'CVE-2021-41773',
        'name': 'Apache Path Traversal',
        'port': 80,
        'service': 'http',
        'severity': 'HIGH',
        'cvss': 7.5,
        'check': lambda banner: 'Apache/2.4.49' in banner or 'Apache/2.4.50' in banner
    },
    {
        'id': 'CVE-2014-0160',
        'name': 'Heartbleed',
        'port': 443,
        'service': 'https',
        'severity': 'HIGH',
        'cvss': 7.5,
        'check': lambda banner: 'OpenSSL' in banner
    },
    {
        'id': 'CVE-2020-0796',
        'name': 'SMBGhost',
        'port': 445,
        'service': 'smb',
        'severity': 'CRITICAL',
        'cvss': 9.8,
        'check': lambda banner: 'Windows 10' in banner
    }
]

def check_vulnerabilities(port, service, banner):
    """Vérifie les vulnérabilités connues pour un service"""
    
    vulnerabilities = []
    
    for cve in CVE_DATABASE:
        if cve['port'] == port or cve['service'].lower() == service.lower():
            try:
                if cve['check'](banner):
                    vulnerabilities.append({
                        'cve_id': cve['id'],
                        'name': cve['name'],
                        'severity': cve['severity'],
                        'cvss_score': cve['cvss'],
                        'port': port,
                        'service': service
                    })
            except:
                pass
    
    return vulnerabilities

def get_risk_level(severity):
    """Retourne le niveau de risque en texte"""
    levels = {
        'CRITICAL': '🔴 CRITIQUE',
        'HIGH': '🟠 ELEVE',
        'MEDIUM': '🟡 MOYEN',
        'LOW': '🟢 FAIBLE'
    }
    return levels.get(severity, '⚪ INCONNU')